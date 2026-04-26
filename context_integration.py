from typing import Dict
import json

class ContextIntegration:
    """Integrates geopolitical and sentiment context from data files"""
    
    def __init__(self):
        self.geopolitical_factors = self._load_geopolitical_context()
        self.sentiment_rules = self._load_sentiment_rules()
    
    def _load_geopolitical_context(self) -> Dict:
        """Load geopolitical context from data/geopolitical_context.md"""
        try:
            with open('data/geopolitical_context.md', 'r') as f:
                content = f.read()
            
            # Parse the context into actionable factors
            return {
                'active_conflicts': self._assess_conflicts(),
                'trade_tensions': self._assess_trade_tensions(),
                'energy_markets': self._assess_energy_markets(),
                'central_bank_policies': self._assess_central_banks(),
                'regional_instability': self._assess_regional_stability(),
            }
        except Exception as e:
            print(f"Error loading geopolitical context: {e}")
            return self._default_geopolitical_context()
    
    def _load_sentiment_rules(self) -> Dict:
        """Load sentiment rules from data/sentiment_rules.md"""
        try:
            with open('data/sentiment_rules.md', 'r') as f:
                content = f.read()
            
            return {
                'verified_weight': 1.0,
                'questionable_weight': 0.5,
                'fake_weight': 0.15,
                'fake_news_threshold': 0.3,  # If 30%+ news is fake
            }
        except Exception as e:
            print(f"Error loading sentiment rules: {e}")
            return self._default_sentiment_rules()
    
    def _default_geopolitical_context(self) -> Dict:
        """Default geopolitical context if file not available"""
        return {
            'active_conflicts': {'level': 'low', 'impact': 0.1},
            'trade_tensions': {'level': 'low', 'impact': 0.1},
            'energy_markets': {'level': 'low', 'impact': 0.1},
            'central_bank_policies': {'level': 'neutral', 'impact': 0.0},
            'regional_instability': {'level': 'low', 'impact': 0.1},
        }
    
    def _default_sentiment_rules(self) -> Dict:
        """Default sentiment rules if file not available"""
        return {
            'verified_weight': 1.0,
            'questionable_weight': 0.5,
            'fake_weight': 0.15,
            'fake_news_threshold': 0.3,
        }
    
    def _assess_conflicts(self) -> Dict:
        """Assess active conflicts (simplified - would need news API)"""
        # Placeholder - in production, this would analyze news for conflict keywords
        return {'level': 'low', 'impact': 0.1}
    
    def _assess_trade_tensions(self) -> Dict:
        """Assess trade tensions"""
        # Placeholder
        return {'level': 'low', 'impact': 0.1}
    
    def _assess_energy_markets(self) -> Dict:
        """Assess energy market stability"""
        # Placeholder
        return {'level': 'low', 'impact': 0.1}
    
    def _assess_central_banks(self) -> Dict:
        """Assess central bank policies"""
        # Placeholder
        return {'level': 'neutral', 'impact': 0.0}
    
    def _assess_regional_stability(self) -> Dict:
        """Assess regional stability"""
        # Placeholder
        return {'level': 'low', 'impact': 0.1}
    
    def adjust_confidence_for_geopolitics(self, base_confidence: float) -> float:
        """
        Adjust signal confidence based on geopolitical context
        
        From geopolitical_context.md:
        - Adjust all signal confidence levels
        - Increase volatility assumptions
        """
        total_impact = sum(factor['impact'] for factor in self.geopolitical_factors.values())
        
        # Reduce confidence if geopolitical risk is high
        adjustment = min(0.3, total_impact * 0.5)
        adjusted_confidence = max(0.4, base_confidence - adjustment)
        
        return adjusted_confidence
    
    def adjust_sentiment_weight(self, news_item: Dict) -> float:
        """
        Adjust sentiment weight based on news credibility
        
        From sentiment_rules.md:
        - Verified → full weight
        - Questionable → 50% weight
        - Fake / hype → 10–20% weight
        """
        # Simplified - in production, would use NLP to assess credibility
        source = news_item.get('source', '').lower()
        
        if any(trusted in source for trusted in ['reuters', 'bloomberg', 'wsj', 'ft']):
            return self.sentiment_rules['verified_weight']
        elif any(questionable in source for questionable in ['blog', 'social', 'twitter']):
            return self.sentiment_rules['questionable_weight']
        else:
            return self.sentiment_rules['verified_weight']  # Default to verified
    
    def get_volatility_adjustment(self) -> float:
        """
        Get volatility adjustment based on geopolitical context
        """
        total_impact = sum(factor['impact'] for factor in self.geopolitical_factors.values())
        return min(0.5, total_impact)
    
    def get_context_summary(self) -> Dict:
        """Get summary of current context factors"""
        return {
            'geopolitical_risk': self.geopolitical_factors,
            'sentiment_rules': self.sentiment_rules,
            'volatility_adjustment': self.get_volatility_adjustment(),
        }
