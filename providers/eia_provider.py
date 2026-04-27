"""
EIA (Energy Information Administration) API Provider
Documentation: https://www.eia.gov/opendata/documentation.php
"""

import requests
import pandas as pd
from datetime import datetime, timezone
from typing import Optional, Dict, List
import logging
from config import config

logger = logging.getLogger(__name__)


class EIAProvider:
    """
    EIA API provider for energy and economic data
    Free API with no rate limits
    """
    
    def __init__(self):
        self.api_key = config.EIA_API_KEY
        self.base_url = "https://api.eia.gov/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        if not self.api_key:
            logger.warning("EIA API key not configured")
            return None
            
        try:
            params = params or {}
            params['api_key'] = self.api_key
            
            response = self.session.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if 'error' in data:
                logger.error(f"EIA API error: {data['error']}")
                return None
                
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"EIA request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"EIA unexpected error: {e}")
            return None
    
    def get_electricity_retail_sales(self, state: str = 'CO', 
                                    start_date: str = None, 
                                    end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Get retail electricity sales data by state
        
        Args:
            state: State abbreviation (e.g., 'CO', 'TX', 'CA')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with electricity sales data
        """
        params = {
            'frequency': 'monthly',
            'data[0]': 'value',
            'facets[seriesid][]': f'ELEC.SALES.{state}-RES.A',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc'
        }
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        data = self._make_request('electricity/retail-sales/data', params)
        
        if not data or 'response' not in data:
            return None
        
        records = data['response']['data']
        
        df = pd.DataFrame(records)
        
        if 'period' in df.columns:
            df['period'] = pd.to_datetime(df['period'])
            df.set_index('period', inplace=True)
            df.sort_index(inplace=True)
        
        return df
    
    def get_natural_gas_prices(self, area: str = 'RG-EPP', 
                              start_date: str = None,
                              end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Get natural gas prices
        
        Args:
            area: Area code (e.g., 'RG-EPP' for Henry Hub)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with natural gas price data
        """
        params = {
            'frequency': 'daily',
            'data[0]': 'value',
            'facets[seriesid][]': f'NG.{area}.PR',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc'
        }
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        data = self._make_request('natural-gas/prices/data', params)
        
        if not data or 'response' not in data:
            return None
        
        records = data['response']['data']
        
        df = pd.DataFrame(records)
        
        if 'period' in df.columns:
            df['period'] = pd.to_datetime(df['period'])
            df.set_index('period', inplace=True)
            df.sort_index(inplace=True)
        
        return df
    
    def get_petroleum_prices(self, series_id: str = 'PET.RWTC.D',
                            start_date: str = None,
                            end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Get petroleum prices
        
        Args:
            series_id: EIA series ID (e.g., 'PET.RWTC.D' for WTI crude)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with petroleum price data
        """
        params = {
            'frequency': 'daily',
            'data[0]': 'value',
            'facets[seriesid][]': series_id,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc'
        }
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        data = self._make_request('petroleum/prices/data', params)
        
        if not data or 'response' not in data:
            return None
        
        records = data['response']['data']
        
        df = pd.DataFrame(records)
        
        if 'period' in df.columns:
            df['period'] = pd.to_datetime(df['period'])
            df.set_index('period', inplace=True)
            df.sort_index(inplace=True)
        
        return df
    
    def get_coal_production(self, start_date: str = None,
                           end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Get coal production data
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with coal production data
        """
        params = {
            'frequency': 'monthly',
            'data[0]': 'value',
            'facets[seriesid][]': 'COAL.PROD.TOT-US-T',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc'
        }
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        data = self._make_request('coal/production/data', params)
        
        if not data or 'response' not in data:
            return None
        
        records = data['response']['data']
        
        df = pd.DataFrame(records)
        
        if 'period' in df.columns:
            df['period'] = pd.to_datetime(df['period'])
            df.set_index('period', inplace=True)
            df.sort_index(inplace=True)
        
        return df
    
    def get_renewable_energy(self, series_id: str = None,
                           start_date: str = None,
                           end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Get renewable energy data
        
        Args:
            series_id: EIA series ID for renewable energy
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with renewable energy data
        """
        if not series_id:
            series_id = 'RENEW.TOT.CONS-US-T'
        
        params = {
            'frequency': 'monthly',
            'data[0]': 'value',
            'facets[seriesid][]': series_id,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc'
        }
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        data = self._make_request('total-energy/data', params)
        
        if not data or 'response' not in data:
            return None
        
        records = data['response']['data']
        
        df = pd.DataFrame(records)
        
        if 'period' in df.columns:
            df['period'] = pd.to_datetime(df['period'])
            df.set_index('period', inplace=True)
            df.sort_index(inplace=True)
        
        return df
    
    def search_series(self, keyword: str) -> Optional[List[Dict]]:
        """
        Search for data series by keyword
        
        Args:
            keyword: Search term
            
        Returns:
            List of matching series
        """
        # Use the seriesid endpoint to search
        data = self._make_request(f'seriesid/{keyword}')
        
        if not data or 'response' not in data:
            return None
        
        return data['response']['data']
