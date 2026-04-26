import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import yfinance as yf

# Try to import featuretools
try:
    import featuretools as ft
    FEATURETOOLS_AVAILABLE = True
except ImportError:
    FEATURETOOLS_AVAILABLE = False
    print("Featuretools not available. Install with: pip install featuretools")

from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.ensemble import RandomForestClassifier

@dataclass
class FeatureSet:
    """Set of engineered features"""
    features: pd.DataFrame
    feature_names: List[str]
    importance_scores: Dict[str, float]
    selected_features: List[str]

class AutoFeatureEngineer:
    """
    Automated feature engineering for financial data
    
    Features:
    - Automatic feature generation
    - Feature selection
    - Feature importance ranking
    - Feature evolution
    """
    
    def __init__(self):
        self.base_features = [
            'rsi', 'macd', 'momentum_20d', 'volume_change',
            'price_vs_sma50', 'price_vs_sma200', 'volatility',
            'high_low_range', 'gap', 'trend_strength'
        ]
        self.engineered_features = []
        self.feature_importance = {}
        self.selected_features = []
    
    def generate_base_features(self, hist: pd.DataFrame) -> pd.DataFrame:
        """
        Generate base technical features
        
        Args:
            hist: Historical price data
        """
        if len(hist) < 50:
            return pd.DataFrame()
        
        features_list = []
        
        for i in range(50, len(hist)):
            window = hist.iloc[:i+1]
            features = self._calculate_features(window)
            if features is not None:
                features_list.append(features)
        
        return pd.DataFrame(features_list, columns=self.base_features)
    
    def _calculate_features(self, hist: pd.DataFrame) -> Optional[np.ndarray]:
        """Calculate technical features"""
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
    
    def generate_advanced_features(self, hist: pd.DataFrame) -> pd.DataFrame:
        """
        Generate advanced features
        
        Args:
            hist: Historical price data
        """
        if len(hist) < 50:
            return pd.DataFrame()
        
        base_features = self.generate_base_features(hist)
        if base_features.empty:
            return pd.DataFrame()
        
        advanced_features = base_features.copy()
        
        # Add advanced features
        advanced_features['rsi_smoothed'] = base_features['rsi'].rolling(5).mean()
        advanced_features['macd_signal'] = base_features['macd'].rolling(9).mean()
        advanced_features['momentum_acceleration'] = base_features['momentum_20d'].diff()
        advanced_features['volatility_ratio'] = base_features['volatility'] / base_features['volatility'].rolling(20).mean()
        advanced_features['price_momentum_rank'] = base_features['momentum_20d'].rolling(20).rank(pct=True)
        
        # Cross features
        advanced_features['rsi_macd_ratio'] = base_features['rsi'] / (base_features['macd'] + 1)
        advanced_features['momentum_volatility'] = base_features['momentum_20d'] * base_features['volatility']
        advanced_features['trend_gap_combo'] = base_features['trend_strength'] * base_features['gap']
        
        # Lag features
        for lag in [1, 2, 3]:
            advanced_features[f'rsi_lag_{lag}'] = base_features['rsi'].shift(lag)
            advanced_features[f'momentum_lag_{lag}'] = base_features['momentum_20d'].shift(lag)
        
        # Rolling statistics
        advanced_features['rsi_rolling_mean'] = base_features['rsi'].rolling(10).mean()
        advanced_features['rsi_rolling_std'] = base_features['rsi'].rolling(10).std()
        advanced_features['momentum_rolling_max'] = base_features['momentum_20d'].rolling(10).max()
        advanced_features['momentum_rolling_min'] = base_features['momentum_20d'].rolling(10).min()
        
        # Fill NaN values
        advanced_features = advanced_features.fillna(0)
        
        return advanced_features
    
    def select_features(self, X: pd.DataFrame, y: np.ndarray, 
                       method: str = 'importance', k: int = 20) -> List[str]:
        """
        Select best features
        
        Args:
            X: Feature DataFrame
            y: Labels
            method: 'importance', 'mutual_info', 'kbest'
            k: Number of features to select
        """
        if method == 'importance':
            # Use Random Forest for feature importance
            rf = RandomForestClassifier(n_estimators=100, random_state=42)
            rf.fit(X, y)
            
            importance = dict(zip(X.columns, rf.feature_importances_))
            self.feature_importance = importance
            
            # Select top k features
            sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            selected = [f[0] for f in sorted_features[:k]]
        
        elif method == 'mutual_info':
            # Use mutual information
            mi_scores = mutual_info_classif(X, y, random_state=42)
            importance = dict(zip(X.columns, mi_scores))
            self.feature_importance = importance
            
            sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            selected = [f[0] for f in sorted_features[:k]]
        
        elif method == 'kbest':
            # Use SelectKBest
            selector = SelectKBest(f_classif, k=k)
            selector.fit(X, y)
            
            selected_indices = selector.get_support(indices=True)
            selected = X.columns[selected_indices].tolist()
            
            importance = dict(zip(X.columns, selector.scores_))
            self.feature_importance = importance
        
        else:
            selected = X.columns.tolist()[:k]
        
        self.selected_features = selected
        return selected
    
    def generate_labels(self, hist: pd.DataFrame, forward_days: int = 3) -> np.ndarray:
        """
        Generate labels for training
        
        Args:
            hist: Historical price data
            forward_days: Days to look ahead
        """
        if len(hist) < forward_days + 50:
            return np.array([])
        
        labels = []
        for i in range(50, len(hist) - forward_days):
            current_price = hist['Close'].iloc[i]
            future_price = hist['Close'].iloc[i + forward_days]
            
            if future_price > current_price * 1.015:
                labels.append(1)  # bullish
            elif future_price < current_price * 0.985:
                labels.append(0)  # bearish
            else:
                labels.append(2)  # neutral
        
        return np.array(labels)
    
    def prepare_training_data(self, symbol: str, period: str = '2y',
                             feature_method: str = 'advanced',
                             selection_method: str = 'importance',
                             k_features: int = 20) -> Tuple[pd.DataFrame, np.ndarray, List[str]]:
        """
        Prepare complete training dataset
        
        Args:
            symbol: Stock ticker
            period: Historical period
            feature_method: 'base' or 'advanced'
            selection_method: Feature selection method
            k_features: Number of features to select
        """
        # Fetch data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if len(hist) < 100:
            raise ValueError("Insufficient data")
        
        # Generate features
        if feature_method == 'advanced':
            features_df = self.generate_advanced_features(hist)
        else:
            features_df = self.generate_base_features(hist)
        
        if features_df.empty:
            raise ValueError("Failed to generate features")
        
        # Generate labels
        labels = self.generate_labels(hist)
        
        if len(labels) == 0:
            raise ValueError("Failed to generate labels")
        
        # Align features and labels
        min_len = min(len(features_df), len(labels))
        features_df = features_df.iloc[:min_len]
        labels = labels[:min_len]
        
        # Select features
        selected = self.select_features(features_df, labels, selection_method, k_features)
        features_selected = features_df[selected]
        
        return features_selected, labels, selected
    
    def get_feature_importance_report(self) -> Dict:
        """Get feature importance report"""
        if not self.feature_importance:
            return {'error': 'No feature importance calculated'}
        
        sorted_importance = sorted(self.feature_importance.items(), 
                                  key=lambda x: x[1], reverse=True)
        
        return {
            'total_features': len(self.feature_importance),
            'top_features': [
                {'feature': f, 'importance': round(i, 4)}
                for f, i in sorted_importance[:10]
            ],
            'selected_features': self.selected_features
        }
    
    def evolve_features(self, X: pd.DataFrame, y: np.ndarray, 
                      performance_threshold: float = 0.6) -> List[str]:
        """
        Evolve features based on performance
        
        Args:
            X: Current features
            y: Labels
            performance_threshold: Minimum accuracy to keep features
        """
        # Calculate current performance with all features
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score
        
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        scores = cross_val_score(rf, X, y, cv=5)
        current_performance = scores.mean()
        
        if current_performance < performance_threshold:
            # Try adding interaction features
            new_features = []
            
            for i, col1 in enumerate(X.columns):
                for col2 in X.columns[i+1:]:
                    # Multiplicative interaction
                    new_col = f"{col1}_x_{col2}"
                    X[new_col] = X[col1] * X[col2]
                    new_features.append(new_col)
                    
                    # Additive interaction
                    new_col = f"{col1}_plus_{col2}"
                    X[new_col] = X[col1] + X[col2]
                    new_features.append(new_col)
            
            # Select best new features
            self.select_features(X, y, method='importance', k=len(self.selected_features) + 5)
            
            return new_features
        
        return []
