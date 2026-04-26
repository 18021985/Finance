from typing import Dict, Tuple

class DecisionLogic:
    """Implements decision logic from decision_logic.md"""
    
    def __init__(self):
        pass
    
    def interpret_score(self, net_score: float, conviction: str = 'high') -> Dict:
        """
        Interpret net score into recommendation
        
        Interpretation from decision_logic.md:
        > +25 → Strong Bullish
        +10 to +25 → Bullish
        -10 to +10 → Neutral
        -10 to -25 → Bearish
        < -25 → Strong Bearish
        """
        # Adjust thresholds based on conviction
        if conviction == 'low':
            thresholds = {
                'strong_bullish': 35,
                'bullish': 20,
                'neutral_low': -15,
                'bearish': -20,
                'strong_bearish': -35
            }
        elif conviction == 'medium':
            thresholds = {
                'strong_bullish': 30,
                'bullish': 15,
                'neutral_low': -12,
                'bearish': -18,
                'strong_bearish': -30
            }
        else:  # high conviction
            thresholds = {
                'strong_bullish': 25,
                'bullish': 10,
                'neutral_low': -10,
                'bearish': -10,
                'strong_bearish': -25
            }
        
        if net_score >= thresholds['strong_bullish']:
            verdict = 'Strong Buy'
            direction = 'Strong Bullish'
            probability = min(0.85, 0.60 + (net_score - 25) / 100)
        elif net_score >= thresholds['bullish']:
            verdict = 'Buy'
            direction = 'Bullish'
            probability = min(0.70, 0.55 + (net_score - 10) / 100)
        elif net_score >= thresholds['neutral_low']:
            verdict = 'Hold'
            direction = 'Neutral'
            probability = 0.50
        elif net_score >= thresholds['bearish']:
            verdict = 'Sell'
            direction = 'Bearish'
            probability = min(0.70, 0.55 + (abs(net_score) - 10) / 100)
        else:
            verdict = 'Strong Sell'
            direction = 'Strong Bearish'
            probability = min(0.85, 0.60 + (abs(net_score) - 25) / 100)
        
        return {
            'verdict': verdict,
            'direction': direction,
            'probability': round(probability, 2),
        }
    
    def generate_forecast(self, scores: Dict, fundamentals: Dict) -> Dict:
        """Generate short-term and long-term forecasts"""
        net_score = scores['net_score']
        adjusted_score = scores.get('adjusted_net_score', net_score)
        
        # Short-term forecast (0-3 months) - more influenced by technical signals
        short_term = self._short_term_forecast(adjusted_score, fundamentals)
        
        # Long-term forecast (1-5 years) - more influenced by fundamentals
        long_term = self._long_term_forecast(adjusted_score, fundamentals)
        
        return {
            'short_term': short_term,
            'long_term': long_term,
        }
    
    def _short_term_forecast(self, score: float, fundamentals: Dict) -> Dict:
        """Generate short-term forecast"""
        if score > 20:
            direction = 'Bullish'
            probability = min(0.75, 0.55 + score / 100)
        elif score > 5:
            direction = 'Slightly Bullish'
            probability = 0.55
        elif score > -5:
            direction = 'Neutral'
            probability = 0.50
        elif score > -20:
            direction = 'Slightly Bearish'
            probability = 0.55
        else:
            direction = 'Bearish'
            probability = min(0.75, 0.55 + abs(score) / 100)
        
        return {
            'direction': direction,
            'probability': round(probability, 2),
            'timeframe': '0-3 months',
        }
    
    def _long_term_forecast(self, score: float, fundamentals: Dict) -> Dict:
        """Generate long-term forecast based on fundamentals"""
        # Long-term more dependent on fundamentals
        revenue_growth = fundamentals.get('revenue_growth', 0)
        roe = fundamentals.get('return_on_equity', 0)
        debt_to_equity = fundamentals.get('debt_to_equity', 0)
        
        fundamental_score = 0
        if revenue_growth > 0.1:
            fundamental_score += 2
        if roe > 0.15:
            fundamental_score += 2
        if debt_to_equity < 1:
            fundamental_score += 1
        
        # Combine with overall score
        combined_score = (score + fundamental_score * 5) / 2
        
        if combined_score > 15:
            direction = 'Bullish'
            outlook = 'Positive structural outlook with strong fundamentals'
        elif combined_score > 0:
            direction = 'Slightly Bullish'
            outlook = 'Moderately positive outlook with some strengths'
        elif combined_score > -15:
            direction = 'Neutral'
            outlook = 'Balanced outlook with mixed signals'
        else:
            direction = 'Bearish'
            outlook = 'Challenging outlook with fundamental concerns'
        
        return {
            'direction': direction,
            'structural_outlook': outlook,
            'timeframe': '1-5 years',
        }
    
    def identify_key_drivers(self, bullish_signals: list, bearish_signals: list) -> Dict:
        """Identify top 3 bullish and bearish drivers"""
        # Sort by weighted score
        sorted_bullish = sorted(bullish_signals, key=lambda s: s.weighted_score, reverse=True)
        sorted_bearish = sorted(bearish_signals, key=lambda s: s.weighted_score, reverse=True)
        
        top_bullish = sorted_bullish[:3]
        top_bearish = sorted_bearish[:3]
        
        return {
            'top_bullish': [
                {
                    'name': s.name,
                    'category': s.category,
                    'weighted_score': round(s.weighted_score, 2),
                }
                for s in top_bullish
            ],
            'top_risks': [
                {
                    'name': s.name,
                    'category': s.category,
                    'weighted_score': round(s.weighted_score, 2),
                }
                for s in top_bearish
            ]
        }
