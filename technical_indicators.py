import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, Tuple

class TechnicalIndicators:
    """Calculate technical indicators for signal generation"""
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> Dict:
        """Calculate all technical indicators"""
        if df.empty or len(df) < 200:
            return {}
        
        indicators = {}
        
        # Moving Averages
        indicators['sma_50'] = df['Close'].rolling(window=50).mean().iloc[-1]
        indicators['sma_200'] = df['Close'].rolling(window=200).mean().iloc[-1]
        
        # RSI
        rsi_series = ta.rsi(df['Close'], length=14)
        indicators['rsi'] = rsi_series.iloc[-1] if not rsi_series.empty else 50
        
        # MACD
        macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        if macd is not None and not macd.empty:
            indicators['macd'] = macd['MACD_12_26_9'].iloc[-1]
            indicators['macd_signal'] = macd['MACDs_12_26_9'].iloc[-1]
            indicators['macd_histogram'] = macd['MACDh_12_26_9'].iloc[-1]
        
        # ADX (Trend strength)
        adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        if adx is not None and not adx.empty:
            indicators['adx'] = adx['ADX_14'].iloc[-1]
        
        # Bollinger Bands
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is not None and not bb.empty:
            # Map columns dynamically based on what pandas-ta returns
            bb_cols = bb.columns.tolist()
            if 'BBL_20_2.0' in bb_cols:
                indicators['bb_lower'] = bb['BBL_20_2.0'].iloc[-1]
                indicators['bb_middle'] = bb['BBM_20_2.0'].iloc[-1]
                indicators['bb_upper'] = bb['BBU_20_2.0'].iloc[-1]
            else:
                # Fallback: use first three columns
                if len(bb_cols) >= 3:
                    indicators['bb_lower'] = bb[bb_cols[0]].iloc[-1]
                    indicators['bb_middle'] = bb[bb_cols[1]].iloc[-1]
                    indicators['bb_upper'] = bb[bb_cols[2]].iloc[-1]
        
        # Support and Resistance (using recent highs/lows)
        indicators['recent_high'] = df['High'].rolling(window=20).max().iloc[-1]
        indicators['recent_low'] = df['Low'].rolling(window=20).min().iloc[-1]
        
        # Volatility (ATR)
        atr = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        if atr is not None and not atr.empty:
            indicators['atr'] = atr.iloc[-1]
        
        # Current price
        indicators['current_price'] = df['Close'].iloc[-1]
        
        return indicators
    
    @staticmethod
    def golden_cross(indicators: Dict) -> Tuple[bool, float]:
        """Check for Golden Cross (50MA > 200MA)"""
        sma_50 = indicators.get('sma_50', 0)
        sma_200 = indicators.get('sma_200', 0)
        
        if sma_50 > sma_200:
            strength = min(5, 3 + (sma_50 / sma_200 - 1) * 50)
            return True, max(0, min(5, strength))
        return False, 0
    
    @staticmethod
    def death_cross(indicators: Dict) -> Tuple[bool, float]:
        """Check for Death Cross (50MA < 200MA)"""
        sma_50 = indicators.get('sma_50', 0)
        sma_200 = indicators.get('sma_200', 0)
        
        if sma_50 < sma_200:
            strength = min(5, 3 + (1 - sma_50 / sma_200) * 50)
            return True, max(0, min(5, strength))
        return False, 0
    
    @staticmethod
    def rsi_oversold(indicators: Dict) -> Tuple[bool, float]:
        """Check for RSI oversold (<30) and rising"""
        rsi = indicators.get('rsi', 50)
        
        if rsi < 30:
            strength = (30 - rsi) / 30 * 5
            return True, max(0, min(5, strength))
        return False, 0
    
    @staticmethod
    def rsi_overbought(indicators: Dict) -> Tuple[bool, float]:
        """Check for RSI overbought (>70) and falling"""
        rsi = indicators.get('rsi', 50)
        
        if rsi > 70:
            strength = (rsi - 70) / 30 * 5
            return True, max(0, min(5, strength))
        return False, 0
    
    @staticmethod
    def macd_bullish(indicators: Dict) -> Tuple[bool, float]:
        """Check for MACD bullish crossover"""
        macd = indicators.get('macd', 0)
        signal = indicators.get('macd_signal', 0)
        
        if macd > signal and macd > 0:
            strength = min(5, 3 + abs(macd - signal) * 10)
            return True, max(0, min(5, strength))
        return False, 0
    
    @staticmethod
    def macd_bearish(indicators: Dict) -> Tuple[bool, float]:
        """Check for MACD bearish crossover"""
        macd = indicators.get('macd', 0)
        signal = indicators.get('macd_signal', 0)
        
        if macd < signal and macd < 0:
            strength = min(5, 3 + abs(macd - signal) * 10)
            return True, max(0, min(5, strength))
        return False, 0
    
    @staticmethod
    def breakout_above_resistance(indicators: Dict) -> Tuple[bool, float]:
        """Check for breakout above recent resistance"""
        current = indicators.get('current_price', 0)
        resistance = indicators.get('recent_high', 0)
        
        if current > resistance * 0.99:  # Near or above resistance
            strength = min(5, (current / resistance - 0.99) * 500)
            return True, max(0, min(5, strength))
        return False, 0
    
    @staticmethod
    def breakdown_below_support(indicators: Dict) -> Tuple[bool, float]:
        """Check for breakdown below recent support"""
        current = indicators.get('current_price', 0)
        support = indicators.get('recent_low', 0)
        
        if current < support * 1.01:  # Near or below support
            strength = min(5, (1.01 - current / support) * 500)
            return True, max(0, min(5, strength))
        return False, 0
    
    @staticmethod
    def strong_trend(indicators: Dict) -> Tuple[bool, float]:
        """Check for strong trend using ADX (>25)"""
        adx = indicators.get('adx', 0)
        
        if adx > 25:
            strength = min(5, (adx - 25) / 25 * 5)
            return True, max(0, min(5, strength))
        return False, 0
    
    @staticmethod
    def volatility_spike(indicators: Dict, df: pd.DataFrame) -> Tuple[bool, float]:
        """Check for volatility spike"""
        atr = indicators.get('atr', 0)
        current_price = indicators.get('current_price', 0)
        
        if atr > 0 and current_price > 0:
            atr_pct = (atr / current_price) * 100
            if atr_pct > 3:  # High volatility threshold
                strength = min(5, atr_pct / 3)
                return True, max(0, min(5, strength))
        return False, 0
