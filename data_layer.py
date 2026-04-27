import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from config import config
from providers.market_data import CachedProvider, YFinanceMarketDataProvider
from news_events import enrich_news_items
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

class DataLayer:
    """Data layer using free APIs: yfinance and Alpha Vantage"""
    
    def __init__(self):
        self.alpha_vantage_key = config.ALPHA_VANTAGE_API_KEY
        self.last_request_time = 0
        self.request_count = 0
        # Pluggable market data provider (yfinance fallback)
        self.market_data = CachedProvider(YFinanceMarketDataProvider(), quote_ttl_seconds=15, bars_ttl_seconds=60)

        # Extra TTL caches for expensive yfinance calls (notably ticker.info and news)
        self._cache: Dict[str, tuple] = {}
        self._executor = ThreadPoolExecutor(max_workers=6)

    def _call_with_timeout(self, fn, timeout_s: float, fallback=None):
        """
        Run blocking provider calls with a hard timeout.
        This prevents yfinance/network stalls from hanging API requests.
        """
        try:
            fut = self._executor.submit(fn)
            return fut.result(timeout=timeout_s)
        except FuturesTimeoutError:
            return fallback
        except Exception:
            return fallback

    def _cache_get(self, key: str, ttl_seconds: int):
        import time

        now = time.time()
        item = self._cache.get(key)
        if not item:
            return None
        ts, val = item
        if (now - ts) <= ttl_seconds:
            return val
        return None

    def _cache_set(self, key: str, val):
        import time

        self._cache[key] = (time.time(), val)
        
    def _rate_limit(self):
        """Rate limiting for Alpha Vantage free tier (5 requests/minute)"""
        current_time = time.time()
        if current_time - self.last_request_time < 12:  # 12 seconds between requests
            time.sleep(12 - (current_time - self.last_request_time))
        self.last_request_time = time.time()
        self.request_count += 1
        
    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Get historical stock data using yfinance (free, no rate limits)
        Enforces timeout to prevent blocking.
        Includes data quality safeguards.

        Args:
            symbol: Stock ticker (e.g., 'AAPL', 'RELIANCE.NS')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        """
        def _fetch():
            data = self.market_data.get_bars(symbol, period=period, interval="1d")
            if data is None or data.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            # Data quality guard: ensure ascending unique index
            try:
                data = data[~data.index.duplicated(keep="last")].sort_index()
            except Exception:
                pass
            # Data quality safeguards
            data = self._apply_data_quality_safeguards(data, symbol)
            return data

        result = self._call_with_timeout(_fetch, timeout_s=10.0, fallback=None)
        if result is None:
            raise Exception(f"Timeout fetching stock data for {symbol}")
        return result

    def _apply_data_quality_safeguards(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Apply data quality safeguards to stock data.
        - Handle missing values
        - Detect and handle outliers
        - Validate data consistency
        """
        if data is None or data.empty:
            return data

        try:
            # Remove any rows with missing critical data (Open, High, Low, Close)
            critical_cols = ['Open', 'High', 'Low', 'Close']
            data = data.dropna(subset=critical_cols, how='any')

            # Forward-fill remaining missing values (e.g., Volume)
            data = data.ffill().bfill()

            # Remove rows with unrealistic values
            # Price must be positive
            for col in critical_cols:
                data = data[data[col] > 0]

            # High >= Low
            data = data[data['High'] >= data['Low']]

            # Close within High-Low range
            data = data[(data['Close'] <= data['High']) & (data['Close'] >= data['Low'])]

            # Remove extreme outliers (prices > 10x median or < 0.1x median)
            if len(data) > 10:
                median_close = data['Close'].median()
                data = data[data['Close'] <= median_close * 10]
                data = data[data['Close'] >= median_close * 0.1]

            # Ensure minimum data points (at least 20 days)
            if len(data) < 20:
                raise ValueError(f"Insufficient data quality for {symbol}: only {len(data)} points after cleaning")

        except Exception as e:
            # If safeguards fail, return original data with warning
            print(f"Warning: Data quality safeguards failed for {symbol}: {str(e)}")
            # Still apply basic deduplication
            try:
                data = data[~data.index.duplicated(keep="last")].sort_index()
            except:
                pass

        return data

    def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get near-current quote (provider-dependent; may be delayed on yfinance).
        Enforces timeout to prevent blocking.
        """
        def _fetch():
            q = self.market_data.get_quote(symbol)
            if q is None:
                return None
            return {
                "symbol": q.symbol,
                "price": q.price,
                "timestamp": q.timestamp.isoformat(),
                "currency": q.currency,
                "bid": q.bid,
                "ask": q.ask,
                "source": q.source,
            }

        return self._call_with_timeout(_fetch, timeout_s=5.0, fallback=None)
    
    def get_company_info(self, symbol: str) -> Dict:
        """Get company information using yfinance"""
        try:
            cached = self._cache_get(f"company_info:{symbol}", ttl_seconds=6 * 3600)
            if cached:
                return cached

            def _fetch_info():
                ticker = yf.Ticker(symbol)
                return ticker.info

            info = self._call_with_timeout(_fetch_info, timeout_s=4.0, fallback={}) or {}
            
            # Extract key fundamentals and convert to float
            result = {
                'symbol': symbol,
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': float(info.get('marketCap', 0) or 0),
                'current_price': float(info.get('currentPrice', info.get('regularMarketPrice', 0)) or 0),
                'pe_ratio': float(info.get('forwardPE', info.get('trailingPE', 0)) or 0),
                'pb_ratio': float(info.get('priceToBook', 0) or 0),
                'dividend_yield': float(info.get('dividendYield', 0) or 0),
                'beta': float(info.get('beta', 0) or 0),
                'revenue': float(info.get('totalRevenue', 0) or 0),
                'profit_margin': float(info.get('profitMargins', 0) or 0),
                'operating_margin': float(info.get('operatingMargins', 0) or 0),
                'return_on_equity': float(info.get('returnOnEquity', 0) or 0),
                'debt_to_equity': float(info.get('debtToEquity', 0) or 0),
                'free_cash_flow': float(info.get('freeCashflow', 0) or 0),
                'earnings_growth': float(info.get('earningsQuarterlyGrowth', 0) or 0),
                'revenue_growth': float(info.get('revenueGrowth', 0) or 0),
                '52_week_high': float(info.get('fiftyTwoWeekHigh', 0) or 0),
                '52_week_low': float(info.get('fiftyTwoWeekLow', 0) or 0),
            }
            self._cache_set(f"company_info:{symbol}", result)
            return result
        except Exception as e:
            raise Exception(f"Error fetching company info for {symbol}: {str(e)}")
    
    def get_fundamental_data(self, symbol: str) -> Dict:
        """
        Get detailed fundamental data using Alpha Vantage (free tier)
        Note: Limited to 25 requests/day
        Enforces timeout to prevent blocking.
        """
        cached = self._cache_get(f"fundamentals:{symbol}", ttl_seconds=6 * 3600)
        if cached:
            return cached

        if not self.alpha_vantage_key:
            # Fallback to yfinance if no Alpha Vantage key
            result = self.get_company_info(symbol)
            self._cache_set(f"fundamentals:{symbol}", result)
            return result

        def _fetch_fundamentals():
            self._rate_limit()

            # Get overview data
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }

            response = requests.get(url, params=params, timeout=8)
            data = response.json()

            if 'Error Message' in data or not data:
                raise ValueError(f"Invalid symbol or API error")

            result = {
                'symbol': symbol,
                'name': data.get('Name', ''),
                'sector': data.get('Sector', ''),
                'industry': data.get('Industry', ''),
                'market_cap': float(data.get('MarketCapitalization', 0)),
                'pe_ratio': float(data.get('PERatio', 0)),
                'pb_ratio': float(data.get('PriceToBookRatio', 0)),
                'dividend_yield': float(data.get('DividendYield', 0)) / 100 if data.get('DividendYield') else 0,
                'beta': float(data.get('Beta', 0)),
                'revenue': float(data.get('RevenueTTM', 0)),
                'profit_margin': float(data.get('ProfitMargin', 0)) / 100 if data.get('ProfitMargin') else 0,
                'operating_margin': float(data.get('OperatingMarginTTM', 0)) / 100 if data.get('OperatingMarginTTM') else 0,
                'return_on_equity': float(data.get('ReturnOnEquityTTM', 0)) / 100 if data.get('ReturnOnEquityTTM') else 0,
                'debt_to_equity': float(data.get('DebtToEquity', 0)),
                'eps': float(data.get('EPS', 0)),
                '52_week_high': float(data.get('52WeekHigh', 0)),
                '52_week_low': float(data.get('52WeekLow', 0)),
            }
            self._cache_set(f"fundamentals:{symbol}", result)
            return result

        try:
            return self._call_with_timeout(_fetch_fundamentals, timeout_s=8.0, fallback=None) or {}
        except Exception as e:
            # Fallback to yfinance on error
            print(f"Alpha Vantage error, falling back to yfinance: {str(e)}")
            result = self.get_company_info(symbol)
            self._cache_set(f"fundamentals:{symbol}", result)
            return result
    
    def get_news_sentiment(self, symbol: str, days: int = 7) -> List[Dict]:
        """
        Get news for sentiment analysis using free sources
        For now, we'll use yfinance news (free)
        """
        try:
            cached = self._cache_get(f"news:v2:{symbol}", ttl_seconds=10 * 60)
            if cached:
                return cached

            def _fetch_news():
                ticker = yf.Ticker(symbol)
                return ticker.news

            news = self._call_with_timeout(_fetch_news, timeout_s=4.0, fallback=[]) or []
            
            if not news:
                return []
            
            articles = []
            for item in news[:20]:  # Limit to 20 articles
                # yfinance payloads vary by version/provider; normalize robustly.
                if isinstance(item, dict) and isinstance(item.get("content"), dict):
                    c = item.get("content") or {}
                    provider = c.get("provider") if isinstance(c.get("provider"), dict) else {}
                    link = None
                    for k in ("canonicalUrl", "clickThroughUrl"):
                        u = c.get(k)
                        if isinstance(u, dict) and u.get("url"):
                            link = u.get("url")
                            break
                    if not link and isinstance(c.get("previewUrl"), str):
                        link = c.get("previewUrl")

                    pub = c.get("pubDate") or c.get("displayTime") or 0
                    # pubDate can be ISO string; keep as-is (news_events handles missing/unparseable)
                    articles.append(
                        {
                            "title": c.get("title", "") or "",
                            "link": link or "",
                            "published": pub,
                            "source": provider.get("displayName") or provider.get("sourceId") or "",
                        }
                    )
                elif isinstance(item, dict):
                    articles.append(
                        {
                            "title": item.get("title", "") or "",
                            "link": item.get("link", "") or "",
                            "published": item.get("providerPublishTime", 0) or 0,
                            "source": item.get("publisher", "") or "",
                        }
                    )
                else:
                    articles.append({"title": "", "link": "", "published": 0, "source": ""})

            # Enrich with event taxonomy + credibility + recency decay + headline sentiment
            enriched = enrich_news_items(articles)
            self._cache_set(f"news:v2:{symbol}", enriched)
            return enriched
        except Exception as e:
            print(f"Error fetching news for {symbol}: {str(e)}")
            return []
    
    def get_market_indices(self) -> Dict[str, float]:
        """Get major market indices using yfinance"""
        indices = {
            'S&P 500': '^GSPC',
            'NASDAQ': '^IXIC',
            'DOW JONES': '^DJI',
            'NIFTY 50': '^NSEI',
        }
        
        data = {}
        for name, symbol in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                data[name] = info.get('regularMarketPrice', 0)
            except:
                continue
        
        return data
    
    def get_macro_indicators(self) -> Dict:
        """
        Get macroeconomic indicators
        Using yfinance for ETFs that track macro indicators
        """
        macro_etfs = {
            'interest_rates': 'TLT',  # 20+ Year Treasury Bond
            'inflation': 'TIP',  # TIPS
            'dollar': 'UUP',  # US Dollar Index
        }
        
        data = {}
        for name, symbol in macro_etfs.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")
                if not hist.empty:
                    data[name] = {
                        'current': hist['Close'].iloc[-1],
                        'change_1m': (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
                    }
            except:
                continue
        
        return data
