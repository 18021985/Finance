import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import yfinance as yf

# Try to import TensorFlow/Keras
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("TensorFlow not available. Install with: pip install tensorflow")

@dataclass
class DLPrediction:
    """Deep learning prediction result"""
    direction: str
    probability: float
    confidence: float
    model_type: str
    sequence_length: int

class DeepLearningPredictor:
    """
    Deep learning predictor using LSTM/GRU models
    
    Features:
    - LSTM for sequence modeling
    - GRU for faster training
    - Bidirectional layers
    - Attention mechanism
    """
    
    def __init__(self, sequence_length: int = 50):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = None
        self.is_trained = False
        self.model_type = 'lstm'
        
        # Feature names
        self.feature_names = [
            'rsi', 'macd', 'momentum_20d', 'volume_change',
            'price_vs_sma50', 'price_vs_sma200', 'volatility',
            'high_low_range', 'gap', 'trend_strength'
        ]
    
    def prepare_sequences(self, hist: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequences for LSTM/GRU
        
        Args:
            hist: Historical price data
        """
        if len(hist) < self.sequence_length + 10:
            return None, None
        
        # Prepare features
        features_list = []
        for i in range(50, len(hist) - 3):
            window = hist.iloc[:i+3]
            features = self._prepare_features(window)
            if features is not None:
                features_list.append(features)
        
        if len(features_list) < self.sequence_length + 10:
            return None, None
        
        features_array = np.array(features_list)
        
        # Create sequences
        X = []
        y = []
        
        for i in range(len(features_array) - self.sequence_length - 3):
            X.append(features_array[i:i+self.sequence_length])
            
            # Label
            current_price = hist['Close'].iloc[i + 50]
            future_price = hist['Close'].iloc[i + 50 + 3]
            
            if future_price > current_price * 1.015:
                y.append(1)  # bullish
            elif future_price < current_price * 0.985:
                y.append(0)  # bearish
            else:
                y.append(2)  # neutral
        
        return np.array(X), np.array(y)
    
    def _prepare_features(self, hist: pd.DataFrame) -> np.ndarray:
        """Prepare features for a single window"""
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
        
        # Momentum
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
        
        # Volatility
        returns = hist['Close'].pct_change()
        volatility = returns.rolling(20).std().iloc[-1] * np.sqrt(252)
        features.append(volatility)
        
        # High-low range
        high_low_range = (hist['High'].iloc[-1] / hist['Low'].iloc[-1] - 1) * 100
        features.append(high_low_range)
        
        # Gap
        gap = (hist['Open'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100
        features.append(gap)
        
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
        trend_strength = dx.rolling(14).mean().iloc[-1]
        features.append(trend_strength)
        
        return np.array(features)
    
    def build_lstm_model(self, input_shape: Tuple[int, int]):
        """
        Build LSTM model
        
        Args:
            input_shape: (sequence_length, n_features)
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is not available. Install with: pip install tensorflow")
        
        model = keras.Sequential([
            layers.LSTM(128, return_sequences=True, input_shape=input_shape),
            layers.Dropout(0.2),
            layers.LSTM(64, return_sequences=True),
            layers.Dropout(0.2),
            layers.LSTM(32),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(3, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def build_gru_model(self, input_shape: Tuple[int, int]):
        """
        Build GRU model (faster than LSTM)
        
        Args:
            input_shape: (sequence_length, n_features)
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is not available. Install with: pip install tensorflow")
        
        model = keras.Sequential([
            layers.GRU(128, return_sequences=True, input_shape=input_shape),
            layers.Dropout(0.2),
            layers.GRU(64, return_sequences=True),
            layers.Dropout(0.2),
            layers.GRU(32),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(3, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def build_bidirectional_lstm(self, input_shape: Tuple[int, int]):
        """
        Build bidirectional LSTM model
        
        Args:
            input_shape: (sequence_length, n_features)
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is not available. Install with: pip install tensorflow")
        
        model = keras.Sequential([
            layers.Bidirectional(layers.LSTM(128, return_sequences=True), input_shape=input_shape),
            layers.Dropout(0.2),
            layers.Bidirectional(layers.LSTM(64)),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(3, activation='softmax')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def build_attention_model(self, input_shape: Tuple[int, int]):
        """
        Build LSTM with attention mechanism
        
        Args:
            input_shape: (sequence_length, n_features)
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is not available. Install with: pip install tensorflow")
        
        inputs = keras.Input(shape=input_shape)
        
        # LSTM layers
        lstm_out = layers.LSTM(128, return_sequences=True)(inputs)
        lstm_out = layers.Dropout(0.2)(lstm_out)
        
        # Attention mechanism
        attention = layers.Dense(1, activation='tanh')(lstm_out)
        attention = layers.Softmax(axis=1)(attention)
        attention = layers.Permute([2, 1])(attention)
        
        # Apply attention
        weighted = layers.multiply([lstm_out, attention])
        weighted = layers.Lambda(lambda x: tf.reduce_sum(x, axis=1))(weighted)
        
        # Output layers
        dense = layers.Dense(32, activation='relu')(weighted)
        dense = layers.Dropout(0.2)(dense)
        outputs = layers.Dense(3, activation='softmax')(dense)
        
        model = keras.Model(inputs=inputs, outputs=outputs)
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, symbol: str, period: str = '2y', model_type: str = 'lstr',
              epochs: int = 50, batch_size: int = 32) -> Dict:
        """
        Train deep learning model
        
        Args:
            symbol: Stock ticker
            period: Historical period
            model_type: 'lstm', 'gru', 'bidirectional', 'attention'
            epochs: Number of training epochs
            batch_size: Batch size
        """
        if not TENSORFLOW_AVAILABLE:
            return {'error': 'TensorFlow not available'}
        
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if len(hist) < self.sequence_length + 100:
                return {'error': 'Insufficient data for training'}
            
            # Prepare sequences
            X, y = self.prepare_sequences(hist)
            
            if X is None or y is None:
                return {'error': 'Failed to prepare sequences'}
            
            # Normalize features
            from sklearn.preprocessing import StandardScaler
            self.scaler = StandardScaler()
            
            # Reshape for scaling
            n_samples, seq_len, n_features = X.shape
            X_reshaped = X.reshape(-1, n_features)
            X_scaled = self.scaler.fit_transform(X_reshaped)
            X = X_scaled.reshape(n_samples, seq_len, n_features)
            
            # Build model
            input_shape = (self.sequence_length, n_features)
            
            if model_type == 'lstm':
                self.model = self.build_lstm_model(input_shape)
            elif model_type == 'gru':
                self.model = self.build_gru_model(input_shape)
            elif model_type == 'bidirectional':
                self.model = self.build_bidirectional_lstm(input_shape)
            elif model_type == 'attention':
                self.model = self.build_attention_model(input_shape)
            else:
                self.model = self.build_lstm_model(input_shape)
            
            self.model_type = model_type
            
            # Train model
            history = self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=0.2,
                verbose=0
            )
            
            self.is_trained = True
            
            return {
                'status': 'success',
                'samples': len(X),
                'final_accuracy': round(history.history['accuracy'][-1], 4),
                'final_loss': round(history.history['loss'][-1], 4),
                'model_type': model_type
            }
        except Exception as e:
            return {'error': str(e)}
    
    def predict(self, symbol: str) -> DLPrediction:
        """
        Predict using deep learning model
        
        Args:
            symbol: Stock ticker
        """
        if not TENSORFLOW_AVAILABLE or not self.is_trained:
            return DLPrediction(
                direction='neutral',
                probability=0.5,
                confidence=0.0,
                model_type='none',
                sequence_length=self.sequence_length
            )
        
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if len(hist) < self.sequence_length + 50:
                return DLPrediction(
                    direction='neutral',
                    probability=0.5,
                    confidence=0.0,
                    model_type=self.model_type,
                    sequence_length=self.sequence_length
                )
            
            # Prepare features
            features_list = []
            for i in range(50, len(hist)):
                window = hist.iloc[:i+1]
                features = self._prepare_features(window)
                if features is not None:
                    features_list.append(features)
            
            if len(features_list) < self.sequence_length:
                return DLPrediction(
                    direction='neutral',
                    probability=0.5,
                    confidence=0.0,
                    model_type=self.model_type,
                    sequence_length=self.sequence_length
                )
            
            # Get last sequence
            features_array = np.array(features_list[-self.sequence_length:])
            
            # Scale
            n_samples, n_features = features_array.shape
            features_reshaped = features_array.reshape(-1, n_features)
            features_scaled = self.scaler.transform(features_reshaped)
            X = features_scaled.reshape(1, self.sequence_length, n_features)
            
            # Predict
            prediction_proba = self.model.predict(X, verbose=0)[0]
            
            # Get prediction
            prediction = np.argmax(prediction_proba)
            probability = prediction_proba[prediction]
            
            if prediction == 1:
                direction = 'bullish'
            elif prediction == 0:
                direction = 'bearish'
            else:
                direction = 'neutral'
            
            confidence = max(prediction_proba)
            
            return DLPrediction(
                direction=direction,
                probability=round(probability, 3),
                confidence=round(confidence, 3),
                model_type=self.model_type,
                sequence_length=self.sequence_length
            )
        except Exception as e:
            print(f"Error in prediction: {e}")
            return DLPrediction(
                direction='neutral',
                probability=0.5,
                confidence=0.0,
                model_type=self.model_type,
                sequence_length=self.sequence_length
            )
    
    def save_model(self, path: str):
        """Save model to disk"""
        if self.model is not None:
            self.model.save(path)
            print(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load model from disk"""
        if TENSORFLOW_AVAILABLE:
            self.model = keras.models.load_model(path)
            self.is_trained = True
            print(f"Model loaded from {path}")
