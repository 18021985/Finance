"""
iTick API Provider
Provides market data using iTick API
"""
import requests
import logging
from typing import Dict, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ITickAPIProvider:
    """Provider for market data using iTick API"""
    
    def __init__(self, api_key: str, base_url: str = "https://api-free.itick.org"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json',
            'token': api_key  # iTick uses 'token' header, not 'Authorization'
        })
    
    def get_stock_kline(self, region: str, code: str, kType: int = 2, limit: int = 10) -> Dict:
        """
        Get stock kline (candlestick) data
        region: Market region (e.g., 'IN' for India, 'HK' for Hong Kong)
        code: Stock symbol/code
        kType: Kline type (1=1min, 2=5min, 3=15min, 4=30min, 5=60min, 6=24h, 7=7d, 8=30d)
        limit: Number of data points
        """
        try:
            url = f"{self.base_url}/stock/kline"
            params = {
                'region': region,
                'code': code,
                'kType': kType,
                'limit': limit
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check if API returned success
            if data.get('code') == 0:
                return data.get('data', [])
            else:
                logger.error(f"iTick API error: {data.get('msg', 'Unknown error')}")
                return {"error": data.get('msg', 'Unknown error')}
        except Exception as e:
            logger.error(f"Failed to get kline data for {code}: {e}")
            return {"error": str(e)}
    
    def get_indices_kline(self, region: str, code: str, kType: int = 2, limit: int = 10) -> Dict:
        """Get indices kline data"""
        try:
            url = f"{self.base_url}/indices/kline"
            params = {
                'region': region,
                'code': code,
                'kType': kType,
                'limit': limit
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 0:
                return data.get('data', [])
            else:
                logger.error(f"iTick API error: {data.get('msg', 'Unknown error')}")
                return {"error": data.get('msg', 'Unknown error')}
        except Exception as e:
            logger.error(f"Failed to get indices kline for {code}: {e}")
            return {"error": str(e)}
    
    def get_nifty_50(self) -> Dict:
        """Get NIFTY 50 index data"""
        try:
            # Try NIFTY 50 with India region
            data = self.get_indices_kline(region='IN', code='NIFTY50', kType=6, limit=1)
            if data and not data.get('error') and len(data) > 0:
                latest = data[0]
                return {
                    'lastPrice': float(latest.get('c', 0) or 0),
                    'pChange': 0.0,  # Need previous close to calculate
                    'timestamp': latest.get('t')
                }
            return {"error": "NIFTY 50 not found"}
        except Exception as e:
            logger.error(f"Failed to get NIFTY 50: {e}")
            return {"error": str(e)}
    
    def get_stock_quote(self, region: str, code: str) -> Dict:
        """Get stock quote using kline data"""
        try:
            data = self.get_stock_kline(region=region, code=code, kType=6, limit=1)
            if data and not data.get('error') and len(data) > 0:
                latest = data[0]
                return {
                    'lastPrice': float(latest.get('c', 0) or 0),
                    'high': float(latest.get('h', 0) or 0),
                    'low': float(latest.get('l', 0) or 0),
                    'open': float(latest.get('o', 0) or 0),
                    'volume': float(latest.get('v', 0) or 0),
                    'timestamp': latest.get('t')
                }
            return {"error": "No data available"}
        except Exception as e:
            logger.error(f"Failed to get quote for {code}: {e}")
            return {"error": str(e)}
