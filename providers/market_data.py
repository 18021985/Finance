from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional, Protocol, Tuple

import pandas as pd


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: float
    timestamp: datetime
    currency: Optional[str] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    source: str = "unknown"


class MarketDataProvider(Protocol):
    """
    Provider abstraction so the system can swap between:
    - yfinance (fallback/free)
    - broker/data APIs (near-real-time quotes)
    - market-specific feeds (India, crypto, FX)
    """

    def get_bars(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        ...

    def get_quote(self, symbol: str) -> Optional[Quote]:
        ...


class CachedProvider:
    """
    Thin caching decorator around any MarketDataProvider.
    Keeps API usage low and ensures consistent timestamps.
    """

    def __init__(
        self,
        inner: MarketDataProvider,
        quote_ttl_seconds: int = 15,
        bars_ttl_seconds: int = 60,
    ):
        self._inner = inner
        self._quote_ttl = quote_ttl_seconds
        self._bars_ttl = bars_ttl_seconds

        self._quote_cache: Dict[str, Tuple[float, Quote]] = {}
        self._bars_cache: Dict[Tuple[str, str, str], Tuple[float, pd.DataFrame]] = {}

    def get_bars(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        import time

        key = (symbol, period, interval)
        now = time.time()
        cached = self._bars_cache.get(key)
        if cached and (now - cached[0]) < self._bars_ttl:
            return cached[1].copy()

        df = self._inner.get_bars(symbol, period=period, interval=interval)
        self._bars_cache[key] = (now, df.copy())
        return df

    def get_quote(self, symbol: str) -> Optional[Quote]:
        import time

        now = time.time()
        cached = self._quote_cache.get(symbol)
        if cached and (now - cached[0]) < self._quote_ttl:
            return cached[1]

        q = self._inner.get_quote(symbol)
        if q is not None:
            self._quote_cache[symbol] = (now, q)
        return q


class YFinanceMarketDataProvider:
    """
    yfinance-based provider.
    Note: yfinance data timeliness varies by asset and market.
    """

    def get_bars(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        import yfinance as yf

        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df is None or df.empty:
            return pd.DataFrame()

        # Normalize index timezone if missing (pandas often returns tz-naive)
        idx = df.index
        if getattr(idx, "tz", None) is None:
            df = df.copy()
            df.index = df.index.tz_localize(timezone.utc)
        return df

    def get_quote(self, symbol: str) -> Optional[Quote]:
        import yfinance as yf

        ticker = yf.Ticker(symbol)

        # Prefer fast_info when available (lighter than full info)
        price = None
        currency = None
        try:
            fast = getattr(ticker, "fast_info", None)
            if fast:
                price = fast.get("last_price") or fast.get("lastPrice") or fast.get("regular_market_price")
                currency = fast.get("currency")
        except Exception:
            price = None

        if price is None:
            try:
                info = ticker.info
                currency = info.get("currency")
                price = info.get("currentPrice", info.get("regularMarketPrice"))
            except Exception:
                return None

        if price is None:
            return None

        return Quote(
            symbol=symbol,
            price=float(price),
            timestamp=datetime.now(tz=timezone.utc),
            currency=currency,
            source="yfinance",
        )

