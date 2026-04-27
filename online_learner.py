import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import yfinance as yf

# Try to import River for online learning
try:
    from river import linear_model
    from river import optim
    from river import metrics
    from river import preprocessing
    RIVER_AVAILABLE = True
except ImportError:
    RIVER_AVAILABLE = False
    print("River not available. Install with: pip install river")

@dataclass
class OnlineLearningResult:
    """Result of online learning"""
    prediction: str
    probability: float
    confidence: float
    samples_seen: int
    current_accuracy: float

if RIVER_AVAILABLE:
    class OnlineLearner:
        """
        Online learning system for incremental model updates
        
        Uses River library for streaming machine learning
        """
        
        def __init__(self):
            # Initialize online model
            self.model = linear_model.LogisticRegression(
                optimizer=optim.SGD(0.01),
                loss=optim.losses.Log()
            )
            
            # Initialize scaler
            self.scaler = preprocessing.StandardScaler()
            
            # Pipeline: scale -> model
            self.pipeline = (
                self.scaler |
                self.model
            )
            
            # Metrics
            self.accuracy = metrics.Accuracy()
            self.samples_seen = 0
            
            # Feature names
            self.feature_names = [
                'rsi', 'macd', 'momentum_20d', 'volume_change',
                'price_vs_sma50', 'price_vs_sma200', 'volatility',
                'high_low_range', 'gap', 'trend_strength'
            ]
        
        def prepare_features(self, hist) -> Dict:
            """
            Prepare features as dictionary for River
            
            Args:
                hist: Historical price data
            """
            if len(hist) < 50:
                return None
            
            features = {}
            
            # RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            features['rsi'] = float(rsi.iloc[-1]) if not rsi.empty else 50.0
            
            # MACD
            ema_12 = hist['Close'].ewm(span=12).mean()
            ema_26 = hist['Close'].ewm(span=26).mean()
            macd = ema_12 - ema_26
            features['macd'] = float(macd.iloc[-1]) if not macd.empty else 0.0
            
            # Momentum
            momentum_20d = float((hist['Close'].iloc[-1] / hist['Close'].iloc[-21] - 1) * 100) if len(hist) > 20 else 0.0
            features['momentum_20d'] = momentum_20d
            
            # Volume change
            if 'Volume' in hist.columns:
                volume_change = float((hist['Volume'].iloc[-1] / hist['Volume'].iloc[-5:].mean() - 1) * 100) if len(hist) > 5 else 0.0
            else:
                volume_change = 0.0
            features['volume_change'] = volume_change
            
            # Price vs SMA50
            sma_50 = hist['Close'].rolling(50).mean()
            price_vs_sma50 = float((hist['Close'].iloc[-1] / sma_50.iloc[-1] - 1) * 100) if not sma_50.empty else 0.0
            features['price_vs_sma50'] = price_vs_sma50
            
            # Price vs SMA200
            sma_200 = hist['Close'].rolling(200).mean()
            price_vs_sma200 = float((hist['Close'].iloc[-1] / sma_200.iloc[-1] - 1) * 100) if not sma_200.empty else 0.0
            features['price_vs_sma200'] = price_vs_sma200
            
            # Volatility
            returns = hist['Close'].pct_change()
            volatility = float(returns.rolling(20).std().iloc[-1] * np.sqrt(252)) if not returns.empty else 0.0
            features['volatility'] = volatility
            
            # High-low range
            high_low_range = float((hist['High'].iloc[-1] / hist['Low'].iloc[-1] - 1) * 100) if not hist.empty else 0.0
            features['high_low_range'] = high_low_range
            
            # Gap
            gap = float((hist['Open'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100) if len(hist) > 2 else 0.0
            features['gap'] = gap
            
            # Trend strength
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
            trend_strength = float(dx.rolling(14).mean().iloc[-1]) if not dx.empty else 0.0
            features['trend_strength'] = trend_strength
            
            return features
        
        def learn_one(self, features: Dict, label: int):
            """
            Learn from one sample
            
            Args:
                features: Feature dictionary
                label: True label (0=bearish, 1=bullish, 2=neutral)
            """
            # Learn from sample
            self.pipeline.learn_one(features, label)
            self.samples_seen += 1
            
            # Update metrics
            prediction = self.pipeline.predict_one(features)
            self.accuracy.update(label, prediction)
        
        def predict_one(self, features: Dict) -> OnlineLearningResult:
            """
            Predict for one sample
            
            Args:
                features: Feature dictionary
            """
            # Get prediction probabilities
            proba = self.pipeline.predict_proba_one(features)
            
            # River returns probabilities for each class
            # Get the class with highest probability
            if proba:
                prediction = max(proba, key=proba.get)
                probability = proba[prediction]
            else:
                prediction = 2  # neutral
                probability = 0.5
            
            # Convert to direction
            if prediction == 1:
                direction = 'bullish'
            elif prediction == 0:
                direction = 'bearish'
            else:
                direction = 'neutral'
            
            # Confidence
            confidence = probability if probability > 0.5 else 1 - probability
            
            return OnlineLearningResult(
                prediction=direction,
                probability=round(probability, 3),
                confidence=round(confidence, 3),
                samples_seen=self.samples_seen,
                current_accuracy=round(self.accuracy.get(), 4)
            )
        
        def train_online(self, symbol: str, period: str = '1y'):
            """
            Train model online on historical data
            
            Args:
                symbol: Stock ticker
                period: Historical period
            """
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                
                if len(hist) < 100:
                    print("Insufficient data for online training")
                    return
                
                # Train on historical data
                for i in range(50, len(hist) - 3):
                    window = hist.iloc[:i+3]
                    features = self.prepare_features(window)
                    
                    if features is not None:
                        # Generate label
                        current_price = hist['Close'].iloc[i]
                        future_price = hist['Close'].iloc[min(i+3, len(hist)-1)]
                        
                        if future_price > current_price * 1.015:
                            label = 1  # bullish
                        elif future_price < current_price * 0.985:
                            label = 0  # bearish
                        else:
                            label = 2  # neutral
                        
                        # Learn from sample
                        self.learn_one(features, label)
                
                print(f"Online training complete. Samples seen: {self.samples_seen}")
                print(f"Current accuracy: {self.accuracy.get():.4f}")
            except Exception as e:
                print(f"Error in online training: {e}")
        
        def predict(self, symbol: str) -> OnlineLearningResult:
            """
            Predict for a symbol
            
            Args:
                symbol: Stock ticker
            """
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1y")
                
                if hist.empty:
                    return OnlineLearningResult(
                        prediction='neutral',
                        probability=0.5,
                        confidence=0.0,
                        samples_seen=self.samples_seen,
                        current_accuracy=0.0
                    )
                
                features = self.prepare_features(hist)
                if features is None:
                    return OnlineLearningResult(
                        prediction='neutral',
                        probability=0.5,
                        confidence=0.0,
                        samples_seen=self.samples_seen,
                        current_accuracy=0.0
                    )
                
                return self.predict_one(features)
            except Exception as e:
                print(f"Error in prediction: {e}")
                return OnlineLearningResult(
                    prediction='neutral',
                    probability=0.5,
                    confidence=0.0,
                    samples_seen=self.samples_seen,
                    current_accuracy=0.0
                )
        
        def get_metrics(self) -> Dict:
            """Get current metrics"""
            return {
                'samples_seen': self.samples_seen,
                'accuracy': self.accuracy.get(),
                'model': str(self.model)
            }
        
        def reset(self):
            """Reset the model"""
            self.model = linear_model.LogisticRegression(
                optimizer=optim.SGD(0.01),
                loss=optim.losses.Log()
            )
            self.scaler = preprocessing.StandardScaler()
            self.pipeline = (self.scaler | self.model)
            self.accuracy = metrics.Accuracy()
            self.samples_seen = 0
            print("Model reset")
else:
    # Dummy class when River is not available
    class OnlineLearner:
        def __init__(self):
            raise ImportError("River library not available. Install with: pip install river")
