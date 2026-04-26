import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ChartPattern:
    """Represents a detected chart pattern"""
    pattern_type: str
    direction: str  # 'bullish' or 'bearish'
    confidence: float  # 0-1
    description: str
    entry_zone: Tuple[float, float]
    target_zone: Tuple[float, float]
    stop_loss: float

@dataclass
class SupportResistance:
    """Represents support/resistance levels"""
    level: float
    type: str  # 'support' or 'resistance'
    strength: float  # 0-1
    touches: int
    last_tested: str

class ChartAnalyzer:
    """Analyzes price charts for patterns, support/resistance, and performance"""
    
    def __init__(self):
        pass
    
    def analyze_chart(self, df: pd.DataFrame, symbol: str) -> Dict:
        """
        Comprehensive chart analysis
        """
        if len(df) < 50:
            return {'error': 'Insufficient data for chart analysis'}
        
        analysis = {
            'symbol': symbol,
            'current_price': df['Close'].iloc[-1],
            'price_action': self._analyze_price_action(df),
            'support_resistance': self._find_support_resistance(df),
            'chart_patterns': self._detect_chart_patterns(df),
            'trend_analysis': self._analyze_trend(df),
            'volume_analysis': self._analyze_volume(df),
            'performance_metrics': self._calculate_performance_metrics(df),
            'key_levels': self._identify_key_levels(df),
        }
        
        return analysis
    
    def _analyze_price_action(self, df: pd.DataFrame) -> Dict:
        """Analyze recent price action"""
        recent = df.tail(20)
        
        # Price changes
        daily_changes = recent['Close'].pct_change().dropna()
        avg_change = daily_changes.mean() * 100
        volatility = daily_changes.std() * 100
        
        # Up vs down days
        up_days = sum(daily_changes > 0)
        down_days = sum(daily_changes < 0)
        total_days = len(daily_changes)
        
        # Price relative to moving averages
        current = df['Close'].iloc[-1]
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(50).mean().iloc[-1]
        
        return {
            'avg_daily_change': round(avg_change, 3),
            'volatility': round(volatility, 3),
            'up_days': up_days,
            'down_days': down_days,
            'up_day_ratio': round(up_days / total_days, 3) if total_days > 0 else 0,
            'above_sma_20': current > sma_20,
            'above_sma_50': current > sma_50,
            'distance_from_sma_20': round((current / sma_20 - 1) * 100, 2),
            'distance_from_sma_50': round((current / sma_50 - 1) * 100, 2),
        }
    
    def _find_support_resistance(self, df: pd.DataFrame, lookback: int = 100) -> List[Dict]:
        """Find key support and resistance levels"""
        if len(df) < lookback:
            lookback = len(df)
        
        recent = df.tail(lookback)
        levels = []
        
        # Find local maxima (resistance) and minima (support)
        for i in range(2, len(recent) - 2):
            # Local maximum (potential resistance)
            if (recent['High'].iloc[i] > recent['High'].iloc[i-1] and 
                recent['High'].iloc[i] > recent['High'].iloc[i-2] and
                recent['High'].iloc[i] > recent['High'].iloc[i+1] and
                recent['High'].iloc[i] > recent['High'].iloc[i+2]):
                
                # Check if this level has been tested before
                level = recent['High'].iloc[i]
                touches = self._count_level_touches(recent, level, tolerance=0.02)
                
                if touches >= 2:
                    levels.append({
                        'level': round(level, 2),
                        'type': 'resistance',
                        'strength': min(1.0, touches / 5),
                        'touches': touches,
                        'last_tested': recent.index[i].strftime('%Y-%m-%d'),
                    })
            
            # Local minimum (potential support)
            if (recent['Low'].iloc[i] < recent['Low'].iloc[i-1] and 
                recent['Low'].iloc[i] < recent['Low'].iloc[i-2] and
                recent['Low'].iloc[i] < recent['Low'].iloc[i+1] and
                recent['Low'].iloc[i] < recent['Low'].iloc[i+2]):
                
                level = recent['Low'].iloc[i]
                touches = self._count_level_touches(recent, level, tolerance=0.02)
                
                if touches >= 2:
                    levels.append({
                        'level': round(level, 2),
                        'type': 'support',
                        'strength': min(1.0, touches / 5),
                        'touches': touches,
                        'last_tested': recent.index[i].strftime('%Y-%m-%d'),
                    })
        
        # Sort by strength and proximity to current price
        current_price = df['Close'].iloc[-1]
        levels.sort(key=lambda x: (x['strength'], -abs(x['level'] - current_price)), reverse=True)
        
        return levels[:10]  # Return top 10 levels
    
    def _count_level_touches(self, df: pd.DataFrame, level: float, tolerance: float = 0.02) -> int:
        """Count how many times price has touched a level"""
        touches = 0
        for _, row in df.iterrows():
            if abs(row['High'] - level) / level < tolerance or abs(row['Low'] - level) / level < tolerance:
                touches += 1
        return touches
    
    def _detect_chart_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect common chart patterns"""
        patterns = []
        
        # Double Top/Bottom
        double_pattern = self._detect_double_pattern(df)
        if double_pattern:
            patterns.append(double_pattern)
        
        # Head and Shoulders
        hs_pattern = self._detect_head_shoulders(df)
        if hs_pattern:
            patterns.append(hs_pattern)
        
        # Triangle patterns
        triangle = self._detect_triangle(df)
        if triangle:
            patterns.append(triangle)
        
        # Flag/Pennant
        flag = self._detect_flag_pennant(df)
        if flag:
            patterns.append(flag)
        
        return patterns
    
    def _detect_double_pattern(self, df: pd.DataFrame) -> Dict:
        """Detect double top or double bottom"""
        recent = df.tail(50)
        peaks = []
        troughs = []
        
        # Find peaks and troughs
        for i in range(2, len(recent) - 2):
            if (recent['High'].iloc[i] > recent['High'].iloc[i-1] and 
                recent['High'].iloc[i] > recent['High'].iloc[i-2] and
                recent['High'].iloc[i] > recent['High'].iloc[i+1] and
                recent['High'].iloc[i] > recent['High'].iloc[i+2]):
                peaks.append((i, recent['High'].iloc[i]))
            
            if (recent['Low'].iloc[i] < recent['Low'].iloc[i-1] and 
                recent['Low'].iloc[i] < recent['Low'].iloc[i-2] and
                recent['Low'].iloc[i] < recent['Low'].iloc[i+1] and
                recent['Low'].iloc[i] < recent['Low'].iloc[i+2]):
                troughs.append((i, recent['Low'].iloc[i]))
        
        # Check for double top
        if len(peaks) >= 2:
            for i in range(len(peaks) - 1):
                peak1 = peaks[i]
                peak2 = peaks[i + 1]
                if abs(peak1[1] - peak2[1]) / peak1[1] < 0.03:  # Within 3%
                    return {
                        'pattern': 'Double Top',
                        'direction': 'bearish',
                        'confidence': 0.7,
                        'description': 'Two peaks at similar level, potential reversal',
                        'level': round(peak1[1], 2),
                    }
        
        # Check for double bottom
        if len(troughs) >= 2:
            for i in range(len(troughs) - 1):
                trough1 = troughs[i]
                trough2 = troughs[i + 1]
                if abs(trough1[1] - trough2[1]) / trough1[1] < 0.03:
                    return {
                        'pattern': 'Double Bottom',
                        'direction': 'bullish',
                        'confidence': 0.7,
                        'description': 'Two troughs at similar level, potential reversal',
                        'level': round(trough1[1], 2),
                    }
        
        return None
    
    def _detect_head_shoulders(self, df: pd.DataFrame) -> Dict:
        """Detect head and shoulders pattern"""
        # Simplified detection - would need more sophisticated algorithm for production
        recent = df.tail(100)
        
        # Look for three peaks with middle one highest
        peaks = []
        for i in range(5, len(recent) - 5):
            window = recent.iloc[i-5:i+6]
            if recent['High'].iloc[i] == window['High'].max():
                peaks.append((i, recent['High'].iloc[i]))
        
        if len(peaks) >= 3:
            # Check if middle peak is highest
            mid_idx = len(peaks) // 2
            if peaks[mid_idx][1] > peaks[mid_idx-1][1] and peaks[mid_idx][1] > peaks[mid_idx+1][1]:
                return {
                    'pattern': 'Head and Shoulders',
                    'direction': 'bearish',
                    'confidence': 0.6,
                    'description': 'Three peaks with middle highest, bearish reversal signal',
                    'neckline': round(min(peaks[mid_idx-1][1], peaks[mid_idx+1][1]), 2),
                }
        
        return None
    
    def _detect_triangle(self, df: pd.DataFrame) -> Dict:
        """Detect triangle patterns (ascending, descending, symmetrical)"""
        recent = df.tail(40)
        
        highs = recent['High'].tail(20)
        lows = recent['Low'].tail(20)
        
        # Calculate trend of highs and lows
        high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
        low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
        
        # Ascending triangle: flat top, rising bottom
        if abs(high_slope) < 0.1 and low_slope > 0.5:
            return {
                'pattern': 'Ascending Triangle',
                'direction': 'bullish',
                'confidence': 0.65,
                'description': 'Flat resistance with rising support, bullish breakout likely',
            }
        
        # Descending triangle: falling top, flat bottom
        if high_slope < -0.5 and abs(low_slope) < 0.1:
            return {
                'pattern': 'Descending Triangle',
                'direction': 'bearish',
                'confidence': 0.65,
                'description': 'Falling resistance with flat support, bearish breakdown likely',
            }
        
        # Symmetrical triangle: converging highs and lows
        if high_slope < -0.2 and low_slope > 0.2:
            return {
                'pattern': 'Symmetrical Triangle',
                'direction': 'neutral',
                'confidence': 0.5,
                'description': 'Converging highs and lows, breakout direction uncertain',
            }
        
        return None
    
    def _detect_flag_pennant(self, df: pd.DataFrame) -> Dict:
        """Detect flag or pennant patterns"""
        recent = df.tail(30)
        
        # Check for strong prior move (pole)
        prior_move = (recent['Close'].iloc[-20] / recent['Close'].iloc[-30] - 1) * 100
        
        # Check for consolidation after move
        consolidation = recent['Close'].tail(10)
        consolidation_volatility = consolidation.pct_change().std() * 100
        
        if abs(prior_move) > 5 and consolidation_volatility < 2:
            direction = 'bullish' if prior_move > 0 else 'bearish'
            return {
                'pattern': 'Flag/Pennant',
                'direction': direction,
                'confidence': 0.6,
                'description': f'Consolidation after {direction} move, continuation likely',
            }
        
        return None
    
    def _analyze_trend(self, df: pd.DataFrame) -> Dict:
        """Analyze overall trend"""
        # Multiple timeframe trend analysis
        current = df['Close'].iloc[-1]
        
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(50).mean().iloc[-1]
        sma_200 = df['Close'].rolling(200).mean().iloc[-1]
        
        # Trend based on moving averages
        if current > sma_20 > sma_50 > sma_200:
            trend = 'strong_uptrend'
            strength = 'strong'
        elif current > sma_20 > sma_50:
            trend = 'uptrend'
            strength = 'moderate'
        elif current < sma_20 < sma_50 < sma_200:
            trend = 'strong_downtrend'
            strength = 'strong'
        elif current < sma_20 < sma_50:
            trend = 'downtrend'
            strength = 'moderate'
        else:
            trend = 'sideways'
            strength = 'weak'
        
        # Trend duration
        if trend == 'uptrend' or trend == 'strong_uptrend':
            # Find when price crossed below SMA 50
            cross_date = None
            for i in range(len(df) - 1, 0, -1):
                if df['Close'].iloc[i] < df['Close'].rolling(50).mean().iloc[i]:
                    cross_date = df.index[i]
                    break
        else:
            cross_date = None
        
        return {
            'trend': trend,
            'strength': strength,
            'sma_20': round(sma_20, 2),
            'sma_50': round(sma_50, 2),
            'sma_200': round(sma_200, 2),
            'trend_since': cross_date.strftime('%Y-%m-%d') if cross_date else 'N/A',
        }
    
    def _analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Analyze volume patterns"""
        if 'Volume' not in df.columns:
            return {'error': 'No volume data'}
        
        recent_volume = df['Volume'].tail(20)
        avg_volume = df['Volume'].tail(50).mean()
        
        # Volume trend
        volume_trend = 'increasing' if recent_volume.iloc[-1] > recent_volume.iloc[0] else 'decreasing'
        
        # Volume spike detection
        current_volume = df['Volume'].iloc[-1]
        volume_spike = current_volume > avg_volume * 1.5
        
        # Volume divergence
        price_change = (df['Close'].iloc[-1] / df['Close'].iloc[-5] - 1) * 100
        volume_change = (df['Volume'].iloc[-1] / df['Volume'].iloc[-5] - 1) * 100
        
        divergence = None
        if price_change > 0 and volume_change < 0:
            divergence = 'bearish'  # Price up on low volume
        elif price_change < 0 and volume_change > 0:
            divergence = 'bullish'  # Price down on high volume (capitulation)
        
        return {
            'current_volume': int(current_volume),
            'avg_volume': int(avg_volume),
            'volume_ratio': round(current_volume / avg_volume, 2),
            'volume_trend': volume_trend,
            'volume_spike': volume_spike,
            'volume_divergence': divergence,
        }
    
    def _calculate_performance_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate key performance metrics"""
        current = df['Close'].iloc[-1]
        
        # Returns over different periods
        returns = {
            '1d': (current / df['Close'].iloc[-2] - 1) * 100 if len(df) > 1 else 0,
            '1w': (current / df['Close'].iloc[-6] - 1) * 100 if len(df) > 5 else 0,
            '1m': (current / df['Close'].iloc[-21] - 1) * 100 if len(df) > 20 else 0,
            '3m': (current / df['Close'].iloc[-63] - 1) * 100 if len(df) > 62 else 0,
            '6m': (current / df['Close'].iloc[-126] - 1) * 100 if len(df) > 125 else 0,
            '1y': (current / df['Close'].iloc[0] - 1) * 100 if len(df) > 0 else 0,
        }
        
        # Max drawdown
        rolling_max = df['Close'].expanding().max()
        drawdown = (df['Close'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        # Volatility (annualized)
        daily_returns = df['Close'].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100
        
        # Sharpe ratio (simplified, assuming 0% risk-free rate)
        sharpe = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0
        
        return {
            'returns': {k: round(v, 2) for k, v in returns.items()},
            'max_drawdown': round(max_drawdown, 2),
            'volatility': round(volatility, 2),
            'sharpe_ratio': round(sharpe, 2),
        }
    
    def _identify_key_levels(self, df: pd.DataFrame) -> Dict:
        """Identify key price levels for trading"""
        current = df['Close'].iloc[-1]
        
        # Recent high/low
        recent_high = df['High'].tail(52).max()  # 52-week high
        recent_low = df['Low'].tail(52).min()  # 52-week low
        
        # Pivot points (simplified)
        pivot = (recent_high + recent_low + current) / 3
        r1 = 2 * pivot - recent_low
        s1 = 2 * pivot - recent_high
        
        return {
            'current_price': round(current, 2),
            '52_week_high': round(recent_high, 2),
            '52_week_low': round(recent_low, 2),
            'distance_from_high': round((current / recent_high - 1) * 100, 2),
            'distance_from_low': round((current / recent_low - 1) * 100, 2),
            'pivot_point': round(pivot, 2),
            'resistance_1': round(r1, 2),
            'support_1': round(s1, 2),
        }
