from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class RiskMetrics:
    """Risk metrics for a position or portfolio"""
    position_size: float  # Percentage of portfolio
    stop_loss: float
    take_profit: float
    risk_per_trade: float  # Percentage of portfolio at risk
    reward_risk_ratio: float
    max_position_size: float
    position_limit: float

class RiskManager:
    """Risk management and position sizing"""
    
    def __init__(self):
        self.max_portfolio_risk = 0.02  # Max 2% risk per trade
        self.max_position_size = 0.25  # Max 25% of portfolio in single position
        self.max_total_exposure = 0.80  # Max 80% total market exposure
        self.target_annual_vol = 0.18  # Vol targeting baseline (18% annualized)
        self.min_risk_per_trade = 0.005  # 0.5%
        self.max_risk_per_trade = 0.03   # 3%
    
    def calculate_position_size(self, portfolio_value: float, entry_price: float,
                               stop_loss: float, confidence: float = 0.5) -> Dict:
        """
        Calculate optimal position size based on risk parameters
        
        Args:
            portfolio_value: Total portfolio value
            entry_price: Entry price per share
            stop_loss: Stop loss price per share
            confidence: Trade confidence (0-1)
        """
        # Calculate risk per share
        risk_per_share = entry_price - stop_loss
        risk_per_share_pct = (risk_per_share / entry_price) * 100
        
        # Calculate max position based on risk per trade
        max_risk_amount = portfolio_value * self.max_portfolio_risk
        max_shares_by_risk = int(max_risk_amount / risk_per_share) if risk_per_share > 0 else 0
        max_position_by_risk = (max_shares_by_risk * entry_price) / portfolio_value
        
        # Calculate max position by size limit
        max_position_by_size = self.max_position_size
        
        # Use the more conservative limit
        max_position_pct = min(max_position_by_risk, max_position_by_size)
        
        # Adjust based on confidence
        adjusted_position_pct = max_position_pct * (0.5 + confidence * 0.5)
        
        # Calculate actual position
        position_value = portfolio_value * adjusted_position_pct
        shares = int(position_value / entry_price)
        
        # Calculate actual risk
        actual_risk = (shares * risk_per_share) / portfolio_value
        
        return {
            'shares': shares,
            'position_value': round(position_value, 2),
            'position_size_pct': round(adjusted_position_pct * 100, 2),
            'risk_per_share': round(risk_per_share, 2),
            'risk_per_share_pct': round(risk_per_share_pct, 2),
            'actual_risk_pct': round(actual_risk * 100, 2),
            'max_risk_limit': round(self.max_portfolio_risk * 100, 2),
            'confidence': confidence,
        }

    def calculate_position_size_vol_target(
        self,
        portfolio_value: float,
        entry_price: float,
        stop_loss: float,
        annualized_vol: float,
        confidence: float = 0.5,
        risk_budget: Optional[float] = None,
    ) -> Dict:
        """
        Volatility targeting + risk budgeting position sizing.

        - annualized_vol: e.g., 0.25 for 25% annualized volatility
        - risk_budget: optional per-trade risk budget as fraction of portfolio (defaults to max_portfolio_risk)
        """
        # Convert annualized vol into a risk scaler (higher vol => smaller size)
        vol = max(0.05, float(annualized_vol or self.target_annual_vol))
        vol_scale = min(2.0, max(0.25, self.target_annual_vol / vol))

        base_budget = float(risk_budget) if risk_budget is not None else float(self.max_portfolio_risk)
        base_budget = max(self.min_risk_per_trade, min(self.max_risk_per_trade, base_budget))

        # Confidence adjusts budget mildly (avoid overconfidence)
        conf = max(0.05, min(0.95, float(confidence)))
        conf_scale = 0.75 + 0.5 * conf  # 0.775..1.225

        effective_budget = base_budget * vol_scale * conf_scale
        effective_budget = max(self.min_risk_per_trade, min(self.max_risk_per_trade, effective_budget))

        # Temporarily apply and reuse existing sizing logic by overriding max_portfolio_risk
        prev = self.max_portfolio_risk
        try:
            self.max_portfolio_risk = effective_budget
            out = self.calculate_position_size(portfolio_value, entry_price, stop_loss, confidence=conf)
            out["annualized_vol"] = round(vol, 4)
            out["effective_risk_budget_pct"] = round(effective_budget * 100, 3)
            out["vol_scale"] = round(vol_scale, 3)
            return out
        finally:
            self.max_portfolio_risk = prev
    
    def calculate_stop_loss(self, entry_price: float, volatility: float,
                           method: str = 'atr') -> Dict:
        """
        Calculate stop loss level
        
        Args:
            entry_price: Entry price
            volatility: Volatility measure (ATR or standard deviation)
            method: 'atr', 'percentage', 'support'
        """
        if method == 'atr':
            # ATR-based stop loss (2x ATR)
            stop_loss = entry_price - (2 * volatility)
            stop_distance_pct = (2 * volatility / entry_price) * 100
        elif method == 'percentage':
            # Fixed percentage stop loss
            stop_distance_pct = 5  # 5% stop loss
            stop_loss = entry_price * (1 - stop_distance_pct / 100)
        elif method == 'support':
            # Support-based stop loss
            stop_loss = entry_price - volatility
            stop_distance_pct = (volatility / entry_price) * 100
        else:
            stop_loss = entry_price * 0.95
            stop_distance_pct = 5
        
        return {
            'stop_loss': round(stop_loss, 2),
            'stop_distance_pct': round(stop_distance_pct, 2),
            'method': method,
        }
    
    def calculate_take_profit(self, entry_price: float, stop_loss: float,
                            reward_risk_ratio: float = 2.0) -> Dict:
        """
        Calculate take profit level based on reward:risk ratio
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            reward_risk_ratio: Desired reward:risk ratio
        """
        risk = entry_price - stop_loss
        reward = risk * reward_risk_ratio
        take_profit = entry_price + reward
        
        return {
            'take_profit': round(take_profit, 2),
            'reward': round(reward, 2),
            'risk': round(risk, 2),
            'reward_risk_ratio': reward_risk_ratio,
            'potential_return_pct': round((reward / entry_price) * 100, 2),
        }
    
    def assess_portfolio_risk(self, holdings: Dict[str, float],
                             prices: Dict[str, float],
                             volatilities: Dict[str, float]) -> Dict:
        """
        Assess overall portfolio risk
        
        Args:
            holdings: {symbol: shares}
            prices: {symbol: current_price}
            volatilities: {symbol: volatility}
        """
        total_value = sum(holdings[s] * prices[s] for s in holdings)
        position_values = {s: holdings[s] * prices[s] for s in holdings}
        
        # Calculate position sizes
        position_sizes = {s: v / total_value for s, v in position_values.items()}
        
        # Calculate portfolio volatility (simplified)
        weighted_volatility = sum(
            position_sizes[s] * volatilities.get(s, 0.2) 
            for s in holdings
        )
        
        # Calculate concentration risk
        max_position = max(position_sizes.values()) if position_sizes else 0
        herfindahl = sum(s**2 for s in position_sizes.values())
        
        # Risk assessment
        risk_level = 'low'
        if max_position > 0.3 or weighted_volatility > 0.3:
            risk_level = 'high'
        elif max_position > 0.2 or weighted_volatility > 0.2:
            risk_level = 'medium'
        
        return {
            'total_value': round(total_value, 2),
            'position_sizes': {s: round(v * 100, 2) for s, v in position_sizes.items()},
            'max_position_pct': round(max_position * 100, 2),
            'portfolio_volatility': round(weighted_volatility * 100, 2),
            'concentration_index': round(herfindahl, 3),
            'risk_level': risk_level,
            'recommendations': self._generate_risk_recommendations(
                max_position, weighted_volatility, herfindahl
            ),
        }
    
    def _generate_risk_recommendations(self, max_position: float, 
                                     volatility: float, concentration: float) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        if max_position > 0.3:
            recommendations.append(f"Reduce largest position (currently {max_position*100:.1f}%)")
        
        if volatility > 0.25:
            recommendations.append(f"Portfolio volatility is high ({volatility*100:.1f}%) - consider hedging")
        
        if concentration > 0.25:
            recommendations.append(f"High concentration (index {concentration:.2f}) - diversify")
        
        if not recommendations:
            recommendations.append("Portfolio risk levels are acceptable")
        
        return recommendations
    
    def calculate_var(self, returns: List[float], confidence: float = 0.95) -> Dict:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            returns: List of historical returns
            confidence: Confidence level (e.g., 0.95 for 95% VaR)
        """
        if not returns:
            return {'error': 'No returns data'}
        
        returns_sorted = sorted(returns)
        n = len(returns_sorted)
        index = int((1 - confidence) * n)
        
        var = returns_sorted[index]
        cvar = sum(returns_sorted[:index]) / index if index > 0 else var
        
        return {
            'var_pct': round(var * 100, 2),
            'cvar_pct': round(cvar * 100, 2),
            'confidence': confidence,
            'interpretation': f"There is a {confidence*100:.0f}% chance that losses will not exceed {abs(var)*100:.2f}%",
        }
    
    def validate_trade(self, portfolio_value: float, current_exposure: float,
                      new_position_value: float, confidence: float) -> Dict:
        """
        Validate if a new trade meets risk criteria
        
        Args:
            portfolio_value: Total portfolio value
            current_exposure: Current market exposure as percentage
            new_position_value: Value of new position
            confidence: Trade confidence
        """
        new_exposure = current_exposure + (new_position_value / portfolio_value)
        
        validation = {
            'approved': True,
            'reasons': [],
            'warnings': [],
        }
        
        # Check total exposure
        if new_exposure > self.max_total_exposure:
            validation['approved'] = False
            validation['reasons'].append(
                f"Total exposure would be {new_exposure*100:.1f}% (max: {self.max_total_exposure*100:.1f}%)"
            )
        
        # Check position size
        position_size = new_position_value / portfolio_value
        if position_size > self.max_position_size:
            validation['approved'] = False
            validation['reasons'].append(
                f"Position size would be {position_size*100:.1f}% (max: {self.max_position_size*100:.1f}%)"
            )
        
        # Check confidence
        if confidence < 0.3:
            validation['warnings'].append("Low confidence trade - consider reducing size")
        
        # Exposure warning
        if new_exposure > 0.7:
            validation['warnings'].append(f"High market exposure ({new_exposure*100:.1f}%)")
        
        return validation
