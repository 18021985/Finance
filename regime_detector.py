from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Regime:
    volatility_regime: str  # low/medium/high
    trend_regime: str  # bullish/neutral/bearish
    correlation_regime: Optional[str] = None  # risk-on/risk-off/neutral


class RegimeDetector:
    """
    Lightweight regime detection to stabilize recommendations across environments.
    This is intentionally simple and fast; it becomes more powerful once
    evaluation + observability are in place.
    """

    def detect_from_prices(self, prices: pd.Series) -> Regime:
        prices = prices.dropna()
        if len(prices) < 60:
            return Regime(volatility_regime="medium", trend_regime="neutral", correlation_regime=None)

        rets = prices.pct_change().dropna()
        vol = float(rets.rolling(20).std().iloc[-1])
        vol_ann = vol * np.sqrt(252)

        if vol_ann < 0.15:
            vol_regime = "low"
        elif vol_ann < 0.25:
            vol_regime = "medium"
        else:
            vol_regime = "high"

        ma20 = float(prices.rolling(20).mean().iloc[-1])
        ma60 = float(prices.rolling(60).mean().iloc[-1])
        if ma20 > ma60 * 1.01:
            trend_regime = "bullish"
        elif ma20 < ma60 * 0.99:
            trend_regime = "bearish"
        else:
            trend_regime = "neutral"

        return Regime(volatility_regime=vol_regime, trend_regime=trend_regime, correlation_regime=None)

    def detect(self, stock_data: pd.DataFrame, macro: Optional[Dict] = None) -> Dict:
        if stock_data is None or stock_data.empty or "Close" not in stock_data:
            return Regime(volatility_regime="medium", trend_regime="neutral", correlation_regime=None).__dict__

        reg = self.detect_from_prices(stock_data["Close"])

        # Macro overlay: if VIX-like indicator exists, upgrade risk-off when high
        corr_regime = reg.correlation_regime
        try:
            vix = None
            if macro and isinstance(macro, dict):
                vix = macro.get("vix") or (macro.get("risk_sentiment", {}) if isinstance(macro.get("risk_sentiment"), dict) else {}).get("vix")
            if vix and float(vix) >= 25:
                corr_regime = "risk-off"
        except Exception:
            pass

        return Regime(
            volatility_regime=reg.volatility_regime,
            trend_regime=reg.trend_regime,
            correlation_regime=corr_regime,
        ).__dict__

