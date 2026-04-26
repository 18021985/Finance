import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import yfinance as yf

from ensemble_predictor import EnsemblePredictor

@dataclass
class BacktestResult:
    """Result of backtesting"""
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    average_win: float
    average_loss: float
    profit_factor: float
    start_date: datetime
    end_date: datetime

class MLBacktester:
    """
    Backtesting system for ML models
    
    Features:
    - Walk-forward backtesting
    - Performance metrics calculation
    - Strategy comparison
    """
    
    def __init__(self, predictor: EnsemblePredictor):
        self.predictor = predictor
        self.backtest_history: List[BacktestResult] = []
    
    def backtest_strategy(self, symbol: str, period: str = '2y', 
                         train_window: int = 252, test_window: int = 20,
                         strategy: str = 'long_only') -> BacktestResult:
        """
        Backtest ML strategy
        
        Args:
            symbol: Stock ticker
            period: Historical period
            train_window: Training window size
            test_window: Test window size
            strategy: 'long_only', 'long_short', 'neutral'
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if len(hist) < train_window + test_window + 50:
                raise ValueError("Insufficient data for backtesting")
            
            # Track trades
            trades = []
            positions = []
            portfolio_value = 100000  # Starting with $100k
            current_position = 0  # 0 = neutral, 1 = long, -1 = short
            
            # Walk-forward
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
                for j in range(50, len(test_data) - 3):
                    window = test_data.iloc[:j+3]
                    features = self.predictor.prepare_features(window)
                    if features is not None:
                        features_scaled = self.predictor.scaler.transform(features)
                        
                        # Get prediction
                        prediction = self.predictor.predict(symbol)
                        
                        # Execute trade based on prediction
                        current_price = test_data['Close'].iloc[j]
                        next_price = test_data['Close'].iloc[j+1]
                        
                        if strategy == 'long_only':
                            if prediction.direction == 'bullish' and current_position == 0:
                                # Enter long
                                trades.append({
                                    'entry': current_price,
                                    'exit': next_price,
                                    'direction': 'long',
                                    'date': test_data.index[j]
                                })
                                current_position = 1
                            elif prediction.direction == 'bearish' and current_position == 1:
                                # Exit long
                                if trades:
                                    trades[-1]['exit'] = current_price
                                current_position = 0
                        
                        elif strategy == 'long_short':
                            if prediction.direction == 'bullish' and current_position != 1:
                                # Enter long or cover short
                                if current_position == -1 and trades:
                                    trades[-1]['exit'] = current_price
                                trades.append({
                                    'entry': current_price,
                                    'exit': next_price,
                                    'direction': 'long',
                                    'date': test_data.index[j]
                                })
                                current_position = 1
                            elif prediction.direction == 'bearish' and current_position != -1:
                                # Enter short or cover long
                                if current_position == 1 and trades:
                                    trades[-1]['exit'] = current_price
                                trades.append({
                                    'entry': current_price,
                                    'exit': next_price,
                                    'direction': 'short',
                                    'date': test_data.index[j]
                                })
                                current_position = -1
            
            # Calculate metrics
            if not trades:
                return BacktestResult(
                    total_return=0.0, annualized_return=0.0, sharpe_ratio=0.0,
                    max_drawdown=0.0, win_rate=0.0, total_trades=0,
                    winning_trades=0, losing_trades=0, average_win=0.0,
                    average_loss=0.0, profit_factor=0.0,
                    start_date=hist.index[0], end_date=hist.index[-1]
                )
            
            # Calculate returns
            returns = []
            for trade in trades:
                if trade['direction'] == 'long':
                    ret = (trade['exit'] - trade['entry']) / trade['entry']
                else:
                    ret = (trade['entry'] - trade['exit']) / trade['entry']
                returns.append(ret)
            
            total_return = np.sum(returns)
            annualized_return = (1 + total_return) ** (252 / len(hist)) - 1
            
            # Sharpe ratio
            sharpe = 0.0
            if returns:
                sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
            
            # Max drawdown
            cumulative = np.cumprod(1 + np.array(returns))
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            max_dd = np.min(drawdown)
            
            # Win rate
            winning_trades = sum(1 for r in returns if r > 0)
            losing_trades = sum(1 for r in returns if r < 0)
            win_rate = winning_trades / len(returns) if returns else 0
            
            # Average win/loss
            wins = [r for r in returns if r > 0]
            losses = [r for r in returns if r < 0]
            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean(losses) if losses else 0
            
            # Profit factor
            profit_factor = abs(sum(wins) / sum(losses)) if losses else float('inf')
            
            result = BacktestResult(
                total_return=round(total_return, 4),
                annualized_return=round(annualized_return, 4),
                sharpe_ratio=round(sharpe, 4),
                max_drawdown=round(max_dd, 4),
                win_rate=round(win_rate, 4),
                total_trades=len(trades),
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                average_win=round(avg_win, 4),
                average_loss=round(avg_loss, 4),
                profit_factor=round(profit_factor, 4),
                start_date=hist.index[0],
                end_date=hist.index[-1]
            )
            
            self.backtest_history.append(result)
            return result
        except Exception as e:
            print(f"Error in backtesting: {e}")
            return BacktestResult(
                total_return=0.0, annualized_return=0.0, sharpe_ratio=0.0,
                max_drawdown=0.0, win_rate=0.0, total_trades=0,
                winning_trades=0, losing_trades=0, average_win=0.0,
                average_loss=0.0, profit_factor=0.0,
                start_date=datetime.now(), end_date=datetime.now()
            )
    
    def compare_strategies(self, symbol: str, period: str = '2y') -> Dict:
        """
        Compare different strategies
        
        Args:
            symbol: Stock ticker
            period: Historical period
        """
        strategies = ['long_only', 'long_short']
        results = {}
        
        for strategy in strategies:
            result = self.backtest_strategy(symbol, period, strategy=strategy)
            results[strategy] = {
                'total_return': result.total_return,
                'sharpe_ratio': result.sharpe_ratio,
                'max_drawdown': result.max_drawdown,
                'win_rate': result.win_rate
            }
        
        # Compare with buy and hold
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        buy_hold_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1)
        
        results['buy_hold'] = {
            'total_return': round(buy_hold_return, 4),
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0
        }
        
        return results
    
    def get_backtest_summary(self) -> Dict:
        """Get summary of all backtests"""
        if not self.backtest_history:
            return {'error': 'No backtest results'}
        
        avg_return = np.mean([r.total_return for r in self.backtest_history])
        avg_sharpe = np.mean([r.sharpe_ratio for r in self.backtest_history])
        avg_win_rate = np.mean([r.win_rate for r in self.backtest_history])
        
        return {
            'total_backtests': len(self.backtest_history),
            'average_return': round(avg_return, 4),
            'average_sharpe': round(avg_sharpe, 4),
            'average_win_rate': round(avg_win_rate, 4),
            'best_sharpe': max(self.backtest_history, key=lambda x: x.sharpe_ratio).sharpe_ratio
        }
