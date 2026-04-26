import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os

class MultiSourceDataFetcher:
    """
    Multi-source data fetcher supporting multiple financial data APIs
    
    Sources:
    - Yahoo Finance (primary, free)
    - Alpha Vantage (requires API key)
    - FRED (Federal Reserve Economic Data)
    """
    
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.fred_api_key = os.getenv('FRED_API_KEY')
        
    def get_stock_data(self, symbol: str, period: str = '1y') -> pd.DataFrame:
        """
        Get stock data from Yahoo Finance with fallback to Alpha Vantage
        
        Args:
            symbol: Stock ticker
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        """
        try:
            # Primary: Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            if not data.empty:
                return data
            
            # Fallback: Alpha Vantage (if API key available)
            if self.alpha_vantage_key:
                return self._get_alpha_vantage_data(symbol, period)
                
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
        
        return pd.DataFrame()
    
    def _get_alpha_vantage_data(self, symbol: str, period: str) -> pd.DataFrame:
        """Fetch data from Alpha Vantage API"""
        try:
            from alpha_vantage.timeseries import TimeSeries
            ts = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
            
            # Map period to Alpha Vantage function
            if period in ['1d', '5d']:
                data, _ = ts.get_intraday(symbol, outputsize='full')
            else:
                data, _ = ts.get_daily(symbol, outputsize='full')
            
            return data
        except ImportError:
            print("Alpha Vantage library not installed. Install with: pip install alpha-vantage")
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
        
        return pd.DataFrame()
    
    def get_economic_indicators(self) -> Dict:
        """
        Get economic indicators from multiple sources
        
        Returns:
            Dictionary with GDP, inflation, unemployment, etc.
        """
        indicators = {}
        
        # FRED data (if API key available)
        if self.fred_api_key:
            indicators.update(self._get_fred_indicators())
        
        # Yahoo Finance macro data
        indicators.update(self._get_yahoo_macro_data())
        
        return indicators
    
    def _get_fred_indicators(self) -> Dict:
        """Fetch economic indicators from FRED API"""
        try:
            from fredapi import Fred
            fred = Fred(api_key=self.fred_api_key)
            
            indicators = {
                'gdp': fred.get_series('GDP'),
                'cpi': fred.get_series('CPIAUCSL'),
                'unemployment': fred.get_series('UNRATE'),
                'fed_funds_rate': fred.get_series('FEDFUNDS'),
                '10y_treasury': fred.get_series('GS10'),
            }
            
            # Get latest values
            latest = {}
            for key, series in indicators.items():
                if not series.empty:
                    latest[key] = series.iloc[-1]
            
            return latest
        except ImportError:
            print("FRED library not installed. Install with: pip install fredapi")
        except Exception as e:
            print(f"FRED error: {e}")
        
        return {}
    
    def _get_yahoo_macro_data(self) -> Dict:
        """Fetch macro data from Yahoo Finance"""
        indicators = {}
        
        try:
            # Interest rates
            fed_ticker = yf.Ticker('^IRX')
            fed_data = fed_ticker.history(period='1mo')
            if not fed_data.empty:
                indicators['fed_funds_rate'] = fed_data['Close'].iloc[-1]
            
            # 10Y Treasury
            treasury_ticker = yf.Ticker('^TNX')
            treasury_data = treasury_ticker.history(period='1mo')
            if not treasury_data.empty:
                indicators['10y_treasury'] = treasury_data['Close'].iloc[-1]
            
            # VIX
            vix_ticker = yf.Ticker('^VIX')
            vix_data = vix_ticker.history(period='1mo')
            if not vix_data.empty:
                indicators['vix'] = vix_data['Close'].iloc[-1]
                
        except Exception as e:
            print(f"Yahoo macro data error: {e}")
        
        return indicators
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get historical data for a specific date range
        
        Args:
            symbol: Stock ticker
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            return data
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()
    
    def get_company_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Get news for a company from Yahoo Finance
        
        Args:
            symbol: Stock ticker
            limit: Number of news items to return
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if news:
                return news[:limit]
        except Exception as e:
            print(f"Error fetching news: {e}")
        
        return []
