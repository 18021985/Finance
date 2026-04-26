from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ForecastDistribution:
    horizon_days: int
    p10: float
    p50: float
    p90: float
    direction_up_prob: float


class ProbabilisticForecaster:
    """
    Quantile-based forecaster using empirical returns.
    This is robust, explainable, and works without heavy ML dependencies.
    Includes probability calibration to avoid overconfidence.
    """

    def __init__(self):
        # Simple calibration tracking (lightweight for free-data system)
        self._recent_predictions = []  # List of (predicted_prob, actual_outcome)
        self._max_history = 100

    def _apply_calibration(self, raw_prob: float) -> float:
        """
        Apply simple calibration adjustment based on recent prediction accuracy.
        This helps reduce overconfidence by nudging probabilities toward actual performance.
        """
        if not self._recent_predictions or len(self._recent_predictions) < 10:
            return raw_prob

        # Calculate recent calibration factor
        preds = np.array([p for p, _ in self._recent_predictions])
        actuals = np.array([a for _, a in self._recent_predictions])
        
        # Simple calibration: if we've been overconfident, adjust toward 0.5
        # If we've been underconfident, adjust toward extremes
        avg_pred = np.mean(preds)
        avg_actual = np.mean(actuals)
        
        # Calibration adjustment (bounded to avoid extreme shifts)
        calib_shift = (avg_actual - avg_pred) * 0.3  # 30% correction factor
        calib_shift = max(-0.1, min(0.1, calib_shift))  # Bound shift to +/- 10%
        
        calibrated_prob = raw_prob + calib_shift
        return float(max(0.05, min(0.95, calibrated_prob)))  # Keep bounds

    def record_outcome(self, predicted_prob: float, actual_up: bool):
        """
        Record prediction outcome for continuous calibration.
        actual_up: True if price went up, False otherwise
        """
        self._recent_predictions.append((predicted_prob, 1.0 if actual_up else 0.0))
        if len(self._recent_predictions) > self._max_history:
            self._recent_predictions.pop(0)

    def forecast(
        self,
        close_prices: pd.Series,
        horizon_days: int,
        score: float,
    ) -> ForecastDistribution:
        close_prices = close_prices.dropna()
        if len(close_prices) < 80:
            return ForecastDistribution(horizon_days=horizon_days, p10=-0.05, p50=0.0, p90=0.06, direction_up_prob=0.5)

        rets = close_prices.pct_change().dropna()

        # Aggregate horizon returns by rolling sum approximation
        horizon_rets = (1 + rets).rolling(horizon_days).apply(np.prod, raw=True) - 1
        horizon_rets = horizon_rets.dropna()
        if horizon_rets.empty:
            return ForecastDistribution(horizon_days=horizon_days, p10=-0.05, p50=0.0, p90=0.06, direction_up_prob=0.5)

        p10 = float(np.quantile(horizon_rets.values, 0.10))
        p50 = float(np.quantile(horizon_rets.values, 0.50))
        p90 = float(np.quantile(horizon_rets.values, 0.90))

        # Map score (roughly centered at 50) into a probability shift
        # This is intentionally bounded to avoid overconfidence.
        score_shift = max(-0.15, min(0.15, (float(score) - 50.0) / 200.0))
        base_up = float(np.mean(horizon_rets.values > 0))
        raw_prob = float(max(0.05, min(0.95, base_up + score_shift)))

        # Apply calibration to reduce overconfidence
        direction_up_prob = self._apply_calibration(raw_prob)

        return ForecastDistribution(
            horizon_days=horizon_days,
            p10=p10,
            p50=p50,
            p90=p90,
            direction_up_prob=direction_up_prob,
        )

    def forecast_prices(
        self,
        last_price: float,
        dist: ForecastDistribution,
    ) -> Dict:
        lp = float(last_price)
        return {
            "horizon_days": dist.horizon_days,
            "return_quantiles": {"p10": round(dist.p10, 4), "p50": round(dist.p50, 4), "p90": round(dist.p90, 4)},
            "price_quantiles": {
                "p10": round(lp * (1 + dist.p10), 2),
                "p50": round(lp * (1 + dist.p50), 2),
                "p90": round(lp * (1 + dist.p90), 2),
            },
            "direction_up_prob": round(dist.direction_up_prob, 3),
        }

