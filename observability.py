from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@dataclass(frozen=True)
class RecommendationTrace:
    symbol: str
    action: str
    confidence: float
    time_horizon: str
    trace: Dict[str, Any]
    created_at: str


class Observability:
    """
    Minimal observability layer:
    - structured JSON logs (stdout)
    - optional Supabase persistence (if configured)
    """

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self._client = None

        if self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client

                self._client = create_client(self.supabase_url, self.supabase_key)
            except Exception:
                self._client = None

    def log_recommendation(self, payload: Dict[str, Any]) -> None:
        """
        Payload is expected to contain recommendation fields + trace dict.
        """
        # 1) Structured log
        try:
            import json

            print(json.dumps({"type": "recommendation", "ts": _utc_now(), **payload}, default=str))
        except Exception:
            pass

        # 2) Persist to Supabase if available
        if not self._client:
            return
        try:
            self._client.table("recommendations").insert(payload).execute()
        except Exception:
            # Never break the request path on observability failures
            return

    def log_recommendation_outcome(self, payload: Dict[str, Any]) -> None:
        """
        Log realized outcomes for later calibration/evaluation.
        This is intentionally best-effort and non-blocking.
        """
        try:
            import json

            print(json.dumps({"type": "recommendation_outcome", "ts": _utc_now(), **(payload or {})}, default=str))
        except Exception:
            pass

