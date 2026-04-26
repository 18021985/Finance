import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import yfinance as yf

from ensemble_predictor import EnsemblePredictor
from performance_tracker import PerformanceTracker

@dataclass
class ValidationResult:
    """Result of validation"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    sharpe_ratio: float
    max_drawdown: float
    window_start: datetime
    window_end: datetime
    window_size: int
    degradation_detected: bool
    recommendation: str

class ContinuousValidator:
    """
    Continuous validation pipeline for ML models
    
    Features:
    - Walk-forward validation
    - Rolling window validation
    - Performance degradation detection
    - Automatic retraining triggers
    """
    
    def __init__(self, predictor: EnsemblePredictor, tracker: PerformanceTracker):
        self.predictor = predictor
        self.tracker = tracker
        self.validation_history: List[ValidationResult] = []
        self.baseline_metrics: Optional[Dict] = None
        self.degradation_threshold = 0.05  # 5% degradation
        self.retrain_threshold = 0.10  # 10% degradation triggers retrain
    
    def set_baseline(self, symbol: str, period: str = '2y'):
        """
        Set baseline metrics from historical data
        
        Args:
            symbol: Stock ticker
            period: Historical period
        """
        # Train model on full dataset
        train_result = self.predictor.train(symbol, period)
        
        if 'error' in train_result:
            print(f"Error setting baseline: {train_result['error']}")
            return
        
        # Calculate baseline metrics
        metrics = self.tracker.calculate_metrics()
        
        self.baseline_metrics = {
            'accuracy': metrics.accuracy,
            'precision': metrics.precision,
            'recall': metrics.recall,
            'f1_score': metrics.f1_score,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown
        }
        
        print(f"Baseline metrics set: {self.baseline_metrics}")
    
    def walk_forward_validation(self, symbol: str, period: str = '2y', 
                              train_window: int = 252, test_window: int = 20) -> List[ValidationResult]:
        """
        Walk-forward validation
        
        Args:
            symbol: Stock ticker
            period: Historical period
            train_window: Training window size (in days)
            test_window: Test window size (in days)
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if len(hist) < train_window + test_window + 50:
                print("Insufficient data for walk-forward validation")
                return []
            
            results = []
            total_windows = (len(hist) - train_window - 50) // test_window
            
            for i in range(total_windows):
                train_start = i * test_window
                train_end = train_start + train_window
                test_start = train_end
                test_end = test_start + test_window
                
                if test_end >= len(hist):
                    break
                
                # Train on training window
                train_data = hist.iloc[train_start:train_end]
                test_data = hist.iloc[test_start:test_end]
                
                # Prepare training data
                features_list = []
                labels_list = []
                
                for j in range(50, len(train_data) - 3):
                    window = train_data.iloc[:j+3]
                    features = self.predictor.prepare_features(window)
                    if features is not None:
                        features_list.append(features[0])
                        
                        current_price = train_data['Close'].iloc[j]
                        future_price = train_data['Close'].iloc[min(j+3, len(train_data)-1)]
                        
                        if future_price > current_price * 1.015:
                            labels_list.append(1)
                        elif future_price < current_price * 0.985:
                            labels_list.append(0)
                        else:
                            labels_list.append(2)
                
                if len(features_list) < 50:
                    continue
                
                X_train = np.array(features_list)
                y_train = np.array(labels_list)
                X_train_scaled = self.predictor.scaler.fit_transform(X_train)
                
                # Train model
                for name, model in self.predictor.models.items():
                    try:
                        model.fit(X_train_scaled, y_train)
                    except:
                        pass
                
                # Test on test window
                test_predictions = []
                test_actuals = []
                
                for j in range(50, len(test_data) - 3):
                    window = test_data.iloc[:j+3]
                    features = self.predictor.prepare_features(window)
                    if features is not None:
                        features_scaled = self.predictor.scaler.transform(features)
                        
                        # Get prediction
                        prediction = self.predictor.predict(symbol)
                        test_predictions.append(prediction.direction)
                        
                        # Get actual
                        current_price = test_data['Close'].iloc[j]
                        future_price = test_data['Close'].iloc[min(j+3, len(test_data)-1)]
                        
                        if future_price > current_price * 1.015:
                            actual = 'bullish'
                        elif future_price < current_price * 0.985:
                            actual = 'bearish'
                        else:
                            actual = 'neutral'
                        
                        test_actuals.append(actual)
                
                if len(test_predictions) < 5:
                    continue
                
                # Calculate metrics
                y_pred = [self._direction_to_int(p) for p in test_predictions]
                y_true = [self._direction_to_int(a) for a in test_actuals]
                
                accuracy = accuracy_score(y_true, y_pred)
                precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
                recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
                f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
                
                # Calculate returns
                returns = []
                for j in range(len(test_predictions)):
                    if test_predictions[j] == 'bullish':
                        returns.append(test_data['Close'].pct_change().iloc[j+50])
                    elif test_predictions[j] == 'bearish':
                        returns.append(-test_data['Close'].pct_change().iloc[j+50])
                
                sharpe = 0.0
                max_dd = 0.0
                if returns:
                    returns_array = np.array(returns)
                    sharpe = np.mean(returns_array) / np.std(returns_array) if np.std(returns_array) > 0 else 0
                    cumulative = np.cumprod(1 + returns_array)
                    running_max = np.maximum.accumulate(cumulative)
                    drawdown = (cumulative - running_max) / running_max
                    max_dd = np.min(drawdown)
                
                # Check degradation
                degradation = False
                if self.baseline_metrics:
                    if accuracy < self.baseline_metrics['accuracy'] - self.degradation_threshold:
                        degradation = True
                
                # Recommendation
                if degradation:
                    if accuracy < self.baseline_metrics['accuracy'] - self.retrain_threshold:
                        recommendation = "RETRAIN_MODEL"
                    else:
                        recommendation = "MONITOR"
                else:
                    recommendation = "CONTINUE"
                
                result = ValidationResult(
                    accuracy=round(accuracy, 4),
                    precision=round(precision, 4),
                    recall=round(recall, 4),
                    f1_score=round(f1, 4),
                    sharpe_ratio=round(sharpe, 4),
                    max_drawdown=round(max_dd, 4),
                    window_start=test_data.index[0],
                    window_end=test_data.index[-1],
                    window_size=test_window,
                    degradation_detected=degradation,
                    recommendation=recommendation
                )
                
                results.append(result)
                self.validation_history.append(result)
                
                print(f"Window {i+1}/{total_windows}: Accuracy={accuracy:.4f}, {recommendation}")
            
            return results
        except Exception as e:
            print(f"Error in walk-forward validation: {e}")
            return []
    
    def rolling_validation(self, symbol: str, period: str = '1y', 
                          window: int = 50, step: int = 10) -> List[ValidationResult]:
        """
        Rolling window validation
        
        Args:
            symbol: Stock ticker
            period: Historical period
            window: Window size
            step: Step size
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if len(hist) < window + 50:
                print("Insufficient data for rolling validation")
                return []
            
            results = []
            
            for i in range(50, len(hist) - window, step):
                window_data = hist.iloc[i:i+window]
                
                # Prepare features
                features_list = []
                labels_list = []
                
                for j in range(50, len(window_data) - 3):
                    window_slice = window_data.iloc[:j+3]
                    features = self.predictor.prepare_features(window_slice)
                    if features is not None:
                        features_list.append(features[0])
                        
                        current_price = window_data['Close'].iloc[j]
                        future_price = window_data['Close'].iloc[min(j+3, len(window_data)-1)]
                        
                        if future_price > current_price * 1.015:
                            labels_list.append(1)
                        elif future_price < current_price * 0.985:
                            labels_list.append(0)
                        else:
                            labels_list.append(2)
                
                if len(features_list) < 10:
                    continue
                
                X = np.array(features_list)
                y = np.array(labels_list)
                X_scaled = self.predictor.scaler.fit_transform(X)
                
                # Quick train
                for name, model in self.predictor.models.items():
                    try:
                        model.fit(X_scaled, y)
                    except:
                        pass
                
                # Predict on last sample
                if len(features_list) > 0:
                    last_features = features_list[-1].reshape(1, -1)
                    last_features_scaled = self.predictor.scaler.transform(last_features)
                    
                    prediction = self.predictor.predict(symbol)
                    
                    # Calculate metrics on this window
                    y_pred = [self._direction_to_int(prediction.direction)]
                    y_true = [labels_list[-1]]
                    
                    accuracy = accuracy_score(y_true, y_pred)
                    
                    degradation = False
                    if self.baseline_metrics:
                        if accuracy < self.baseline_metrics['accuracy'] - self.degradation_threshold:
                            degradation = True
                    
                    result = ValidationResult(
                        accuracy=round(accuracy, 4),
                        precision=0.0,
                        recall=0.0,
                        f1_score=0.0,
                        sharpe_ratio=0.0,
                        max_drawdown=0.0,
                        window_start=window_data.index[0],
                        window_end=window_data.index[-1],
                        window_size=window,
                        degradation_detected=degradation,
                        recommendation="RETRAIN" if degradation else "CONTINUE"
                    )
                    
                    results.append(result)
            
            return results
        except Exception as e:
            print(f"Error in rolling validation: {e}")
            return []
    
    def check_retrain_needed(self) -> bool:
        """
        Check if retraining is needed based on recent validation results
        """
        if len(self.validation_history) < 2:
            return False
        
        recent = self.validation_history[-5:]  # Last 5 validations
        
        # Check if recent accuracy is below threshold
        if self.baseline_metrics:
            for result in recent:
                if result.accuracy < self.baseline_metrics['accuracy'] - self.retrain_threshold:
                    return True
        
        return False
    
    def get_validation_summary(self) -> Dict:
        """Get summary of validation results"""
        if not self.validation_history:
            return {'error': 'No validation results'}
        
        recent = self.validation_history[-10:]
        
        avg_accuracy = np.mean([r.accuracy for r in recent])
        avg_sharpe = np.mean([r.sharpe_ratio for r in recent])
        degradation_count = sum(1 for r in recent if r.degradation_detected)
        
        return {
            'total_validations': len(self.validation_history),
            'recent_average_accuracy': round(avg_accuracy, 4),
            'recent_average_sharpe': round(avg_sharpe, 4),
            'degradation_count': degradation_count,
            'retrain_needed': self.check_retrain_needed(),
            'baseline_metrics': self.baseline_metrics
        }
    
    def _direction_to_int(self, direction: str) -> int:
        """Convert direction to integer"""
        mapping = {'bullish': 1, 'bearish': 0, 'neutral': 2}
        return mapping.get(direction, 2)
