import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
import yfinance as yf

# Try to import SHAP
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("SHAP not available. Install with: pip install shap")

from ensemble_predictor import EnsemblePredictor

@dataclass
class ExplanationResult:
    """Result of model explanation"""
    feature_importance: Dict[str, float]
    shap_values: np.ndarray
    base_value: float
    prediction: str
    top_positive_features: List[Dict]
    top_negative_features: List[Dict]
    explanation_text: str

class ModelExplainer:
    """
    Model explainability using SHAP
    
    Features:
    - Feature importance
    - SHAP values for individual predictions
    - Local explanations
    - Global explanations
    """
    
    def __init__(self, predictor: EnsemblePredictor):
        self.predictor = predictor
        self.explainer = None
        self.feature_names = predictor.feature_names
    
    def initialize_explainer(self, symbol: str, period: str = '1y'):
        """
        Initialize SHAP explainer
        
        Args:
            symbol: Stock ticker
            period: Historical period
        """
        if not SHAP_AVAILABLE:
            raise ImportError("SHAP library not available")
        
        try:
            # Prepare background data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if len(hist) < 100:
                raise ValueError("Insufficient data for explainer initialization")
            
            # Prepare features
            features_list = []
            for i in range(50, len(hist) - 3):
                window = hist.iloc[:i+3]
                features = self.predictor.prepare_features(window)
                if features is not None:
                    features_list.append(features[0])
            
            if len(features_list) < 50:
                raise ValueError("Insufficient features for explainer")
            
            X = np.array(features_list)
            X_scaled = self.predictor.scaler.fit_transform(X)
            
            # Use Random Forest for SHAP (tree-based)
            if 'random_forest' in self.predictor.models:
                model = self.predictor.models['random_forest']
                self.explainer = shap.TreeExplainer(model, X_scaled[:100])
            else:
                # Use KernelExplainer for other models
                def model_predict(x):
                    return self.predictor.models['gradient_boosting'].predict_proba(x)
                self.explainer = shap.KernelExplainer(model_predict, X_scaled[:50])
            
            print("SHAP explainer initialized")
        except Exception as e:
            print(f"Error initializing explainer: {e}")
    
    def explain_prediction(self, symbol: str) -> ExplanationResult:
        """
        Explain a single prediction
        
        Args:
            symbol: Stock ticker
        """
        if not SHAP_AVAILABLE or self.explainer is None:
            return ExplanationResult(
                feature_importance={},
                shap_values=np.array([]),
                base_value=0.0,
                prediction='neutral',
                top_positive_features=[],
                top_negative_features=[],
                explanation_text="SHAP not available"
            )
        
        try:
            # Get current features
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return ExplanationResult(
                    feature_importance={},
                    shap_values=np.array([]),
                    base_value=0.0,
                    prediction='neutral',
                    top_positive_features=[],
                    top_negative_features=[],
                    explanation_text="No data available"
                )
            
            features = self.predictor.prepare_features(hist)
            if features is None:
                return ExplanationResult(
                    feature_importance={},
                    shap_values=np.array([]),
                    base_value=0.0,
                    prediction='neutral',
                    top_positive_features=[],
                    top_negative_features=[],
                    explanation_text="Insufficient features"
                )
            
            features_scaled = self.predictor.scaler.transform(features)
            
            # Get SHAP values
            shap_values = self.explainer.shap_values(features_scaled)
            base_value = self.explainer.expected_value
            
            # Get prediction
            prediction = self.predictor.predict(symbol)
            
            # Feature importance
            if isinstance(shap_values, list):
                shap_values_array = shap_values[0]  # For multi-class
            else:
                shap_values_array = shap_values
            
            # Calculate feature importance
            importance = dict(zip(self.feature_names, np.abs(shap_values_array).mean(axis=0)))
            
            # Top positive and negative features
            feature_shap = list(zip(self.feature_names, shap_values_array[0]))
            
            # Sort by SHAP value
            feature_shap.sort(key=lambda x: x[1], reverse=True)
            
            top_positive = [
                {'feature': f, 'value': v, 'impact': 'positive'}
                for f, v in feature_shap[:5] if v > 0
            ]
            
            top_negative = [
                {'feature': f, 'value': v, 'impact': 'negative'}
                for f, v in feature_shap[-5:] if v < 0
            ]
            
            # Generate explanation text
            explanation = self._generate_explanation(
                prediction.direction, top_positive, top_negative
            )
            
            return ExplanationResult(
                feature_importance=importance,
                shap_values=shap_values_array,
                base_value=float(base_value) if not isinstance(base_value, np.ndarray) else float(base_value[0]),
                prediction=prediction.direction,
                top_positive_features=top_positive,
                top_negative_features=top_negative,
                explanation_text=explanation
            )
        except Exception as e:
            print(f"Error explaining prediction: {e}")
            return ExplanationResult(
                feature_importance={},
                shap_values=np.array([]),
                base_value=0.0,
                prediction='neutral',
                top_positive_features=[],
                top_negative_features=[],
                explanation_text=f"Error: {str(e)}"
            )
    
    def _generate_explanation(self, prediction: str, 
                            positive: List[Dict], 
                            negative: List[Dict]) -> str:
        """Generate human-readable explanation"""
        parts = []
        
        parts.append(f"Prediction: {prediction.upper()}")
        
        if positive:
            pos_features = [f"{p['feature']} (+{p['value']:.3f})" for p in positive]
            parts.append(f"Supporting factors: {', '.join(pos_features)}")
        
        if negative:
            neg_features = [f"{n['feature']} ({n['value']:.3f})" for n in negative]
            parts.append(f"Opposing factors: {', '.join(neg_features)}")
        
        return '. '.join(parts)
    
    def get_global_importance(self, symbol: str, period: str = '1y') -> Dict:
        """
        Get global feature importance
        
        Args:
            symbol: Stock ticker
            period: Historical period
        """
        if not SHAP_AVAILABLE:
            return {'error': 'SHAP not available'}
        
        try:
            # Initialize explainer if not already
            if self.explainer is None:
                self.initialize_explainer(symbol, period)
            
            # Get background data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            features_list = []
            for i in range(50, len(hist) - 3):
                window = hist.iloc[:i+3]
                features = self.predictor.prepare_features(window)
                if features is not None:
                    features_list.append(features[0])
            
            X = np.array(features_list)
            X_scaled = self.predictor.scaler.transform(X)
            
            # Get SHAP values for all samples
            shap_values = self.explainer.shap_values(X_scaled)
            
            if isinstance(shap_values, list):
                shap_values_array = shap_values[0]
            else:
                shap_values_array = shap_values
            
            # Calculate mean absolute SHAP values
            mean_importance = np.abs(shap_values_array).mean(axis=0)
            
            importance = dict(zip(self.feature_names, mean_importance))
            
            # Sort by importance
            sorted_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
            
            return {
                'feature_importance': sorted_importance,
                'total_features': len(self.feature_names)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def plot_summary(self, symbol: str, save_path: Optional[str] = None):
        """
        Generate SHAP summary plot
        
        Args:
            symbol: Stock ticker
            save_path: Path to save plot (optional)
        """
        if not SHAP_AVAILABLE:
            print("SHAP not available")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            # Get data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            features_list = []
            for i in range(50, len(hist) - 3):
                window = hist.iloc[:i+3]
                features = self.predictor.prepare_features(window)
                if features is not None:
                    features_list.append(features[0])
            
            X = np.array(features_list)
            X_scaled = self.predictor.scaler.transform(X)
            
            # Plot
            shap.summary_plot(self.explainer.shap_values(X_scaled), X_scaled, 
                            feature_names=self.feature_names, show=False)
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Plot saved to {save_path}")
            else:
                plt.show()
            
            plt.close()
        except Exception as e:
            print(f"Error generating plot: {e}")
