import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AssetAnalysis:
    """Analysis result for any asset class"""
    asset: str
    asset_class: str  # 'equity', 'bond', 'commodity', 'crypto', 'forex'
    current_price: float
    trend: str
    momentum: str
    technical_score: float
    fundamental_score: float
    macro_alignment: str
    composite_score: float
    insight: str
    strategic_consideration: str

class MultiAssetAnalyzer:
    """
    Multi-asset analysis supporting:
    - Equities (stocks)
    - Bonds (government, corporate)
    - Commodities (gold, oil, metals, agriculture)
    - Crypto (BTC, ETH, etc.)
    - Forex (currency pairs)
    """
    
    def __init__(self):
        self.asset_mappings = {
            # Equities
            'AAPL': ('equity', 'AAPL'),
            'GOOGL': ('equity', 'GOOGL'),
            'MSFT': ('equity', 'MSFT'),
            
            # Bonds (using ETFs as proxies)
            'TLT': ('bond', 'TLT'),  # 20+ Year Treasury
            'IEF': ('bond', 'IEF'),  # 7-10 Year Treasury
            'LQD': ('bond', 'LQD'),  # Investment Grade Corporate
            
            # Commodities
            'GLD': ('commodity', 'GLD'),  # Gold
            'SLV': ('commodity', 'SLV'),  # Silver
            'USO': ('commodity', 'USO'),  # Oil
            'DBA': ('commodity', 'DBA'),  # Agriculture
            
            # Crypto
            'BTC-USD': ('crypto', 'BTC-USD'),
            'ETH-USD': ('crypto', 'ETH-USD'),
            
            # Forex
            'EURUSD=X': ('forex', 'EURUSD=X'),
            'GBPUSD=X': ('forex', 'GBPUSD=X'),
            'USDJPY=X': ('forex', 'USDJPY=X'),
        }
    
    def analyze_asset(self, symbol: str) -> Dict:
        """
        Analyze any asset class
        
        Args:
            symbol: Asset ticker
        """
        # Determine asset class
        asset_class, ticker = self._get_asset_info(symbol)
        
        if asset_class == 'equity':
            return self._analyze_equity(ticker)
        elif asset_class == 'bond':
            return self._analyze_bond(ticker)
        elif asset_class == 'commodity':
            return self._analyze_commodity(ticker)
        elif asset_class == 'crypto':
            return self._analyze_crypto(ticker)
        elif asset_class == 'forex':
            return self._analyze_forex(ticker)
        else:
            return {'error': f'Unknown asset class for {symbol}'}
    
    def _get_asset_info(self, symbol: str) -> tuple:
        """Get asset class and ticker"""
        if symbol in self.asset_mappings:
            return self.asset_mappings[symbol]
        
        # Auto-detect based on suffix
        if symbol.endswith('-USD'):
            return ('crypto', symbol)
        elif '=' in symbol:
            return ('forex', symbol)
        elif symbol in ['TLT', 'IEF', 'LQD', 'HYG', 'JNK']:
            return ('bond', symbol)
        elif symbol in ['GLD', 'SLV', 'USO', 'DBA', 'GLW']:
            return ('commodity', symbol)
        else:
            return ('equity', symbol)
    
    def _analyze_equity(self, symbol: str) -> Dict:
        """Analyze equity (stock)"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            info = ticker.info
            
            if hist.empty:
                return {'error': f'No data for {symbol}'}
            
            # Technical analysis
            technical = self._calculate_technical_metrics(hist)
            
            # Fundamental analysis
            fundamental = self._calculate_equity_fundamentals(info)
            
            # Generate insight
            insight = self._generate_equity_insight(technical, fundamental)
            
            return {
                'asset': symbol,
                'asset_class': 'equity',
                'current_price': round(float(hist['Close'].iloc[-1]), 2),
                'technical': technical,
                'fundamental': fundamental,
                'insight': insight,
                'strategic_consideration': self._get_equity_strategy(technical, fundamental)
            }
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}
    
    def _analyze_bond(self, symbol: str) -> Dict:
        """Analyze bond (using ETF as proxy)"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return {'error': f'No data for {symbol}'}
            
            # Bond-specific analysis
            technical = self._calculate_technical_metrics(hist)
            
            # Yield analysis (simplified)
            current_price = float(hist['Close'].iloc[-1])
            yield_estimate = self._estimate_bond_yield(symbol, current_price)
            
            # Duration sensitivity
            duration = self._estimate_duration(symbol)
            
            # Generate insight
            insight = self._generate_bond_insight(technical, yield_estimate, duration)
            
            return {
                'asset': symbol,
                'asset_class': 'bond',
                'current_price': round(current_price, 2),
                'estimated_yield': round(yield_estimate, 3),
                'estimated_duration': duration,
                'technical': technical,
                'insight': insight,
                'strategic_consideration': self._get_bond_strategy(technical, yield_estimate)
            }
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}
    
    def _analyze_commodity(self, symbol: str) -> Dict:
        """Analyze commodity"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return {'error': f'No data for {symbol}'}
            
            technical = self._calculate_technical_metrics(hist)
            
            # Commodity-specific factors
            commodity_type = self._identify_commodity_type(symbol)
            seasonal_pattern = self._get_seasonal_pattern(commodity_type)
            
            # Generate insight
            insight = self._generate_commodity_insight(technical, commodity_type)
            
            return {
                'asset': symbol,
                'asset_class': 'commodity',
                'commodity_type': commodity_type,
                'current_price': round(float(hist['Close'].iloc[-1]), 2),
                'technical': technical,
                'seasonal_pattern': seasonal_pattern,
                'insight': insight,
                'strategic_consideration': self._get_commodity_strategy(technical, commodity_type)
            }
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}
    
    def _analyze_crypto(self, symbol: str) -> Dict:
        """Analyze cryptocurrency"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return {'error': f'No data for {symbol}'}
            
            technical = self._calculate_technical_metrics(hist)
            
            # Crypto-specific metrics
            volatility = hist['Close'].pct_change().std() * np.sqrt(252)
            
            # On-chain metrics (placeholder - would need specialized API)
            on_chain = {
                'network_health': 'healthy',
                'adoption_trend': 'growing'
            }
            
            # Generate insight
            insight = self._generate_crypto_insight(technical, volatility)
            
            return {
                'asset': symbol,
                'asset_class': 'crypto',
                'current_price': round(float(hist['Close'].iloc[-1]), 2),
                'technical': technical,
                'volatility': round(float(volatility), 2),
                'on_chain': on_chain,
                'insight': insight,
                'strategic_consideration': self._get_crypto_strategy(technical, volatility)
            }
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}
    
    def _analyze_forex(self, symbol: str) -> Dict:
        """Analyze forex pair"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return {'error': f'No data for {symbol}'}
            
            technical = self._calculate_technical_metrics(hist)
            
            # Forex-specific analysis
            pair = self._parse_forex_pair(symbol)
            rate_differential = self._estimate_rate_differential(pair)
            
            # Generate insight
            insight = self._generate_forex_insight(technical, rate_differential)
            
            return {
                'asset': symbol,
                'asset_class': 'forex',
                'pair': pair,
                'current_rate': round(float(hist['Close'].iloc[-1]), 4),
                'technical': technical,
                'rate_differential': rate_differential,
                'insight': insight,
                'strategic_consideration': self._get_forex_strategy(technical, rate_differential)
            }
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}
    
    def _calculate_technical_metrics(self, hist: pd.DataFrame) -> Dict:
        """Calculate technical metrics for any asset"""
        if len(hist) < 50:
            return {'error': 'Insufficient data'}
        
        current = float(hist['Close'].iloc[-1])
        
        # Moving averages
        sma_20 = float(hist['Close'].rolling(20).mean().iloc[-1])
        sma_50 = float(hist['Close'].rolling(50).mean().iloc[-1])
        sma_200 = float(hist['Close'].rolling(200).mean().iloc[-1])
        
        # RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = float(100 - (100 / (1 + rs.iloc[-1])))
        
        # Trend
        if current > sma_20 > sma_50 > sma_200:
            trend = 'strong_uptrend'
        elif current > sma_50:
            trend = 'uptrend'
        elif current < sma_20 < sma_50 < sma_200:
            trend = 'strong_downtrend'
        elif current < sma_50:
            trend = 'downtrend'
        else:
            trend = 'sideways'
        
        # Momentum
        momentum_20 = float((current / hist['Close'].iloc[-21] - 1) * 100) if len(hist) > 20 else 0.0
        if momentum_20 > 5:
            momentum = 'strong'
        elif momentum_20 > 2:
            momentum = 'moderate'
        elif momentum_20 > -2:
            momentum = 'neutral'
        elif momentum_20 > -5:
            momentum = 'weak'
        else:
            momentum = 'very_weak'
        
        return {
            'trend': trend,
            'momentum': momentum,
            'rsi': round(rsi, 2),
            'above_sma_20': current > sma_20,
            'above_sma_50': current > sma_50,
            'above_sma_200': current > sma_200,
            'momentum_20d': round(momentum_20, 2)
        }
    
    def _calculate_equity_fundamentals(self, info: Dict) -> Dict:
        """Calculate equity fundamentals"""
        return {
            'pe_ratio': info.get('forwardPE', info.get('trailingPE', 0)),
            'pb_ratio': info.get('priceToBook', 0),
            'ev_ebitda': info.get('enterpriseToEbitda', 0),
            'revenue_growth': info.get('revenueGrowth', 0),
            'earnings_growth': info.get('earningsGrowth', 0),
            'profit_margin': info.get('profitMargins', 0),
            'return_on_equity': info.get('returnOnEquity', 0),
            'debt_to_equity': info.get('debtToEquity', 0),
            'dividend_yield': info.get('dividendYield', 0)
        }
    
    def _estimate_bond_yield(self, symbol: str, price: float) -> float:
        """Estimate bond yield from price (simplified)"""
        # In production, would use actual yield data
        if symbol == 'TLT':  # 20+ Year Treasury
            return 4.5  # Approximate current yield
        elif symbol == 'IEF':  # 7-10 Year Treasury
            return 4.2
        elif symbol == 'LQD':  # Investment Grade Corporate
            return 5.0
        else:
            return 4.0
    
    def _estimate_duration(self, symbol: str) -> float:
        """Estimate bond duration"""
        if symbol == 'TLT':
            return 17.0  # High duration
        elif symbol == 'IEF':
            return 7.5
        elif symbol == 'LQD':
            return 8.0
        else:
            return 5.0
    
    def _identify_commodity_type(self, symbol: str) -> str:
        """Identify commodity type"""
        if symbol in ['GLD', 'SLV']:
            return 'precious_metal'
        elif symbol in ['USO', 'CL=F']:
            return 'energy'
        elif symbol in ['DBA']:
            return 'agriculture'
        elif symbol in ['HG=F', 'GLW']:
            return 'industrial_metal'
        else:
            return 'other'
    
    def _get_seasonal_pattern(self, commodity_type: str) -> str:
        """Get seasonal pattern for commodity"""
        patterns = {
            'precious_metal': 'Strength in Q1-Q2, weakness in Q3',
            'energy': 'Strength in summer driving season, winter heating',
            'agriculture': 'Varies by crop planting/harvest cycles',
            'industrial_metal': 'Correlates with economic activity'
        }
        return patterns.get(commodity_type, 'No strong seasonal pattern')
    
    def _parse_forex_pair(self, symbol: str) -> tuple:
        """Parse forex pair"""
        if '=' in symbol:
            base_quote = symbol.replace('=X', '').replace('=', '')
            return base_quote[:3], base_quote[3:]
        return 'USD', 'EUR'
    
    def _estimate_rate_differential(self, pair: tuple) -> float:
        """Estimate interest rate differential"""
        # Simplified - in production would use actual central bank rates
        base, quote = pair
        rates = {
            'USD': 5.25,
            'EUR': 4.50,
            'GBP': 5.25,
            'JPY': 0.00
        }
        return rates.get(base, 0) - rates.get(quote, 0)
    
    # Insight generation methods
    def _generate_equity_insight(self, technical: Dict, fundamental: Dict) -> str:
        """Generate equity insight"""
        trend = technical.get('trend', 'neutral')
        pe = fundamental.get('pe_ratio', 0)
        
        if trend == 'strong_uptrend' and pe < 25:
            return "Strong uptrend with reasonable valuation - favorable setup"
        elif trend == 'uptrend' and pe < 30:
            return "Positive trend with acceptable valuation - consider exposure"
        elif trend == 'downtrend':
            return "Negative trend - wait for stabilization signals"
        else:
            return "Mixed signals - monitor for clarity"
    
    def _get_equity_strategy(self, technical: Dict, fundamental: Dict) -> str:
        """Get equity strategic consideration"""
        return "Consider position sizing based on conviction, monitor macro alignment"
    
    def _generate_bond_insight(self, technical: Dict, yield_estimate: float, duration: float) -> str:
        """Generate bond insight"""
        if yield_estimate > 5 and duration < 10:
            return "Attractive yield with moderate duration - income opportunity"
        elif yield_estimate > 4:
            return "Reasonable yield - consider for income allocation"
        else:
            return "Low yield environment - consider duration risk"
    
    def _get_bond_strategy(self, technical: Dict, yield_estimate: float) -> str:
        """Get bond strategic consideration"""
        return "Consider duration management in rising rate environment"
    
    def _generate_commodity_insight(self, technical: Dict, commodity_type: str) -> str:
        """Generate commodity insight"""
        trend = technical.get('trend', 'neutral')
        if commodity_type == 'precious_metal':
            if trend == 'uptrend':
                return "Precious metals showing strength - potential inflation hedge"
            else:
                return "Precious metals weak - monitor real yields"
        else:
            return f"{commodity_type} {trend} - monitor supply-demand dynamics"
    
    def _get_commodity_strategy(self, technical: Dict, commodity_type: str) -> str:
        """Get commodity strategic consideration"""
        return "Consider as diversification and inflation hedge"
    
    def _generate_crypto_insight(self, technical: Dict, volatility: float) -> str:
        """Generate crypto insight"""
        trend = technical.get('trend', 'neutral')
        if volatility > 0.8:
            risk_note = "High volatility - size positions accordingly"
        else:
            risk_note = "Moderate volatility"
        
        if trend == 'uptrend':
            return f"Positive trend - {risk_note}"
        else:
            return f"Negative trend - {risk_note}"
    
    def _get_crypto_strategy(self, technical: Dict, volatility: float) -> str:
        """Get crypto strategic consideration"""
        return "High volatility asset - limit allocation, use risk management"
    
    def _generate_forex_insight(self, technical: Dict, rate_differential: float) -> str:
        """Generate forex insight"""
        trend = technical.get('trend', 'neutral')
        if rate_differential > 1:
            carry_note = "Positive carry differential"
        elif rate_differential < -1:
            carry_note = "Negative carry differential"
        else:
            carry_note = "Neutral carry"
        
        return f"{trend} with {carry_note}"
    
    def _get_forex_strategy(self, technical: Dict, rate_differential: float) -> str:
        """Get forex strategic consideration"""
        return "Consider macro factors and central bank policies"
