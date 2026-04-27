import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from dataclasses import dataclass

@dataclass
class MomentumSignal:
    """Represents a momentum prediction signal"""
    direction: str  # 'bullish', 'bearish', 'neutral'
    strength: float  # 0-100
    confidence: float  # 0-1
    timeframe: str  # 'short', 'medium', 'long'
    expected_change: float  # Expected percentage change
    action: str  # 'buy', 'sell', 'hold'
    reason: str

class MomentumPredictor:
    """Predicts momentum changes and provides action advice"""
    
    def __init__(self):
        pass
    
    def predict_momentum(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Predict momentum changes using multiple indicators
        
        Returns comprehensive momentum analysis
        """
        if len(df) < 50:
            return {'error': 'Insufficient data for momentum prediction'}
        
        signals = []
        
        # 1. Rate of Change (ROC) analysis
        roc_signal = self._analyze_roc(df, current_price)
        signals.append(roc_signal)
        
        # 2. Momentum oscillator
        momentum_signal = self._analyze_momentum_oscillator(df)
        signals.append(momentum_signal)
        
        # 3. Trend strength analysis
        trend_signal = self._analyze_trend_strength(df)
        signals.append(trend_signal)
        
        # 4. Volume momentum
        volume_signal = self._analyze_volume_momentum(df)
        signals.append(volume_signal)
        
        # 5. Price velocity
        velocity_signal = self._analyze_price_velocity(df)
        signals.append(velocity_signal)
        
        # Aggregate signals
        aggregated = self._aggregate_signals(signals)
        
        return {
            'current_momentum': aggregated,
            'individual_signals': [s.__dict__ for s in signals],
            'prediction': self._generate_prediction(aggregated, signals),
            'action_advice': self._generate_action_advice(aggregated, signals),
        }
    
    def _analyze_roc(self, df: pd.DataFrame, current_price: float) -> MomentumSignal:
        """Analyze Rate of Change for momentum"""
        # Calculate ROC for different periods
        roc_5 = float((df['Close'].iloc[-1] / df['Close'].iloc[-6] - 1) * 100) if len(df) > 5 else 0.0
        roc_10 = float((df['Close'].iloc[-1] / df['Close'].iloc[-11] - 1) * 100) if len(df) > 10 else 0.0
        roc_20 = float((df['Close'].iloc[-1] / df['Close'].iloc[-21] - 1) * 100) if len(df) > 20 else 0.0
        
        # Weight recent ROC more heavily
        weighted_roc = (roc_5 * 0.5 + roc_10 * 0.3 + roc_20 * 0.2)
        
        if weighted_roc > 3:
            direction = 'bullish'
            strength = min(100, weighted_roc * 10)
            action = 'buy'
            reason = f"Strong positive momentum (ROC: {weighted_roc:.2f}%)"
        elif weighted_roc < -3:
            direction = 'bearish'
            strength = min(100, abs(weighted_roc) * 10)
            action = 'sell'
            reason = f"Negative momentum (ROC: {weighted_roc:.2f}%)"
        else:
            direction = 'neutral'
            strength = 50
            action = 'hold'
            reason = f"Neutral momentum (ROC: {weighted_roc:.2f}%)"
        
        return MomentumSignal(
            direction=direction,
            strength=strength,
            confidence=0.7,
            timeframe='short',
            expected_change=weighted_roc,
            action=action,
            reason=reason
        )
    
    def _analyze_momentum_oscillator(self, df: pd.DataFrame) -> MomentumSignal:
        """Analyze momentum oscillator"""
        # Simple momentum: current price - N periods ago
        momentum_10 = float(df['Close'].iloc[-1] - df['Close'].iloc[-11]) if len(df) > 10 else 0.0
        momentum_20 = float(df['Close'].iloc[-1] - df['Close'].iloc[-21]) if len(df) > 20 else 0.0
        
        # Normalize by price
        normalized_momentum = float(((momentum_10 + momentum_20) / 2) / df['Close'].iloc[-1] * 100) if not df.empty else 0.0
        
        if normalized_momentum > 2:
            direction = 'bullish'
            strength = min(100, normalized_momentum * 20)
            action = 'buy'
            reason = f"Positive momentum oscillator ({normalized_momentum:.2f}%)"
        elif normalized_momentum < -2:
            direction = 'bearish'
            strength = min(100, abs(normalized_momentum) * 20)
            action = 'sell'
            reason = f"Negative momentum oscillator ({normalized_momentum:.2f}%)"
        else:
            direction = 'neutral'
            strength = 50
            action = 'hold'
            reason = f"Neutral momentum oscillator ({normalized_momentum:.2f}%)"
        
        return MomentumSignal(
            direction=direction,
            strength=strength,
            confidence=0.65,
            timeframe='medium',
            expected_change=normalized_momentum,
            action=action,
            reason=reason
        )
    
    def _analyze_trend_strength(self, df: pd.DataFrame) -> MomentumSignal:
        """Analyze trend strength using linear regression slope"""
        # Calculate linear regression slope on last 20 periods
        if len(df) < 20:
            return MomentumSignal('neutral', 50, 0.5, 'medium', 0, 'hold', 'Insufficient data')
        
        recent_prices = df['Close'].tail(20).values
        x = np.arange(len(recent_prices))
        slope = np.polyfit(x, recent_prices, 1)[0]
        
        # Normalize slope by average price
        avg_price = np.mean(recent_prices)
        normalized_slope = (slope / avg_price) * 100
        
        if normalized_slope > 0.5:
            direction = 'bullish'
            strength = min(100, normalized_slope * 50)
            action = 'buy'
            reason = f"Strong uptrend (slope: {normalized_slope:.3f})"
        elif normalized_slope < -0.5:
            direction = 'bearish'
            strength = min(100, abs(normalized_slope) * 50)
            action = 'sell'
            reason = f"Downtrend (slope: {normalized_slope:.3f})"
        else:
            direction = 'neutral'
            strength = 50
            action = 'hold'
            reason = f"Weak trend (slope: {normalized_slope:.3f})"
        
        return MomentumSignal(
            direction=direction,
            strength=strength,
            confidence=0.75,
            timeframe='medium',
            expected_change=normalized_slope * 10,
            action=action,
            reason=reason
        )
    
    def _analyze_volume_momentum(self, df: pd.DataFrame) -> MomentumSignal:
        """Analyze volume momentum"""
        if 'Volume' not in df.columns:
            return MomentumSignal('neutral', 50, 0.3, 'short', 0, 'hold', 'No volume data')
        
        # Compare recent volume to average
        recent_volume = df['Volume'].tail(5).mean()
        avg_volume = df['Volume'].tail(50).mean()
        
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # Price change during high volume
        price_change = float((df['Close'].iloc[-1] / df['Close'].iloc[-6] - 1) * 100) if len(df) > 5 else 0.0
        
        if volume_ratio > 1.5 and price_change > 0:
            direction = 'bullish'
            strength = min(100, volume_ratio * 30)
            action = 'buy'
            reason = f"High volume buying (volume ratio: {volume_ratio:.2f})"
        elif volume_ratio > 1.5 and price_change < 0:
            direction = 'bearish'
            strength = min(100, volume_ratio * 30)
            action = 'sell'
            reason = f"High volume selling (volume ratio: {volume_ratio:.2f})"
        else:
            direction = 'neutral'
            strength = 50
            action = 'hold'
            reason = f"Normal volume (volume ratio: {volume_ratio:.2f})"
        
        return MomentumSignal(
            direction=direction,
            strength=strength,
            confidence=0.6,
            timeframe='short',
            expected_change=price_change * volume_ratio,
            action=action,
            reason=reason
        )
    
    def _analyze_price_velocity(self, df: pd.DataFrame) -> MomentumSignal:
        """Analyze price velocity (rate of change of rate of change)"""
        if len(df) < 10:
            return MomentumSignal('neutral', 50, 0.5, 'short', 0, 'hold', 'Insufficient data')
        
        # Calculate second derivative (acceleration)
        returns = df['Close'].pct_change().tail(10)
        velocity = float(returns.diff().iloc[-1] * 100) if len(returns) > 1 else 0.0
        
        if velocity > 0.5:
            direction = 'bullish'
            strength = min(100, velocity * 50)
            action = 'buy'
            reason = f"Positive acceleration (velocity: {velocity:.3f})"
        elif velocity < -0.5:
            direction = 'bearish'
            strength = min(100, abs(velocity) * 50)
            action = 'sell'
            reason = f"Negative acceleration (velocity: {velocity:.3f})"
        else:
            direction = 'neutral'
            strength = 50
            action = 'hold'
            reason = f"Stable velocity (velocity: {velocity:.3f})"
        
        return MomentumSignal(
            direction=direction,
            strength=strength,
            confidence=0.55,
            timeframe='short',
            expected_change=velocity * 5,
            action=action,
            reason=reason
        )
    
    def _aggregate_signals(self, signals: List[MomentumSignal]) -> Dict:
        """Aggregate individual signals into overall momentum"""
        bullish_count = sum(1 for s in signals if s.direction == 'bullish')
        bearish_count = sum(1 for s in signals if s.direction == 'bearish')
        neutral_count = sum(1 for s in signals if s.direction == 'neutral')
        
        # Calculate weighted strength
        bullish_strength = sum(s.strength for s in signals if s.direction == 'bullish')
        bearish_strength = sum(s.strength for s in signals if s.direction == 'bearish')
        
        if bullish_count > bearish_count:
            overall_direction = 'bullish'
            overall_strength = bullish_strength / max(bullish_count, 1)
        elif bearish_count > bullish_count:
            overall_direction = 'bearish'
            overall_strength = bearish_strength / max(bearish_count, 1)
        else:
            overall_direction = 'neutral'
            overall_strength = 50
        
        # Calculate average confidence
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        
        return {
            'direction': overall_direction,
            'strength': round(overall_strength, 2),
            'confidence': round(avg_confidence, 2),
            'bullish_signals': bullish_count,
            'bearish_signals': bearish_count,
            'neutral_signals': neutral_count,
        }
    
    def _generate_prediction(self, aggregated: Dict, signals: List[MomentumSignal]) -> Dict:
        """Generate momentum prediction"""
        direction = aggregated['direction']
        strength = aggregated['strength']
        
        # Calculate expected change based on signals
        expected_changes = [s.expected_change for s in signals if s.expected_change != 0]
        avg_expected_change = np.mean(expected_changes) if expected_changes else 0
        
        if direction == 'bullish':
            if strength > 70:
                prediction = 'Strong upward momentum expected'
                probability = 0.75
            elif strength > 50:
                prediction = 'Moderate upward momentum expected'
                probability = 0.65
            else:
                prediction = 'Slight upward momentum expected'
                probability = 0.55
        elif direction == 'bearish':
            if strength > 70:
                prediction = 'Strong downward momentum expected'
                probability = 0.75
            elif strength > 50:
                prediction = 'Moderate downward momentum expected'
                probability = 0.65
            else:
                prediction = 'Slight downward momentum expected'
                probability = 0.55
        else:
            prediction = 'Sideways momentum expected'
            probability = 0.50
        
        return {
            'prediction': prediction,
            'probability': round(probability, 2),
            'expected_change_pct': round(avg_expected_change, 2),
            'timeframe': '1-2 weeks',
        }
    
    def _generate_action_advice(self, aggregated: Dict, signals: List[MomentumSignal]) -> Dict:
        """Generate actionable advice based on momentum"""
        direction = aggregated['direction']
        strength = aggregated['strength']
        confidence = aggregated['confidence']
        
        # Count actions
        buy_signals = sum(1 for s in signals if s.action == 'buy')
        sell_signals = sum(1 for s in signals if s.action == 'sell')
        hold_signals = sum(1 for s in signals if s.action == 'hold')
        
        if direction == 'bullish' and strength > 60 and confidence > 0.6:
            action = 'buy'
            urgency = 'high' if strength > 80 else 'medium'
            advice = 'Consider establishing or adding to positions'
        elif direction == 'bearish' and strength > 60 and confidence > 0.6:
            action = 'sell'
            urgency = 'high' if strength > 80 else 'medium'
            advice = 'Consider reducing or exiting positions'
        else:
            action = 'hold'
            urgency = 'low'
            advice = 'Wait for clearer momentum signals'
        
        return {
            'action': action,
            'urgency': urgency,
            'advice': advice,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'hold_signals': hold_signals,
        }
