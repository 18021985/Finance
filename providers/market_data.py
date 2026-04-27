from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional, Protocol, Tuple
import time
import logging

import pandas as pd

logger = logging.getLogger(__name__)


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

    def __init__(self):
        # Configure user-agent to avoid blocking
        import yfinance as yf
        yf.utils.request_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _retry_with_backoff(self, func, max_retries=3, base_delay=1):
        """Retry logic with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed after {max_retries} retries: {e}")
                    raise
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s delay: {e}")
                time.sleep(delay)

    def get_bars(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        import yfinance as yf

        def _fetch():
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval, timeout=30)
            if df is None or df.empty:
                logger.warning(f"No data returned for {symbol} (period={period})")
                return pd.DataFrame()

            # Normalize index timezone if missing (pandas often returns tz-naive)
            idx = df.index
            if getattr(idx, "tz", None) is None:
                df = df.copy()
                df.index = df.index.tz_localize(timezone.utc)
            return df

        try:
            return self._retry_with_backoff(_fetch, max_retries=3, base_delay=1)
        except Exception as e:
            logger.error(f"Error fetching bars for {symbol}: {e}")
            return pd.DataFrame()

    def get_quote(self, symbol: str) -> Optional[Quote]:
        import yfinance as yf

        def _fetch():
            ticker = yf.Ticker(symbol)

            # Prefer fast_info when available (lighter than full info)
            price = None
            currency = None
            try:
                fast = getattr(ticker, "fast_info", None)
                if fast:
                    price = fast.get("last_price") or fast.get("lastPrice") or fast.get("regular_market_price")
                    currency = fast.get("currency")
            except Exception as e:
                logger.warning(f"Fast info failed for {symbol}: {e}")
                price = None

            if price is None:
                try:
                    info = ticker.info
                    currency = info.get("currency")
                    price = info.get("currentPrice", info.get("regularMarketPrice"))
                except Exception as e:
                    logger.warning(f"Info fetch failed for {symbol}: {e}")
                    return None

            if price is None:
                logger.warning(f"No price found for {symbol}")
                return None

            return Quote(
                symbol=symbol,
                price=float(price),
                timestamp=datetime.now(tz=timezone.utc),
                currency=currency,
                source="yfinance",
            )

        try:
            return self._retry_with_backoff(_fetch, max_retries=2, base_delay=0.5)
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None

