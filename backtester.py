import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from probabilistic_forecast import ProbabilisticForecaster
from evaluation import walk_forward_direction_eval

@dataclass
class BacktestResult:
    """Represents backtest results"""
    strategy_name: str
    total_return: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float

class Backtester:
    """Backtesting module for strategy validation"""
    
    def __init__(self):
        self.prob_forecaster = ProbabilisticForecaster()
    
    def _detect_regime(self, data: pd.DataFrame, window: int = 63) -> pd.Series:
        """
        Detect market regime based on volatility and trend.
        Returns regime labels: 'bull', 'bear', 'sideways'
        """
        close = data['Close']
        returns = close.pct_change().dropna()
        
        # Rolling volatility
        vol = returns.rolling(window).std()
        
        # Rolling trend (simple moving average slope)
        ma_short = close.rolling(window // 2).mean()
        ma_long = close.rolling(window).mean()
        trend = (ma_short - ma_long) / ma_long
        
        regime = []
        for i in range(len(data)):
            if pd.isna(vol.iloc[i]) or pd.isna(trend.iloc[i]):
                regime.append('sideways')
            elif vol.iloc[i] > vol.quantile(0.7):
                # High volatility - likely bear or transition
                regime.append('bear' if trend.iloc[i] < 0 else 'sideways')
            elif trend.iloc[i] > 0.02:  # Strong uptrend
                regime.append('bull')
            elif trend.iloc[i] < -0.02:  # Strong downtrend
                regime.append('bear')
            else:
                regime.append('sideways')
        
        return pd.Series(regime, index=data.index)
    
    def _calculate_hit_rate_by_regime(self, trades: List[Dict], data: pd.DataFrame) -> Dict:
        """
        Calculate hit rate broken down by market regime.
        """
        if not trades:
            return {}
        
        # Detect regimes for the entire period
        regimes = self._detect_regime(data)
        
        # Map each trade to its regime
        regime_stats = {'bull': {'wins': 0, 'total': 0}, 
                        'bear': {'wins': 0, 'total': 0},
                        'sideways': {'wins': 0, 'total': 0}}
        
        for trade in trades:
            if 'date' not in trade:
                continue
            
            trade_date = trade['date']
            if trade_date not in regimes.index:
                continue
            
            regime = regimes.loc[trade_date]
            if regime in regime_stats:
                regime_stats[regime]['total'] += 1
                if trade.get('pnl', 0) > 0:
                    regime_stats[regime]['wins'] += 1
        
        # Calculate hit rates
        hit_rates = {}
        for regime, stats in regime_stats.items():
            if stats['total'] > 0:
                hit_rates[regime] = {
                    'hit_rate': round(stats['wins'] / stats['total'] * 100, 2),
                    'total_trades': stats['total'],
                    'winning_trades': stats['wins']
                }
        
        return hit_rates
    
    def backtest_strategy(self, data: pd.DataFrame, signals: pd.DataFrame,
                         initial_capital: float = 100000) -> Dict:
        """
        Backtest a trading strategy
        
        Args:
            data: Price data with OHLCV
            signals: DataFrame with 'signal' column (1=buy, -1=sell, 0=hold)
            initial_capital: Starting capital
        """
        if data.empty or signals.empty:
            return {'error': 'Insufficient data for backtesting'}
        
        # Align data and signals
        aligned_data = data.copy()
        aligned_data['signal'] = signals['signal'].reindex(aligned_data.index, fill_value=0)
        
        # Initialize tracking
        capital = initial_capital
        position = 0
        holdings = 0
        trades = []
        equity_curve = [capital]
        
        for i in range(1, len(aligned_data)):
            current_price = aligned_data['Close'].iloc[i]
            signal = aligned_data['signal'].iloc[i]
            prev_signal = aligned_data['signal'].iloc[i-1]
            
            # Execute trades based on signal changes
            if signal == 1 and prev_signal != 1 and position == 0:
                # Buy signal
                holdings = capital / current_price
                position = 1
                trades.append({
                    'date': aligned_data.index[i],
                    'action': 'buy',
                    'price': current_price,
                    'shares': holdings,
                    'value': capital
                })
                capital = 0
                
            elif signal == -1 and prev_signal != -1 and position == 1:
                # Sell signal
                capital = holdings * current_price
                trades[-1]['exit_price'] = current_price
                trades[-1]['exit_date'] = aligned_data.index[i]
                trades[-1]['exit_value'] = capital
                trades[-1]['pnl'] = capital - trades[-1]['value']
                trades[-1]['pnl_pct'] = (capital / trades[-1]['value'] - 1) * 100
                position = 0
                holdings = 0
            
            # Calculate current equity
            if position == 1:
                current_equity = holdings * current_price
            else:
                current_equity = capital
            
            equity_curve.append(current_equity)
        
        # Close final position if still open
        if position == 1:
            final_price = float(aligned_data['Close'].iloc[-1]) if not aligned_data.empty else 0
            capital = holdings * final_price
            trades[-1]['exit_price'] = final_price
            trades[-1]['exit_date'] = aligned_data.index[-1]
            trades[-1]['exit_value'] = capital
            trades[-1]['pnl'] = capital - trades[-1]['value']
            trades[-1]['pnl_pct'] = (capital / trades[-1]['value'] - 1) * 100
        
        # Calculate metrics
        equity_curve = pd.Series(equity_curve)
        returns = equity_curve.pct_change().dropna()
        
        total_return = float((equity_curve.iloc[-1] / initial_capital - 1) * 100) if not equity_curve.empty else 0.0
        annualized_return = float((equity_curve.iloc[-1] / initial_capital) ** (252 / len(equity_curve)) - 1) if not equity_curve.empty else 0.0
        
        # Max drawdown
        rolling_max = equity_curve.expanding().max()
        drawdown = (equity_curve - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        # Sharpe ratio
        if returns.std() > 0:
            sharpe_ratio = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
        else:
            sharpe_ratio = 0
        
        # Trade statistics
        completed_trades = [t for t in trades if 'pnl' in t]
        winning_trades = [t for t in completed_trades if t['pnl'] > 0]
        losing_trades = [t for t in completed_trades if t['pnl'] < 0]
        
        win_rate = len(winning_trades) / len(completed_trades) if completed_trades else 0
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        gross_profit = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t['pnl'] for t in losing_trades)) if losing_trades else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Hit rate by regime
        hit_rate_by_regime = self._calculate_hit_rate_by_regime(completed_trades, aligned_data)
        
        return {
            'strategy_name': 'Signal-Based Strategy',
            'initial_capital': initial_capital,
            'final_capital': round(equity_curve.iloc[-1], 2),
            'total_return': round(total_return, 2),
            'annualized_return': round(annualized_return * 100, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'win_rate': round(win_rate * 100, 2),
            'profit_factor': round(profit_factor, 2),
            'total_trades': len(completed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'equity_curve': equity_curve.tolist(),
            'trades': completed_trades[-10:],  # Last 10 trades
            'hit_rate_by_regime': hit_rate_by_regime,
        }
    
    def backtest_buy_and_hold(self, data: pd.DataFrame, 
                             initial_capital: float = 100000) -> Dict:
        """Backtest simple buy and hold strategy for comparison"""
        if data.empty:
            return {'error': 'Insufficient data'}
        
        initial_price = float(data['Close'].iloc[0]) if not data.empty else 0
        final_price = float(data['Close'].iloc[-1]) if not data.empty else 0
        
        shares = initial_capital / initial_price if initial_price > 0 else 0
        final_value = shares * final_price
        
        total_return = float((final_value / initial_capital - 1) * 100)
        annualized_return = float((final_value / initial_capital) ** (252 / len(data)) - 1) if len(data) > 0 else 0.0
        
        # Calculate max drawdown
        equity = shares * data['Close']
        rolling_max = equity.expanding().max()
        drawdown = (equity - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        return {
            'strategy_name': 'Buy and Hold',
            'initial_capital': initial_capital,
            'final_capital': round(final_value, 2),
            'total_return': round(total_return, 2),
            'annualized_return': round(annualized_return * 100, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': 0,  # Would need risk-free rate
        }
    
    def compare_strategies(self, strategy_results: List[Dict]) -> Dict:
        """Compare multiple backtest results"""
        comparison = []
        
        for result in strategy_results:
            comparison.append({
                'strategy': result['strategy_name'],
                'total_return': result['total_return'],
                'annualized_return': result['annualized_return'],
                'max_drawdown': result['max_drawdown'],
                'sharpe_ratio': result.get('sharpe_ratio', 0),
                'win_rate': result.get('win_rate', 0),
            })
        
        # Sort by Sharpe ratio
        comparison.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
        
        return {
            'comparison': comparison,
            'best_strategy': comparison[0] if comparison else None,
            'worst_strategy': comparison[-1] if comparison else None,
        }

    def walk_forward_probabilistic_forecast_eval(
        self,
        data: pd.DataFrame,
        horizon_days: int = 20,
        step_days: int = 5,
        score_proxy: float = 50.0,
    ) -> Dict:
        """
        Walk-forward evaluation for probabilistic direction forecasts.

        Uses the empirical quantile forecaster to compute P(up) at each step based on
        the trailing history available at that time (no lookahead).
        """
        if data is None or data.empty or "Close" not in data:
            return {"error": "Insufficient data"}

        close = data["Close"].dropna()
        if len(close) < (horizon_days + 80):
            return {"error": "Insufficient data for walk-forward evaluation"}

        probs = []
        idx = close.index
        prob_series = pd.Series(index=idx, dtype=float)

        # Use a rolling window as "training" set
        window = max(120, horizon_days * 4)
        for i in range(window, len(close)):
            history = close.iloc[i - window : i]
            dist = self.prob_forecaster.forecast(history, horizon_days=horizon_days, score=score_proxy)
            prob_series.iloc[i] = dist.direction_up_prob

        prob_series = prob_series.dropna()
        return walk_forward_direction_eval(close, prob_series, horizon_days=horizon_days, step_days=step_days)
    
    def generate_signals_from_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals from technical indicators
        
        Returns DataFrame with signal column (1=buy, -1=sell, 0=hold)
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        # Calculate indicators
        data['sma_20'] = data['Close'].rolling(20).mean()
        data['sma_50'] = data['Close'].rolling(50).mean()
        data['rsi'] = self._calculate_rsi(data['Close'], 14)
        
        # Generate signals
        # Buy: Price above SMA 50 and RSI oversold
        buy_condition = (data['Close'] > data['sma_50']) & (data['rsi'] < 30)
        signals.loc[buy_condition, 'signal'] = 1
        
        # Sell: Price below SMA 50 and RSI overbought
        sell_condition = (data['Close'] < data['sma_50']) & (data['rsi'] > 70)
        signals.loc[sell_condition, 'signal'] = -1
        
        return signals
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
