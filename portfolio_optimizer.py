import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class PortfolioRecommendation:
    """Represents portfolio optimization recommendation"""
    symbol: str
    current_weight: float
    recommended_weight: float
    action: str  # 'buy', 'sell', 'hold'
    reason: str
    expected_return: float
    risk_contribution: float

class PortfolioOptimizer:
    """Portfolio optimization and rebalancing recommendations"""
    
    def __init__(self):
        pass
    
    def optimize_portfolio(self, holdings: Dict[str, float], 
                         expected_returns: Dict[str, float],
                         risk_matrix: Dict[str, Dict[str, float]] = None) -> Dict:
        """
        Optimize portfolio allocation using mean-variance optimization
        
        Args:
            holdings: Current holdings {symbol: weight}
            expected_returns: Expected returns {symbol: return}
            risk_matrix: Covariance matrix (optional, will use simplified if not provided)
        """
        symbols = list(holdings.keys())
        n = len(symbols)
        
        if n == 0:
            return {'error': 'No holdings provided'}
        
        # If no risk matrix provided, use simplified assumptions
        if risk_matrix is None:
            risk_matrix = self._simplified_risk_matrix(symbols)
        
        # Calculate current portfolio metrics
        current_weights = np.array([holdings[s] for s in symbols])
        current_return = sum(expected_returns.get(s, 0) * holdings[s] for s in symbols)
        current_risk = self._calculate_portfolio_risk(current_weights, risk_matrix, symbols)
        
        # Optimize using mean-variance (simplified)
        optimal_weights = self._mean_variance_optimization(
            expected_returns, risk_matrix, symbols
        )
        
        # Generate recommendations
        recommendations = []
        for i, symbol in enumerate(symbols):
            current_weight = holdings[symbol]
            optimal_weight = optimal_weights[i]
            
            if optimal_weight > current_weight + 0.05:
                action = 'buy'
                reason = f'Increase allocation from {current_weight*100:.1f}% to {optimal_weight*100:.1f}%'
            elif optimal_weight < current_weight - 0.05:
                action = 'sell'
                reason = f'Reduce allocation from {current_weight*100:.1f}% to {optimal_weight*100:.1f}%'
            else:
                action = 'hold'
                reason = 'Maintain current allocation'
            
            recommendations.append(PortfolioRecommendation(
                symbol=symbol,
                current_weight=current_weight,
                recommended_weight=optimal_weight,
                action=action,
                reason=reason,
                expected_return=expected_returns.get(symbol, 0),
                risk_contribution=self._calculate_risk_contribution(
                    optimal_weights, risk_matrix, symbols, i
                )
            ))
        
        # Calculate optimized portfolio metrics
        optimized_return = sum(expected_returns.get(s, 0) * optimal_weights[i] for i, s in enumerate(symbols))
        optimized_risk = self._calculate_portfolio_risk(optimal_weights, risk_matrix, symbols)
        
        return {
            'current_portfolio': {
                'weights': {s: holdings[s] for s in symbols},
                'expected_return': round(current_return * 100, 2),
                'risk': round(current_risk * 100, 2),
                'sharpe_ratio': round(current_return / current_risk if current_risk > 0 else 0, 2),
            },
            'optimized_portfolio': {
                'weights': {s: round(optimal_weights[i], 3) for i, s in enumerate(symbols)},
                'expected_return': round(optimized_return * 100, 2),
                'risk': round(optimized_risk * 100, 2),
                'sharpe_ratio': round(optimized_return / optimized_risk if optimized_risk > 0 else 0, 2),
            },
            'recommendations': [r.__dict__ for r in recommendations],
            'rebalancing_needed': any(r.action != 'hold' for r in recommendations),
            'improvement': {
                'return_increase': round((optimized_return - current_return) * 100, 2),
                'risk_reduction': round((current_risk - optimized_risk) * 100, 2),
            }
        }
    
    def _simplified_risk_matrix(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """Generate simplified risk matrix based on sector assumptions"""
        # In production, this would use historical covariance
        n = len(symbols)
        matrix = {}
        
        for i, s1 in enumerate(symbols):
            matrix[s1] = {}
            for j, s2 in enumerate(symbols):
                if i == j:
                    matrix[s1][s2] = 0.25  # 25% annual volatility
                else:
                    matrix[s1][s2] = 0.05  # 5% correlation
        
        return matrix
    
    def _calculate_portfolio_risk(self, weights: np.ndarray, 
                                risk_matrix: Dict, symbols: List[str]) -> float:
        """Calculate portfolio risk (standard deviation)"""
        n = len(symbols)
        portfolio_variance = 0
        
        for i in range(n):
            for j in range(n):
                portfolio_variance += weights[i] * weights[j] * risk_matrix[symbols[i]][symbols[j]]
        
        return np.sqrt(portfolio_variance)
    
    def _calculate_risk_contribution(self, weights: np.ndarray, risk_matrix: Dict,
                                     symbols: List[str], index: int) -> float:
        """Calculate risk contribution of a single asset"""
        marginal_risk = 0
        for j in range(len(symbols)):
            marginal_risk += weights[j] * risk_matrix[symbols[index]][symbols[j]]
        
        return weights[index] * marginal_risk
    
    def _mean_variance_optimization(self, expected_returns: Dict, 
                                    risk_matrix: Dict, symbols: List[str]) -> np.ndarray:
        """
        Simplified mean-variance optimization
        In production, would use cvxpy or similar for proper optimization
        """
        n = len(symbols)
        returns = np.array([expected_returns.get(s, 0) for s in symbols])
        
        # Calculate Sharpe ratio for each asset
        risk_free_rate = 0.02  # 2% risk-free rate
        sharpe_ratios = (returns - risk_free_rate) / np.array([np.sqrt(risk_matrix[s][s]) for s in symbols])
        
        # Allocate based on Sharpe ratio (simplified)
        sharpe_ratios = np.maximum(sharpe_ratios, 0)  # Only positive Sharpe
        total_sharpe = sharpe_ratios.sum()
        
        if total_sharpe == 0:
            return np.ones(n) / n  # Equal weight if no positive Sharpe
        
        weights = sharpe_ratios / total_sharpe
        
        # Cap individual weights at 25%
        weights = np.minimum(weights, 0.25)
        
        # Re-normalize
        weights = weights / weights.sum()
        
        return weights
    
    def generate_rebalancing_plan(self, holdings: Dict[str, float],
                                  target_weights: Dict[str, float],
                                  portfolio_value: float) -> Dict:
        """
        Generate specific rebalancing trades
        
        Args:
            holdings: Current holdings {symbol: shares or weight}
            target_weights: Target weights {symbol: weight}
            portfolio_value: Total portfolio value
        """
        trades = []
        total_trade_value = 0
        
        for symbol, target_weight in target_weights.items():
            current_weight = holdings.get(symbol, 0)
            
            if isinstance(current_weight, (int, float)) and current_weight > 1:
                # If holdings are in shares, convert to weight (simplified)
                current_weight = current_weight / portfolio_value if portfolio_value > 0 else 0
            
            weight_diff = target_weight - current_weight
            trade_value = weight_diff * portfolio_value
            
            if abs(trade_value) > portfolio_value * 0.01:  # Only if > 1% of portfolio
                trades.append({
                    'symbol': symbol,
                    'action': 'buy' if trade_value > 0 else 'sell',
                    'current_weight': round(current_weight * 100, 2),
                    'target_weight': round(target_weight * 100, 2),
                    'trade_value': round(abs(trade_value), 2),
                    'trade_percentage': round(abs(weight_diff) * 100, 2),
                })
                total_trade_value += abs(trade_value)
        
        return {
            'trades': trades,
            'total_trade_value': round(total_trade_value, 2),
            'rebalancing_cost_estimate': round(total_trade_value * 0.001, 2),  # 0.1% trading cost
            'rebalancing_needed': len(trades) > 0,
        }
    
    def assess_diversification(self, holdings: Dict[str, float], 
                             sectors: Dict[str, str]) -> Dict:
        """
        Assess portfolio diversification across sectors
        
        Args:
            holdings: Current holdings {symbol: weight}
            sectors: Symbol to sector mapping {symbol: sector}
        """
        sector_weights = {}
        
        for symbol, weight in holdings.items():
            sector = sectors.get(symbol, 'Other')
            sector_weights[sector] = sector_weights.get(sector, 0) + weight
        
        # Calculate concentration metrics
        max_sector_weight = max(sector_weights.values()) if sector_weights else 0
        herfindahl_index = sum(w**2 for w in sector_weights.values())
        
        # Diversification score (0 = concentrated, 1 = diversified)
        n_sectors = len(sector_weights)
        diversification_score = 1 - herfindahl_index if n_sectors > 0 else 0
        
        return {
            'sector_weights': {k: round(v * 100, 2) for k, v in sector_weights.items()},
            'number_of_sectors': n_sectors,
            'max_sector_weight': round(max_sector_weight * 100, 2),
            'herfindahl_index': round(herfindahl_index, 3),
            'diversification_score': round(diversification_score, 3),
            'assessment': self._interpret_diversification(diversification_score, max_sector_weight),
        }
    
    def _interpret_diversification(self, score: float, max_weight: float) -> str:
        """Interpret diversification metrics"""
        if score > 0.8 and max_weight < 0.3:
            return 'Well diversified'
        elif score > 0.6 and max_weight < 0.4:
            return 'Moderately diversified'
        elif score > 0.4:
            return 'Somewhat concentrated'
        else:
            return 'Highly concentrated - consider diversification'
