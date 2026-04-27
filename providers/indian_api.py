"""
Indian Stock Exchange API Provider
Uses indianapi.in for Indian stock market data
"""
import requests
import logging
from typing import Dict, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class IndianAPIProvider:
    """Provider for Indian stock market data using indianapi.in"""
    
    def __init__(self, base_url: str = "https://indianapi.in"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_stock_data(self, name: str) -> Dict:
        """Get stock data by company name"""
        try:
            url = f"{self.base_url}/stock"
            params = {'name': name}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get stock data for {name}: {e}")
            return {"error": str(e)}
    
    def get_trending_stocks(self) -> Dict:
        """Get trending stocks (top gainers/losers)"""
        try:
            url = f"{self.base_url}/trending"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get trending stocks: {e}")
            return {"error": str(e)}
    
    def get_nifty_50_data(self) -> Dict:
        """Get NIFTY 50 data by fetching a major NIFTY stock"""
        try:
            # Use RELIANCE as a proxy for market data
            data = self.get_stock_data("Reliance")
            if data and not data.get('error'):
                return {
                    'lastPrice': data.get('currentPrice', {}).get('NSE', 0),
                    'pChange': data.get('percentChange', 0),
                    'yearHigh': data.get('yearHigh', 0),
                    'yearLow': data.get('yearLow', 0)
                }
            return {"error": "Failed to fetch NIFTY data"}
        except Exception as e:
            logger.error(f"Failed to get NIFTY 50 data: {e}")
            return {"error": str(e)}
    
    def get_stock_quote(self, name: str) -> Dict:
        """Get stock quote"""
        try:
            data = self.get_stock_data(name)
            if data and not data.get('error'):
                return {
                    'lastPrice': data.get('currentPrice', {}).get('NSE', 0),
                    'high': data.get('yearHigh', 0),
                    'low': data.get('yearLow', 0),
                    'percentChange': data.get('percentChange', 0),
                    'tickerId': data.get('tickerId', ''),
                    'companyName': data.get('companyName', '')
                }
            return {"error": "No data available"}
        except Exception as e:
            logger.error(f"Failed to get quote for {name}: {e}")
            return {"error": str(e)}
