import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import json
import os
import uuid

@dataclass
class PredictionRecord:
    """Single prediction record"""
    id: str
    symbol: str
    timestamp: datetime
    predicted_direction: str  # 'bullish', 'bearish', 'neutral'
    predicted_probability: float
    actual_direction: Optional[str] = None
    actual_return: Optional[float] = None
    confidence: float = 0.0
    model_used: str = ""
    features: Dict = field(default_factory=dict)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a period"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_predictions: int
    period_start: datetime
    period_end: datetime

class PerformanceTracker:
    """
    Track and analyze prediction performance
    
    Features:
    - Log predictions and actual outcomes
    - Calculate performance metrics
    - Track model performance over time
    - Detect performance degradation
    - Generate performance reports
    """
    
    def __init__(self, storage_path: str = "performance_data"):
        self.storage_path = storage_path
        self.predictions: List[PredictionRecord] = []
        self.metrics_history: List[PerformanceMetrics] = []
        
        # Create storage directory
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing data
        self._load_data()
    
    def log_prediction(self, symbol: str, predicted_direction: str, 
                      predicted_probability: float, confidence: float,
                      model_used: str = "", features: Dict = None) -> PredictionRecord:
        """
        Log a prediction
        
        Args:
            symbol: Asset symbol
            predicted_direction: Predicted direction
            predicted_probability: Predicted probability
            confidence: Confidence level
            model_used: Model name
            features: Feature values
        """
        record = PredictionRecord(
            id=str(uuid.uuid4()),
            symbol=symbol,
            timestamp=datetime.now(),
            predicted_direction=predicted_direction,
            predicted_probability=predicted_probability,
            confidence=confidence,
            model_used=model_used,
            features=features or {}
        )
        
        self.predictions.append(record)
        self._save_data()
        
        return record

    def update_outcome_by_id(self, prediction_id: str, actual_direction: str, actual_return: float) -> bool:
        """Update prediction with actual outcome by id."""
        pid = str(prediction_id or "")
        for p in self.predictions:
            if getattr(p, "id", "") == pid:
                p.actual_direction = actual_direction
                p.actual_return = actual_return
                self._save_data()
                return True
        return False
    
    def update_outcome(self, record_index: int, actual_direction: str, actual_return: float):
        """
        Update prediction with actual outcome
        
        Args:
            record_index: Index of prediction record
            actual_direction: Actual direction
            actual_return: Actual return
        """
        if 0 <= record_index < len(self.predictions):
            self.predictions[record_index].actual_direction = actual_direction
            self.predictions[record_index].actual_return = actual_return
            self._save_data()
    
    def calculate_metrics(self, window_size: Optional[int] = None) -> PerformanceMetrics:
        """
        Calculate performance metrics
        
        Args:
            window_size: Number of recent predictions to analyze (None = all)
        """
        # Filter predictions with actual outcomes
        completed = [p for p in self.predictions if p.actual_direction is not None]
        
        if window_size:
            completed = completed[-window_size:]
        
        if len(completed) < 2:
            return PerformanceMetrics(
                accuracy=0.0, precision=0.0, recall=0.0, f1_score=0.0,
                sharpe_ratio=0.0, max_drawdown=0.0, win_rate=0.0,
                total_predictions=len(completed),
                period_start=(completed[0].timestamp if completed else datetime.now()),
                period_end=(completed[-1].timestamp if completed else datetime.now()),
            )
        
        # Prepare data
        y_pred = [self._direction_to_int(p.predicted_direction) for p in completed]
        y_true = [self._direction_to_int(p.actual_direction) for p in completed]
        returns = [p.actual_return for p in completed if p.actual_return is not None]
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Calculate Sharpe ratio
        sharpe = 0.0
        if returns:
            returns_array = np.array(returns)
            sharpe = np.mean(returns_array) / np.std(returns_array) if np.std(returns_array) > 0 else 0
        
        # Calculate max drawdown
        max_dd = 0.0
        if returns:
            cumulative = np.cumprod(1 + np.array(returns))
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            max_dd = np.min(drawdown)
        
        # Calculate win rate
        win_rate = sum(1 for p in completed if p.actual_direction == p.predicted_direction) / len(completed)
        
        period_start = completed[0].timestamp
        period_end = completed[-1].timestamp
        
        metrics = PerformanceMetrics(
            accuracy=round(accuracy, 4),
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1, 4),
            sharpe_ratio=round(sharpe, 4),
            max_drawdown=round(max_dd, 4),
            win_rate=round(win_rate, 4),
            total_predictions=len(completed),
            period_start=period_start,
            period_end=period_end
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def _direction_to_int(self, direction: str) -> int:
        """Convert direction to integer"""
        mapping = {'bullish': 1, 'bearish': 0, 'neutral': 2}
        return mapping.get(direction, 2)
    
    def get_confusion_matrix(self, window_size: Optional[int] = None) -> np.ndarray:
        """Get confusion matrix"""
        completed = [p for p in self.predictions if p.actual_direction is not None]
        
        if window_size:
            completed = completed[-window_size:]
        
        if len(completed) < 2:
            return np.zeros((3, 3))
        
        y_pred = [self._direction_to_int(p.predicted_direction) for p in completed]
        y_true = [self._direction_to_int(p.actual_direction) for p in completed]
        
        return confusion_matrix(y_true, y_pred)
    
    def detect_performance_degradation(self, threshold: float = 0.05) -> bool:
        """
        Detect if performance has degraded
        
        Args:
            threshold: Performance degradation threshold (5%)
        """
        if len(self.metrics_history) < 2:
            return False
        
        recent = self.metrics_history[-1]
        baseline = self.metrics_history[0]
        
        # Check if accuracy dropped by threshold
        if recent.accuracy < baseline.accuracy - threshold:
            return True
        
        # Check if Sharpe ratio dropped significantly
        if recent.sharpe_ratio < baseline.sharpe_ratio - 0.5:
            return True
        
        return False
    
    def get_performance_by_symbol(self, symbol: str) -> Dict:
        """Get performance metrics for a specific symbol"""
        symbol_predictions = [p for p in self.predictions if p.symbol == symbol and p.actual_direction is not None]
        
        if len(symbol_predictions) < 2:
            return {'error': 'Insufficient data for symbol'}
        
        y_pred = [self._direction_to_int(p.predicted_direction) for p in symbol_predictions]
        y_true = [self._direction_to_int(p.actual_direction) for p in symbol_predictions]
        
        return {
            'symbol': symbol,
            'total_predictions': len(symbol_predictions),
            'accuracy': round(accuracy_score(y_true, y_pred), 4),
            'win_rate': round(sum(1 for p in symbol_predictions if p.actual_direction == p.predicted_direction) / len(symbol_predictions), 4)
        }
    
    def get_performance_by_model(self, model: str) -> Dict:
        """Get performance metrics for a specific model"""
        model_predictions = [p for p in self.predictions if p.model_used == model and p.actual_direction is not None]
        
        if len(model_predictions) < 2:
            return {'error': 'Insufficient data for model'}
        
        y_pred = [self._direction_to_int(p.predicted_direction) for p in model_predictions]
        y_true = [self._direction_to_int(p.actual_direction) for p in model_predictions]
        
        return {
            'model': model,
            'total_predictions': len(model_predictions),
            'accuracy': round(accuracy_score(y_true, y_pred), 4),
            'win_rate': round(sum(1 for p in model_predictions if p.actual_direction == p.predicted_direction) / len(model_predictions), 4)
        }
    
    def get_rolling_metrics(self, window: int = 50) -> List[Dict]:
        """
        Get rolling performance metrics
        
        Args:
            window: Rolling window size
        """
        completed = [p for p in self.predictions if p.actual_direction is not None]
        
        if len(completed) < window:
            return []
        
        rolling_metrics = []
        for i in range(window, len(completed) + 1):
            window_data = completed[i-window:i]
            
            y_pred = [self._direction_to_int(p.predicted_direction) for p in window_data]
            y_true = [self._direction_to_int(p.actual_direction) for p in window_data]
            
            accuracy = accuracy_score(y_true, y_pred)
            win_rate = sum(1 for p in window_data if p.actual_direction == p.predicted_direction) / len(window_data)
            
            rolling_metrics.append({
                'timestamp': window_data[-1].timestamp,
                'accuracy': round(accuracy, 4),
                'win_rate': round(win_rate, 4)
            })
        
        return rolling_metrics
    
    def generate_report(self) -> Dict:
        """Generate comprehensive performance report"""
        overall_metrics = self.calculate_metrics()
        
        # Performance by symbol
        symbols = set(p.symbol for p in self.predictions)
        symbol_performance = {}
        for symbol in symbols:
            symbol_perf = self.get_performance_by_symbol(symbol)
            if 'error' not in symbol_perf:
                symbol_performance[symbol] = symbol_perf
        
        # Performance by model
        models = set(p.model_used for p in self.predictions if p.model_used)
        model_performance = {}
        for model in models:
            model_perf = self.get_performance_by_model(model)
            if 'error' not in model_perf:
                model_performance[model] = model_perf
        
        # Rolling metrics
        rolling = self.get_rolling_metrics(window=50)
        
        return {
            'overall_metrics': {
                'accuracy': overall_metrics.accuracy,
                'precision': overall_metrics.precision,
                'recall': overall_metrics.recall,
                'f1_score': overall_metrics.f1_score,
                'sharpe_ratio': overall_metrics.sharpe_ratio,
                'max_drawdown': overall_metrics.max_drawdown,
                'win_rate': overall_metrics.win_rate,
                'total_predictions': overall_metrics.total_predictions
            },
            'symbol_performance': symbol_performance,
            'model_performance': model_performance,
            'rolling_metrics': rolling[-10:] if rolling else [],
            'degradation_detected': self.detect_performance_degradation()
        }
    
    def _save_data(self):
        """Save data to disk"""
        # Save predictions
        predictions_data = [
            {
                'id': getattr(p, 'id', ''),
                'symbol': p.symbol,
                'timestamp': p.timestamp.isoformat(),
                'predicted_direction': p.predicted_direction,
                'predicted_probability': p.predicted_probability,
                'actual_direction': p.actual_direction,
                'actual_return': p.actual_return,
                'confidence': p.confidence,
                'model_used': p.model_used,
                'features': p.features
            }
            for p in self.predictions
        ]
        
        with open(os.path.join(self.storage_path, 'predictions.json'), 'w') as f:
            json.dump(predictions_data, f, indent=2)
        
        # Save metrics
        metrics_data = [
            {
                'accuracy': m.accuracy,
                'precision': m.precision,
                'recall': m.recall,
                'f1_score': m.f1_score,
                'sharpe_ratio': m.sharpe_ratio,
                'max_drawdown': m.max_drawdown,
                'win_rate': m.win_rate,
                'total_predictions': m.total_predictions,
                'period_start': m.period_start.isoformat(),
                'period_end': m.period_end.isoformat()
            }
            for m in self.metrics_history
        ]
        
        with open(os.path.join(self.storage_path, 'metrics.json'), 'w') as f:
            json.dump(metrics_data, f, indent=2)
    
    def _load_data(self):
        """Load data from disk"""
        # Load predictions
        predictions_file = os.path.join(self.storage_path, 'predictions.json')
        if os.path.exists(predictions_file):
            with open(predictions_file, 'r') as f:
                predictions_data = json.load(f)
            
            self.predictions = [
                PredictionRecord(
                    id=p.get('id') or str(uuid.uuid4()),
                    symbol=p['symbol'],
                    timestamp=datetime.fromisoformat(p['timestamp']),
                    predicted_direction=p['predicted_direction'],
                    predicted_probability=p['predicted_probability'],
                    actual_direction=p.get('actual_direction'),
                    actual_return=p.get('actual_return'),
                    confidence=p.get('confidence', 0.0),
                    model_used=p.get('model_used', ''),
                    features=p.get('features', {})
                )
                for p in predictions_data
            ]
        
        # Load metrics
        metrics_file = os.path.join(self.storage_path, 'metrics.json')
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r') as f:
                metrics_data = json.load(f)
            
            self.metrics_history = [
                PerformanceMetrics(
                    accuracy=m['accuracy'],
                    precision=m['precision'],
                    recall=m['recall'],
                    f1_score=m['f1_score'],
                    sharpe_ratio=m['sharpe_ratio'],
                    max_drawdown=m['max_drawdown'],
                    win_rate=m['win_rate'],
                    total_predictions=m['total_predictions'],
                    period_start=datetime.fromisoformat(m['period_start']),
                    period_end=datetime.fromisoformat(m['period_end'])
                )
                for m in metrics_data
            ]
    
    def clear_old_data(self, days: int = 30):
        """Clear data older than specified days"""
        cutoff = datetime.now() - pd.Timedelta(days=days)
        self.predictions = [p for p in self.predictions if p.timestamp > cutoff]
        self._save_data()
