import yfinance as yf
import pandas as pd
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class SectorSignal:
    """Represents a sector rotation signal"""
    sector: str
    direction: str  # 'bullish', 'bearish', 'neutral'
    strength: float  # 0-100
    confidence: float  # 0-1
    relative_performance: float  # vs market
    recommendation: str

class SectorAnalyzer:
    """Analyzes sector performance and rotation signals"""
    
    def __init__(self):
        self.us_sectors = {
            'Technology': 'XLK',
            'Financials': 'XLF',
            'Healthcare': 'XLV',
            'Consumer Discretionary': 'XLY',
            'Consumer Staples': 'XLP',
            'Energy': 'XLE',
            'Industrials': 'XLI',
            'Materials': 'XLB',
            'Real Estate': 'XLRE',
            'Utilities': 'XLU',
            'Communication Services': 'XLC',
        }
        
        self.indian_sectors = {
            'NIFTY IT': '^CNXIT',
            'NIFTY Bank': '^NSEBANK',
            'NIFTY FMCG': '^CNXFMC',
            'NIFTY Auto': '^CNXAUTO',
            'NIFTY Pharma': '^CNXPHARMA',
            'NIFTY Metal': '^CNXMETAL',
        }
    
    def analyze_sector_rotation(self, market: str = 'US') -> Dict:
        """
        Analyze sector rotation and identify opportunities
        
        Args:
            market: 'US' or 'India'
        """
        sectors = self.us_sectors if market == 'US' else self.indian_sectors
        market_index = '^GSPC' if market == 'US' else '^NSEI'
        
        # Fetch market index
        try:
            market_ticker = yf.Ticker(market_index)
            market_hist = market_ticker.history(period="3mo")
            market_return = (market_hist['Close'].iloc[-1] / market_hist['Close'].iloc[0] - 1) * 100
        except:
            market_return = 0
        
        sector_analysis = []
        
        for sector_name, sector_symbol in sectors.items():
            try:
                ticker = yf.Ticker(sector_symbol)
                hist = ticker.history(period="3mo")
                
                if hist.empty:
                    continue
                
                # Calculate sector performance
                sector_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
                relative_performance = sector_return - market_return
                
                # Calculate momentum
                recent_trend = (hist['Close'].iloc[-1] / hist['Close'].iloc[-20] - 1) * 100 if len(hist) > 20 else 0
                
                # Generate signal
                signal = self._generate_sector_signal(
                    sector_name, sector_return, relative_performance, recent_trend
                )
                sector_analysis.append(signal)
                
            except Exception as e:
                continue
        
        # Sort by strength
        sector_analysis.sort(key=lambda x: x.strength, reverse=True)
        
        return {
            'market': market,
            'market_return': round(market_return, 2),
            'market_index': market_index,
            'sectors': [s.__dict__ for s in sector_analysis],
            'top_sectors': [s.__dict__ for s in sector_analysis[:3]],
            'bottom_sectors': [s.__dict__ for s in sector_analysis[-3:]],
            'rotation_signals': self._identify_rotation_signals(sector_analysis),
        }
    
    def _generate_sector_signal(self, sector_name: str, sector_return: float,
                               relative_performance: float, recent_trend: float) -> SectorSignal:
        """Generate sector signal based on performance metrics"""
        # Calculate strength score
        strength = 50
        
        if relative_performance > 5:
            strength += 30
        elif relative_performance > 2:
            strength += 15
        elif relative_performance < -5:
            strength -= 30
        elif relative_performance < -2:
            strength -= 15
        
        if recent_trend > 5:
            strength += 20
        elif recent_trend > 2:
            strength += 10
        elif recent_trend < -5:
            strength -= 20
        elif recent_trend < -2:
            strength -= 10
        
        strength = min(100, max(0, strength))
        
        # Determine direction
        if strength > 65:
            direction = 'bullish'
            recommendation = 'overweight'
        elif strength > 55:
            direction = 'bullish'
            recommendation = 'slightly overweight'
        elif strength < 35:
            direction = 'bearish'
            recommendation = 'underweight'
        elif strength < 45:
            direction = 'bearish'
            recommendation = 'slightly underweight'
        else:
            direction = 'neutral'
            recommendation = 'equal weight'
        
        # Confidence based on consistency
        confidence = min(1.0, abs(relative_performance) / 10 + 0.3)
        
        return SectorSignal(
            sector=sector_name,
            direction=direction,
            strength=round(strength, 1),
            confidence=round(confidence, 2),
            relative_performance=round(relative_performance, 2),
            recommendation=recommendation
        )
    
    def _identify_rotation_signals(self, sector_analysis: List[SectorSignal]) -> List[Dict]:
        """Identify sector rotation opportunities"""
        signals = []
        
        # Find sectors with improving momentum
        bullish_sectors = [s for s in sector_analysis if s.direction == 'bullish']
        bearish_sectors = [s for s in sector_analysis if s.direction == 'bearish']
        
        # Rotation from bearish to bullish sectors
        for sector in sector_analysis:
            if sector.direction == 'bullish' and sector.strength > 70:
                signals.append({
                    'type': 'rotation_into',
                    'sector': sector.sector,
                    'reason': f'Strong outperformance with {sector.strength:.0f} strength',
                    'action': 'Increase exposure'
                })
            elif sector.direction == 'bearish' and sector.strength < 30:
                signals.append({
                    'type': 'rotation_out_of',
                    'sector': sector.sector,
                    'reason': f'Weak underperformance with {sector.strength:.0f} strength',
                    'action': 'Reduce exposure'
                })
        
        return signals
    
    def compare_stocks_to_sector(self, symbol: str, sector: str, market: str = 'US') -> Dict:
        """
        Compare a stock's performance to its sector
        
        Args:
            symbol: Stock ticker
            sector: Sector name
            market: 'US' or 'India'
        """
        sectors = self.us_sectors if market == 'US' else self.indian_sectors
        sector_symbol = sectors.get(sector)
        
        if not sector_symbol:
            return {'error': f'Sector {sector} not found'}
        
        try:
            # Fetch stock data
            stock_ticker = yf.Ticker(symbol)
            stock_hist = stock_ticker.history(period="3mo")
            
            # Fetch sector data
            sector_ticker = yf.Ticker(sector_symbol)
            sector_hist = sector_ticker.history(period="3mo")
            
            if stock_hist.empty or sector_hist.empty:
                return {'error': 'Insufficient data'}
            
            # Calculate returns
            stock_return = (stock_hist['Close'].iloc[-1] / stock_hist['Close'].iloc[0] - 1) * 100
            sector_return = (sector_hist['Close'].iloc[-1] / sector_hist['Close'].iloc[0] - 1) * 100
            relative_return = stock_return - sector_return
            
            # Calculate beta (simplified)
            stock_daily = stock_hist['Close'].pct_change().dropna()
            sector_daily = sector_hist['Close'].pct_change().dropna()
            
            # Align dates
            common_dates = stock_daily.index.intersection(sector_daily.index)
            if len(common_dates) < 20:
                beta = 1.0
            else:
                stock_aligned = stock_daily[common_dates]
                sector_aligned = sector_daily[common_dates]
                covariance = stock_aligned.cov(sector_aligned)
                sector_variance = sector_aligned.var()
                beta = covariance / sector_variance if sector_variance > 0 else 1.0
            
            return {
                'symbol': symbol,
                'sector': sector,
                'stock_return_3m': round(stock_return, 2),
                'sector_return_3m': round(sector_return, 2),
                'relative_performance': round(relative_return, 2),
                'outperforming': relative_return > 0,
                'beta': round(beta, 2),
                'interpretation': self._interpret_relative_performance(relative_return, beta),
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _interpret_relative_performance(self, relative_return: float, beta: float) -> str:
        """Interpret relative performance vs sector"""
        if relative_return > 10:
            return 'Significantly outperforming sector'
        elif relative_return > 5:
            return 'Outperforming sector'
        elif relative_return > 0:
            return 'Slightly outperforming sector'
        elif relative_return > -5:
            return 'Slightly underperforming sector'
        elif relative_return > -10:
            return 'Underperforming sector'
        else:
            return 'Significantly underperforming sector'
    
    def get_sector_recommendations(self, market: str = 'US') -> Dict:
        """
        Get sector allocation recommendations based on rotation analysis
        """
        rotation = self.analyze_sector_rotation(market)
        
        recommendations = {
            'overweight': [],
            'equal_weight': [],
            'underweight': [],
        }
        
        for sector in rotation['sectors']:
            if sector['recommendation'] in ['overweight', 'slightly overweight']:
                recommendations['overweight'].append(sector)
            elif sector['recommendation'] in ['underweight', 'slightly underweight']:
                recommendations['underweight'].append(sector)
            else:
                recommendations['equal_weight'].append(sector)
        
        return {
            'market': market,
            'recommendations': recommendations,
            'allocation_strategy': self._generate_allocation_strategy(recommendations),
        }
    
    def _generate_allocation_strategy(self, recommendations: Dict) -> str:
        """Generate allocation strategy based on recommendations"""
        overweight_count = len(recommendations['overweight'])
        underweight_count = len(recommendations['underweight'])
        
        if overweight_count > 3:
            return f"Aggressive tilt toward {overweight_count} outperforming sectors"
        elif overweight_count > 1:
            return f"Moderate overweight in {overweight_count} sectors"
        elif underweight_count > 3:
            return f"Defensive stance with {underweight_count} sectors underweighted"
        else:
            return "Balanced sector allocation with no strong tilts"
