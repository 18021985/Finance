from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Scenario:
    """Represents a forward-looking scenario"""
    name: str
    probability: float  # 0-1
    description: str
    trigger_conditions: List[str]
    asset_implications: Dict[str, str]  # asset_class -> expected outcome
    time_horizon: str
    confidence: float  # 0-1

@dataclass
class ScenarioOutcome:
    """Outcome of scenario analysis"""
    base_case: Scenario
    bull_case: Scenario
    bear_case: Scenario
    recommended_positioning: str
    key_monitoring_points: List[str]

class ScenarioAnalyzer:
    """
    Scenario analysis engine for forward-looking insights
    
    Generates IF-THEN scenarios:
    - IF inflation rises → THEN bonds fall, USD rises
    - IF recession hits → THEN defensive assets outperform
    - IF rates cut → THEN growth stocks benefit
    """
    
    def __init__(self):
        pass
    
    def generate_scenarios(self, asset: str, current_context: Dict) -> ScenarioOutcome:
        """
        Generate scenarios for a specific asset
        
        Args:
            asset: Asset ticker
            current_context: Current macro and market context
        """
        # Determine asset class
        asset_class = self._classify_asset(asset)
        
        # Generate base, bull, and bear cases
        base_case = self._generate_base_case(asset, asset_class, current_context)
        bull_case = self._generate_bull_case(asset, asset_class, current_context)
        bear_case = self._generate_bear_case(asset, asset_class, current_context)
        
        # Generate positioning recommendation
        positioning = self._generate_positioning_recommendation(
            base_case, bull_case, bear_case
        )
        
        # Identify key monitoring points
        monitoring_points = self._identify_monitoring_points(asset, asset_class)
        
        return ScenarioOutcome(
            base_case=base_case,
            bull_case=bull_case,
            bear_case=bear_case,
            recommended_positioning=positioning,
            key_monitoring_points=monitoring_points
        )
    
    def _classify_asset(self, asset: str) -> str:
        """Classify asset into category"""
        if asset in ['BTC-USD', 'ETH-USD']:
            return 'crypto'
        elif asset in ['GLD', 'SLV', 'USO']:
            return 'commodity'
        elif asset in ['TLT', 'IEF', 'LQD']:
            return 'bond'
        elif '=' in asset:
            return 'forex'
        else:
            return 'equity'
    
    def _generate_base_case(self, asset: str, asset_class: str, 
                           context: Dict) -> Scenario:
        """Generate base case scenario (most likely)"""
        
        scenarios = {
            'equity': Scenario(
                name='Base Case: Moderate Growth',
                probability=0.50,
                description='Economic growth continues at moderate pace, inflation stabilizes',
                trigger_conditions=[
                    'GDP growth 2-3%',
                    'Inflation 2-3%',
                    'Central banks hold rates steady'
                ],
                asset_implications={
                    'equities': 'Modest gains with rotation to quality',
                    'bonds': 'Flat to slightly positive',
                    'commodities': 'Mixed performance',
                    'crypto': 'Stable to modest upside',
                    'forex': 'Range-bound with slight USD strength'
                },
                time_horizon='12 months',
                confidence=0.60
            ),
            'bond': Scenario(
                name='Base Case: Stable Rates',
                probability=0.50,
                description='Interest rates remain stable with gradual adjustments',
                trigger_conditions=[
                    'Fed funds rate 5.0-5.5%',
                    'Yield curve flattens gradually',
                    'Inflation moderates to 2.5%'
                ],
                asset_implications={
                    'bonds': 'Modest total return from yield',
                    'equities': 'Selective opportunities',
                    'duration_risk': 'Moderate'
                },
                time_horizon='12 months',
                confidence=0.60
            ),
            'commodity': Scenario(
                name='Base Case: Balanced Supply/Demand',
                probability=0.50,
                description='Supply and demand in balance, moderate price movement',
                trigger_conditions=[
                    'Global growth 2.5%',
                    'Stable inventories',
                    'No major supply disruptions'
                ],
                asset_implications={
                    'commodities': 'Range-bound with trend following growth',
                    'inflation_hedge': 'Moderate effectiveness'
                },
                time_horizon='12 months',
                confidence=0.55
            ),
            'crypto': Scenario(
                name='Base Case: Gradual Adoption',
                probability=0.50,
                description='Institutional adoption continues, regulatory clarity improves',
                trigger_conditions=[
                    'ETF approvals expand',
                    'Regulatory framework clarifies',
                    'Institutional inflows moderate'
                ],
                asset_implications={
                    'crypto': 'Gradual appreciation with high volatility',
                    'correlation': 'Moderating with equities'
                },
                time_horizon='12 months',
                confidence=0.50
            ),
            'forex': Scenario(
                name='Base Case: Divergent Central Bank Policies',
                probability=0.50,
                description='Central banks follow divergent paths based on local conditions',
                trigger_conditions=[
                    'Fed holds steady',
                    'ECB potentially cuts',
                    'BOJ maintains ultra-loose policy'
                ],
                asset_implications={
                    'forex': 'Currency pairs reflect rate differentials',
                    'carry_trades': 'Selective opportunities'
                },
                time_horizon='12 months',
                confidence=0.55
            )
        }
        
        return scenarios.get(asset_class, scenarios['equity'])
    
    def _generate_bull_case(self, asset: str, asset_class: str,
                           context: Dict) -> Scenario:
        """Generate bull case scenario (optimistic)"""
        
        scenarios = {
            'equity': Scenario(
                name='Bull Case: Soft Landing',
                probability=0.30,
                description='Inflation moderates without recession, growth accelerates',
                trigger_conditions=[
                    'Inflation falls below 2.5%',
                    'GDP growth 3%+',
                    'Central banks begin cutting rates'
                ],
                asset_implications={
                    'equities': 'Strong rally, cyclical outperformance',
                    'bonds': 'Positive from rate cuts',
                    'commodities': 'Bullish on growth',
                    'crypto': 'Strong risk-on performance',
                    'forex': 'Emerging market strength'
                },
                time_horizon='12-18 months',
                confidence=0.40
            ),
            'bond': Scenario(
                name='Bull Case: Rate Cuts',
                probability=0.30,
                description='Aggressive rate cuts due to economic slowdown',
                trigger_conditions=[
                    'Fed cuts rates 100+ bps',
                    'Recession concerns rise',
                    'Yield curve steepens'
                ],
                asset_implications={
                    'bonds': 'Strong capital gains from duration',
                    'credit_risk': 'Rising in corporates'
                },
                time_horizon='12 months',
                confidence=0.45
            ),
            'commodity': Scenario(
                name='Bull Case: Supply Constraints',
                probability=0.30,
                description='Supply disruptions meet strong demand',
                trigger_conditions=[
                    'Geopolitical tensions rise',
                    'Production disruptions',
                    'Strong demand from emerging markets'
                ],
                asset_implications={
                    'commodities': 'Strong upside, especially energy and metals',
                    'inflation_hedge': 'Highly effective'
                },
                time_horizon='12-24 months',
                confidence=0.40
            ),
            'crypto': Scenario(
                name='Bull Case: Mainstream Adoption',
                probability=0.30,
                description='Mass adoption, regulatory approval, institutional flood',
                trigger_conditions=[
                    'Major sovereign adoption',
                    'Full regulatory clarity',
                    'Traditional finance integration'
                ],
                asset_implications={
                    'crypto': 'Parabolic upside potential',
                    'volatility': 'Remains high but with upward bias'
                },
                time_horizon='12-24 months',
                confidence=0.35
            ),
            'forex': Scenario(
                name='Bull Case: USD Weakness',
                probability=0.30,
                description='Fed cuts while others hold, global growth recovers',
                trigger_conditions=[
                    'Fed cuts aggressively',
                    'Global growth outperforms US',
                    'Risk-on sentiment dominates'
                ],
                asset_implications={
                    'forex': 'Emerging market and commodity currencies outperform',
                    'carry_trades': 'Attractive opportunities'
                },
                time_horizon='12 months',
                confidence=0.40
            )
        }
        
        return scenarios.get(asset_class, scenarios['equity'])
    
    def _generate_bear_case(self, asset: str, asset_class: str,
                           context: Dict) -> Scenario:
        """Generate bear case scenario (pessimistic)"""
        
        scenarios = {
            'equity': Scenario(
                name='Bear Case: Hard Landing',
                probability=0.20,
                description='Recession hits, earnings collapse, risk aversion spikes',
                trigger_conditions=[
                    'GDP contraction',
                    'Unemployment rises above 6%',
                    'Corporate earnings decline 15%+'
                ],
                asset_implications={
                    'equities': 'Significant drawdown, defensive outperforms',
                    'bonds': 'Strong flight to safety',
                    'commodities': 'Demand destruction',
                    'crypto': 'Severe drawdown',
                    'forex': 'USD safe haven strength'
                },
                time_horizon='12-18 months',
                confidence=0.35
            ),
            'bond': Scenario(
                name='Bear Case: Rising Rates',
                probability=0.20,
                description='Inflation persists, rates rise further',
                trigger_conditions=[
                    'Inflation remains above 4%',
                    'Fed hikes to 6%+',
                    'Wage-price spiral'
                ],
                asset_implications={
                    'bonds': 'Significant duration losses',
                    'credit_risk': 'Rising stress in high yield'
                },
                time_horizon='12 months',
                confidence=0.40
            ),
            'commodity': Scenario(
                name='Bear Case: Demand Destruction',
                probability=0.20,
                description='Global recession crushes demand',
                trigger_conditions=[
                    'Global recession',
                    'Industrial production declines',
                    'Inventory buildup'
                ],
                asset_implications={
                    'commodities': 'Significant downside, especially cyclical',
                    'inflation_hedge': 'Limited effectiveness in deflation'
                },
                time_horizon='12-24 months',
                confidence=0.45
            ),
            'crypto': Scenario(
                name='Bear Case: Regulatory Crackdown',
                probability=0.20,
                description='Severe regulation, institutional retreat',
                trigger_conditions=[
                    'Major regulatory restrictions',
                    'Institutional exodus',
                    'Security breaches or failures'
                ],
                asset_implications={
                    'crypto': 'Severe and prolonged drawdown',
                    'adoption': 'Stalls or reverses'
                },
                time_horizon='12-24 months',
                confidence=0.40
            ),
            'forex': Scenario(
                name='Bear Case: USD Strength',
                probability=0.20,
                description='US outperforms, safe haven flows',
                trigger_conditions=[
                    'Global recession',
                    'US relative outperformance',
                    'Risk-off sentiment'
                ],
                asset_implications={
                    'forex': 'USD dominance, emerging market weakness',
                    'carry_trades': 'Unwind rapidly'
                },
                time_horizon='12 months',
                confidence=0.45
            )
        }
        
        return scenarios.get(asset_class, scenarios['equity'])
    
    def _generate_positioning_recommendation(self, base_case: Scenario,
                                           bull_case: Scenario,
                                           bear_case: Scenario) -> str:
        """Generate strategic positioning recommendation"""
        
        # Weighted expected outcome
        expected_outcome = (
            base_case.probability * 0 +
            bull_case.probability * 1 +
            bear_case.probability * -1
        )
        
        if expected_outcome > 0.3:
            return "Consider overweight position with risk management"
        elif expected_outcome > 0.1:
            return "Consider moderate exposure with selective entry"
        elif expected_outcome > -0.1:
            return "Maintain neutral allocation, monitor for signals"
        elif expected_outcome > -0.3:
            return "Consider underweight or defensive positioning"
        else:
            return "Avoid or minimize exposure, focus on capital preservation"
    
    def _identify_monitoring_points(self, asset: str, asset_class: str) -> List[str]:
        """Identify key points to monitor"""
        
        monitoring_points = {
            'equity': [
                'Earnings growth trends',
                'Valuation multiples vs historical',
                'Interest rate sensitivity',
                'Sector rotation patterns',
                'Insider trading activity'
            ],
            'bond': [
                'Yield curve dynamics',
                'Inflation data (CPI, PPI)',
                'Central bank policy statements',
                'Credit spreads',
                'Duration positioning'
            ],
            'commodity': [
                'Supply chain disruptions',
                'Inventory levels',
                'Geopolitical tensions',
                'Chinese demand indicators',
                'Weather patterns (for agriculture)'
            ],
            'crypto': [
                'Regulatory developments',
                'Institutional flow data',
                'On-chain metrics',
                'Correlation with risk assets',
                'Technical support levels'
            ],
            'forex': [
                'Central bank policy divergence',
                'Relative economic data',
                'Risk sentiment indicators',
                'Trade balance data',
                'Political developments'
            ]
        }
        
        return monitoring_points.get(asset_class, monitoring_points['equity'])
    
    def generate_macro_scenarios(self) -> List[Scenario]:
        """
        Generate macro-level scenarios affecting all assets
        
        Returns:
            List of macro scenarios with cross-asset implications
        """
        scenarios = []
        
        # Scenario 1: Disinflation
        scenarios.append(Scenario(
            name='Disinflation',
            probability=0.40,
            description='Inflation moderates steadily without recession',
            trigger_conditions=[
                'CPI declining to 2-2.5%',
                'Wage growth moderating',
                'Supply chains normalizing'
            ],
            asset_implications={
                'equities': 'Bullish, especially growth and duration-sensitive',
                'bonds': 'Bullish from rate cut expectations',
                'commodities': 'Bearish to neutral (inflation hedge less needed)',
                'crypto': 'Bullish (risk-on, lower discount rates)',
                'forex': 'Bearish USD (rate cut expectations)',
                'strategy': 'Growth tilt, duration extension'
            },
            time_horizon='12-18 months',
            confidence=0.60
        ))
        
        # Scenario 2: Stagflation
        scenarios.append(Scenario(
            name='Stagflation',
            probability=0.15,
            description='High inflation with low growth',
            trigger_conditions=[
                'Inflation above 4%',
                'GDP growth below 1%',
                'Wage-price spiral'
            ],
            asset_implications={
                'equities': 'Bearish (valuation pressure, weak earnings)',
                'bonds': 'Bearish (rising yields, inflation erosion)',
                'commodities': 'Bullish (inflation hedge)',
                'crypto': 'Mixed (inflation hedge vs risk-off)',
                'forex': 'Bullish USD (safe haven)',
                'strategy': 'Real assets, defensive equities, short duration'
            },
            time_horizon='12-24 months',
            confidence=0.35
        ))
        
        # Scenario 3: Growth Scare
        scenarios.append(Scenario(
            name='Growth Scare',
            probability=0.25,
            description='Temporary growth slowdown, inflation remains',
            trigger_conditions=[
                'GDP growth slows to 1-2%',
                'Inflation remains 3-4%',
                'Consumer spending weakens'
            ],
            asset_implications={
                'equities': 'Volatile, rotation to quality',
                'bonds': 'Mixed (flight to safety vs inflation)',
                'commodities': 'Bearish (demand weakness)',
                'crypto': 'Bearish (risk-off)',
                'forex': 'Bullish USD (safe haven)',
                'strategy': 'Quality focus, defensive positioning'
            },
            time_horizon='6-12 months',
            confidence=0.50
        ))
        
        # Scenario 4: Policy Error
        scenarios.append(Scenario(
            name='Policy Error',
            probability=0.10,
            description='Central banks overtighten, causing recession',
            trigger_conditions=[
                'Rates raised too high',
                'Credit conditions tighten sharply',
                'Liquidity stress emerges'
            ],
            asset_implications={
                'equities': 'Bearish (recession risk)',
                'bonds': 'Bullish (eventual rate cuts, flight to safety)',
                'commodities': 'Bearish (demand destruction)',
                'crypto': 'Bearish (liquidity withdrawal)',
                'forex': 'Mixed (USD safe haven vs rate cuts)',
                'strategy': 'High quality bonds, defensive equities, cash'
            },
            time_horizon='12-18 months',
            confidence=0.30
        ))
        
        # Scenario 5: Supply-Driven Inflation
        scenarios.append(Scenario(
            name='Supply-Driven Inflation',
            probability=0.10,
            description='Supply shocks drive inflation higher',
            trigger_conditions=[
                'Energy price spikes',
                'Geopolitical disruptions',
                'Supply chain bottlenecks'
            ],
            asset_implications={
                'equities': 'Mixed (inflation vs margin pressure)',
                'bonds': 'Bearish (rising yields)',
                'commodities': 'Bullish (especially energy)',
                'crypto': 'Mixed (inflation hedge vs risk-off)',
                'forex': 'Bullish commodity currencies',
                'strategy': 'Commodities, energy equities, TIPS'
            },
            time_horizon='6-12 months',
            confidence=0.35
        ))
        
        return scenarios
    
    def get_scenario_probability_matrix(self) -> Dict:
        """
        Get probability matrix for scenario combinations
        
        Returns:
            Cross-asset scenario probabilities
        """
        return {
            'disinflation': {
                'probability': 0.40,
                'equities': 'bullish',
                'bonds': 'bullish',
                'commodities': 'bearish',
                'crypto': 'bullish',
                'usd': 'bearish'
            },
            'stagflation': {
                'probability': 0.15,
                'equities': 'bearish',
                'bonds': 'bearish',
                'commodities': 'bullish',
                'crypto': 'neutral',
                'usd': 'bullish'
            },
            'growth_scare': {
                'probability': 0.25,
                'equities': 'neutral',
                'bonds': 'neutral',
                'commodities': 'bearish',
                'crypto': 'bearish',
                'usd': 'bullish'
            },
            'policy_error': {
                'probability': 0.10,
                'equities': 'bearish',
                'bonds': 'bullish',
                'commodities': 'bearish',
                'crypto': 'bearish',
                'usd': 'neutral'
            },
            'supply_shock': {
                'probability': 0.10,
                'equities': 'neutral',
                'bonds': 'bearish',
                'commodities': 'bullish',
                'crypto': 'neutral',
                'usd': 'neutral'
            }
        }
