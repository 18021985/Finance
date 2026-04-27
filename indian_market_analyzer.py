import yfinance as yf
import pandas as pd
from typing import Dict, List
from datetime import datetime
import math
import logging
import time

logger = logging.getLogger(__name__)

class IndianMarketAnalyzer:
    """Specialized analyzer for Indian stock market (NSE/BSE)"""
    
    def __init__(self):
        # Configure user-agent to avoid yfinance blocking
        yf.utils.request_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        self.nse_indices = {
            'NIFTY 50': '^NSEI',
            'NIFTY BANK': '^NSEBANK',
            'NIFTY IT': '^CNXIT',
            'NIFTY AUTO': '^CNXAUTO',
            'NIFTY PHARMA': '^CNXPHARMA',
            'SENSEX': '^BSESN',
        }
        
        self.key_stocks = {
            'Reliance': 'RELIANCE.NS',
            'TCS': 'TCS.NS',
            'HDFC Bank': 'HDFCBANK.NS',
            'Infosys': 'INFY.NS',
            'ICICI Bank': 'ICICIBANK.NS',
            'Hindustan Unilever': 'HINDUNILVR.NS',
            'ITC': 'ITC.NS',
            'SBIN': 'SBIN.NS',
            'Bharti Airtel': 'BHARTIARTL.NS',
            'L&T': 'LT.NS',
        }

        # Cache (symbol, period) -> (ts, payload)
        self._cache = {}
        self._cache_ttl_seconds = 10 * 60  # 10 minutes
    
    def _fetch_with_retry(self, fetch_func, max_retries=3, base_delay=1):
        """Retry logic with exponential backoff for yfinance calls"""
        for attempt in range(max_retries):
            try:
                return fetch_func()
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed after {max_retries} retries: {e}")
                    raise
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s delay: {e}")
                time.sleep(delay)
    
    def get_indian_market_overview(self) -> Dict:
        """Get overview of Indian market indices and sectors"""
        logger.info("Fetching Indian market overview")
        overview = {
            'indices': {},
            'sectors': {},
            'market_sentiment': 'neutral',
            'market_cap': None,
            'volume': None,
            'vix': None,
        }
        
        # Fetch major indices
        for name, symbol in self.nse_indices.items():
            def _fetch_index():
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo", timeout=30)
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    change = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
                    overview['indices'][name] = {
                        'current': current,
                        'change': round(change, 2),
                        'symbol': symbol
                    }
                    logger.info(f"Fetched {name}: {current}, change: {change}%")
                else:
                    logger.warning(f"No data for {name} ({symbol})")
            
            try:
                self._fetch_with_retry(_fetch_index, max_retries=2, base_delay=0.5)
            except Exception as e:
                logger.error(f"Failed to fetch {name}: {e}")
                continue
        
        # Fetch India VIX
        def _fetch_vix():
            vix_ticker = yf.Ticker('^INDIAVIX')
            vix_hist = vix_ticker.history(period="1d", timeout=30)
            if not vix_hist.empty:
                overview['vix'] = round(vix_hist['Close'].iloc[-1], 2)
                logger.info(f"Fetched India VIX: {overview['vix']}")
        
        try:
            self._fetch_with_retry(_fetch_vix, max_retries=2, base_delay=0.5)
        except Exception as e:
            logger.error(f"Failed to fetch India VIX: {e}")
        
        # Calculate total market cap from key stocks (approximate)
        total_market_cap = 0
        total_volume = 0
        for name, symbol in self.key_stocks.items():
            def _fetch_stock():
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d", timeout=30)
                if info and not hist.empty:
                    market_cap = info.get('marketCap', 0)
                    volume = hist['Volume'].iloc[-1] if not hist.empty else 0
                    return market_cap, volume
                return 0, 0
            
            try:
                market_cap, volume = self._fetch_with_retry(_fetch_stock, max_retries=2, base_delay=0.5)
                total_market_cap += market_cap
                total_volume += volume
            except Exception as e:
                logger.warning(f"Failed to fetch {name} market cap/volume: {e}")
                continue
        
        if total_market_cap > 0:
            overview['market_cap'] = total_market_cap
            logger.info(f"Total market cap: {total_market_cap}")
        if total_volume > 0:
            overview['volume'] = total_volume
            logger.info(f"Total volume: {total_volume}")
        
        # Add sector performance based on sector indices
        sector_mapping = {
            'IT': 'NIFTY IT',
            'Banking': 'NIFTY BANK',
            'Auto': 'NIFTY AUTO',
            'Pharma': 'NIFTY PHARMA',
        }
        
        for sector, index_name in sector_mapping.items():
            if index_name in overview['indices']:
                overview['sectors'][sector] = {
                    'change': overview['indices'][index_name]['change']
                }
        
        # Determine market sentiment
        nifty_change = overview['indices'].get('NIFTY 50', {}).get('change', 0)
        if nifty_change > 2:
            overview['market_sentiment'] = 'bullish'
        elif nifty_change < -2:
            overview['market_sentiment'] = 'bearish'
        
        logger.info(f"Market overview complete: {len(overview['indices'])} indices, market_cap={overview['market_cap']}, volume={overview['volume']}")
        return self._to_json_safe(overview)
    
    def analyze_indian_stock(self, symbol: str, period: str = "3mo") -> Dict:
        """
        Analyze an Indian stock (NSE/BSE)
        Symbol should include .NS suffix for NSE stocks
        """
        if not symbol.endswith('.NS'):
            symbol = symbol + '.NS'

        # Cache hit
        try:
            import time
            key = (symbol, period)
            cached = self._cache.get(key)
            if cached and (time.time() - cached[0]) < self._cache_ttl_seconds:
                return cached[1]
        except Exception:
            pass
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period=period)
            
            if hist.empty:
                return {'error': f'No data found for {symbol}'}
            
            # Calculate Indian market specific metrics
            analysis = {
                'symbol': symbol,
                'name': info.get('longName', ''),
                'exchange': 'NSE' if '.NS' in symbol else 'BSE',
                'current_price': hist['Close'].iloc[-1],
                'currency': 'INR',
                
                # Price performance
                'performance': {
                    '1d': (hist['Close'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100 if len(hist) > 1 else 0,
                    '1w': (hist['Close'].iloc[-1] / hist['Close'].iloc[-6] - 1) * 100 if len(hist) > 5 else 0,
                    '1m': (hist['Close'].iloc[-1] / hist['Close'].iloc[-21] - 1) * 100 if len(hist) > 20 else 0,
                    '3m': (hist['Close'].iloc[-1] / hist['Close'].iloc[-63] - 1) * 100 if len(hist) > 62 else 0,
                    '1y': (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100 if len(hist) > 0 else 0,
                },
                
                # Valuation metrics
                'valuation': {
                    'pe_ratio': info.get('forwardPE', info.get('trailingPE', 0)),
                    'pb_ratio': info.get('priceToBook', 0),
                    'ev_ebitda': info.get('enterpriseToEbitda', 0),
                    'market_cap': info.get('marketCap', 0),
                },
                
                # Fundamentals
                'fundamentals': {
                    'revenue': info.get('totalRevenue', 0),
                    'profit_margin': info.get('profitMargins', 0),
                    'operating_margin': info.get('operatingMargins', 0),
                    'return_on_equity': info.get('returnOnEquity', 0),
                    'debt_to_equity': info.get('debtToEquity', 0),
                    'dividend_yield': info.get('dividendYield', 0),
                },
                
                # Technical indicators
                'technical': self._calculate_technical_indicators(hist),
                
                # Indian market specific
                'indian_context': {
                    'nifty_comparison': self._compare_to_nifty(hist),
                    'sector_performance': self._get_sector_performance(info.get('sector', '')),
                }
            }
            payload = self._to_json_safe(analysis)
            try:
                import time
                self._cache[(symbol, period)] = (time.time(), payload)
            except Exception:
                pass
            return payload
            
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}
    
    def _to_json_safe(self, obj):
        """
        Convert pandas/numpy scalars to native Python types and remove NaN/inf
        so FastAPI JSON serialization doesn't 500.
        """
        # Pandas / numpy scalars
        try:
            import numpy as np
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                v = float(obj)
                return None if (math.isnan(v) or math.isinf(v)) else v
        except Exception:
            pass

        if isinstance(obj, float):
            return None if (math.isnan(obj) or math.isinf(obj)) else obj
        if isinstance(obj, (int, str, bool)) or obj is None:
            return obj
        if isinstance(obj, dict):
            return {k: self._to_json_safe(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._to_json_safe(v) for v in obj]

        # Pandas Timestamp, etc.
        if hasattr(obj, "to_pydatetime"):
            try:
                return obj.to_pydatetime().isoformat()
            except Exception:
                return str(obj)
        return str(obj)

    def _calculate_technical_indicators(self, hist: pd.DataFrame) -> Dict:
        """Calculate technical indicators for Indian stock"""
        if len(hist) < 50:
            return {}
        
        indicators = {}
        
        # Moving averages
        indicators['sma_20'] = hist['Close'].rolling(window=20).mean().iloc[-1]
        indicators['sma_50'] = hist['Close'].rolling(window=50).mean().iloc[-1]
        indicators['sma_200'] = hist['Close'].rolling(window=200).mean().iloc[-1]
        
        # RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_val = 100 - (100 / (1 + rs.iloc[-1]))
        try:
            rsi_float = float(rsi_val)
            indicators['rsi'] = None if (math.isnan(rsi_float) or math.isinf(rsi_float)) else rsi_float
        except Exception:
            indicators['rsi'] = None
        
        # Bollinger Bands
        sma_20 = hist['Close'].rolling(window=20).mean()
        std_20 = hist['Close'].rolling(window=20).std()
        indicators['bb_upper'] = (sma_20 + 2 * std_20).iloc[-1]
        indicators['bb_lower'] = (sma_20 - 2 * std_20).iloc[-1]
        
        # Support/Resistance
        indicators['recent_high'] = hist['High'].rolling(window=20).max().iloc[-1]
        indicators['recent_low'] = hist['Low'].rolling(window=20).min().iloc[-1]
        
        return indicators
    
    def _compare_to_nifty(self, stock_hist: pd.DataFrame) -> Dict:
        """Compare stock performance to NIFTY 50"""
        try:
            nifty = yf.Ticker('^NSEI')
            nifty_hist = nifty.history(period="1y")
            
            if nifty_hist.empty or len(stock_hist) < 20:
                return {'error': 'Insufficient data for comparison'}
            
            stock_return = (stock_hist['Close'].iloc[-1] / stock_hist['Close'].iloc[-20] - 1) * 100
            nifty_return = (nifty_hist['Close'].iloc[-1] / nifty_hist['Close'].iloc[-20] - 1) * 100
            
            relative_performance = stock_return - nifty_return
            
            return {
                'stock_1m_return': round(stock_return, 2),
                'nifty_1m_return': round(nifty_return, 2),
                'relative_performance': round(relative_performance, 2),
                'outperforming': relative_performance > 0
            }
        except:
            return {'error': 'Could not fetch NIFTY data'}
    
    def _get_sector_performance(self, sector: str) -> Dict:
        """Get sector performance relative to NIFTY"""
        sector_mapping = {
            'Technology': '^CNXIT',
            'Information Technology': '^CNXIT',
            'Financial Services': '^NSEBANK',
            'Banking': '^NSEBANK',
            'Consumer Goods': '^CNXFMC',
            'FMCG': '^CNXFMC',
            'Automobile': '^CNXAUTO',
            'Auto': '^CNXAUTO',
            'Pharmaceuticals': '^CNXPHARMA',
            'Healthcare': '^CNXPHARMA',
        }
        
        sector_symbol = sector_mapping.get(sector)
        if not sector_symbol:
            return {'error': 'Sector index not available'}
        
        try:
            sector_ticker = yf.Ticker(sector_symbol)
            sector_hist = sector_ticker.history(period="1mo")
            
            if sector_hist.empty:
                return {'error': 'No sector data'}
            
            sector_change = (sector_hist['Close'].iloc[-1] / sector_hist['Close'].iloc[0] - 1) * 100
            
            return {
                'sector': sector,
                'sector_index': sector_symbol,
                'change_1m': round(sector_change, 2),
            }
        except:
            return {'error': 'Could not fetch sector data'}
    
    def scan_indian_opportunities(self, symbols: List[str] = None) -> Dict:
        """
        Scan Indian stocks for investment opportunities
        If no symbols provided, scans key Indian stocks
        """
        if symbols is None:
            symbols = list(self.key_stocks.values())
        
        opportunities = []
        
        for symbol in symbols:
            try:
                analysis = self.analyze_indian_stock(symbol)
                if 'error' not in analysis:
                    score = self._calculate_opportunity_score(analysis)
                    if score > 60:
                        opportunities.append({
                            'symbol': symbol,
                            'name': analysis.get('name', ''),
                            'score': score,
                            'current_price': analysis.get('current_price', 0),
                            'verdict': self._get_verdict(score),
                        })
            except Exception as e:
                continue
        
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'opportunities': opportunities[:10],
            'total_analyzed': len(symbols),
            'market_overview': self.get_indian_market_overview()
        }
    
    def _calculate_opportunity_score(self, analysis: Dict) -> float:
        """Calculate opportunity score for Indian stock"""
        score = 50  # Base score
        
        # Performance contribution
        perf_1m = analysis.get('performance', {}).get('1m', 0)
        if perf_1m > 5:
            score += 15
        elif perf_1m > 0:
            score += 5
        elif perf_1m < -5:
            score -= 10
        
        # Valuation contribution
        pe = analysis.get('valuation', {}).get('pe_ratio', 0)
        if 10 < pe < 25:
            score += 10
        elif pe < 10:
            score += 5
        elif pe > 40:
            score -= 10
        
        # Fundamentals contribution
        roe = analysis.get('fundamentals', {}).get('return_on_equity', 0)
        if roe > 0.15:
            score += 15
        elif roe > 0.10:
            score += 5
        
        # Technical contribution
        rsi = analysis.get('technical', {}).get('rsi', 50)
        if 40 < rsi < 60:
            score += 10
        elif rsi < 30:
            score += 5  # Oversold bounce potential
        
        return min(100, max(0, score))
    
    def _get_verdict(self, score: float) -> str:
        """Get verdict based on score"""
        if score > 80:
            return 'Strong Buy'
        elif score > 65:
            return 'Buy'
        elif score > 50:
            return 'Hold'
        elif score > 35:
            return 'Sell'
        else:
            return 'Strong Sell'
    
    def get_indian_market_calendar(self) -> Dict:
        """Get Indian market trading calendar info"""
        return {
            'exchange': 'NSE/BSE',
            'trading_days': 'Monday to Friday',
            'trading_hours': '9:15 AM - 3:30 PM IST',
            'currency': 'INR',
            'settlement_cycle': 'T+1',
            'note': 'Market closed on Indian holidays and weekends'
        }
