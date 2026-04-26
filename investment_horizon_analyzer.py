import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class InvestmentOpportunity:
    """Represents an investment opportunity for a specific horizon"""
    symbol: str
    horizon: str  # 'short_term', 'long_term'
    entry_price: float
    target_price: float
    stop_loss: float
    potential_return: float  # percentage
    risk_reward_ratio: float
    confidence: float  # 0-1
    time_horizon: str  # e.g., '3-6 months', '3-5 years'
    thesis: str
    key_catalysts: List[str]
    key_risks: List[str]

class InvestmentHorizonAnalyzer:
    """Analyzes investment opportunities for different time horizons"""
    
    def __init__(self):
        pass
    
    def analyze_short_term_opportunities(self, symbol: str, stock_data: pd.DataFrame, 
                                         fundamentals: Dict, technical_indicators: Dict) -> Dict:
        """
        Analyze short-term investment opportunities (3-6 months)
        Focus on technicals, momentum, and near-term catalysts
        """
        opportunities = []
        
        # 1. Momentum-based opportunity
        momentum_opp = self._momentum_opportunity(symbol, stock_data, technical_indicators)
        if momentum_opp:
            opportunities.append(momentum_opp)
        
        # 2. Breakout opportunity
        breakout_opp = self._breakout_opportunity(symbol, stock_data, technical_indicators)
        if breakout_opp:
            opportunities.append(breakout_opp)
        
        # 3. Mean reversion opportunity
        mean_reversion_opp = self._mean_reversion_opportunity(symbol, stock_data, technical_indicators)
        if mean_reversion_opp:
            opportunities.append(mean_reversion_opp)
        
        # 4. Earnings catalyst opportunity
        earnings_opp = self._earnings_catalyst_opportunity(symbol, fundamentals)
        if earnings_opp:
            opportunities.append(earnings_opp)
        
        return {
            'horizon': 'short_term',
            'timeframe': '3-6 months',
            'opportunities': [opp.__dict__ for opp in opportunities],
            'best_opportunity': self._select_best_opportunity(opportunities).__dict__ if opportunities else None,
        }
    
    def analyze_long_term_opportunities(self, symbol: str, stock_data: pd.DataFrame,
                                       fundamentals: Dict, technical_indicators: Dict) -> Dict:
        """
        Analyze long-term investment opportunities (3-5 years)
        Focus on fundamentals, competitive advantage, and growth potential
        """
        opportunities = []
        
        # 1. Growth at reasonable price (GARP)
        garp_opp = self._garp_opportunity(symbol, fundamentals)
        if garp_opp:
            opportunities.append(garp_opp)
        
        # 2. Value opportunity
        value_opp = self._value_opportunity(symbol, fundamentals)
        if value_opp:
            opportunities.append(value_opp)
        
        # 3. Quality compounder
        quality_opp = self._quality_compounder(symbol, fundamentals)
        if quality_opp:
            opportunities.append(quality_opp)
        
        # 4. Turnaround opportunity
        turnaround_opp = self._turnaround_opportunity(symbol, fundamentals)
        if turnaround_opp:
            opportunities.append(turnaround_opp)
        
        return {
            'horizon': 'long_term',
            'timeframe': '3-5 years',
            'opportunities': [opp.__dict__ for opp in opportunities],
            'best_opportunity': self._select_best_opportunity(opportunities).__dict__ if opportunities else None,
        }
    
    def _momentum_opportunity(self, symbol: str, stock_data: pd.DataFrame, 
                            technical_indicators: Dict) -> InvestmentOpportunity:
        """Identify momentum-based short-term opportunity"""
        current_price = stock_data['Close'].iloc[-1]
        rsi = technical_indicators.get('rsi', 50)
        macd = technical_indicators.get('macd', 0)
        
        # Bullish momentum conditions
        if rsi > 50 and rsi < 70 and macd > 0:
            # Calculate target based on recent volatility
            atr = technical_indicators.get('atr', current_price * 0.02)
            target_price = current_price + (atr * 3)
            stop_loss = current_price - (atr * 1.5)
            
            potential_return = ((target_price - current_price) / current_price) * 100
            risk = ((current_price - stop_loss) / current_price) * 100
            risk_reward = potential_return / risk if risk > 0 else 0
            
            return InvestmentOpportunity(
                symbol=symbol,
                horizon='short_term',
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                potential_return=round(potential_return, 2),
                risk_reward_ratio=round(risk_reward, 2),
                confidence=0.65,
                time_horizon='1-3 months',
                thesis='Positive momentum with RSI in healthy range',
                key_catalysts=['Continued momentum', 'Positive technical setup'],
                key_risks=['Momentum reversal', 'Market volatility']
            )
        return None
    
    def _breakout_opportunity(self, symbol: str, stock_data: pd.DataFrame,
                             technical_indicators: Dict) -> InvestmentOpportunity:
        """Identify breakout opportunity"""
        current_price = stock_data['Close'].iloc[-1]
        resistance = technical_indicators.get('recent_high', current_price * 1.05)
        
        # Near resistance with strong volume
        if current_price > resistance * 0.98:
            target_price = resistance * 1.1
            stop_loss = resistance * 0.95
            
            potential_return = ((target_price - current_price) / current_price) * 100
            risk = ((current_price - stop_loss) / current_price) * 100
            risk_reward = potential_return / risk if risk > 0 else 0
            
            return InvestmentOpportunity(
                symbol=symbol,
                horizon='short_term',
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                potential_return=round(potential_return, 2),
                risk_reward_ratio=round(risk_reward, 2),
                confidence=0.6,
                time_horizon='2-4 weeks',
                thesis='Breakout above key resistance level',
                key_catalysts=['Breakout confirmation', 'Volume support'],
                key_risks=['Failed breakout', 'Resistance at higher levels']
            )
        return None
    
    def _mean_reversion_opportunity(self, symbol: str, stock_data: pd.DataFrame,
                                   technical_indicators: Dict) -> InvestmentOpportunity:
        """Identify mean reversion opportunity"""
        current_price = stock_data['Close'].iloc[-1]
        rsi = technical_indicators.get('rsi', 50)
        sma_50 = technical_indicators.get('sma_50', current_price)
        
        # Oversold conditions
        if rsi < 35 and current_price < sma_50:
            target_price = sma_50
            stop_loss = current_price * 0.92
            
            potential_return = ((target_price - current_price) / current_price) * 100
            risk = ((current_price - stop_loss) / current_price) * 100
            risk_reward = potential_return / risk if risk > 0 else 0
            
            return InvestmentOpportunity(
                symbol=symbol,
                horizon='short_term',
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                potential_return=round(potential_return, 2),
                risk_reward_ratio=round(risk_reward, 2),
                confidence=0.55,
                time_horizon='2-6 weeks',
                thesis='Oversold conditions suggest mean reversion',
                key_catalysts=['Oversold bounce', 'Support at 50-day MA'],
                key_risks=['Continued selling', 'Fundamental deterioration']
            )
        return None
    
    def _earnings_catalyst_opportunity(self, symbol: str, fundamentals: Dict) -> InvestmentOpportunity:
        """Identify earnings catalyst opportunity"""
        current_price = fundamentals.get('current_price', 0)
        earnings_growth = fundamentals.get('earnings_growth', 0)
        
        # Strong earnings growth
        if earnings_growth > 0.15:
            target_price = current_price * 1.15
            stop_loss = current_price * 0.92
            
            potential_return = ((target_price - current_price) / current_price) * 100
            risk = ((current_price - stop_loss) / current_price) * 100
            risk_reward = potential_return / risk if risk > 0 else 0
            
            return InvestmentOpportunity(
                symbol=symbol,
                horizon='short_term',
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                potential_return=round(potential_return, 2),
                risk_reward_ratio=round(risk_reward, 2),
                confidence=0.6,
                time_horizon='1-3 months',
                thesis='Strong earnings growth driving upside',
                key_catalysts=['Earnings beat', 'Guidance raise'],
                key_risks=['Earnings miss', 'Guidance cut']
            )
        return None
    
    def _garp_opportunity(self, symbol: str, fundamentals: Dict) -> InvestmentOpportunity:
        """Growth at Reasonable Price opportunity"""
        current_price = fundamentals.get('current_price', 0)
        pe_ratio = fundamentals.get('pe_ratio', 0)
        revenue_growth = fundamentals.get('revenue_growth', 0)
        roe = fundamentals.get('return_on_equity', 0)
        
        # GARP conditions: Good growth, reasonable PE, high ROE
        if revenue_growth > 0.10 and 10 < pe_ratio < 25 and roe > 0.15:
            target_price = current_price * 1.5  # 50% upside over 3 years
            stop_loss = current_price * 0.8
            
            potential_return = ((target_price - current_price) / current_price) * 100
            risk = ((current_price - stop_loss) / current_price) * 100
            risk_reward = potential_return / risk if risk > 0 else 0
            
            return InvestmentOpportunity(
                symbol=symbol,
                horizon='long_term',
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                potential_return=round(potential_return, 2),
                risk_reward_ratio=round(risk_reward, 2),
                confidence=0.7,
                time_horizon='3-5 years',
                thesis='Growth at reasonable price with strong ROE',
                key_catalysts=['Revenue growth', 'Margin expansion', 'Market share gains'],
                key_risks=['Growth slowdown', 'Valuation compression', 'Competition']
            )
        return None
    
    def _value_opportunity(self, symbol: str, fundamentals: Dict) -> InvestmentOpportunity:
        """Value investing opportunity"""
        current_price = fundamentals.get('current_price', 0)
        pe_ratio = fundamentals.get('pe_ratio', 0)
        pb_ratio = fundamentals.get('pb_ratio', 0)
        
        # Value conditions: Low PE, low PB
        if pe_ratio < 15 and pb_ratio < 2:
            target_price = current_price * 1.4  # 40% upside over 3 years
            stop_loss = current_price * 0.85
            
            potential_return = ((target_price - current_price) / current_price) * 100
            risk = ((current_price - stop_loss) / current_price) * 100
            risk_reward = potential_return / risk if risk > 0 else 0
            
            return InvestmentOpportunity(
                symbol=symbol,
                horizon='long_term',
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                potential_return=round(potential_return, 2),
                risk_reward_ratio=round(risk_reward, 2),
                confidence=0.65,
                time_horizon='3-5 years',
                thesis='Undervalued relative to peers and history',
                key_catalysts=['Valuation re-rating', 'Operational improvements'],
                key_risks=['Value trap', 'Structural decline']
            )
        return None
    
    def _quality_compounder(self, symbol: str, fundamentals: Dict) -> InvestmentOpportunity:
        """Quality compounder opportunity"""
        current_price = fundamentals.get('current_price', 0)
        roe = fundamentals.get('return_on_equity', 0)
        profit_margin = fundamentals.get('profit_margin', 0)
        revenue_growth = fundamentals.get('revenue_growth', 0)
        
        # Quality conditions: High ROE, high margins, consistent growth
        if roe > 0.20 and profit_margin > 0.15 and revenue_growth > 0.10:
            target_price = current_price * 2.0  # 100% upside over 5 years
            stop_loss = current_price * 0.75
            
            potential_return = ((target_price - current_price) / current_price) * 100
            risk = ((current_price - stop_loss) / current_price) * 100
            risk_reward = potential_return / risk if risk > 0 else 0
            
            return InvestmentOpportunity(
                symbol=symbol,
                horizon='long_term',
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                potential_return=round(potential_return, 2),
                risk_reward_ratio=round(risk_reward, 2),
                confidence=0.75,
                time_horizon='5+ years',
                thesis='High-quality business with compounding potential',
                key_catalysts=['Compound earnings growth', 'Market expansion', 'Pricing power'],
                key_risks=['Competition', 'Regulatory changes', 'Execution risk']
            )
        return None
    
    def _turnaround_opportunity(self, symbol: str, fundamentals: Dict) -> InvestmentOpportunity:
        """Turnaround opportunity"""
        current_price = fundamentals.get('current_price', 0)
        revenue_growth = fundamentals.get('revenue_growth', 0)
        debt_to_equity = fundamentals.get('debt_to_equity', 0)
        
        # Turnaround conditions: Negative growth but improving, manageable debt
        if revenue_growth < 0 and debt_to_equity < 2:
            target_price = current_price * 1.6  # 60% upside over 3 years
            stop_loss = current_price * 0.7
            
            potential_return = ((target_price - current_price) / current_price) * 100
            risk = ((current_price - stop_loss) / current_price) * 100
            risk_reward = potential_return / risk if risk > 0 else 0
            
            return InvestmentOpportunity(
                symbol=symbol,
                horizon='long_term',
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                potential_return=round(potential_return, 2),
                risk_reward_ratio=round(risk_reward, 2),
                confidence=0.5,
                time_horizon='3-5 years',
                thesis='Turnaround situation with recovery potential',
                key_catalysts=['Operational improvements', 'Cost restructuring', 'New management'],
                key_risks=['Turnaround fails', 'Liquidity issues', 'Extended timeline']
            )
        return None
    
    def _select_best_opportunity(self, opportunities: List[InvestmentOpportunity]) -> InvestmentOpportunity:
        """Select the best opportunity based on risk-reward and confidence"""
        if not opportunities:
            return None
        
        # Score each opportunity
        scored = []
        for opp in opportunities:
            score = (opp.confidence * 0.5) + (min(opp.risk_reward_ratio, 5) / 5 * 0.3) + (min(opp.potential_return, 50) / 50 * 0.2)
            scored.append((score, opp))
        
        # Return highest scored
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
