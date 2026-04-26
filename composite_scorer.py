from typing import Dict, List
from dataclasses import dataclass

@dataclass
class CompositeScore:
    """Composite score for an asset"""
    total_score: float  # 0-100
    technical_score: float  # 0-100, 30% weight
    momentum_score: float  # 0-100, 25% weight
    macro_score: float  # 0-100, 20% weight
    fundamental_score: float  # 0-100, 15% weight
    ml_probability: float  # 0-100% directional probability (display)
    ml_score: float  # 0-100 score used inside composite weighting (centered at 50)
    trend: str  # 'bullish', 'bearish', 'neutral'
    momentum: str  # 'strong', 'moderate', 'weak'
    macro_alignment: str  # 'aligned', 'neutral', 'misaligned'
    fundamental_strength: str  # 'strong', 'moderate', 'weak'
    confidence: float  # 0-1

class CompositeScorer:
    """
    Composite scoring system unifying technical, momentum, macro, fundamental, and ML signals
    
    Weights:
    - Technical: 30%
    - Momentum: 25%
    - Macro Alignment: 20%
    - Fundamental Strength: 15%
    - ML Probability: 10%
    """
    
    def __init__(self):
        self.weights = {
            'technical': 0.30,
            'momentum': 0.25,
            'macro': 0.20,
            'fundamental': 0.15,
            'ml': 0.10
        }
    
    def calculate_composite_score(self, technical: Dict, momentum: Dict, 
                                 macro: Dict, fundamental: Dict, 
                                 ml_prediction: Dict = None) -> CompositeScore:
        """
        Calculate composite score from all signal sources
        
        Args:
            technical: Technical analysis results
            momentum: Momentum analysis results
            macro: Macro analysis results
            fundamental: Fundamental analysis results
            ml_prediction: ML prediction results (optional)
        """
        # Normalize each component to 0-100 scale
        technical_score = self._normalize_technical(technical)
        momentum_score = self._normalize_momentum(momentum)
        macro_score = self._normalize_macro(macro, fundamental)
        fundamental_score = self._normalize_fundamental(fundamental)
        ml_score = self._normalize_ml(ml_prediction) if ml_prediction else 50
        # Display probability is distinct from the composite score.
        # It is simply the model's directional probability expressed as a percentage.
        if ml_prediction:
            prob = float(ml_prediction.get("probability", 0.5))
            ml_probability = round(max(0.0, min(1.0, prob)) * 100.0, 1)
        else:
            ml_probability = 50.0
        
        # Calculate weighted composite score
        total_score = (
            technical_score * self.weights['technical'] +
            momentum_score * self.weights['momentum'] +
            macro_score * self.weights['macro'] +
            fundamental_score * self.weights['fundamental'] +
            ml_score * self.weights['ml']
        )
        
        # Determine qualitative assessments
        trend = self._assess_trend(technical_score)
        momentum_qual = self._assess_momentum(momentum_score)
        macro_alignment = self._assess_macro_alignment(macro_score)
        fundamental_strength = self._assess_fundamental(fundamental_score)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(
            technical, momentum, macro, fundamental, ml_prediction
        )
        
        return CompositeScore(
            total_score=round(total_score, 1),
            technical_score=round(technical_score, 1),
            momentum_score=round(momentum_score, 1),
            macro_score=round(macro_score, 1),
            fundamental_score=round(fundamental_score, 1),
            ml_probability=ml_probability,
            ml_score=round(ml_score, 1),
            trend=trend,
            momentum=momentum_qual,
            macro_alignment=macro_alignment,
            fundamental_strength=fundamental_strength,
            confidence=round(confidence, 2)
        )
    
    def _normalize_technical(self, technical: Dict) -> float:
        """Normalize technical signals to 0-100"""
        score = 50  # Base score
        
        # Trend analysis
        if technical.get('trend') == 'strong_uptrend':
            score += 25
        elif technical.get('trend') == 'uptrend':
            score += 15
        elif technical.get('trend') == 'strong_downtrend':
            score -= 25
        elif technical.get('trend') == 'downtrend':
            score -= 15
        
        # Technical indicators
        rsi = technical.get('rsi', 50)
        if 40 < rsi < 60:
            score += 10  # Healthy RSI
        elif rsi < 30:
            score += 5  # Oversold bounce potential
        elif rsi > 70:
            score -= 10  # Overbought
        
        # Moving averages
        if technical.get('above_sma_50', False):
            score += 10
        if technical.get('above_sma_200', False):
            score += 10
        
        # Chart patterns
        patterns = technical.get('chart_patterns', [])
        for pattern in patterns:
            if pattern.get('direction') == 'bullish':
                score += pattern.get('confidence', 0) * 5
            elif pattern.get('direction') == 'bearish':
                score -= pattern.get('confidence', 0) * 5
        
        return min(100, max(0, score))
    
    def _normalize_momentum(self, momentum: Dict) -> float:
        """Normalize momentum signals to 0-100"""
        score = 50
        
        current_momentum = momentum.get('current_momentum', {})
        direction = current_momentum.get('direction', 'neutral')
        strength = current_momentum.get('strength', 50)
        
        if direction == 'bullish':
            score += (strength - 50) * 0.8
        elif direction == 'bearish':
            score -= (strength - 50) * 0.8
        
        # Consider confidence
        confidence = current_momentum.get('confidence', 0.5)
        score *= (0.5 + confidence * 0.5)
        
        return min(100, max(0, score))
    
    def _normalize_macro(self, macro: Dict, fundamental: Dict) -> float:
        """
        Normalize macro alignment to 0-100.

        Sector-aware: the same macro environment impacts sectors differently
        (e.g., rising rates penalize long-duration growth more than financials).
        """
        score = 50
        
        # Interest rate environment
        # Supports both:
        # - DataLayer macro format: {'interest_rates': {'change_1m': ...}, 'dollar': {'change_1m': ...}}
        # - MacroAnalyzer overview format: {'interest_rates': {'US_10Y': {'change_1m': ...}, ...}, 'yield_curve': {...}, 'risk_sentiment': {...}}
        rates = macro.get('interest_rates', {}) or {}

        rate_change = 0.0
        if isinstance(rates, dict):
            # DataLayer style
            if "change_1m" in rates:
                try:
                    rate_change = float(rates.get("change_1m") or 0.0)
                except Exception:
                    rate_change = 0.0
            else:
                # MacroAnalyzer style: use US_10Y if present, else average available changes
                if isinstance(rates.get("US_10Y"), dict) and "change_1m" in rates["US_10Y"]:
                    try:
                        rate_change = float(rates["US_10Y"].get("change_1m") or 0.0)
                    except Exception:
                        rate_change = 0.0
                else:
                    changes = []
                    for v in rates.values():
                        if isinstance(v, dict) and "change_1m" in v:
                            try:
                                changes.append(float(v.get("change_1m") or 0.0))
                            except Exception:
                                continue
                    rate_change = float(sum(changes) / len(changes)) if changes else 0.0
        
        # Rising rates typically bearish for equities, bullish for USD
        if rate_change > 0.5:
            score -= 10
        elif rate_change < -0.5:
            score += 10
        
        # Inflation
        inflation = macro.get('inflation', {})
        inflation_change = inflation.get('change_1m', 0)
        
        # Rising inflation typically bearish for bonds, mixed for equities
        if inflation_change > 1:
            score -= 5
        elif inflation_change < -1:
            score += 5
        
        # Dollar strength
        dollar = macro.get('dollar', {}) or {}
        dollar_change = 0.0
        if isinstance(dollar, dict) and "change_1m" in dollar:
            try:
                dollar_change = float(dollar.get("change_1m") or 0.0)
            except Exception:
                dollar_change = 0.0

        # If MacroAnalyzer style, use DXY from commodities as a proxy
        if dollar_change == 0.0:
            commodities = macro.get("commodities", {}) or {}
            if isinstance(commodities, dict) and isinstance(commodities.get("DXY"), dict):
                try:
                    dollar_change = float(commodities["DXY"].get("change_1m") or 0.0)
                except Exception:
                    dollar_change = 0.0
        
        # Strong dollar typically bearish for commodities, emerging markets
        if dollar_change > 0.5:
            score -= 5
        elif dollar_change < -0.5:
            score += 5

        # Risk sentiment (MacroAnalyzer style): penalize risk-off regimes
        risk_sent = macro.get("risk_sentiment", {}) or {}
        if isinstance(risk_sent, dict):
            sent = (risk_sent.get("sentiment") or "").lower()
            try:
                vix = float(risk_sent.get("vix") or 0.0)
            except Exception:
                vix = 0.0

            if "extreme" in sent or vix >= 35:
                score -= 10
            elif "risk-off" in sent or vix >= 25:
                score -= 5
            elif "risk-on" in sent or (0 < vix < 15):
                score += 3

        # Sector-aware macro sensitivity
        sector = str((fundamental or {}).get("sector") or "").strip().lower()
        # A few common Yahoo Finance sector labels:
        # - technology, communication services, consumer discretionary, consumer staples, financial services,
        #   healthcare, energy, industrials, materials, utilities, real estate

        # (1) Rate sensitivity (duration)
        # Growth/long-duration sectors: more negative when yields rise
        rate_sensitive_high = {"technology", "communication services", "consumer discretionary", "real estate"}
        rate_sensitive_low = {"utilities", "consumer staples", "healthcare"}
        financials = {"financial", "financial services"}

        if rate_change > 0.5:
            if sector in rate_sensitive_high:
                score -= 6
            elif sector in rate_sensitive_low:
                score -= 2
            elif sector in financials:
                score += 3  # banks often benefit from higher yields (simplified)
        elif rate_change < -0.5:
            if sector in rate_sensitive_high:
                score += 5
            elif sector in financials:
                score -= 2

        # (2) USD sensitivity
        # Strong USD tends to pressure multinationals/commodities; weaker USD helps them.
        if dollar_change > 0.5:
            if sector in {"materials", "energy"}:
                score -= 4
            elif sector in rate_sensitive_high:
                score -= 2
        elif dollar_change < -0.5:
            if sector in {"materials", "energy"}:
                score += 3

        # (3) Oil sensitivity (Energy)
        oil_change_1m = 0.0
        try:
            commodities = macro.get("commodities", {}) or {}
            if isinstance(commodities, dict):
                oil = commodities.get("Oil")
                if isinstance(oil, dict) and "change_1m" in oil:
                    oil_change_1m = float(oil.get("change_1m") or 0.0)
        except Exception:
            oil_change_1m = 0.0

        if sector == "energy":
            if oil_change_1m > 2:
                score += 5
            elif oil_change_1m < -2:
                score -= 5
        
        # Geopolitical context
        context = macro.get('context', {})
        if context.get('geopolitical_risk') == 'high':
            score -= 10
        
        return min(100, max(0, score))
    
    def _normalize_fundamental(self, fundamental: Dict) -> float:
        """Normalize fundamental strength to 0-100"""
        score = 50
        
        # Earnings growth
        earnings_growth = fundamental.get('earnings_growth', 0)
        if earnings_growth > 0.15:
            score += 20
        elif earnings_growth > 0.10:
            score += 15
        elif earnings_growth > 0.05:
            score += 10
        elif earnings_growth < 0:
            score -= 15
        
        # Valuation (P/E)
        pe_ratio = fundamental.get('pe_ratio', 0)
        if 10 < pe_ratio < 20:
            score += 15  # Attractive valuation
        elif pe_ratio < 10:
            score += 10  # Value
        elif pe_ratio > 40:
            score -= 20  # Expensive
        
        # ROE
        roe = fundamental.get('return_on_equity', 0)
        if roe > 0.20:
            score += 15
        elif roe > 0.15:
            score += 10
        elif roe < 0.10:
            score -= 10
        
        # Debt levels
        debt_to_equity = fundamental.get('debt_to_equity', 0)
        if debt_to_equity < 1:
            score += 10
        elif debt_to_equity > 2:
            score -= 15
        
        # Profit margins
        profit_margin = fundamental.get('profit_margin', 0)
        if profit_margin > 0.20:
            score += 10
        elif profit_margin < 0.05:
            score -= 10
        
        return min(100, max(0, score))
    
    def _normalize_ml(self, ml_prediction: Dict) -> float:
        """Normalize ML prediction to 0-100"""
        if not ml_prediction:
            return 50
        
        probability = ml_prediction.get('probability', 0.5)
        direction = ml_prediction.get('direction', 'neutral')
        
        if direction == 'bullish':
            return 50 + (probability * 50)
        elif direction == 'bearish':
            return 50 - (probability * 50)
        else:
            return 50
    
    def _assess_trend(self, score: float) -> str:
        """Assess trend based on technical score"""
        if score > 70:
            return 'bullish'
        elif score > 55:
            return 'bullish'
        elif score < 30:
            return 'bearish'
        elif score < 45:
            return 'bearish'
        else:
            return 'neutral'
    
    def _assess_momentum(self, score: float) -> str:
        """Assess momentum strength"""
        if score > 75:
            return 'strong'
        elif score > 60:
            return 'moderate'
        elif score < 25:
            return 'weak'
        elif score < 40:
            return 'weak'
        else:
            return 'moderate'
    
    def _assess_macro_alignment(self, score: float) -> str:
        """Assess macro alignment"""
        if score > 65:
            return 'aligned'
        elif score < 35:
            return 'misaligned'
        else:
            return 'neutral'
    
    def _assess_fundamental(self, score: float) -> str:
        """Assess fundamental strength"""
        if score > 70:
            return 'strong'
        elif score > 50:
            return 'moderate'
        else:
            return 'weak'
    
    def _calculate_confidence(self, technical: Dict, momentum: Dict,
                            macro: Dict, fundamental: Dict,
                            ml_prediction: Dict) -> float:
        """Calculate overall confidence in the composite score"""
        confidences = []
        
        # Technical confidence
        if technical.get('confidence'):
            confidences.append(technical['confidence'])
        
        # Momentum confidence
        momentum_conf = momentum.get('current_momentum', {}).get('confidence', 0.5)
        confidences.append(momentum_conf)
        
        # Fundamental confidence (based on data quality)
        if fundamental.get('data_quality') == 'high':
            confidences.append(0.8)
        elif fundamental.get('data_quality') == 'medium':
            confidences.append(0.6)
        else:
            confidences.append(0.4)
        
        # ML confidence
        if ml_prediction:
            confidences.append(ml_prediction.get('confidence', 0.5))
        
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def generate_insight(self, composite_score: CompositeScore, asset: str) -> Dict:
        """
        Generate insight summary based on composite score
        
        Returns structured insight with strategic considerations
        """
        score = composite_score.total_score
        
        # Determine overall assessment
        if score > 75:
            assessment = "Strong favorable setup with multiple supportive factors"
            strategic_consideration = "Consider increasing exposure on pullbacks, monitor for continuation signals"
        elif score > 60:
            assessment = "Favorable setup with moderate strength across factors"
            strategic_consideration = "Potential opportunity exists, consider selective exposure with risk management"
        elif score > 45:
            assessment = "Mixed signals with no clear directional bias"
            strategic_consideration = "Maintain neutral stance, wait for clearer signal alignment"
        elif score > 30:
            assessment = "Unfavorable setup with multiple negative factors"
            strategic_consideration = "Consider reducing exposure, defensive positioning may be warranted"
        else:
            assessment = "Strongly unfavorable with significant headwinds"
            strategic_consideration = "Avoid new exposure, consider existing position review"
        
        # Identify key drivers
        drivers = []
        if composite_score.technical_score > 60:
            drivers.append("Strong technical trend")
        if composite_score.momentum_score > 60:
            drivers.append("Positive momentum")
        if composite_score.macro_score > 60:
            drivers.append("Favorable macro environment")
        if composite_score.fundamental_score > 60:
            drivers.append("Solid fundamentals")

        # Identify key risks
        risks = []
        if composite_score.technical_score < 40:
            risks.append("Weak technical structure")
        if composite_score.momentum_score < 40:
            risks.append("Negative momentum")
        if composite_score.macro_score < 40:
            risks.append("Unfavorable macro conditions")
        if composite_score.fundamental_score < 40:
            risks.append("Weak fundamentals")

        # Avoid blank UX: if nothing trips a hard risk threshold, provide a clear default.
        if not risks:
            if 45 <= composite_score.total_score <= 60:
                risks.append("Signal disagreement / low alignment across factors")
            else:
                risks.append("No dominant risk factor below threshold; monitor regime shifts and news events")
        
        return {
            'asset': asset,
            'composite_score': composite_score.total_score,
            'assessment': assessment,
            'strategic_consideration': strategic_consideration,
            'key_drivers': drivers,
            'key_risks': risks,
            'component_scores': {
                'technical': composite_score.technical_score,
                'momentum': composite_score.momentum_score,
                'macro': composite_score.macro_score,
                'fundamental': composite_score.fundamental_score,
                'ml_score': composite_score.ml_score,
                'ml_probability': composite_score.ml_probability
            },
            'confidence': composite_score.confidence
        }
