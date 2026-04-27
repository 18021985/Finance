import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MacroIndicator:
    """Represents a macroeconomic indicator"""
    name: str
    current_value: float
    change_1m: float
    change_3m: float
    change_1y: float
    trend: str  # 'rising', 'falling', 'stable'
    significance: str  # 'high', 'medium', 'low'

@dataclass
class CentralBankPolicy:
    """Represents central bank policy stance"""
    bank: str  # 'Fed', 'ECB', 'BOE', 'BOJ'
    policy_rate: float
    stance: str  # 'hawkish', 'dovish', 'neutral'
    next_meeting: str
    expected_action: str

class MacroAnalyzer:
    """
    Bank-level macro analysis engine
    
    Analyzes:
    - Interest rates (Fed funds, ECB, BOE, BOJ)
    - Inflation (CPI, PPI)
    - Central bank policies
    - Economic indicators (GDP, unemployment, PMI)
    - Yield curve dynamics
    """
    
    def __init__(self):
        self.rate_tickers = {
            'US_10Y': '^TNX',
            'US_2Y': '^FVX',
            'US_30Y': '^TYX',
            # NOTE: Some international yield tickers are unreliable on Yahoo Finance and can spam 404 logs.
            # Add them back only when a stable provider is used.
        }
        
        self.commodity_tickers = {
            'Gold': 'GC=F',
            'Oil': 'CL=F',
            'Copper': 'HG=F',
            'DXY': 'DX-Y.NYB',  # US Dollar Index
        }
    
    def _convert_to_native(self, value: Any) -> Any:
        """Convert numpy types to native Python types for JSON serialization"""
        if isinstance(value, (np.integer, np.int64, np.int32)):
            return int(value)
        elif isinstance(value, (np.floating, np.float64, np.float32)):
            return float(value)
        elif isinstance(value, (np.bool_, bool)):
            return bool(value)
        elif isinstance(value, np.ndarray):
            return value.tolist()
        elif isinstance(value, dict):
            return {k: self._convert_to_native(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._convert_to_native(v) for v in value]
        return value
    
    def get_macro_overview(self) -> Dict:
        """
        Get comprehensive macro overview
        
        Returns:
            Interest rates, inflation trends, central bank stances, yield curve analysis
        """
        overview = {
            'interest_rates': self._analyze_interest_rates(),
            'inflation': self._analyze_inflation(),
            'central_banks': self._analyze_central_banks(),
            'yield_curve': self._analyze_yield_curve(),
            'commodities': self._analyze_commodities(),
            'risk_sentiment': self._assess_risk_sentiment(),
            'economic_cycle': self._identify_economic_cycle(),
        }
        
        return self._convert_to_native(overview)

    # Backwards-compatible alias (older callers used analyze_macro)
    def analyze_macro(self) -> Dict:
        return self.get_macro_overview()
    
    def _analyze_interest_rates(self) -> Dict:
        """Analyze interest rate environment"""
        rates = {}
        
        for name, ticker in self.rate_tickers.items():
            try:
                data = yf.Ticker(ticker).history(period="3mo")
                if not data.empty:
                    current = float(data['Close'].iloc[-1])
                    change_1m = float((data['Close'].iloc[-1] / data['Close'].iloc[-21] - 1) * 100) if len(data) > 20 else 0.0
                    change_3m = float((data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100) if len(data) > 0 else 0.0
                    
                    trend = 'rising' if change_3m > 0.5 else 'falling' if change_3m < -0.5 else 'stable'
                    
                    rates[name] = {
                        'current': round(current, 3),
                        'change_1m': round(change_1m, 3),
                        'change_3m': round(change_3m, 3),
                        'trend': trend
                    }
            except:
                continue
        
        return rates
    
    def _analyze_inflation(self) -> Dict:
        """
        Analyze inflation trends
        
        Note: This uses market-based inflation expectations (TIPS breakeven rates)
        as proxy for actual CPI data which requires paid APIs
        """
        inflation = {
            'US_CPI_Expectation': {
                'current': 2.5,  # Placeholder - would use FRED API in production
                'trend': 'stable',
                'significance': 'high'
            },
            'Eurozone_CPI_Expectation': {
                'current': 2.3,
                'trend': 'falling',
                'significance': 'high'
            },
            'interpretation': self._interpret_inflation_environment()
        }
        
        return inflation
    
    def _interpret_inflation_environment(self) -> str:
        """Interpret current inflation environment"""
        # Simplified logic - in production would use actual data
        return "Moderate inflation with disinflationary trends in developed markets"
    
    def _analyze_central_banks(self) -> Dict:
        """Analyze central bank policy stances"""
        central_banks = {
            'Federal Reserve': CentralBankPolicy(
                bank='Fed',
                policy_rate=5.25,
                stance='hawkish',
                next_meeting='2024-06-12',
                expected_action='hold'
            ),
            'European Central Bank': CentralBankPolicy(
                bank='ECB',
                policy_rate=4.50,
                stance='neutral',
                next_meeting='2024-06-06',
                expected_action='hold'
            ),
            'Bank of England': CentralBankPolicy(
                bank='BOE',
                policy_rate=5.25,
                stance='hawkish',
                next_meeting='2024-06-20',
                expected_action='hold'
            ),
            'Bank of Japan': CentralBankPolicy(
                bank='BOJ',
                policy_rate=0.00,
                stance='dovish',
                next_meeting='2024-06-14',
                expected_action='hold'
            )
        }
        
        return {
            bank: {
                'policy_rate': policy.policy_rate,
                'stance': policy.stance,
                'next_meeting': policy.next_meeting,
                'expected_action': policy.expected_action
            }
            for bank, policy in central_banks.items()
        }
    
    def _analyze_yield_curve(self) -> Dict:
        """Analyze yield curve dynamics"""
        try:
            us_10y = yf.Ticker('^TNX').history(period="1mo")
            us_2y = yf.Ticker('^FVX').history(period="1mo")
            
            if not us_10y.empty and not us_2y.empty:
                current_10y = us_10y['Close'].iloc[-1]
                current_2y = us_2y['Close'].iloc[-1]
                spread = current_10y - current_2y
                
                # Interpret yield curve
                if spread > 0.5:
                    curve_shape = 'normal'
                    interpretation = 'Normal yield curve suggests economic expansion'
                elif spread > -0.5:
                    curve_shape = 'flat'
                    interpretation = 'Flat yield curve suggests economic uncertainty'
                else:
                    curve_shape = 'inverted'
                    interpretation = 'Inverted yield curve suggests recession risk'
                
                return {
                    '10y_rate': round(current_10y, 3),
                    '2y_rate': round(current_2y, 3),
                    'spread': round(spread, 3),
                    'curve_shape': curve_shape,
                    'interpretation': interpretation,
                    'recession_indicator': spread < 0
                }
        except:
            pass
        
        return {'error': 'Unable to fetch yield curve data'}
    
    def _analyze_commodities(self) -> Dict:
        """Analyze commodity prices as macro indicators"""
        commodities = {}
        
        for name, ticker in self.commodity_tickers.items():
            try:
                data = yf.Ticker(ticker).history(period="3mo")
                if not data.empty:
                    current = data['Close'].iloc[-1]
                    change_1m = (data['Close'].iloc[-1] / data['Close'].iloc[-21] - 1) * 100 if len(data) > 20 else 0
                    
                    commodities[name] = {
                        'current': round(current, 2),
                        'change_1m': round(change_1m, 2),
                        'trend': 'rising' if change_1m > 2 else 'falling' if change_1m < -2 else 'stable'
                    }
            except:
                continue
        
        return commodities
    
    def _assess_risk_sentiment(self) -> Dict:
        """Assess overall risk sentiment (risk-on vs risk-off)"""
        try:
            # Use VIX as fear gauge
            vix = yf.Ticker('^VIX').history(period="1mo")
            
            if not vix.empty:
                current_vix = vix['Close'].iloc[-1]
                
                # Interpret VIX
                if current_vix < 15:
                    sentiment = 'risk-on'
                    interpretation = 'Low volatility suggests complacency/risk-seeking behavior'
                elif current_vix < 25:
                    sentiment = 'neutral'
                    interpretation = 'Normal volatility levels'
                elif current_vix < 35:
                    sentiment = 'risk-off'
                    interpretation = 'Elevated volatility suggests risk aversion'
                else:
                    sentiment = 'extreme risk-off'
                    interpretation = 'High volatility suggests fear/panic'
                
                return {
                    'vix': round(current_vix, 2),
                    'sentiment': sentiment,
                    'interpretation': interpretation
                }
        except:
            pass
        
        return {'error': 'Unable to assess risk sentiment'}
    
    def _identify_economic_cycle(self) -> Dict:
        """Identify current economic cycle phase"""
        # Simplified cycle identification
        # In production, would use GDP growth, unemployment, PMI, etc.
        
        cycle_phases = ['expansion', 'peak', 'contraction', 'trough']
        
        # Based on yield curve and risk sentiment
        yield_curve = self._analyze_yield_curve()
        risk_sentiment = self._assess_risk_sentiment()
        
        if yield_curve.get('curve_shape') == 'inverted':
            phase = 'contraction'
            confidence = 0.7
        elif yield_curve.get('curve_shape') == 'flat':
            phase = 'peak'
            confidence = 0.6
        elif risk_sentiment.get('sentiment') == 'risk-on':
            phase = 'expansion'
            confidence = 0.6
        else:
            phase = 'expansion'
            confidence = 0.5
        
        return {
            'current_phase': phase,
            'confidence': confidence,
            'characteristics': self._get_cycle_characteristics(phase)
        }
    
    def _get_cycle_characteristics(self, phase: str) -> Dict:
        """Get characteristics of economic cycle phase"""
        characteristics = {
            'expansion': {
                'equities': 'generally bullish',
                'bonds': 'bearish (rising rates)',
                'commodities': 'bullish',
                'strategy': 'growth-oriented allocation'
            },
            'peak': {
                'equities': 'cautious',
                'bonds': 'mixed',
                'commodities': 'peak demand',
                'strategy': 'defensive positioning'
            },
            'contraction': {
                'equities': 'bearish',
                'bonds': 'bullish (falling rates)',
                'commodities': 'bearish',
                'strategy': 'capital preservation'
            },
            'trough': {
                'equities': 'opportunity',
                'bonds': 'bullish',
                'commodities': 'bottoming',
                'strategy': 'accumulation phase'
            }
        }
        
        return characteristics.get(phase, {})
    
    def generate_macro_scenarios(self) -> List[Dict]:
        """
        Generate forward-looking macro scenarios
        
        Returns:
            List of scenarios with probability and market implications
        """
        scenarios = []
        
        # Scenario 1: Soft landing
        scenarios.append({
            'name': 'Soft Landing',
            'probability': 0.45,
            'description': 'Inflation moderates without recession',
            'implications': {
                'equities': 'Bullish with rotation to quality',
                'bonds': 'Neutral to slightly bullish',
                'commodities': 'Mixed',
                'usd': 'Neutral',
                'strategy': 'Balanced growth with quality tilt'
            }
        })
        
        # Scenario 2: No landing (inflation persists)
        scenarios.append({
            'name': 'No Landing',
            'probability': 0.25,
            'description': 'Inflation remains elevated, rates stay high',
            'implications': {
                'equities': 'Bearish (valuation pressure)',
                'bonds': 'Bearish (rising yields)',
                'commodities': 'Bullish (inflation hedge)',
                'usd': 'Bullish (rate differential)',
                'strategy': 'Defensive, focus on real assets'
            }
        })
        
        # Scenario 3: Hard landing (recession)
        scenarios.append({
            'name': 'Hard Landing',
            'probability': 0.20,
            'description': 'Economic contraction, aggressive rate cuts',
            'implications': {
                'equities': 'Bearish initially, then opportunity',
                'bonds': 'Bullish (flight to safety, rate cuts)',
                'commodities': 'Bearish (demand destruction)',
                'usd': 'Mixed (safe haven vs rate cuts)',
                'strategy': 'High quality bonds, defensive equities'
            }
        })
        
        # Scenario 4: Growth acceleration
        scenarios.append({
            'name': 'Growth Acceleration',
            'probability': 0.10,
            'description': 'Stronger than expected growth',
            'implications': {
                'equities': 'Bullish (cyclicals)',
                'bonds': 'Bearish (rate hike risk)',
                'commodities': 'Bullish (demand)',
                'usd': 'Bullish',
                'strategy': 'Cyclical exposure, growth stocks'
            }
        })
        
        return scenarios
    
    def get_asset_class_implications(self, asset_class: str) -> Dict:
        """
        Get macro implications for a specific asset class
        
        Args:
            asset_class: 'equities', 'bonds', 'commodities', 'crypto', 'forex'
        """
        macro_overview = self.get_macro_overview()
        scenarios = self.generate_macro_scenarios()
        
        implications = {
            'current_environment': self._interpret_current_environment(macro_overview),
            'scenarios': scenarios,
            'key_risks': self._identify_key_risks(macro_overview),
            'key_opportunities': self._identify_key_opportunities(macro_overview)
        }
        
        return implications
    
    def _interpret_current_environment(self, macro: Dict) -> str:
        """Interpret current macro environment"""
        yield_curve = macro.get('yield_curve', {})
        risk_sentiment = macro.get('risk_sentiment', {})
        
        interpretations = []
        
        if yield_curve.get('curve_shape') == 'inverted':
            interpretations.append("Inverted yield curve signals recession risk")
        elif yield_curve.get('curve_shape') == 'flat':
            interpretations.append("Flat yield curve suggests economic uncertainty")
        
        if risk_sentiment.get('sentiment') == 'risk-off':
            interpretations.append("Risk-off environment favors defensive assets")
        elif risk_sentiment.get('sentiment') == 'risk-on':
            interpretations.append("Risk-on environment favors growth assets")
        
        return "; ".join(interpretations) if interpretations else "Normal macro environment"
    
    def _identify_key_risks(self, macro: Dict) -> List[str]:
        """Identify key macro risks"""
        risks = []
        
        yield_curve = macro.get('yield_curve', {})
        if yield_curve.get('recession_indicator'):
            risks.append("Yield curve inversion suggests recession risk")
        
        central_banks = macro.get('central_banks', {})
        hawkish_count = sum(1 for bank in central_banks.values() if bank.get('stance') == 'hawkish')
        if hawkish_count >= 2:
            risks.append("Multiple central banks in hawkish stance")
        
        risk_sentiment = macro.get('risk_sentiment', {})
        if risk_sentiment.get('sentiment') == 'extreme risk-off':
            risks.append("Extreme risk aversion in markets")
        
        return risks if risks else ["Normal risk levels"]
    
    def _identify_key_opportunities(self, macro: Dict) -> List[str]:
        """Identify key macro opportunities"""
        opportunities = []
        
        risk_sentiment = macro.get('risk_sentiment', {})
        if risk_sentiment.get('sentiment') == 'risk-on':
            opportunities.append("Risk-on environment favors cyclical and growth assets")
        
        yield_curve = macro.get('yield_curve', {})
        if yield_curve.get('curve_shape') == 'normal':
            opportunities.append("Normal yield curve supports balanced allocation")
        
        return opportunities if opportunities else ["Wait for clearer macro signals"]
