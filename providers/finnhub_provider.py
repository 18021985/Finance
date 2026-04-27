"""
Finnhub API Provider for stock market data
Documentation: https://finnhub.io/docs/api
"""

import requests
import pandas as pd
from datetime import datetime, timezone
from typing import Optional, Dict
import logging
from config import config

logger = logging.getLogger(__name__)


class FinnhubProvider:
    """
    Finnhub API provider for real-time and historical stock data
    Free tier: 60 calls/minute
    """
    
    def __init__(self):
        self.api_key = config.FINNHUB_API_KEY
        self.base_url = "https://finnhub.io/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        if not self.api_key:
            logger.warning("Finnhub API key not configured")
            return None
            
        try:
            params = params or {}
            params['token'] = self.api_key
            
            response = self.session.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if 'error' in data:
                logger.error(f"Finnhub API error: {data['error']}")
                return None
                
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Finnhub request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Finnhub unexpected error: {e}")
            return None
    
    def get_stock_candles(self, symbol: str, resolution: str = 'D', 
                         from_ts: int = None, to_ts: int = None) -> Optional[pd.DataFrame]:
        """
        Get stock candles (OHLCV data)
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'RELIANCE.NS')
            resolution: Time resolution (1, 5, 15, 30, 60, D, W, M)
            from_ts: Unix timestamp for start date
            to_ts: Unix timestamp for end date
            
        Returns:
            DataFrame with columns: t (time), o (open), h (high), l (low), c (close), v (volume)
        """
        import time
        
        # Default to 1 year of data if not specified
        if from_ts is None:
            from_ts = int((datetime.now() - pd.Timedelta(days=365)).timestamp())
        if to_ts is None:
            to_ts = int(datetime.now().timestamp())
        
        params = {
            'symbol': symbol,
            'resolution': resolution,
            'from': from_ts,
            'to': to_ts
        }
        
        data = self._make_request('stock/candle', params)
        
        if not data or data.get('s') == 'no_data':
            logger.warning(f"No data returned for {symbol}")
            return None
        
        if data.get('s') != 'ok':
            logger.warning(f"Finnhub returned status: {data.get('s')}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame({
            'Date': pd.to_datetime(data['t'], unit='s'),
            'Open': data['o'],
            'High': data['h'],
            'Low': data['l'],
            'Close': data['c'],
            'Volume': data['v']
        })
        
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        return df
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time quote for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with current price, change, etc.
        """
        data = self._make_request('quote', {'symbol': symbol})
        
        if not data:
            return None
        
        return {
            'symbol': symbol,
            'price': data.get('c'),  # Current price
            'change': data.get('d'),  # Change
            'percent_change': data.get('dp'),  # Percent change
            'high': data.get('h'),  # High price of the day
            'low': data.get('l'),  # Low price of the day
            'open': data.get('o'),  # Open price of the day
            'previous_close': data.get('pc'),  # Previous close price
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """
        Get company profile information
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with company information
        """
        data = self._make_request('stock/profile2', {'symbol': symbol})
        
        if not data:
            return None
        
        return {
            'symbol': symbol,
            'name': data.get('name'),
            'ticker': data.get('ticker'),
            'exchange': data.get('exchange'),
            'industry': data.get('finnhubIndustry'),
            'sector': data.get('sector'),
            'market_cap': data.get('marketCapitalization'),
            'country': data.get('country'),
            'currency': data.get('currency'),
            'ipo': data.get('ipo'),
            'website': data.get('weburl'),
            'logo': data.get('logo')
        }
    
    def get_company_financials(self, symbol: str) -> Optional[Dict]:
        """
        Get company financials (income statement, balance sheet, cash flow)
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with financial data
        """
        # Get basic financial metrics
        data = self._make_request('stock/metric', {'symbol': symbol, 'metric': 'all'})
        
        if not data:
            return None
        
        metric = data.get('metric', {})
        return {
            'symbol': symbol,
            'pe_ratio': metric.get('peBasicExclExtraTTM'),
            'pb_ratio': metric.get('pbQuarterly'),
            'ps_ratio': metric.get('psTTM'),
            'dividend_yield': metric.get('dividendYieldTTM'),
            'roe': metric.get('roeTTM'),
            'debt_to_equity': metric.get('debtToEquityQuarterly'),
            'revenue_growth': metric.get('revenueGrowthTTMYoy'),
            'earnings_growth': metric.get('earningsGrowthTTMYoy'),
            'profit_margin': metric.get('netProfitMarginTTM'),
            'operating_margin': metric.get('operatingMarginTTM')
        }
