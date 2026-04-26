from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ActionAdvice:
    """Represents actionable trading advice"""
    action: str  # 'buy', 'sell', 'hold', 'wait'
    urgency: str  # 'immediate', 'soon', 'when', 'avoid'
    entry_price: float
    target_price: float
    stop_loss: float
    position_size: float  # percentage of portfolio
    time_horizon: str
    reasoning: str
    key_factors: List[str]
    risks: List[str]

class ActionAdvisor:
    """Provides actionable buy/sell/hold advice with timing"""
    
    def __init__(self):
        pass
    
    def generate_advice(self, symbol: str, analysis: Dict, momentum: Dict, 
                       chart: Dict, fundamentals: Dict) -> ActionAdvice:
        """
        Generate comprehensive action advice based on all analysis
        """
        # Get individual component scores
        signal_score = analysis.get('scores', {}).get('net_score', 0)
        momentum_score = momentum.get('current_momentum', {}).get('strength', 50)
        chart_score = self._calculate_chart_score(chart)
        fundamental_score = self._calculate_fundamental_score(fundamentals)
        
        # Weighted overall score
        overall_score = (
            signal_score * 0.3 +
            (momentum_score - 50) * 0.3 +
            (chart_score - 50) * 0.2 +
            (fundamental_score - 50) * 0.2
        )
        
        # Determine action
        if overall_score > 15:
            action = 'buy'
            urgency = 'immediate' if overall_score > 25 else 'soon'
        elif overall_score > 5:
            action = 'buy'
            urgency = 'when'
        elif overall_score > -5:
            action = 'hold'
            urgency = 'wait'
        elif overall_score > -15:
            action = 'sell'
            urgency = 'when'
        else:
            action = 'sell'
            urgency = 'immediate' if overall_score < -25 else 'soon'
        
        # Calculate entry, target, stop loss
        current_price = analysis.get('company', {}).get('current_price', 0)
        entry, target, stop_loss = self._calculate_price_levels(
            current_price, action, chart, momentum
        )
        
        # Position sizing based on conviction
        conviction = min(1.0, abs(overall_score) / 30)
        position_size = conviction * 0.25  # Max 25% of portfolio
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            action, signal_score, momentum_score, chart_score, fundamental_score
        )
        
        # Key factors and risks
        key_factors = self._identify_key_factors(analysis, momentum, chart, fundamentals)
        risks = self._identify_risks(analysis, momentum, chart, fundamentals)
        
        # Time horizon
        time_horizon = self._determine_time_horizon(action, momentum, fundamentals)
        
        return ActionAdvice(
            action=action,
            urgency=urgency,
            entry_price=entry,
            target_price=target,
            stop_loss=stop_loss,
            position_size=round(position_size * 100, 1),
            time_horizon=time_horizon,
            reasoning=reasoning,
            key_factors=key_factors,
            risks=risks
        )
    
    def _calculate_chart_score(self, chart: Dict) -> float:
        """Calculate chart analysis score"""
        score = 50
        
        # Trend contribution
        trend = chart.get('trend_analysis', {}).get('trend', 'sideways')
        if trend == 'strong_uptrend':
            score += 20
        elif trend == 'uptrend':
            score += 10
        elif trend == 'strong_downtrend':
            score -= 20
        elif trend == 'downtrend':
            score -= 10
        
        # Price action contribution
        up_ratio = chart.get('price_action', {}).get('up_day_ratio', 0.5)
        if up_ratio > 0.6:
            score += 10
        elif up_ratio < 0.4:
            score -= 10
        
        # Pattern contribution
        patterns = chart.get('chart_patterns', [])
        for pattern in patterns:
            if pattern.get('direction') == 'bullish':
                score += pattern.get('confidence', 0) * 10
            elif pattern.get('direction') == 'bearish':
                score -= pattern.get('confidence', 0) * 10
        
        return min(100, max(0, score))
    
    def _calculate_fundamental_score(self, fundamentals: Dict) -> float:
        """Calculate fundamental analysis score"""
        score = 50
        
        # ROE contribution
        roe = fundamentals.get('return_on_equity', 0)
        if roe > 0.20:
            score += 15
        elif roe > 0.15:
            score += 10
        elif roe < 0.10:
            score -= 10
        
        # Growth contribution
        revenue_growth = fundamentals.get('revenue_growth', 0)
        if revenue_growth > 0.15:
            score += 15
        elif revenue_growth > 0.10:
            score += 10
        elif revenue_growth < 0:
            score -= 15
        
        # Valuation contribution
        pe = fundamentals.get('pe_ratio', 0)
        if 10 < pe < 25:
            score += 10
        elif pe < 10:
            score += 5
        elif pe > 40:
            score -= 15
        
        # Debt contribution
        debt_to_equity = fundamentals.get('debt_to_equity', 0)
        if debt_to_equity < 1:
            score += 10
        elif debt_to_equity > 2:
            score -= 15
        
        return min(100, max(0, score))
    
    def _calculate_price_levels(self, current_price: float, action: str, 
                                chart: Dict, momentum: Dict) -> Tuple[float, float, float]:
        """Calculate entry, target, and stop loss levels"""
        if action == 'buy':
            # Entry: current or slightly below support
            support = chart.get('key_levels', {}).get('support_1', current_price * 0.95)
            entry = min(current_price, support)
            
            # Target: based on resistance or momentum
            resistance = chart.get('key_levels', {}).get('resistance_1', current_price * 1.1)
            momentum_expected = momentum.get('prediction', {}).get('expected_change_pct', 5)
            target = max(resistance, current_price * (1 + momentum_expected / 100))
            
            # Stop loss: below support or recent low
            recent_low = chart.get('key_levels', {}).get('52_week_low', current_price * 0.9)
            stop_loss = min(support * 0.98, recent_low)
            
        elif action == 'sell':
            # Entry: current or slightly below resistance
            resistance = chart.get('key_levels', {}).get('resistance_1', current_price * 1.05)
            entry = max(current_price, resistance)
            
            # Target: based on support
            support = chart.get('key_levels', {}).get('support_1', current_price * 0.9)
            target = support
            
            # Stop loss: above resistance
            stop_loss = resistance * 1.02
            
        else:  # hold
            entry = current_price
            target = current_price * 1.05
            stop_loss = current_price * 0.95
        
        return round(entry, 2), round(target, 2), round(stop_loss, 2)
    
    def _generate_reasoning(self, action: str, signal_score: float, 
                           momentum_score: float, chart_score: float, 
                           fundamental_score: float) -> str:
        """Generate reasoning for the action"""
        reasons = []
        
        if action == 'buy':
            if signal_score > 10:
                reasons.append(f"Strong signal analysis (score: {signal_score:.1f})")
            if momentum_score > 60:
                reasons.append(f"Positive momentum (strength: {momentum_score:.0f})")
            if chart_score > 60:
                reasons.append(f"Bullish chart patterns (score: {chart_score:.0f})")
            if fundamental_score > 60:
                reasons.append(f"Solid fundamentals (score: {fundamental_score:.0f})")
        elif action == 'sell':
            if signal_score < -10:
                reasons.append(f"Weak signal analysis (score: {signal_score:.1f})")
            if momentum_score < 40:
                reasons.append(f"Negative momentum (strength: {momentum_score:.0f})")
            if chart_score < 40:
                reasons.append(f"Bearish chart patterns (score: {chart_score:.0f})")
            if fundamental_score < 40:
                reasons.append(f"Weak fundamentals (score: {fundamental_score:.0f})")
        else:
            reasons.append("Mixed signals with no clear directional bias")
        
        return "; ".join(reasons) if reasons else "Balanced risk-reward profile"
    
    def _identify_key_factors(self, analysis: Dict, momentum: Dict, 
                             chart: Dict, fundamentals: Dict) -> List[str]:
        """Identify key factors supporting the action"""
        factors = []
        
        # Signal factors
        top_bullish = analysis.get('bullish_indicators', [])[:2]
        for signal in top_bullish:
            factors.append(f"{signal.get('name', '')}: {signal.get('weighted_score', 0):.1f}")
        
        # Momentum factors
        momentum_dir = momentum.get('current_momentum', {}).get('direction', 'neutral')
        if momentum_dir != 'neutral':
            factors.append(f"{momentum_dir.capitalize()} momentum")
        
        # Chart factors
        trend = chart.get('trend_analysis', {}).get('trend', 'sideways')
        if trend != 'sideways':
            factors.append(f"{trend.replace('_', ' ').title()} trend")
        
        # Fundamental factors
        if fundamentals.get('revenue_growth', 0) > 0.1:
            factors.append(f"Strong revenue growth ({fundamentals['revenue_growth']*100:.1f}%)")
        if fundamentals.get('return_on_equity', 0) > 0.15:
            factors.append(f"High ROE ({fundamentals['return_on_equity']*100:.1f}%)")
        
        return factors[:5]
    
    def _identify_risks(self, analysis: Dict, momentum: Dict, 
                       chart: Dict, fundamentals: Dict) -> List[str]:
        """Identify key risks"""
        risks = []
        
        # Signal risks
        top_bearish = analysis.get('bearish_indicators', [])[:2]
        for signal in top_bearish:
            if signal.get('weighted_score', 0) > 2:
                risks.append(f"{signal.get('name', '')}: {signal.get('weighted_score', 0):.1f}")
        
        # Momentum risks
        if momentum.get('current_momentum', {}).get('confidence', 0) < 0.5:
            risks.append("Low momentum confidence")
        
        # Chart risks
        patterns = chart.get('chart_patterns', [])
        for pattern in patterns:
            if pattern.get('direction') == 'bearish':
                risks.append(f"{pattern.get('pattern', '')} pattern")
        
        # Fundamental risks
        if fundamentals.get('debt_to_equity', 0) > 2:
            risks.append(f"High debt levels (D/E: {fundamentals['debt_to_equity']:.1f})")
        if fundamentals.get('pe_ratio', 0) > 40:
            risks.append(f"High valuation (P/E: {fundamentals['pe_ratio']:.1f})")
        
        # Market risks
        volatility = chart.get('performance_metrics', {}).get('volatility', 0)
        if volatility > 50:
            risks.append(f"High volatility ({volatility:.1f}%)")
        
        return risks[:5]
    
    def _determine_time_horizon(self, action: str, momentum: Dict, 
                               fundamentals: Dict) -> str:
        """Determine recommended holding period"""
        if action == 'buy':
            # If strong fundamentals, longer horizon
            if fundamentals.get('return_on_equity', 0) > 0.15 and fundamentals.get('revenue_growth', 0) > 0.1:
                return '6-12 months'
            # If momentum-driven, shorter horizon
            elif momentum.get('current_momentum', {}).get('strength', 50) > 70:
                return '1-3 months'
            else:
                return '3-6 months'
        elif action == 'sell':
            return 'Immediate exit recommended'
        else:
            return 'Hold until clearer signals'
    
    def generate_timing_advice(self, action: str, chart: Dict, 
                              current_hour: int = None) -> Dict:
        """Generate timing advice for the action"""
        if current_hour is None:
            current_hour = datetime.now().hour
        
        timing = {
            'action': action,
            'best_time': '',
            'intraday_advice': '',
            'conditions_to_wait': [],
        }
        
        if action == 'buy':
            # Best time to buy: near support, on pullback
            support = chart.get('key_levels', {}).get('support_1', 0)
            current = chart.get('current_price', 0)
            
            if current > support * 1.02:
                timing['best_time'] = 'Wait for pullback to support level'
                timing['conditions_to_wait'].append(f'Price near {support:.2f}')
            else:
                timing['best_time'] = 'Current levels are favorable'
            
            # Intraday timing
            if 9 <= current_hour < 11:
                timing['intraday_advice'] = 'Early volatility - consider waiting for stabilization'
            elif 14 <= current_hour < 16:
                timing['intraday_advice'] = 'Late day - good for entry if trend is clear'
            else:
                timing['intraday_advice'] = 'Mid-day - acceptable for entry'
                
        elif action == 'sell':
            # Best time to sell: near resistance
            resistance = chart.get('key_levels', {}).get('resistance_1', 0)
            current = chart.get('current_price', 0)
            
            if current < resistance * 0.98:
                timing['best_time'] = 'Wait for approach to resistance'
                timing['conditions_to_wait'].append(f'Price near {resistance:.2f}')
            else:
                timing['best_time'] = 'Current levels are favorable for exit'
            
            timing['intraday_advice'] = 'Consider exiting on strength'
            
        else:
            timing['best_time'] = 'No action needed'
            timing['intraday_advice'] = 'Monitor for signal changes'
        
        return timing
