import os
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

# Try to import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Supabase not available. Install with: pip install supabase")

@dataclass
class PredictionRecord:
    """Prediction record for database"""
    symbol: str
    predicted_direction: str
    predicted_probability: float
    actual_direction: Optional[str] = None
    actual_return: Optional[float] = None
    confidence: float = 0.0
    model_used: str = ""
    features: Dict = None

class SupabaseClient:
    """
    Supabase client for data persistence
    
    Features:
    - Store predictions
    - Track performance metrics
    - Model versioning
    - Real-time subscriptions
    """
    
    def __init__(self, url: str = None, key: str = None):
        if not SUPABASE_AVAILABLE:
            raise ImportError("Supabase library not available")
        
        # Get credentials from environment or parameters
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and key required")
        
        # Initialize client
        self.client: Client = create_client(self.url, self.key)
        print("Supabase client initialized")
    
    def insert_prediction(self, record: PredictionRecord) -> Dict:
        """
        Insert a prediction record
        
        Args:
            record: PredictionRecord dataclass
        """
        try:
            data = {
                'symbol': record.symbol,
                'predicted_direction': record.predicted_direction,
                'predicted_probability': record.predicted_probability,
                'actual_direction': record.actual_direction,
                'actual_return': record.actual_return,
                'confidence': record.confidence,
                'model_used': record.model_used,
                'features': record.features or {}
            }
            
            result = self.client.table('predictions').insert(data).execute()
            
            return {
                'success': True,
                'id': result.data[0]['id'] if result.data else None
            }
        except Exception as e:
            print(f"Error inserting prediction: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_prediction_outcome(self, prediction_id: str, 
                                actual_direction: str, 
                                actual_return: float) -> Dict:
        """
        Update prediction with actual outcome
        
        Args:
            prediction_id: UUID of prediction
            actual_direction: Actual direction
            actual_return: Actual return
        """
        try:
            result = self.client.table('predictions').update({
                'actual_direction': actual_direction,
                'actual_return': actual_return,
                'updated_at': datetime.now().isoformat()
            }).eq('id', prediction_id).execute()
            
            return {'success': True}
        except Exception as e:
            print(f"Error updating prediction: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_recent_predictions(self, symbol: str = None, limit: int = 100) -> List[Dict]:
        """
        Get recent predictions
        
        Args:
            symbol: Filter by symbol (optional)
            limit: Number of records to return
        """
        try:
            query = self.client.table('predictions').select('*').order('timestamp', desc=True).limit(limit)
            
            if symbol:
                query = query.eq('symbol', symbol)
            
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Error getting predictions: {e}")
            return []
    
    def insert_performance_metrics(self, metrics: Dict) -> Dict:
        """
        Insert performance metrics
        
        Args:
            metrics: Dictionary of performance metrics
        """
        try:
            data = {
                'accuracy': metrics.get('accuracy', 0),
                'precision': metrics.get('precision', 0),
                'recall': metrics.get('recall', 0),
                'f1_score': metrics.get('f1_score', 0),
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'max_drawdown': metrics.get('max_drawdown', 0),
                'win_rate': metrics.get('win_rate', 0),
                'total_predictions': metrics.get('total_predictions', 0),
                'period_start': metrics.get('period_start'),
                'period_end': metrics.get('period_end'),
                'model_version': metrics.get('model_version', '1.0.0')
            }
            
            result = self.client.table('performance_metrics').insert(data).execute()
            
            return {'success': True}
        except Exception as e:
            print(f"Error inserting metrics: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_performance_history(self, model_version: str = None) -> List[Dict]:
        """
        Get performance metrics history
        
        Args:
            model_version: Filter by model version (optional)
        """
        try:
            query = self.client.table('performance_metrics').select('*').order('created_at', desc=True)
            
            if model_version:
                query = query.eq('model_version', model_version)
            
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Error getting performance history: {e}")
            return []
    
    def register_model(self, model_name: str, model_type: str, 
                     version: str, hyperparameters: Dict = None) -> Dict:
        """
        Register a new model version
        
        Args:
            model_name: Name of the model
            model_type: Type of model
            version: Version string
            hyperparameters: Model hyperparameters
        """
        try:
            data = {
                'model_name': model_name,
                'model_type': model_type,
                'version': version,
                'hyperparameters': hyperparameters or {},
                'is_active': False
            }
            
            result = self.client.table('models').insert(data).execute()
            
            return {
                'success': True,
                'id': result.data[0]['id'] if result.data else None
            }
        except Exception as e:
            print(f"Error registering model: {e}")
            return {'success': False, 'error': str(e)}
    
    def set_active_model(self, model_id: str) -> Dict:
        """
        Set a model as active
        
        Args:
            model_id: UUID of the model
        """
        try:
            # Deactivate all models
            self.client.table('models').update({'is_active': False}).execute()
            
            # Activate specified model
            result = self.client.table('models').update({'is_active': True}).eq('id', model_id).execute()
            
            return {'success': True}
        except Exception as e:
            print(f"Error setting active model: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_active_model(self) -> Optional[Dict]:
        """Get the currently active model"""
        try:
            result = self.client.table('models').select('*').eq('is_active', True).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting active model: {e}")
            return None
    
    def insert_feature_importance(self, model_id: str, 
                                 feature_importance: Dict[str, float]) -> Dict:
        """
        Insert feature importance for a model
        
        Args:
            model_id: UUID of the model
            feature_importance: Dictionary of feature names to importance scores
        """
        try:
            data = [
                {
                    'model_id': model_id,
                    'feature_name': feature,
                    'importance_score': score
                }
                for feature, score in feature_importance.items()
            ]
            
            result = self.client.table('feature_importance').insert(data).execute()
            
            return {'success': True}
        except Exception as e:
            print(f"Error inserting feature importance: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_to_watchlist(self, symbol: str) -> Dict:
        """
        Add symbol to watchlist
        
        Args:
            symbol: Stock ticker
        """
        try:
            result = self.client.table('watchlist').insert({'symbol': symbol}).execute()
            return {'success': True}
        except Exception as e:
            print(f"Error adding to watchlist: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_watchlist(self) -> List[str]:
        """Get all symbols in watchlist"""
        try:
            result = self.client.table('watchlist').select('symbol').execute()
            return [item['symbol'] for item in result.data]
        except Exception as e:
            print(f"Error getting watchlist: {e}")
            return []
    
    def create_alert(self, symbol: str, alert_type: str, 
                   message: str, severity: str = 'info') -> Dict:
        """
        Create an alert
        
        Args:
            symbol: Stock ticker
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity
        """
        try:
            data = {
                'symbol': symbol,
                'alert_type': alert_type,
                'message': message,
                'severity': severity
            }
            
            result = self.client.table('alerts').insert(data).execute()
            
            return {'success': True}
        except Exception as e:
            print(f"Error creating alert: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_alerts(self, unread_only: bool = True) -> List[Dict]:
        """
        Get alerts
        
        Args:
            unread_only: Only return unread alerts
        """
        try:
            query = self.client.table('alerts').select('*').order('created_at', desc=True)
            
            if unread_only:
                query = query.eq('is_read', False)
            
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Error getting alerts: {e}")
            return []
    
    def mark_alert_read(self, alert_id: str) -> Dict:
        """Mark an alert as read"""
        try:
            result = self.client.table('alerts').update({'is_read': True}).eq('id', alert_id).execute()
            return {'success': True}
        except Exception as e:
            print(f"Error marking alert as read: {e}")
            return {'success': False, 'error': str(e)}
    
    def subscribe_to_predictions(self, callback):
        """
        Subscribe to real-time prediction updates
        
        Args:
            callback: Function to call on new predictions
        """
        try:
            self.client.table('predictions').on('INSERT', callback).subscribe()
            print("Subscribed to predictions")
        except Exception as e:
            print(f"Error subscribing to predictions: {e}")
    
    def subscribe_to_alerts(self, callback):
        """
        Subscribe to real-time alert updates
        
        Args:
            callback: Function to call on new alerts
        """
        try:
            self.client.table('alerts').on('INSERT', callback).subscribe()
            print("Subscribed to alerts")
        except Exception as e:
            print(f"Error subscribing to alerts: {e}")
