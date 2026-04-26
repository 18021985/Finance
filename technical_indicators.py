import pandas as pd
import numpy as np
from typing import Dict, Tuple

class TechnicalIndicators:
    """Calculate technical indicators for signal generation"""
    
    @staticmethod
    def calculate_rsi(series: pd.Series, length: int = 14) -> pd.Series:
        """Calculate RSI using native pandas"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Calculate MACD using native pandas"""
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return pd.DataFrame({
            'MACD_12_26_9': macd_line,
            'MACDs_12_26_9': signal_line,
            'MACDh_12_26_9': histogram
        })
    
    @staticmethod
    def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.DataFrame:
        """Calculate ADX using native pandas"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr_smooth = tr.rolling(window=length).mean()
        plus_dm_smooth = plus_dm.rolling(window=length).mean()
        minus_dm_smooth = minus_dm.rolling(window=length).mean()
        
        plus_di = 100 * (plus_dm_smooth / tr_smooth)
        minus_di = 100 * (minus_dm_smooth / tr_smooth)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=length).mean()
        
        return pd.DataFrame({'ADX_14': adx})
    
    @staticmethod
    def calculate_bbands(series: pd.Series, length: int = 20, std: int = 2) -> pd.DataFrame:
        """Calculate Bollinger Bands using native pandas"""
        sma = series.rolling(window=length).mean()
        rolling_std = series.rolling(window=length).std()
        upper = sma + (rolling_std * std)
        lower = sma - (rolling_std * std)
        return pd.DataFrame({
            'BBM_20_2.0': sma,
            'BBU_20_2.0': upper,
            'BBL_20_2.0': lower
        })
    
    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
        """Calculate ATR using native pandas"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=length).mean()
    
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
        rsi_series = TechnicalIndicators.calculate_rsi(df['Close'], length=14)
        indicators['rsi'] = rsi_series.iloc[-1] if not rsi_series.empty else 50
        
        # MACD
        macd = TechnicalIndicators.calculate_macd(df['Close'], fast=12, slow=26, signal=9)
        if macd is not None and not macd.empty:
            indicators['macd'] = macd['MACD_12_26_9'].iloc[-1]
            indicators['macd_signal'] = macd['MACDs_12_26_9'].iloc[-1]
            indicators['macd_histogram'] = macd['MACDh_12_26_9'].iloc[-1]
        
        # ADX (Trend strength)
        adx = TechnicalIndicators.calculate_adx(df['High'], df['Low'], df['Close'], length=14)
        if adx is not None and not adx.empty:
            indicators['adx'] = adx['ADX_14'].iloc[-1]
        
        # Bollinger Bands
        bb = TechnicalIndicators.calculate_bbands(df['Close'], length=20, std=2)
        if bb is not None and not bb.empty:
            indicators['bb_lower'] = bb['BBL_20_2.0'].iloc[-1]
            indicators['bb_middle'] = bb['BBM_20_2.0'].iloc[-1]
            indicators['bb_upper'] = bb['BBU_20_2.0'].iloc[-1]
        
        # Support and Resistance (using recent highs/lows)
        indicators['recent_high'] = df['High'].rolling(window=20).max().iloc[-1]
        indicators['recent_low'] = df['Low'].rolling(window=20).min().iloc[-1]
        
        # Volatility (ATR)
        atr = TechnicalIndicators.calculate_atr(df['High'], df['Low'], df['Close'], length=14)
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
