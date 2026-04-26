import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import yfinance as yf

@dataclass
class MLPrediction:
    """ML prediction result"""
    direction: str  # 'bullish', 'bearish', 'neutral'
    probability: float  # 0-1
    confidence: float  # 0-1
    features_importance: Dict[str, float]
    model_type: str

class MLPredictor:
    """
    Machine Learning prediction layer for probabilistic signals
    
    Uses ensemble methods to generate probability-based predictions
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Feature names for interpretation
        self.feature_names = [
            'rsi', 'macd', 'momentum_20d', 'volume_change',
            'price_vs_sma50', 'price_vs_sma200', 'volatility',
            'high_low_range', 'gap', 'trend_strength'
        ]
    
    def prepare_features(self, hist: pd.DataFrame) -> np.ndarray:
        """
        Prepare technical features for ML model
        
        Args:
            hist: Historical price data
        """
        if len(hist) < 50:
            return None
        
        features = []
        
        # RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        features.append(rsi.iloc[-1])
        
        # MACD
        ema_12 = hist['Close'].ewm(span=12).mean()
        ema_26 = hist['Close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        features.append(macd.iloc[-1])
        
        # Momentum (20-day)
        momentum_20d = (hist['Close'].iloc[-1] / hist['Close'].iloc[-21] - 1) * 100
        features.append(momentum_20d)
        
        # Volume change
        if 'Volume' in hist.columns:
            volume_change = (hist['Volume'].iloc[-1] / hist['Volume'].iloc[-5:].mean() - 1) * 100
        else:
            volume_change = 0
        features.append(volume_change)
        
        # Price vs SMA50
        sma_50 = hist['Close'].rolling(50).mean()
        price_vs_sma50 = (hist['Close'].iloc[-1] / sma_50.iloc[-1] - 1) * 100
        features.append(price_vs_sma50)
        
        # Price vs SMA200
        sma_200 = hist['Close'].rolling(200).mean()
        price_vs_sma200 = (hist['Close'].iloc[-1] / sma_200.iloc[-1] - 1) * 100
        features.append(price_vs_sma200)
        
        # Volatility (20-day)
        returns = hist['Close'].pct_change()
        volatility = returns.rolling(20).std().iloc[-1] * np.sqrt(252)
        features.append(volatility)
        
        # High-Low range
        high_low_range = (hist['High'].iloc[-1] / hist['Low'].iloc[-1] - 1) * 100
        features.append(high_low_range)
        
        # Gap
        gap = (hist['Open'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100
        features.append(gap)
        
        # Trend strength (ADX-like)
        high_diff = hist['High'].diff()
        low_diff = hist['Low'].diff()
        plus_dm = high_diff.where((high_diff > 0) & (low_diff < 0), 0)
        minus_dm = -low_diff.where((low_diff > 0) & (high_diff < 0), 0)
        tr = pd.concat([hist['High'] - hist['Low'], 
                       abs(hist['High'] - hist['Close'].shift(1)),
                       abs(hist['Low'] - hist['Close'].shift(1))], axis=1).max(axis=1)
        
        plus_di = 100 * (plus_dm.rolling(14).mean() / tr.rolling(14).mean())
        minus_di = 100 * (minus_dm.rolling(14).mean() / tr.rolling(14).mean())
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        trend_strength = dx.rolling(14).mean().iloc[-1]
        features.append(trend_strength)
        
        return np.array(features).reshape(1, -1)
    
    def generate_labels(self, hist: pd.DataFrame, forward_days: int = 5) -> np.ndarray:
        """
        Generate labels for training (future price direction)
        
        Args:
            hist: Historical price data
            forward_days: Days to look ahead for label
        """
        if len(hist) < forward_days + 50:
            return None
        
        labels = []
        for i in range(50, len(hist) - forward_days):
            current_price = hist['Close'].iloc[i]
            future_price = hist['Close'].iloc[i + forward_days]
            
            if future_price > current_price * 1.02:  # 2% up
                labels.append(1)  # bullish
            elif future_price < current_price * 0.98:  # 2% down
                labels.append(0)  # bearish
            else:
                labels.append(2)  # neutral
        
        return np.array(labels)
    
    def train(self, symbol: str, period: str = '2y') -> Dict:
        """
        Train ML model on historical data
        
        Args:
            symbol: Stock ticker
            period: Historical period for training
        """
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if len(hist) < 100:
                return {'error': 'Insufficient data for training'}
            
            # Prepare features and labels
            features_list = []
            labels_list = []
            
            for i in range(50, len(hist) - 5):
                window = hist.iloc[:i+5]
                features = self.prepare_features(window)
                if features is not None:
                    features_list.append(features[0])
                    
                    # Generate label
                    current_price = hist['Close'].iloc[i]
                    future_price = hist['Close'].iloc[min(i+5, len(hist)-1)]
                    
                    if future_price > current_price * 1.02:
                        labels_list.append(1)
                    elif future_price < current_price * 0.98:
                        labels_list.append(0)
                    else:
                        labels_list.append(2)
            
            if len(features_list) < 50:
                return {'error': 'Insufficient training samples'}
            
            X = np.array(features_list)
            y = np.array(labels_list)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Get feature importance
            importance = dict(zip(self.feature_names, self.model.feature_importances_))
            
            return {
                'status': 'success',
                'samples': len(features_list),
                'feature_importance': importance,
                'accuracy': self.model.score(X_scaled, y)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def predict(self, symbol: str, use_trained: bool = False) -> MLPrediction:
        """
        Generate ML prediction for a symbol
        
        Args:
            symbol: Stock ticker
            use_trained: Whether to use trained model or heuristic
        """
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return MLPrediction(
                    direction='neutral',
                    probability=0.5,
                    confidence=0.0,
                    features_importance={},
                    model_type='none'
                )
            
            # Prepare features
            features = self.prepare_features(hist)
            if features is None:
                return MLPrediction(
                    direction='neutral',
                    probability=0.5,
                    confidence=0.0,
                    features_importance={},
                    model_type='none'
                )
            
            if use_trained and self.is_trained:
                # Use trained model
                features_scaled = self.scaler.transform(features)
                proba = self.model.predict_proba(features_scaled)[0]
                
                # Get prediction
                prediction = self.model.predict(features_scaled)[0]
                
                if prediction == 1:
                    direction = 'bullish'
                    probability = proba[1]
                elif prediction == 0:
                    direction = 'bearish'
                    probability = proba[0]
                else:
                    direction = 'neutral'
                    probability = proba[2] if len(proba) > 2 else 0.5
                
                confidence = max(proba)
                importance = dict(zip(self.feature_names, self.model.feature_importances_))
                model_type = 'trained_random_forest'
            else:
                # Use heuristic (rule-based) prediction
                direction, probability, confidence = self._heuristic_prediction(features[0])
                importance = {}
                model_type = 'heuristic'
            
            return MLPrediction(
                direction=direction,
                probability=round(probability, 3),
                confidence=round(confidence, 3),
                features_importance=importance,
                model_type=model_type
            )
        except Exception as e:
            return MLPrediction(
                direction='neutral',
                probability=0.5,
                confidence=0.0,
                features_importance={},
                model_type='error'
            )
    
    def _heuristic_prediction(self, features: np.ndarray) -> tuple:
        """
        Generate heuristic prediction based on technical indicators
        
        Args:
            features: Array of technical features
        """
        rsi, macd, momentum, volume_change, price_vs_sma50, price_vs_sma200, volatility, high_low_range, gap, trend_strength = features
        
        bullish_score = 0
        bearish_score = 0
        
        # RSI
        if rsi < 30:
            bullish_score += 2
        elif rsi > 70:
            bearish_score += 2
        elif 40 < rsi < 60:
            bullish_score += 1
        
        # MACD
        if macd > 0:
            bullish_score += 1
        else:
            bearish_score += 1
        
        # Momentum
        if momentum > 3:
            bullish_score += 2
        elif momentum > 1:
            bullish_score += 1
        elif momentum < -3:
            bearish_score += 2
        elif momentum < -1:
            bearish_score += 1
        
        # Price vs SMAs
        if price_vs_sma50 > 2:
            bullish_score += 2
        elif price_vs_sma50 < -2:
            bearish_score += 2
        
        if price_vs_sma200 > 5:
            bullish_score += 2
        elif price_vs_sma200 < -5:
            bearish_score += 2
        
        # Trend strength
        if trend_strength > 25:
            bullish_score += 1
        
        # Gap
        if gap > 2:
            bullish_score += 1
        elif gap < -2:
            bearish_score += 1
        
        # Determine direction
        total = bullish_score + bearish_score
        if total == 0:
            direction = 'neutral'
            probability = 0.5
        elif bullish_score > bearish_score:
            direction = 'bullish'
            probability = bullish_score / total
        else:
            direction = 'bearish'
            probability = bearish_score / total
        
        # Confidence based on signal strength
        confidence = min(abs(bullish_score - bearish_score) / 10, 1.0)
        
        return direction, probability, confidence
    
    def batch_predict(self, symbols: List[str]) -> Dict[str, MLPrediction]:
        """
        Generate predictions for multiple symbols
        
        Args:
            symbols: List of stock tickers
        """
        predictions = {}
        for symbol in symbols:
            predictions[symbol] = self.predict(symbol)
        return predictions
