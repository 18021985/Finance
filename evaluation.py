from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def max_drawdown(equity: pd.Series) -> float:
    if equity.empty:
        return 0.0
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return float(dd.min())


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    r = returns.dropna()
    if r.empty or float(r.std()) == 0.0:
        return 0.0
    # daily sharpe annualized
    excess = r - (risk_free_rate / 252.0)
    return float((excess.mean() / excess.std()) * np.sqrt(252))


def brier_score(probs: List[float], outcomes: List[int]) -> float:
    if not probs or len(probs) != len(outcomes):
        return 0.0
    p = np.array(probs, dtype=float)
    y = np.array(outcomes, dtype=float)
    return float(np.mean((p - y) ** 2))


def hit_rate(pred_up: List[int], actual_up: List[int]) -> float:
    if not pred_up or len(pred_up) != len(actual_up):
        return 0.0
    p = np.array(pred_up, dtype=int)
    y = np.array(actual_up, dtype=int)
    return float(np.mean(p == y))


@dataclass(frozen=True)
class WalkForwardResult:
    horizon_days: int
    n_predictions: int
    hit_rate: float
    brier: float
    avg_return: float
    sharpe: float
    max_drawdown: float


def walk_forward_direction_eval(
    close_prices: pd.Series,
    prob_up_series: pd.Series,
    horizon_days: int = 20,
    step_days: int = 5,
) -> Dict:
    """
    Evaluate directional probability forecasts in a walk-forward manner.

    - prob_up_series: aligned with close_prices index; each value is P(up over horizon)
    - actual outcome: whether future return over horizon is positive
    """
    px = close_prices.dropna()
    p = prob_up_series.reindex(px.index).dropna()
    px = px.reindex(p.index)

    if len(px) < (horizon_days + 30):
        return {"error": "Insufficient data for walk-forward evaluation"}

    probs: List[float] = []
    outcomes: List[int] = []
    pred_labels: List[int] = []
    actual_labels: List[int] = []
    realized_returns: List[float] = []

    idx = list(px.index)
    for i in range(0, len(idx) - horizon_days, step_days):
        t0 = idx[i]
        t1 = idx[i + horizon_days]
        r = float(px.loc[t1] / px.loc[t0] - 1.0)
        y = 1 if r > 0 else 0
        prob = float(p.loc[t0])
        probs.append(max(0.0, min(1.0, prob)))
        outcomes.append(y)
        pred_labels.append(1 if prob >= 0.5 else 0)
        actual_labels.append(y)
        realized_returns.append(r)

    ret_series = pd.Series(realized_returns)
    eq = (1 + ret_series.fillna(0)).cumprod()

    res = WalkForwardResult(
        horizon_days=horizon_days,
        n_predictions=len(probs),
        hit_rate=hit_rate(pred_labels, actual_labels),
        brier=brier_score(probs, outcomes),
        avg_return=float(ret_series.mean()) if not ret_series.empty else 0.0,
        sharpe=sharpe_ratio(ret_series),
        max_drawdown=max_drawdown(eq),
    )
    return {
        **res.__dict__,
        "avg_return_pct": round(res.avg_return * 100, 3),
        "max_drawdown_pct": round(res.max_drawdown * 100, 3),
    }

