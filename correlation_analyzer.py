import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class CorrelationPair:
    """Represents correlation between two assets"""
    asset1: str
    asset2: str
    correlation: float
    interpretation: str

class CorrelationAnalyzer:
    """
    Cross-asset correlation matrix analysis
    
    Analyzes relationships between:
    - Equities
    - Bonds
    - Commodities
    - Crypto
    - Forex
    """
    
    def __init__(self):
        self.default_universe = {
            # Equities
            'SPY': 'S&P 500 ETF',
            'QQQ': 'NASDAQ ETF',
            'IWM': 'Russell 2000 ETF',
            
            # Bonds
            'TLT': '20+ Year Treasury',
            'IEF': '7-10 Year Treasury',
            'LQD': 'Investment Grade Corporate',
            
            # Commodities
            'GLD': 'Gold',
            'USO': 'Oil',
            'SLV': 'Silver',
            
            # Crypto
            'BTC-USD': 'Bitcoin',
            
            # Forex
            'DX-Y.NYB': 'US Dollar Index',
        }
    
    def calculate_correlation_matrix(self, assets: List[str] = None,
                                   period: str = '1y') -> Dict:
        """
        Calculate correlation matrix for asset universe
        
        Args:
            assets: List of asset tickers (uses default if None)
            period: Time period for correlation calculation
        """
        if assets is None:
            assets = list(self.default_universe.keys())
        
        # Fetch price data
        price_data = {}
        for asset in assets:
            try:
                ticker = yf.Ticker(asset)
                hist = ticker.history(period=period)
                if not hist.empty:
                    price_data[asset] = hist['Close']
            except:
                continue
        
        if len(price_data) < 2:
            return {'error': 'Insufficient data for correlation analysis'}
        
        # Create DataFrame and calculate returns
        df = pd.DataFrame(price_data)
        returns = df.pct_change().dropna()
        
        # Calculate correlation matrix
        correlation_matrix = returns.corr()
        
        # Generate insights
        insights = self._generate_correlation_insights(correlation_matrix)
        
        # Identify key relationships
        key_relationships = self._identify_key_relationships(correlation_matrix)
        
        return {
            'correlation_matrix': correlation_matrix.round(3).to_dict(),
            'insights': insights,
            'key_relationships': key_relationships,
            'period': period,
            'assets_analyzed': list(correlation_matrix.columns)
        }
    
    def _generate_correlation_insights(self, corr_matrix: pd.DataFrame) -> Dict:
        """Generate insights from correlation matrix"""
        insights = {
            'average_correlation': round(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean(), 3),
            'highest_correlation': None,
            'lowest_correlation': None,
            'diversification_opportunities': [],
            'concentration_risks': []
        }
        
        # Find highest and lowest correlations
        correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                asset1 = corr_matrix.columns[i]
                asset2 = corr_matrix.columns[j]
                corr = corr_matrix.iloc[i, j]
                correlations.append((asset1, asset2, corr))
        
        correlations.sort(key=lambda x: abs(x[2]), reverse=True)
        
        if correlations:
            insights['highest_correlation'] = {
                'assets': (correlations[0][0], correlations[0][1]),
                'correlation': round(correlations[0][2], 3),
                'interpretation': self._interpret_correlation(correlations[0][2])
            }
            
            insights['lowest_correlation'] = {
                'assets': (correlations[-1][0], correlations[-1][1]),
                'correlation': round(correlations[-1][2], 3),
                'interpretation': self._interpret_correlation(correlations[-1][2])
            }
        
        # Identify diversification opportunities (low correlation)
        diversification = [c for c in correlations if abs(c[2]) < 0.3]
        insights['diversification_opportunities'] = [
            {'assets': (d[0], d[1]), 'correlation': round(d[2], 3)}
            for d in diversification[:5]
        ]
        
        # Identify concentration risks (high correlation)
        concentration = [c for c in correlations if abs(c[2]) > 0.8]
        insights['concentration_risks'] = [
            {'assets': (c[0], c[1]), 'correlation': round(c[2], 3)}
            for c in concentration[:5]
        ]
        
        return insights
    
    def _interpret_correlation(self, corr: float) -> str:
        """Interpret correlation coefficient"""
        abs_corr = abs(corr)
        if abs_corr > 0.8:
            strength = 'very strong'
        elif abs_corr > 0.6:
            strength = 'strong'
        elif abs_corr > 0.4:
            strength = 'moderate'
        elif abs_corr > 0.2:
            strength = 'weak'
        else:
            strength = 'very weak'
        
        direction = 'positive' if corr > 0 else 'negative'
        return f"{strength} {direction} correlation"
    
    def _identify_key_relationships(self, corr_matrix: pd.DataFrame) -> List[Dict]:
        """Identify key cross-asset relationships"""
        relationships = []
        
        # Check specific important pairs
        key_pairs = [
            ('SPY', 'TLT', 'Stocks vs Bonds'),
            ('SPY', 'GLD', 'Stocks vs Gold'),
            ('SPY', 'BTC-USD', 'Stocks vs Crypto'),
            ('DX-Y.NYB', 'GLD', 'USD vs Gold'),
            ('TLT', 'GLD', 'Bonds vs Gold'),
        ]
        
        for asset1, asset2, description in key_pairs:
            if asset1 in corr_matrix.columns and asset2 in corr_matrix.columns:
                corr = corr_matrix.loc[asset1, asset2]
                relationships.append({
                    'pair': description,
                    'assets': (asset1, asset2),
                    'correlation': round(corr, 3),
                    'interpretation': self._interpret_cross_asset_relationship(asset1, asset2, corr)
                })
        
        return relationships
    
    def _interpret_cross_asset_relationship(self, asset1: str, asset2: str, 
                                          corr: float) -> str:
        """Interpret specific cross-asset relationship"""
        if 'SPY' in asset1 or 'SPY' in asset2:
            if 'TLT' in asset1 or 'TLT' in asset2:
                if corr < -0.5:
                    return "Strong inverse relationship - flight to safety during stress"
                elif corr < 0:
                    return "Moderate inverse relationship - diversification benefit"
                else:
                    return "Low correlation - potential diversification"
            
            elif 'GLD' in asset1 or 'GLD' in asset2:
                if corr < 0:
                    return "Inverse relationship - gold as hedge"
                else:
                    return "Positive correlation - risk-on behavior"
            
            elif 'BTC' in asset1 or 'BTC' in asset2:
                if corr > 0.5:
                    return "Strong positive correlation - crypto as risk asset"
                else:
                    return "Low correlation - diversification potential"
        
        elif 'DX-Y.NYB' in asset1 or 'DX-Y.NYB' in asset2:
            if 'GLD' in asset1 or 'GLD' in asset2:
                if corr < -0.5:
                    return "Strong inverse relationship - USD strength hurts gold"
                else:
                    return "Weak relationship"
        
        return f"Correlation of {corr:.3f}"
    
    def analyze_rolling_correlation(self, asset1: str, asset2: str,
                                   window: int = 60) -> Dict:
        """
        Analyze rolling correlation between two assets
        
        Args:
            asset1: First asset ticker
            asset2: Second asset ticker
            window: Rolling window in days
        """
        try:
            # Fetch data
            data1 = yf.Ticker(asset1).history(period="2y")['Close']
            data2 = yf.Ticker(asset2).history(period="2y")['Close']
            
            if data1.empty or data2.empty:
                return {'error': 'Insufficient data'}
            
            # Align dates
            common_dates = data1.index.intersection(data2.index)
            data1_aligned = data1[common_dates]
            data2_aligned = data2[common_dates]
            
            # Calculate rolling correlation
            rolling_corr = data1_aligned.rolling(window).corr(data2_aligned)
            
            # Calculate statistics
            current_corr = float(rolling_corr.iloc[-1]) if not rolling_corr.empty else 0.0
            avg_corr = float(rolling_corr.mean()) if not rolling_corr.empty else 0.0
            std_corr = float(rolling_corr.std()) if not rolling_corr.empty else 0.0
            
            # Detect regime changes
            regime_changes = self._detect_regime_changes(rolling_corr)
            
            return {
                'asset1': asset1,
                'asset2': asset2,
                'current_correlation': round(current_corr, 3),
                'average_correlation': round(avg_corr, 3),
                'volatility_of_correlation': round(std_corr, 3),
                'trend': 'increasing' if rolling_corr.iloc[-1] > rolling_corr.iloc[-20] else 'decreasing',
                'regime_changes': regime_changes,
                'interpretation': self._interpret_rolling_correlation(current_corr, avg_corr)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _detect_regime_changes(self, rolling_corr: pd.Series) -> List[Dict]:
        """Detect significant changes in correlation regime"""
        changes = []
        threshold = 2  # Standard deviations
        
        mean = rolling_corr.mean()
        std = rolling_corr.std()
        
        for i in range(1, len(rolling_corr)):
            if abs(rolling_corr.iloc[i] - rolling_corr.iloc[i-1]) > threshold * std:
                changes.append({
                    'date': rolling_corr.index[i].strftime('%Y-%m-%d'),
                    'from': round(rolling_corr.iloc[i-1], 3),
                    'to': round(rolling_corr.iloc[i], 3),
                    'magnitude': round(rolling_corr.iloc[i] - rolling_corr.iloc[i-1], 3)
                })
        
        return changes[-5:]  # Last 5 changes
    
    def _interpret_rolling_correlation(self, current: float, average: float) -> str:
        """Interpret rolling correlation"""
        diff = current - average
        
        if abs(diff) < 0.1:
            return f"Correlation stable around {average:.3f}"
        elif diff > 0.2:
            return f"Correlation increasing significantly above average - potential regime shift"
        elif diff < -0.2:
            return f"Correlation decreasing significantly below average - potential regime shift"
        elif diff > 0:
            return f"Correlation moderately above average"
        else:
            return f"Correlation moderately below average"
    
    def assess_portfolio_diversification(self, holdings: Dict[str, float],
                                        period: str = '1y') -> Dict:
        """
        Assess portfolio diversification based on correlations
        
        Args:
            holdings: {asset: weight}
            period: Time period for correlation calculation
        """
        assets = list(holdings.keys())
        if len(assets) < 2:
            return {'error': 'Need at least 2 assets for diversification analysis'}
        
        # Calculate correlation matrix
        corr_result = self.calculate_correlation_matrix(assets, period)
        
        if 'error' in corr_result:
            return corr_result
        
        corr_matrix = pd.DataFrame(corr_result['correlation_matrix'])
        
        # Calculate portfolio correlation (weighted average)
        portfolio_corr = 0
        n = len(assets)
        
        for i in range(n):
            for j in range(i+1, n):
                weight_i = holdings[assets[i]]
                weight_j = holdings[assets[j]]
                corr = corr_matrix.iloc[i, j]
                portfolio_corr += 2 * weight_i * weight_j * corr
        
        # Diversification ratio
        diversification_ratio = 1 - portfolio_corr
        
        # Concentration risk
        max_weight = max(holdings.values())
        herfindahl = sum(w**2 for w in holdings.values())
        
        return {
            'portfolio_correlation': round(portfolio_corr, 3),
            'diversification_ratio': round(diversification_ratio, 3),
            'max_weight': round(max_weight, 3),
            'herfindahl_index': round(herfindahl, 3),
            'diversification_assessment': self._assess_diversification(
                diversification_ratio, herfindahl
            ),
            'recommendations': self._get_diversification_recommendations(
                diversification_ratio, corr_matrix, holdings
            )
        }
    
    def _assess_diversification(self, div_ratio: float, herfindahl: float) -> str:
        """Assess overall diversification"""
        if div_ratio > 0.7 and herfindahl < 0.2:
            return "Well diversified with low concentration risk"
        elif div_ratio > 0.5 and herfindahl < 0.3:
            return "Moderately diversified"
        elif div_ratio > 0.3:
            return "Somewhat concentrated"
        else:
            return "Highly concentrated - consider diversification"
    
    def _get_diversification_recommendations(self, div_ratio: float,
                                           corr_matrix: pd.DataFrame,
                                           holdings: Dict) -> List[str]:
        """Get diversification recommendations"""
        recommendations = []
        
        if div_ratio < 0.5:
            recommendations.append("Consider adding low-correlation assets")
        
        max_weight = max(holdings.values())
        if max_weight > 0.4:
            recommendations.append("Consider reducing largest position concentration")
        
        # Check for highly correlated pairs
        assets = list(holdings.keys())
        for i in range(len(assets)):
            for j in range(i+1, len(assets)):
                corr = corr_matrix.iloc[i, j]
                if corr > 0.8:
                    recommendations.append(
                        f"High correlation between {assets[i]} and {assets[j]} - consider reducing overlap"
                    )
        
        if not recommendations:
            recommendations.append("Portfolio appears well-diversified")
        
        return recommendations
