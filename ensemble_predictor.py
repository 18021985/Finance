import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    VotingClassifier,
    StackingClassifier
)
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import yfinance as yf

# Try to import advanced libraries
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("XGBoost not available. Install with: pip install xgboost")

try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("LightGBM not available. Install with: pip install lightgbm")

try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    print("CatBoost not available. Install with: pip install catboost")

@dataclass
class EnsemblePrediction:
    """Ensemble prediction result"""
    direction: str  # 'bullish', 'bearish', 'neutral'
    probability: float  # 0-1
    confidence: float  # 0-1
    model_predictions: Dict[str, float]
    ensemble_method: str
    feature_importance: Dict[str, float]

class EnsemblePredictor:
    """
    Ensemble predictor using multiple ML models
    
    Models:
    - XGBoost (if available)
    - LightGBM (if available)
    - CatBoost (if available)
    - Gradient Boosting
    - Random Forest
    """
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'rsi', 'macd', 'momentum_20d', 'volume_change',
            'price_vs_sma50', 'price_vs_sma200', 'volatility',
            'high_low_range', 'gap', 'trend_strength',
            'atr', 'obv', 'cci', 'williams_r', 'stoch_k'
        ]
        
        # Initialize available models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all available models"""
        # XGBoost
        if XGBOOST_AVAILABLE:
            self.models['xgboost'] = XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            )
        
        # LightGBM
        if LIGHTGBM_AVAILABLE:
            self.models['lightgbm'] = LGBMClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                verbose=-1
            )
        
        # CatBoost
        if CATBOOST_AVAILABLE:
            self.models['catboost'] = CatBoostClassifier(
                iterations=100,
                depth=6,
                learning_rate=0.1,
                random_state=42,
                verbose=False
            )
        
        # Gradient Boosting (always available)
        self.models['gradient_boosting'] = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        # Random Forest (always available)
        self.models['random_forest'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            random_state=42
        )
        
        print(f"Initialized {len(self.models)} models: {list(self.models.keys())}")
    
    def prepare_features(self, hist: pd.DataFrame) -> np.ndarray:
        """
        Prepare enhanced technical features for ML model
        
        Args:
            hist: Historical price data
        """
        if len(hist) < 50:
            return None
        
        features = []
        
        # Existing features
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        features.append(rsi.iloc[-1])
        
        ema_12 = hist['Close'].ewm(span=12).mean()
        ema_26 = hist['Close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        features.append(macd.iloc[-1])
        
        momentum_20d = (hist['Close'].iloc[-1] / hist['Close'].iloc[-21] - 1) * 100
        features.append(momentum_20d)
        
        if 'Volume' in hist.columns:
            volume_change = (hist['Volume'].iloc[-1] / hist['Volume'].iloc[-5:].mean() - 1) * 100
        else:
            volume_change = 0
        features.append(volume_change)
        
        sma_50 = hist['Close'].rolling(50).mean()
        price_vs_sma50 = (hist['Close'].iloc[-1] / sma_50.iloc[-1] - 1) * 100
        features.append(price_vs_sma50)
        
        sma_200 = hist['Close'].rolling(200).mean()
        price_vs_sma200 = (hist['Close'].iloc[-1] / sma_200.iloc[-1] - 1) * 100
        features.append(price_vs_sma200)
        
        returns = hist['Close'].pct_change()
        volatility = returns.rolling(20).std().iloc[-1] * np.sqrt(252)
        features.append(volatility)
        
        high_low_range = (hist['High'].iloc[-1] / hist['Low'].iloc[-1] - 1) * 100
        features.append(high_low_range)
        
        gap = (hist['Open'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100
        features.append(gap)
        
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
        
        # New features
        # ATR (Average True Range)
        high_low = hist['High'] - hist['Low']
        high_close = abs(hist['High'] - hist['Close'].shift())
        low_close = abs(hist['Low'] - hist['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(14).mean().iloc[-1]
        features.append(atr)
        
        # OBV (On-Balance Volume)
        if 'Volume' in hist.columns:
            obv = (np.sign(hist['Close'].diff()) * hist['Volume']).cumsum()
            obv_change = (obv.iloc[-1] / obv.iloc[-20:].mean() - 1) * 100 if len(obv) > 20 else 0
        else:
            obv_change = 0
        features.append(obv_change)
        
        # CCI (Commodity Channel Index)
        tp = (hist['High'] + hist['Low'] + hist['Close']) / 3
        sma_tp = tp.rolling(20).mean()
        mad = tp.rolling(20).apply(lambda x: np.mean(np.abs(x - x.mean())))
        cci = (tp - sma_tp) / (0.015 * mad)
        features.append(cci.iloc[-1])
        
        # Williams %R
        high_14 = hist['High'].rolling(14).max()
        low_14 = hist['Low'].rolling(14).min()
        williams_r = -100 * (high_14 - hist['Close']) / (high_14 - low_14)
        features.append(williams_r.iloc[-1])
        
        # Stochastic %K
        low_14 = hist['Low'].rolling(14).min()
        high_14 = hist['High'].rolling(14).max()
        stoch_k = 100 * (hist['Close'] - low_14) / (high_14 - low_14)
        features.append(stoch_k.iloc[-1])
        
        return np.array(features).reshape(1, -1)
    
    def generate_labels(self, hist: pd.DataFrame, forward_days: int = 3) -> np.ndarray:
        """
        Generate labels for training (future price direction)
        
        Uses 3-day forward return for better signal
        """
        if len(hist) < forward_days + 50:
            return None
        
        labels = []
        for i in range(50, len(hist) - forward_days):
            current_price = hist['Close'].iloc[i]
            future_price = hist['Close'].iloc[i + forward_days]
            
            if future_price > current_price * 1.015:  # 1.5% up
                labels.append(1)  # bullish
            elif future_price < current_price * 0.985:  # 1.5% down
                labels.append(0)  # bearish
            else:
                labels.append(2)  # neutral
        
        return np.array(labels)
    
    def train(self, symbol: str, period: str = '2y') -> Dict:
        """
        Train all ensemble models on historical data
        
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
            
            for i in range(50, len(hist) - 3):
                window = hist.iloc[:i+3]
                features = self.prepare_features(window)
                if features is not None:
                    features_list.append(features[0])
                    
                    # Generate label
                    current_price = hist['Close'].iloc[i]
                    future_price = hist['Close'].iloc[min(i+3, len(hist)-1)]
                    
                    if future_price > current_price * 1.015:
                        labels_list.append(1)
                    elif future_price < current_price * 0.985:
                        labels_list.append(0)
                    else:
                        labels_list.append(2)
            
            if len(features_list) < 50:
                return {'error': 'Insufficient training samples'}
            
            X = np.array(features_list)
            y = np.array(labels_list)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train each model
            model_scores = {}
            for name, model in self.models.items():
                try:
                    model.fit(X_scaled, y)
                    score = model.score(X_scaled, y)
                    model_scores[name] = score
                    print(f"{name}: {score:.4f}")
                except Exception as e:
                    print(f"Error training {name}: {e}")
            
            self.is_trained = True
            
            return {
                'status': 'success',
                'samples': len(features_list),
                'model_scores': model_scores,
                'average_score': np.mean(list(model_scores.values()))
            }
        except Exception as e:
            return {'error': str(e)}
    
    def predict(self, symbol: str, method: str = 'voting') -> EnsemblePrediction:
        """
        Generate ensemble prediction for a symbol
        
        Args:
            symbol: Stock ticker
            method: 'voting', 'stacking', 'weighted'
        """
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return EnsemblePrediction(
                    direction='neutral',
                    probability=0.5,
                    confidence=0.0,
                    model_predictions={},
                    ensemble_method=method,
                    feature_importance={}
                )
            
            # Prepare features
            features = self.prepare_features(hist)
            if features is None:
                return EnsemblePrediction(
                    direction='neutral',
                    probability=0.5,
                    confidence=0.0,
                    model_predictions={},
                    ensemble_method=method,
                    feature_importance={}
                )
            
            if not self.is_trained:
                # Use heuristic
                direction, probability, confidence = self._heuristic_prediction(features[0])
                return EnsemblePrediction(
                    direction=direction,
                    probability=probability,
                    confidence=confidence,
                    model_predictions={'heuristic': probability},
                    ensemble_method='heuristic',
                    feature_importance={}
                )
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get predictions from all models
            model_predictions = {}
            for name, model in self.models.items():
                try:
                    proba = model.predict_proba(features_scaled)[0]
                    model_predictions[name] = proba
                except Exception as e:
                    print(f"Error predicting with {name}: {e}")
            
            if not model_predictions:
                return EnsemblePrediction(
                    direction='neutral',
                    probability=0.5,
                    confidence=0.0,
                    model_predictions={},
                    ensemble_method=method,
                    feature_importance={}
                )
            
            # Combine predictions based on method
            if method == 'voting':
                direction, probability, confidence = self._voting_prediction(model_predictions)
            elif method == 'weighted':
                direction, probability, confidence = self._weighted_prediction(model_predictions)
            elif method == 'stacking':
                direction, probability, confidence = self._stacking_prediction(model_predictions, features_scaled)
            else:
                direction, probability, confidence = self._voting_prediction(model_predictions)
            
            # Get feature importance from random forest
            feature_importance = {}
            if 'random_forest' in self.models:
                importance = self.models['random_forest'].feature_importances_
                feature_importance = dict(zip(self.feature_names, importance))
            
            return EnsemblePrediction(
                direction=direction,
                probability=round(probability, 3),
                confidence=round(confidence, 3),
                model_predictions={k: v.tolist() for k, v in model_predictions.items()},
                ensemble_method=method,
                feature_importance=feature_importance
            )
        except Exception as e:
            return EnsemblePrediction(
                direction='neutral',
                probability=0.5,
                confidence=0.0,
                model_predictions={},
                ensemble_method=method,
                feature_importance={}
            )
    
    def _voting_prediction(self, model_predictions: Dict[str, np.ndarray]) -> Tuple[str, float, float]:
        """Soft voting prediction"""
        # Average probabilities
        avg_proba = np.mean(list(model_predictions.values()), axis=0)
        
        # Get prediction
        prediction = np.argmax(avg_proba)
        
        if prediction == 1:
            direction = 'bullish'
            probability = avg_proba[1]
        elif prediction == 0:
            direction = 'bearish'
            probability = avg_proba[0]
        else:
            direction = 'neutral'
            probability = avg_proba[2] if len(avg_proba) > 2 else 0.5
        
        confidence = max(avg_proba)
        return direction, probability, confidence
    
    def _weighted_prediction(self, model_predictions: Dict[str, np.ndarray]) -> Tuple[str, float, float]:
        """Weighted prediction based on model performance"""
        # In production, use actual model performance scores
        weights = {
            'xgboost': 1.2,
            'lightgbm': 1.2,
            'catboost': 1.1,
            'gradient_boosting': 1.0,
            'random_forest': 0.9
        }
        
        weighted_proba = np.zeros(3)
        total_weight = 0
        
        for name, proba in model_predictions.items():
            weight = weights.get(name, 1.0)
            weighted_proba += proba * weight
            total_weight += weight
        
        weighted_proba /= total_weight
        
        prediction = np.argmax(weighted_proba)
        
        if prediction == 1:
            direction = 'bullish'
            probability = weighted_proba[1]
        elif prediction == 0:
            direction = 'bearish'
            probability = weighted_proba[0]
        else:
            direction = 'neutral'
            probability = weighted_proba[2] if len(weighted_proba) > 2 else 0.5
        
        confidence = max(weighted_proba)
        return direction, probability, confidence
    
    def _stacking_prediction(self, model_predictions: Dict[str, np.ndarray], 
                           features: np.ndarray) -> Tuple[str, float, float]:
        """Stacking prediction (simplified)"""
        # Use voting for now (full stacking requires meta-learner)
        return self._voting_prediction(model_predictions)
    
    def _heuristic_prediction(self, features: np.ndarray) -> Tuple[str, float, float]:
        """Heuristic prediction when model not trained"""
        rsi, macd, momentum, volume_change, price_vs_sma50, price_vs_sma200, volatility, high_low_range, gap, trend_strength, atr, obv, cci, williams_r, stoch_k = features
        
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
        if momentum > 2:
            bullish_score += 2
        elif momentum > 0.5:
            bullish_score += 1
        elif momentum < -2:
            bearish_score += 2
        elif momentum < -0.5:
            bearish_score += 1
        
        # Price vs SMAs
        if price_vs_sma50 > 1:
            bullish_score += 2
        elif price_vs_sma50 < -1:
            bearish_score += 2
        
        if price_vs_sma200 > 3:
            bullish_score += 2
        elif price_vs_sma200 < -3:
            bearish_score += 2
        
        # Trend strength
        if trend_strength > 25:
            bullish_score += 1
        
        # Stochastic
        if stoch_k < 20:
            bullish_score += 1
        elif stoch_k > 80:
            bearish_score += 1
        
        # CCI
        if cci < -100:
            bullish_score += 1
        elif cci > 100:
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
        
        confidence = min(abs(bullish_score - bearish_score) / 10, 1.0)
        
        return direction, probability, confidence
    
    def cross_validate(self, symbol: str, period: str = '2y', cv: int = 5) -> Dict:
        """
        Cross-validate ensemble models
        
        Args:
            symbol: Stock ticker
            period: Historical period
            cv: Number of cross-validation folds
        """
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if len(hist) < 100:
                return {'error': 'Insufficient data for cross-validation'}
            
            # Prepare features and labels
            features_list = []
            labels_list = []
            
            for i in range(50, len(hist) - 3):
                window = hist.iloc[:i+3]
                features = self.prepare_features(window)
                if features is not None:
                    features_list.append(features[0])
                    
                    current_price = hist['Close'].iloc[i]
                    future_price = hist['Close'].iloc[min(i+3, len(hist)-1)]
                    
                    if future_price > current_price * 1.015:
                        labels_list.append(1)
                    elif future_price < current_price * 0.985:
                        labels_list.append(0)
                    else:
                        labels_list.append(2)
            
            if len(features_list) < 50:
                return {'error': 'Insufficient samples for cross-validation'}
            
            X = np.array(features_list)
            y = np.array(labels_list)
            X_scaled = self.scaler.fit_transform(X)
            
            # Cross-validate each model
            cv_scores = {}
            for name, model in self.models.items():
                try:
                    scores = cross_val_score(model, X_scaled, y, cv=cv)
                    cv_scores[name] = {
                        'mean': scores.mean(),
                        'std': scores.std(),
                        'scores': scores.tolist()
                    }
                except Exception as e:
                    print(f"Error cross-validating {name}: {e}")
            
            return {
                'status': 'success',
                'cv_scores': cv_scores,
                'best_model': max(cv_scores.items(), key=lambda x: x[1]['mean'])[0] if cv_scores else None
            }
        except Exception as e:
            return {'error': str(e)}
