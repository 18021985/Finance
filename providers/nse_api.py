"""
NSE India API Provider
Uses unofficial NSE API from GitHub as alternative to yfinance
"""
import requests
import logging
from typing import Dict, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class NSEAPIProvider:
    """Provider for NSE India market data using unofficial API"""
    
    def __init__(self, base_url: str = "https://nse-india-api.onrender.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_market_status(self) -> Dict:
        """Get market status"""
        try:
            response = self.session.get(f"{self.base_url}/api/marketStatus", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get market status: {e}")
            return {"status": "unknown", "error": str(e)}
    
    def get_indices(self) -> Dict:
        """Get market indices"""
        try:
            response = self.session.get(f"{self.base_url}/api/indices", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get indices: {e}")
            return {"error": str(e)}
    
    def get_equity(self, symbol: str) -> Dict:
        """Get equity details for a symbol"""
        try:
            response = self.session.get(f"{self.base_url}/api/equity/{symbol}", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get equity {symbol}: {e}")
            return {"error": str(e)}
    
    def get_equity_historical(self, symbol: str) -> Dict:
        """Get historical data for a symbol"""
        try:
            response = self.session.get(f"{self.base_url}/api/equity/{symbol}/historical", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            return {"error": str(e)}
    
    def get_nifty_50_data(self) -> Dict:
        """Get NIFTY 50 index data"""
        try:
            indices = self.get_indices()
            if isinstance(indices, dict) and 'data' in indices:
                for index in indices['data']:
                    if 'NIFTY 50' in str(index.get('name', '')):
                        return index
            return {"error": "NIFTY 50 not found"}
        except Exception as e:
            logger.error(f"Failed to get NIFTY 50 data: {e}")
            return {"error": str(e)}
    
    def get_stock_quote(self, symbol: str) -> Dict:
        """Get stock quote"""
        try:
            equity = self.get_equity(symbol)
            if isinstance(equity, dict) and 'data' in equity:
                return equity['data']
            return {"error": "No data available"}
        except Exception as e:
            logger.error(f"Failed to get quote for {symbol}: {e}")
            return {"error": str(e)}
