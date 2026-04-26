import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
import yfinance as yf

# Try to import scikit-optimize
try:
    from skopt import BayesSearchCV
    from skopt.space import Real, Categorical, Integer
    SKOPT_AVAILABLE = True
except ImportError:
    SKOPT_AVAILABLE = False
    print("scikit-optimize not available. Install with: pip install scikit-optimize")

# Try to import optuna
try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("Optuna not available. Install with: pip install optuna")

from ensemble_predictor import EnsemblePredictor

@dataclass
class OptimizationResult:
    """Result of hyperparameter optimization"""
    best_params: Dict
    best_score: float
    optimization_time: float
    n_iterations: int
    search_space: Dict
    best_model: object

class HyperparameterOptimizer:
    """
    Hyperparameter optimization using Bayesian optimization
    
    Supports:
    - scikit-optimize (BayesSearchCV)
    - Optuna (advanced Bayesian optimization)
    """
    
    def __init__(self, predictor: EnsemblePredictor):
        self.predictor = predictor
        self.best_params = {}
        self.optimization_history = []
    
    def get_search_space(self, model_name: str) -> Dict:
        """
        Get search space for a specific model
        
        Args:
            model_name: Name of the model
        """
        search_spaces = {
            'xgboost': {
                'n_estimators': Integer(50, 500),
                'max_depth': Integer(3, 10),
                'learning_rate': Real(0.01, 0.3, 'log-uniform'),
                'subsample': Real(0.5, 1.0),
                'colsample_bytree': Real(0.5, 1.0),
                'min_child_weight': Integer(1, 10),
                'gamma': Real(0, 5),
                'reg_alpha': Real(0, 1),
                'reg_lambda': Real(0, 1)
            },
            'lightgbm': {
                'n_estimators': Integer(50, 500),
                'max_depth': Integer(3, 10),
                'learning_rate': Real(0.01, 0.3, 'log-uniform'),
                'subsample': Real(0.5, 1.0),
                'colsample_bytree': Real(0.5, 1.0),
                'min_child_samples': Integer(10, 100),
                'reg_alpha': Real(0, 1),
                'reg_lambda': Real(0, 1)
            },
            'catboost': {
                'iterations': Integer(50, 500),
                'depth': Integer(3, 10),
                'learning_rate': Real(0.01, 0.3, 'log-uniform'),
                'l2_leaf_reg': Real(1, 10),
                'border_count': Integer(32, 255)
            },
            'gradient_boosting': {
                'n_estimators': Integer(50, 500),
                'max_depth': Integer(3, 10),
                'learning_rate': Real(0.01, 0.3, 'log-uniform'),
                'subsample': Real(0.5, 1.0),
                'min_samples_split': Integer(2, 20),
                'min_samples_leaf': Integer(1, 10)
            },
            'random_forest': {
                'n_estimators': Integer(50, 500),
                'max_depth': Integer(3, 20),
                'min_samples_split': Integer(2, 20),
                'min_samples_leaf': Integer(1, 10),
                'max_features': Categorical(['sqrt', 'log2', None])
            }
        }
        
        return search_spaces.get(model_name, {})
    
    def prepare_training_data(self, symbol: str, period: str = '2y') -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data for optimization
        
        Args:
            symbol: Stock ticker
            period: Historical period
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if len(hist) < 100:
                return None, None
            
            # Prepare features and labels
            features_list = []
            labels_list = []
            
            for i in range(50, len(hist) - 3):
                window = hist.iloc[:i+3]
                features = self.predictor.prepare_features(window)
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
                return None, None
            
            X = np.array(features_list)
            y = np.array(labels_list)
            X_scaled = self.predictor.scaler.fit_transform(X)
            
            return X_scaled, y
        except Exception as e:
            print(f"Error preparing data: {e}")
            return None, None
    
    def optimize_with_skopt(self, symbol: str, model_name: str = 'random_forest',
                          n_iter: int = 50, cv: int = 5) -> OptimizationResult:
        """
        Optimize hyperparameters using scikit-optimize
        
        Args:
            symbol: Stock ticker
            model_name: Model to optimize
            n_iter: Number of optimization iterations
            cv: Cross-validation folds
        """
        if not SKOPT_AVAILABLE:
            raise ImportError("scikit-optimize not available")
        
        import time
        start_time = time.time()
        
        # Prepare data
        X, y = self.prepare_training_data(symbol)
        if X is None:
            raise ValueError("Insufficient data for optimization")
        
        # Get search space
        search_space = self.get_search_space(model_name)
        if not search_space:
            raise ValueError(f"No search space defined for {model_name}")
        
        # Get model
        if model_name not in self.predictor.models:
            raise ValueError(f"Model {model_name} not available")
        
        model = self.predictor.models[model_name]
        
        # Use time series split for time series data
        tscv = TimeSeriesSplit(n_splits=cv)
        
        # Bayesian optimization
        opt = BayesSearchCV(
            estimator=model,
            search_spaces=search_space,
            n_iter=n_iter,
            cv=tscv,
            n_jobs=-1,
            random_state=42
        )
        
        opt.fit(X, y)
        
        optimization_time = time.time() - start_time
        
        result = OptimizationResult(
            best_params=opt.best_params_,
            best_score=opt.best_score_,
            optimization_time=optimization_time,
            n_iterations=n_iter,
            search_space=search_space,
            best_model=opt.best_estimator_
        )
        
        self.optimization_history.append(result)
        self.best_params[model_name] = opt.best_params_
        
        return result
    
    def optimize_with_optuna(self, symbol: str, model_name: str = 'random_forest',
                           n_trials: int = 100, timeout: int = 3600) -> OptimizationResult:
        """
        Optimize hyperparameters using Optuna
        
        Args:
            symbol: Stock ticker
            model_name: Model to optimize
            n_trials: Number of trials
            timeout: Timeout in seconds
        """
        if not OPTUNA_AVAILABLE:
            raise ImportError("Optuna not available")
        
        import time
        start_time = time.time()
        
        # Prepare data
        X, y = self.prepare_training_data(symbol)
        if X is None:
            raise ValueError("Insufficient data for optimization")
        
        # Get search space
        search_space = self.get_search_space(model_name)
        if not search_space:
            raise ValueError(f"No search space defined for {model_name}")
        
        # Define objective function
        def objective(trial):
            params = {}
            
            for param_name, param_space in search_space.items():
                if isinstance(param_space, Integer):
                    params[param_name] = trial.suggest_int(param_name, param_space.low, param_space.high)
                elif isinstance(param_space, Real):
                    if param_space.prior == 'log-uniform':
                        params[param_name] = trial.suggest_float(param_name, param_space.low, param_space.high, log=True)
                    else:
                        params[param_name] = trial.suggest_float(param_name, param_space.low, param_space.high)
                elif isinstance(param_space, Categorical):
                    params[param_name] = trial.suggest_categorical(param_name, param_space.categories)
            
            # Create model with suggested parameters
            if model_name == 'xgboost':
                from xgboost import XGBClassifier
                model = XGBClassifier(**params, random_state=42, use_label_encoder=False, eval_metric='logloss')
            elif model_name == 'lightgbm':
                from lightgbm import LGBMClassifier
                model = LGBMClassifier(**params, random_state=42, verbose=-1)
            elif model_name == 'catboost':
                from catboost import CatBoostClassifier
                model = CatBoostClassifier(**params, random_state=42, verbose=False)
            elif model_name == 'gradient_boosting':
                model = self.predictor.models['gradient_boosting'].__class__(**params, random_state=42)
            elif model_name == 'random_forest':
                model = self.predictor.models['random_forest'].__class__(**params, random_state=42)
            else:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Cross-validation
            tscv = TimeSeriesSplit(n_splits=5)
            scores = cross_val_score(model, X, y, cv=tscv, scoring='accuracy')
            
            return scores.mean()
        
        # Create study
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials, timeout=timeout)
        
        optimization_time = time.time() - start_time
        
        result = OptimizationResult(
            best_params=study.best_params,
            best_score=study.best_value,
            optimization_time=optimization_time,
            n_iterations=n_trials,
            search_space=search_space,
            best_model=None  # Would need to recreate model with best params
        )
        
        self.optimization_history.append(result)
        self.best_params[model_name] = study.best_params
        
        return result
    
    def optimize_all_models(self, symbol: str, method: str = 'skopt',
                           n_iter: int = 50) -> Dict[str, OptimizationResult]:
        """
        Optimize all available models
        
        Args:
            symbol: Stock ticker
            method: 'skopt' or 'optuna'
            n_iter: Number of iterations
        """
        results = {}
        
        for model_name in self.predictor.models.keys():
            print(f"\nOptimizing {model_name}...")
            try:
                if method == 'skopt':
                    result = self.optimize_with_skopt(symbol, model_name, n_iter)
                elif method == 'optuna':
                    result = self.optimize_with_optuna(symbol, model_name, n_iter)
                else:
                    raise ValueError(f"Unknown method: {method}")
                
                results[model_name] = result
                print(f"Best score for {model_name}: {result.best_score:.4f}")
            except Exception as e:
                print(f"Error optimizing {model_name}: {e}")
        
        return results
    
    def apply_best_params(self, model_name: str):
        """
        Apply best parameters to a model
        
        Args:
            model_name: Name of the model
        """
        if model_name not in self.best_params:
            raise ValueError(f"No optimized parameters for {model_name}")
        
        best_params = self.best_params[model_name]
        model = self.predictor.models[model_name]
        
        # Set parameters
        model.set_params(**best_params)
        
        print(f"Applied best parameters to {model_name}")
        print(f"Parameters: {best_params}")
    
    def get_optimization_summary(self) -> Dict:
        """Get summary of all optimizations"""
        summary = {}
        
        for result in self.optimization_history:
            model_name = list(result.search_space.keys())[0] if result.search_space else 'unknown'
            summary[model_name] = {
                'best_score': result.best_score,
                'best_params': result.best_params,
                'optimization_time': result.optimization_time,
                'n_iterations': result.n_iterations
            }
        
        return summary
