from typing import List, Dict
from signal_engine import Signal

class ScoringModel:
    """Implements scoring model from scoring_model.md"""
    
    def __init__(self):
        pass
    
    def calculate_scores(self, bullish_signals: List[Signal], bearish_signals: List[Signal]) -> Dict:
        """
        Calculate weighted scores for bullish and bearish signals
        
        Formula: Weighted Score = Strength × Confidence
        """
        # Calculate bullish score
        bullish_score = sum(signal.weighted_score for signal in bullish_signals)
        
        # Calculate bearish score
        bearish_score = sum(signal.weighted_score for signal in bearish_signals)
        
        # Calculate net score
        net_score = bullish_score - bearish_score
        
        # Calculate signal ratio
        total_signals = len(bullish_signals) + len(bearish_signals)
        if total_signals > 0:
            signal_ratio = len(bullish_signals) / total_signals
        else:
            signal_ratio = 0.5
        
        return {
            'bullish_score': round(bullish_score, 2),
            'bearish_score': round(bearish_score, 2),
            'net_score': round(net_score, 2),
            'signal_ratio': round(signal_ratio, 3),
            'bullish_count': len(bullish_signals),
            'bearish_count': len(bearish_signals),
        }
    
    def get_top_signals(self, signals: List[Signal], top_n: int = 10) -> List[Dict]:
        """Get top signals by weighted score"""
        sorted_signals = sorted(signals, key=lambda s: s.weighted_score, reverse=True)
        top_signals = sorted_signals[:top_n]
        
        return [
            {
                'name': signal.name,
                'category': signal.category,
                'strength': signal.strength,
                'confidence': signal.confidence,
                'weighted_score': round(signal.weighted_score, 2),
                'description': signal.description,
                'horizon': signal.horizon,
            }
            for signal in top_signals
        ]
    
    def adjust_for_conflicts(self, scores: Dict, bullish_signals: List[Signal], 
                            bearish_signals: List[Signal]) -> Dict:
        """
        Adjust scores if there are high conflicts
        """
        net_score = scores['net_score']
        signal_ratio = scores['signal_ratio']
        
        # Check for high conflict (both sides have strong signals)
        if scores['bullish_count'] >= 10 and scores['bearish_count'] >= 10:
            if abs(net_score) < 10:  # Close scores indicate conflict
                scores['conflict_level'] = 'high'
                scores['adjusted_net_score'] = round(net_score * 0.5, 2)  # Reduce conviction
                scores['conviction'] = 'low'
            elif abs(net_score) < 20:
                scores['conflict_level'] = 'medium'
                scores['adjusted_net_score'] = round(net_score * 0.7, 2)
                scores['conviction'] = 'medium'
            else:
                scores['conflict_level'] = 'low'
                scores['adjusted_net_score'] = net_score
                scores['conviction'] = 'high'
        else:
            scores['conflict_level'] = 'low'
            scores['adjusted_net_score'] = net_score
            scores['conviction'] = 'high'
        
        return scores
