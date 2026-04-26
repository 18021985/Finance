from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _direction_to_int(direction: str) -> int:
    mapping = {"bullish": 1, "bearish": 0, "neutral": 2}
    return mapping.get((direction or "").lower(), 2)


@dataclass
class AutoLearningCounts:
    predictions_logged: int
    outcomes_logged: int


class AutoLearningStore:
    """
    Supabase-first auto-learning store.

    - Uses Supabase Postgres when SUPABASE_URL + SUPABASE_KEY are set and `supabase` is installed.
    - Falls back to an in-memory store (non-durable) when Supabase isn't configured.
      (This is intentional for local dev; production should configure Supabase.)
    """

    def __init__(self):
        self._supabase = None
        self._fallback: List[Dict[str, Any]] = []

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key:
            try:
                from supabase import create_client  # type: ignore

                self._supabase = create_client(url, key)
            except Exception:
                self._supabase = None

    @property
    def using_supabase(self) -> bool:
        return self._supabase is not None

    def log_prediction(
        self,
        *,
        symbol: str,
        predicted_direction: str,
        predicted_probability: float,
        confidence: float = 0.0,
        model_used: str = "",
        features: Optional[Dict[str, Any]] = None,
    ) -> str:
        payload = {
            "symbol": symbol,
            "timestamp": _utc_now().isoformat(),
            "predicted_direction": predicted_direction,
            "predicted_probability": float(predicted_probability),
            "confidence": float(confidence or 0.0),
            "model_used": model_used or "",
            "features": features or {},
        }

        if self._supabase is not None:
            try:
                res = self._supabase.table("predictions").insert(payload).execute()
                # Supabase returns inserted row(s)
                if getattr(res, "data", None):
                    return str(res.data[0].get("id"))
            except Exception:
                # Fall through to local non-durable store to keep system functional.
                pass

        # fallback (non-durable)
        local_id = f"local_{int(time.time() * 1000)}_{len(self._fallback)}"
        payload["id"] = local_id
        payload["created_at"] = _utc_now().isoformat()
        payload["updated_at"] = _utc_now().isoformat()
        payload["actual_direction"] = None
        payload["actual_return"] = None
        self._fallback.append(payload)
        return local_id

    def update_outcome_by_id(self, *, prediction_id: str, actual_direction: str, actual_return: float) -> bool:
        if not prediction_id:
            return False

        if self._supabase is not None:
            try:
                res = (
                    self._supabase.table("predictions")
                    .update(
                        {
                            "actual_direction": actual_direction,
                            "actual_return": float(actual_return),
                            "updated_at": _utc_now().isoformat(),
                        }
                    )
                    .eq("id", str(prediction_id))
                    .execute()
                )
                data = getattr(res, "data", None) or []
                return len(data) > 0
            except Exception:
                # If DB update fails, attempt local update (best-effort).
                pass

        for p in self._fallback:
            if str(p.get("id")) == str(prediction_id):
                p["actual_direction"] = actual_direction
                p["actual_return"] = float(actual_return)
                p["updated_at"] = _utc_now().isoformat()
                return True
        return False

    def _get_recent_predictions(self, *, limit: int) -> List[Dict[str, Any]]:
        limit = int(limit)
        if limit < 1:
            return []

        if self._supabase is not None:
            try:
                res = (
                    self._supabase.table("predictions")
                    .select("*")
                    .order("timestamp", desc=True)
                    .limit(limit)
                    .execute()
                )
                return list(getattr(res, "data", None) or [])
            except Exception:
                # Fall back to local store if reads fail (RLS/misconfig).
                return list(reversed(self._fallback[-limit:]))

        # fallback: newest first
        return list(reversed(self._fallback[-limit:]))

    def get_counts(self) -> AutoLearningCounts:
        if self._supabase is not None:
            # Cheapest reliable approach without RPC: fetch small windows + approximate is not OK.
            # Instead, do two lightweight selects with count preferences is not consistently supported across clients.
            # We'll compute counts from a bounded recent window for UI purposes only.
            # For production analytics, implement an RPC/count view.
            recent = self._get_recent_predictions(limit=5000)
            # If Supabase returns empty but we have fallback data, use fallback
            if not recent and self._fallback:
                recent = self._fallback
        else:
            recent = self._fallback

        outcomes = [p for p in recent if p.get("actual_direction") is not None]
        return AutoLearningCounts(predictions_logged=len(recent), outcomes_logged=len(outcomes))

    def generate_report(self, *, window_size: int = 200) -> Dict[str, Any]:
        window_size = int(window_size)
        if window_size < 20:
            window_size = 20

        recent = self._get_recent_predictions(limit=window_size)
        completed = [p for p in recent if p.get("actual_direction") is not None]

        counts = self.get_counts()

        # default empty
        overall = {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "total_predictions": counts.predictions_logged,  # Total predictions logged
            "completed_predictions": len(completed),  # Predictions with outcomes
        }

        if len(completed) >= 2:
            import numpy as np
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

            y_pred = [_direction_to_int(p.get("predicted_direction")) for p in completed]
            y_true = [_direction_to_int(p.get("actual_direction")) for p in completed]
            returns = [p.get("actual_return") for p in completed if p.get("actual_return") is not None]
            returns_f = [float(x) for x in returns if x is not None]

            overall["accuracy"] = float(round(accuracy_score(y_true, y_pred), 4))
            overall["precision"] = float(round(precision_score(y_true, y_pred, average="weighted", zero_division=0), 4))
            overall["recall"] = float(round(recall_score(y_true, y_pred, average="weighted", zero_division=0), 4))
            overall["f1_score"] = float(round(f1_score(y_true, y_pred, average="weighted", zero_division=0), 4))

            sharpe = 0.0
            max_dd = 0.0
            if returns_f:
                r = np.array(returns_f, dtype=float)
                std = float(np.std(r))
                sharpe = float(np.mean(r) / std) if std > 0 else 0.0
                cumulative = np.cumprod(1 + r)
                running_max = np.maximum.accumulate(cumulative)
                drawdown = (cumulative - running_max) / running_max
                max_dd = float(np.min(drawdown)) if len(drawdown) else 0.0

            overall["sharpe_ratio"] = float(round(sharpe, 4))
            overall["max_drawdown"] = float(round(max_dd, 4))
            overall["win_rate"] = float(
                round(
                    sum(1 for p in completed if (p.get("actual_direction") == p.get("predicted_direction"))) / len(completed),
                    4,
                )
            )

        return {
            "overall_metrics": overall,
            "symbol_performance": {},
            "model_performance": {},
            "rolling_metrics": [],
            "degradation_detected": False,
            "window_size": window_size,
            "counts": {
                "predictions_logged": int(counts.predictions_logged),
                "outcomes_logged": int(counts.outcomes_logged),
            },
            "last_metrics": overall,
        }

