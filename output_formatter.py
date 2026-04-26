from typing import Dict, List
from signal_engine import Signal

class OutputFormatter:
    """Formats analysis output following templates/output_format.md"""
    
    def __init__(self):
        pass
    
    def format_analysis(self, symbol: str, company_info: Dict, scores: Dict, 
                        top_bullish: List[Dict], top_bearish: List[Dict],
                        forecast: Dict, key_drivers: Dict, decision: Dict) -> str:
        """
        Format complete analysis according to output_format.md template
        """
        output = []
        
        # Header
        output.append(f"# Financial Analysis: {symbol}")
        output.append(f"**Company:** {company_info.get('name', 'N/A')}")
        output.append(f"**Sector:** {company_info.get('sector', 'N/A')}")
        output.append(f"**Current Price:** ${company_info.get('current_price', 0):.2f}")
        output.append("")
        
        # Bullish Indicators (Top 10)
        output.append("## Bullish Indicators (Top 10)")
        if top_bullish:
            for i, signal in enumerate(top_bullish, 1):
                output.append(f"{i}. **{signal['name']}** ({signal['category']})")
                output.append(f"   - Strength: {signal['strength']}/5 | Confidence: {signal['confidence']:.0%}")
                output.append(f"   - Weighted Score: {signal['weighted_score']}")
                output.append(f"   - {signal['description']}")
                output.append("")
        else:
            output.append("No strong bullish signals detected.")
            output.append("")
        
        # Bearish Indicators (Top 10)
        output.append("## Bearish Indicators (Top 10)")
        if top_bearish:
            for i, signal in enumerate(top_bearish, 1):
                output.append(f"{i}. **{signal['name']}** ({signal['category']})")
                output.append(f"   - Strength: {signal['strength']}/5 | Confidence: {signal['confidence']:.0%}")
                output.append(f"   - Weighted Score: {signal['weighted_score']}")
                output.append(f"   - {signal['description']}")
                output.append("")
        else:
            output.append("No strong bearish signals detected.")
            output.append("")
        
        # Score Summary
        output.append("## Score Summary")
        output.append(f"- **Bullish Score:** {scores['bullish_score']}")
        output.append(f"- **Bearish Score:** {scores['bearish_score']}")
        output.append(f"- **Net Score:** {scores['net_score']}")
        output.append(f"- **Signal Ratio:** {scores['signal_ratio']:.1%}")
        output.append(f"- **Bullish Signals:** {scores['bullish_count']}")
        output.append(f"- **Bearish Signals:** {scores['bearish_count']}")
        if 'conflict_level' in scores:
            output.append(f"- **Conflict Level:** {scores['conflict_level']}")
            output.append(f"- **Conviction:** {scores['conviction']}")
        output.append("")
        
        # Forecast
        output.append("## Forecast")
        output.append("### Short-Term (0–3 months)")
        output.append(f"- **Direction:** {forecast['short_term']['direction']}")
        output.append(f"- **Probability:** {forecast['short_term']['probability']:.0%}")
        output.append("")
        
        output.append("### Long-Term (1–5 years)")
        output.append(f"- **Direction:** {forecast['long_term']['direction']}")
        output.append(f"- **Structural Outlook:** {forecast['long_term']['structural_outlook']}")
        output.append("")
        
        # Key Drivers
        output.append("## Key Drivers")
        output.append("**Top 3 Bullish Drivers:**")
        for i, driver in enumerate(key_drivers['top_bullish'], 1):
            output.append(f"{i}. {driver['name']} ({driver['category']}) - Score: {driver['weighted_score']}")
        output.append("")
        
        output.append("**Top 3 Risks:**")
        for i, risk in enumerate(key_drivers['top_risks'], 1):
            output.append(f"{i}. {risk['name']} ({risk['category']}) - Score: {risk['weighted_score']}")
        output.append("")
        
        # Final Verdict
        output.append("## Final Verdict")
        output.append(f"**{decision['verdict']}**")
        output.append(f"- Direction: {decision['direction']}")
        output.append(f"- Probability: {decision['probability']:.0%}")
        output.append("")
        
        # Fundamentals Summary
        output.append("## Fundamentals Summary")
        output.append(f"- **Market Cap:** ${company_info.get('market_cap', 0):,.0f}")
        output.append(f"- **P/E Ratio:** {company_info.get('pe_ratio', 0):.2f}")
        output.append(f"- **P/B Ratio:** {company_info.get('pb_ratio', 0):.2f}")
        output.append(f"- **Dividend Yield:** {company_info.get('dividend_yield', 0) * 100:.2f}%")
        output.append(f"- **Beta:** {company_info.get('beta', 0):.2f}")
        output.append(f"- **ROE:** {company_info.get('return_on_equity', 0) * 100:.1f}%")
        output.append(f"- **Debt/Equity:** {company_info.get('debt_to_equity', 0):.2f}")
        output.append(f"- **Revenue Growth:** {company_info.get('revenue_growth', 0) * 100:.1f}%")
        output.append(f"- **52W High:** ${company_info.get('52_week_high', 0):.2f}")
        output.append(f"- **52W Low:** ${company_info.get('52_week_low', 0):.2f}")
        output.append("")
        
        return "\n".join(output)
    
    def format_json(self, symbol: str, company_info: Dict, scores: Dict,
                    top_bullish: List[Dict], top_bearish: List[Dict],
                    forecast: Dict, key_drivers: Dict, decision: Dict) -> Dict:
        """Format analysis as JSON for API responses"""
        return {
            'symbol': symbol,
            'company': company_info,
            'scores': scores,
            'bullish_indicators': top_bullish,
            'bearish_indicators': top_bearish,
            'forecast': forecast,
            'key_drivers': key_drivers,
            'verdict': decision,
        }
