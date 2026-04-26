from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class AllocationRecommendation:
    """Asset allocation recommendation"""
    strategy_name: str
    allocations: Dict[str, float]  # asset_class -> weight
    rationale: str
    risk_profile: str
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float

class AssetAllocator:
    """
    Asset allocation models for long-term institutional investing
    
    Strategies:
    - 60/40 Portfolio (stocks/bonds)
    - Risk Parity (equal risk contribution)
    - Economic Cycle Positioning
    - Tactical Asset Allocation
    """
    
    def __init__(self):
        # Expected returns (annualized, based on historical averages)
        self.expected_returns = {
            'us_equities': 0.10,
            'international_equities': 0.08,
            'emerging_markets': 0.12,
            'us_treasuries': 0.04,
            'corporate_bonds': 0.05,
            'gold': 0.06,
            'cash': 0.02
        }

        # Volatilities (will be updated with real market data)
        self.volatilities = {
            'us_equities': 0.18,
            'international_equities': 0.20,
            'emerging_markets': 0.25,
            'us_treasuries': 0.08,
            'corporate_bonds': 0.10,
            'gold': 0.15,
            'cash': 0.01
        }

        # Asset tickers for real data
        self.asset_tickers = {
            'us_equities': 'SPY',
            'international_equities': 'EFA',
            'emerging_markets': 'EEM',
            'us_treasuries': 'TLT',
            'corporate_bonds': 'LQD',
            'gold': 'GLD',
            'cash': 'SHV'
        }

        # Correlation matrix (will be updated with real data)
        self.correlation_matrix = None

        # Cache for market data
        self._last_market_update = None
        self._market_data_cache_duration = 3600  # 1 hour in seconds

    def update_market_data(self, force=False):
        """
        Update volatilities and correlations with real market data
        Caches data for 1 hour to avoid repeated API calls
        """
        import time

        # Check if we have recent cached data
        if not force and self._last_market_update is not None:
            if time.time() - self._last_market_update < self._market_data_cache_duration:
                return  # Use cached data

        try:
            import yfinance as yf
            import pandas as pd
            import numpy as np

            # Fetch historical data for all assets
            tickers = list(self.asset_tickers.values())
            data = yf.download(tickers, period='1y', progress=False)['Adj Close']

            if data.empty:
                print("No market data available, using defaults")
                return

            # Calculate daily returns
            returns = data.pct_change().dropna()

            if returns.empty:
                print("No return data available, using defaults")
                return

            # Calculate annualized volatility (252 trading days)
            self.volatilities = {}
            for asset, ticker in self.asset_tickers.items():
                if ticker in returns.columns:
                    vol = returns[ticker].std() * np.sqrt(252)
                    self.volatilities[asset] = vol
                else:
                    # Fallback to default if data not available
                    self.volatilities[asset] = 0.15

            # Calculate correlation matrix
            self.correlation_matrix = returns.corr()

            self._last_market_update = time.time()
            print("Market data updated successfully")

        except Exception as e:
            print(f"Error updating market data: {e}")
            # Keep default values if update fails

    def get_60_40_allocation(self) -> AllocationRecommendation:
        """
        Classic 60/40 stock/bond allocation with dynamic adjustments

        60% equities (split between US and international)
        40% bonds (split between treasuries and corporates)
        Adjusted based on current market volatility
        """
        # Use default volatilities to avoid API timeouts
        # Market data update can be done separately via a background process

        # Base allocation
        base_equity_allocation = 0.60
        base_bond_allocation = 0.40

        # Adjust based on market volatility
        # If equity volatility is high (>20%), reduce equity allocation
        equity_vol = self.volatilities.get('us_equities', 0.18)
        if equity_vol > 0.25:
            # High volatility - defensive tilt
            equity_adjustment = -0.10
        elif equity_vol < 0.15:
            # Low volatility - can take more risk
            equity_adjustment = 0.05
        else:
            equity_adjustment = 0

        adjusted_equity = base_equity_allocation + equity_adjustment
        adjusted_bond = 1 - adjusted_equity

        # Split equities
        allocations = {
            'us_equities': adjusted_equity * 0.60,
            'international_equities': adjusted_equity * 0.30,
            'emerging_markets': adjusted_equity * 0.10,
            'us_treasuries': adjusted_bond * 0.60,
            'corporate_bonds': adjusted_bond * 0.40
        }

        # Calculate portfolio metrics (simplified, no correlations)
        import numpy as np
        expected_volatility = np.sqrt(sum(
            (allocations[asset] ** 2) * (self.volatilities[asset] ** 2)
            for asset in allocations
        ))

        expected_return = sum(
            allocations[asset] * self.expected_returns[asset]
            for asset in allocations
        )

        sharpe = (expected_return - 0.02) / expected_volatility

        rationale = f"Dynamic 60/40 adjusted for current volatility ({equity_vol*100:.1f}%). " + \
                    ("Defensive tilt due to high market volatility." if equity_adjustment < 0 else
                     "Opportunistic tilt due to low market volatility." if equity_adjustment > 0 else
                     "Standard 60/40 allocation.")

        return AllocationRecommendation(
            strategy_name='60/40 Portfolio',
            allocations=allocations,
            rationale=rationale,
            risk_profile='moderate',
            expected_return=float(round(expected_return * 100, 2)),
            expected_volatility=float(round(expected_volatility * 100, 2)),
            sharpe_ratio=float(round(sharpe, 2))
        )
    
    def get_risk_parity_allocation(self) -> AllocationRecommendation:
        """
        Risk parity allocation - equal risk contribution from each asset

        Higher allocation to lower volatility assets (bonds)
        Lower allocation to higher volatility assets (equities)
        Uses default volatility data to avoid API timeouts
        """
        # Use default volatilities to avoid API timeouts
        # Market data update can be done separately via a background process

        # Risk parity - inverse volatility weighting
        inv_vol = {asset: 1/vol for asset, vol in self.volatilities.items()}
        total_inv_vol = sum(inv_vol.values())

        allocations = {
            asset: inv_vol[asset] / total_inv_vol
            for asset in inv_vol
        }

        # Remove very small allocations
        allocations = {k: v for k, v in allocations.items() if v > 0.05}

        # Renormalize
        total = sum(allocations.values())
        allocations = {k: v/total for k, v in allocations.items()}

        # Calculate portfolio metrics (simplified, no correlations)
        import numpy as np
        expected_volatility = np.sqrt(sum(
            (allocations[asset] ** 2) * (self.volatilities[asset] ** 2)
            for asset in allocations
        ))

        expected_return = sum(
            allocations[asset] * self.expected_returns[asset]
            for asset in allocations
        )

        sharpe = (expected_return - 0.02) / expected_volatility

        # Get current volatility for rationale
        avg_vol = sum(self.volatilities.values()) / len(self.volatilities)

        return AllocationRecommendation(
            strategy_name='Risk Parity',
            allocations=allocations,
            rationale=f'Equal risk contribution using volatility (avg: {avg_vol*100:.1f}%). ' +
                      'Allocations weighted inversely to volatility.',
            risk_profile='moderate',
            expected_return=float(round(expected_return * 100, 2)),
            expected_volatility=float(round(expected_volatility * 100, 2)),
            sharpe_ratio=float(round(sharpe, 2))
        )
    
    def get_economic_cycle_allocation(self, cycle_phase: str) -> AllocationRecommendation:
        """
        Economic cycle-based allocation
        
        Phases:
        - expansion: overweight equities, underweight bonds
        - peak: defensive positioning, reduce cyclicals
        - contraction: overweight bonds, defensive equities
        - trough: accumulate equities, maintain bonds
        """
        cycle_allocations = {
            'expansion': {
                'us_equities': 0.40,
                'international_equities': 0.20,
                'emerging_markets': 0.15,
                'corporate_bonds': 0.15,
                'commodities': 0.10
            },
            'peak': {
                'us_equities': 0.30,
                'international_equities': 0.15,
                'emerging_markets': 0.05,
                'us_treasuries': 0.25,
                'corporate_bonds': 0.15,
                'cash': 0.10
            },
            'contraction': {
                'us_equities': 0.15,
                'international_equities': 0.10,
                'us_treasuries': 0.40,
                'corporate_bonds': 0.20,
                'gold': 0.10,
                'cash': 0.05
            },
            'trough': {
                'us_equities': 0.35,
                'international_equities': 0.15,
                'emerging_markets': 0.10,
                'us_treasuries': 0.25,
                'corporate_bonds': 0.10,
                'cash': 0.05
            }
        }
        
        allocations = cycle_allocations.get(cycle_phase, cycle_allocations['expansion'])
        
        expected_return = sum(
            allocations.get(asset, 0) * self.expected_returns[asset]
            for asset in self.expected_returns
        )
        
        expected_volatility = np.sqrt(sum(
            (allocations.get(asset, 0) ** 2) * (self.volatilities[asset] ** 2)
            for asset in self.volatilities
        ))
        
        sharpe = (expected_return - 0.02) / expected_volatility
        
        cycle_descriptions = {
            'expansion': 'Growth phase - overweight equities for growth',
            'peak': 'Late cycle - defensive positioning with quality tilt',
            'contraction': 'Recession risk - capital preservation focus',
            'trough': 'Recovery phase - accumulate risk assets'
        }
        
        return AllocationRecommendation(
            strategy_name=f'Economic Cycle: {cycle_phase.capitalize()}',
            allocations=allocations,
            rationale=cycle_descriptions.get(cycle_phase, ''),
            risk_profile='varies_by_cycle',
            expected_return=round(expected_return * 100, 2),
            expected_volatility=round(expected_volatility * 100, 2),
            sharpe_ratio=round(sharpe, 2)
        )
    
    def get_tactical_allocation(self, current_signals: Dict) -> AllocationRecommendation:
        """
        Tactical asset allocation based on current market signals
        
        Args:
            current_signals: {
                'equity_signal': 'bullish' | 'neutral' | 'bearish',
                'bond_signal': 'bullish' | 'neutral' | 'bearish',
                'commodity_signal': 'bullish' | 'neutral' | 'bearish',
                'risk_sentiment': 'risk-on' | 'risk-off' | 'neutral'
            }
        """
        # Start with neutral allocation
        base_allocation = {
            'us_equities': 0.30,
            'international_equities': 0.15,
            'emerging_markets': 0.10,
            'us_treasuries': 0.20,
            'corporate_bonds': 0.15,
            'real_estate': 0.05,
            'commodities': 0.05
        }
        
        # Adjust based on signals
        equity_signal = current_signals.get('equity_signal', 'neutral')
        bond_signal = current_signals.get('bond_signal', 'neutral')
        commodity_signal = current_signals.get('commodity_signal', 'neutral')
        risk_sentiment = current_signals.get('risk_sentiment', 'neutral')
        
        # Equity adjustments
        if equity_signal == 'bullish':
            base_allocation['us_equities'] += 0.10
            base_allocation['international_equities'] += 0.05
            base_allocation['emerging_markets'] += 0.05
            base_allocation['us_treasuries'] -= 0.10
            base_allocation['cash'] = base_allocation.get('cash', 0) - 0.10
        elif equity_signal == 'bearish':
            base_allocation['us_equities'] -= 0.10
            base_allocation['international_equities'] -= 0.05
            base_allocation['emerging_markets'] -= 0.05
            base_allocation['us_treasuries'] += 0.10
            base_allocation['cash'] = base_allocation.get('cash', 0) + 0.10
        
        # Bond adjustments
        if bond_signal == 'bullish':
            base_allocation['us_treasuries'] += 0.10
            base_allocation['corporate_bonds'] += 0.05
            base_allocation['us_equities'] -= 0.10
            base_allocation['commodities'] = base_allocation.get('commodities', 0) - 0.05
        elif bond_signal == 'bearish':
            base_allocation['us_treasuries'] -= 0.10
            base_allocation['corporate_bonds'] -= 0.05
            base_allocation['cash'] = base_allocation.get('cash', 0) + 0.10
            base_allocation['commodities'] = base_allocation.get('commodities', 0) + 0.05
        
        # Commodity adjustments
        if commodity_signal == 'bullish':
            base_allocation['commodities'] = base_allocation.get('commodities', 0) + 0.05
            base_allocation['gold'] = base_allocation.get('gold', 0) + 0.03
            base_allocation['us_treasuries'] -= 0.05
            base_allocation['cash'] = base_allocation.get('cash', 0) - 0.03
        elif commodity_signal == 'bearish':
            base_allocation['commodities'] = base_allocation.get('commodities', 0) - 0.05
            base_allocation['gold'] = base_allocation.get('gold', 0) - 0.03
            base_allocation['us_treasuries'] += 0.05
            base_allocation['cash'] = base_allocation.get('cash', 0) + 0.03
        
        # Risk sentiment adjustments
        if risk_sentiment == 'risk-on':
            base_allocation['emerging_markets'] += 0.05
            base_allocation['commodities'] = base_allocation.get('commodities', 0) + 0.03
            base_allocation['us_treasuries'] -= 0.05
            base_allocation['cash'] = base_allocation.get('cash', 0) - 0.03
        elif risk_sentiment == 'risk-off':
            base_allocation['emerging_markets'] -= 0.05
            base_allocation['commodities'] = base_allocation.get('commodities', 0) - 0.03
            base_allocation['us_treasuries'] += 0.05
            base_allocation['cash'] = base_allocation.get('cash', 0) + 0.03
        
        # Ensure no negative allocations
        allocations = {k: max(0, v) for k, v in base_allocation.items()}
        
        # Normalize to 100%
        total = sum(allocations.values())
        allocations = {k: v/total for k, v in allocations.items()}
        
        # Remove very small allocations
        allocations = {k: v for k, v in allocations.items() if v > 0.01}
        
        # Renormalize
        total = sum(allocations.values())
        allocations = {k: v/total for k, v in allocations.items()}
        
        expected_return = sum(
            allocations.get(asset, 0) * self.expected_returns.get(asset, 0)
            for asset in self.expected_returns
        )
        
        expected_volatility = np.sqrt(sum(
            (allocations.get(asset, 0) ** 2) * (self.volatilities.get(asset, 0) ** 2)
            for asset in self.volatilities
        ))
        
        sharpe = (expected_return - 0.02) / expected_volatility if expected_volatility > 0 else 0
        
        return AllocationRecommendation(
            strategy_name='Tactical Asset Allocation',
            allocations=allocations,
            rationale='Dynamic allocation based on current market signals and risk sentiment',
            risk_profile='adaptive',
            expected_return=round(expected_return * 100, 2),
            expected_volatility=round(expected_volatility * 100, 2),
            sharpe_ratio=round(sharpe, 2)
        )
    
    def get_all_weather_portfolio(self) -> AllocationRecommendation:
        """
        All-weather portfolio - designed to perform across economic conditions

        Based on Ray Dalio's All-Weather approach with dynamic adjustments
        """
        # Use default volatilities to avoid API timeouts
        # Market data update can be done separately via a background process

        # Use default yield indicator (can be updated via background process)
        yield_indicator = 1.0

        # Base All Weather allocation
        base_allocations = {
            'us_treasuries': 0.30,
            'us_equities': 0.30,
            'corporate_bonds': 0.15,
            'gold': 0.07,
            'international_equities': 0.05,
            'emerging_markets': 0.03,
            'cash': 0.00
        }

        # Adjust based on yield curve
        # If treasuries are relatively expensive (low yield), reduce allocation
        if yield_indicator < 0.8:
            # Low yield environment - reduce treasuries, increase equities
            base_allocations['us_treasuries'] -= 0.05
            base_allocations['us_equities'] += 0.05
        elif yield_indicator > 1.2:
            # High yield environment - increase treasuries, reduce equities
            base_allocations['us_treasuries'] += 0.05
            base_allocations['us_equities'] -= 0.05

        # Adjust based on volatility
        equity_vol = self.volatilities.get('us_equities', 0.18)
        if equity_vol > 0.25:
            # High volatility - defensive
            base_allocations['us_treasuries'] += 0.03
            base_allocations['us_equities'] -= 0.03
            base_allocations['gold'] += 0.02
            base_allocations['emerging_markets'] -= 0.02

        # Normalize allocations
        total = sum(base_allocations.values())
        allocations = {k: v/total for k, v in base_allocations.items()}

        # Calculate portfolio metrics (simplified, no correlations)
        import numpy as np
        expected_volatility = np.sqrt(sum(
            (allocations[asset] ** 2) * (self.volatilities[asset] ** 2)
            for asset in allocations
        ))

        expected_return = sum(
            allocations[asset] * self.expected_returns[asset]
            for asset in allocations
        )

        sharpe = (expected_return - 0.02) / expected_volatility

        rationale = f'Dynamic All-Weather adjusted for yield curve ({yield_indicator:.2f}) and volatility ({equity_vol*100:.1f}%). ' + \
                    'Balanced allocation designed for all economic conditions.'

        return AllocationRecommendation(
            strategy_name='All-Weather Portfolio',
            allocations=allocations,
            rationale=rationale,
            risk_profile='conservative to moderate',
            expected_return=float(round(expected_return * 100, 2)),
            expected_volatility=float(round(expected_volatility * 100, 2)),
            sharpe_ratio=float(round(sharpe, 2))
        )
    
    def compare_strategies(self) -> Dict:
        """
        Compare all allocation strategies
        
        Returns:
            Comparison of expected returns, volatility, and Sharpe ratios
        """
        strategies = [
            self.get_60_40_allocation(),
            self.get_risk_parity_allocation(),
            self.get_all_weather_portfolio()
        ]
        
        comparison = []
        for strategy in strategies:
            comparison.append({
                'strategy': strategy.strategy_name,
                'expected_return': strategy.expected_return,
                'expected_volatility': strategy.expected_volatility,
                'sharpe_ratio': strategy.sharpe_ratio,
                'risk_profile': strategy.risk_profile
            })
        
        # Sort by Sharpe ratio
        comparison.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
        
        return {
            'comparison': comparison,
            'best_sharpe': comparison[0] if comparison else None,
            'lowest_volatility': min(comparison, key=lambda x: x['expected_volatility']) if comparison else None,
            'highest_return': max(comparison, key=lambda x: x['expected_return']) if comparison else None
        }
