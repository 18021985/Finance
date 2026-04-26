from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class GeopoliticalEvent:
    """Represents a geopolitical event"""
    title: str
    region: str
    impact_level: str  # low, medium, high, critical
    event_type: str  # trade, diplomatic, military, political, economic
    description: str
    affected_markets: List[str]
    timestamp: datetime

class GeopoliticalRiskAnalyzer:
    """
    Analyzes geopolitical risks and their impact on financial markets
    
    Categories:
    - Trade disputes and tariffs
    - Diplomatic tensions
    - Military conflicts
    - Political instability
    - Economic sanctions
    """
    
    def __init__(self):
        self.risk_factors = {
            'trade': {
                'us_china_tech': {'level': 'high', 'impact': ['technology', 'semiconductors']},
                'brexit': {'level': 'medium', 'impact': ['european_stocks', 'gbp']},
                'supply_chain': {'level': 'medium', 'impact': ['manufacturing', 'logistics']},
            },
            'diplomatic': {
                'nato_expansion': {'level': 'medium', 'impact': ['defense', 'energy']},
                'sanctions': {'level': 'high', 'impact': ['energy', 'commodities', 'banking']},
            },
            'military': {
                'ukraine_conflict': {'level': 'high', 'impact': ['energy', 'grains', 'defense']},
                'middle_east_tensions': {'level': 'high', 'impact': ['oil', 'defense']},
            },
            'political': {
                'us_election': {'level': 'medium', 'impact': ['all_sectors']},
                'eu_stability': {'level': 'low', 'impact': ['european_stocks', 'euro']},
            },
            'economic': {
                'debt_crisis': {'level': 'medium', 'impact': ['banking', 'bonds']},
                'currency_wars': {'level': 'low', 'impact': ['forex', 'emerging_markets']},
            }
        }
    
    def get_current_risks(self) -> Dict:
        """Get current geopolitical risks and their market impact"""
        risks = {
            'overall_risk_level': 'high',
            'critical_events': [],
            'risk_by_region': {},
            'market_impact': {}
        }
        
        # Aggregate risks by category
        for category, events in self.risk_factors.items():
            for event_name, event_data in events.items():
                if event_data['level'] == 'high':
                    risks['critical_events'].append({
                        'name': event_name,
                        'category': category,
                        'impact': event_data['impact']
                    })
        
        # Calculate regional risk
        risks['risk_by_region'] = {
            'europe': 'high',
            'asia_pacific': 'high',
            'middle_east': 'high',
            'north_america': 'medium',
            'emerging_markets': 'medium'
        }
        
        # Market impact assessment
        risks['market_impact'] = {
            'equities': 'negative',
            'commodities': 'positive',
            'bonds': 'mixed',
            'currencies': 'volatile',
            'sectors': {
                'energy': 'positive',
                'defense': 'positive',
                'technology': 'negative',
                'consumer_discretionary': 'negative'
            }
        }
        
        return risks
    
    def analyze_market_impact(self, event: GeopoliticalEvent) -> Dict:
        """
        Analyze the potential impact of a geopolitical event on markets
        
        Args:
            event: Geopolitical event to analyze
        """
        impact = {
            'event': event.title,
            'immediate_impact': [],
            'medium_term_impact': [],
            'long_term_impact': [],
            'recommended_actions': []
        }
        
        # Analyze based on event type
        if event.event_type == 'trade':
            impact['immediate_impact'].extend([
                'Increased volatility in affected sectors',
                'Currency fluctuations'
            ])
            impact['medium_term_impact'].extend([
                'Supply chain disruptions',
                'Pricing pressure on goods'
            ])
            impact['recommended_actions'].extend([
                'Diversify supply chain exposure',
                'Hedge currency risk',
                'Consider defensive positioning'
            ])
        
        elif event.event_type == 'military':
            impact['immediate_impact'].extend([
                'Sharp market sell-off',
                'Flight to safety (gold, bonds)',
                'Oil price spike'
            ])
            impact['medium_term_impact'].extend([
                'Defense sector rally',
                'Commodity inflation',
                'Regional market divergence'
            ])
            impact['recommended_actions'].extend([
                'Increase cash allocation',
                'Add defensive stocks',
                'Consider commodities exposure'
            ])
        
        elif event.event_type == 'diplomatic':
            impact['immediate_impact'].extend([
                'Currency volatility',
                'Sector-specific impacts'
            ])
            impact['medium_term_impact'].extend([
                'Trade flow changes',
                'Regulatory uncertainty'
            ])
            impact['recommended_actions'].extend([
                'Monitor affected regions',
                'Reduce exposure to sensitive sectors'
            ])
        
        return impact
    
    def get_risk_sentiment(self) -> Dict:
        """Get overall risk sentiment based on geopolitical factors"""
        return {
            'current_sentiment': 'cautious',
            'sentiment_trend': 'deteriorating',
            'key_risk_drivers': [
                'Ongoing military conflicts',
                'Trade tensions',
                'Political uncertainty in major economies'
            ],
            'safe_haven_assets': ['gold', 'us_treasuries', 'swiss_franc'],
            'risk_on_assets': ['emerging_markets', 'high_yield_bonds', 'technology']
        }
