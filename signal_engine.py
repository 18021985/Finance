from typing import Dict, List, Tuple
from dataclasses import dataclass
import pandas as pd
from technical_indicators import TechnicalIndicators
from news_events import aggregate_effective_sentiment

@dataclass
class Signal:
    """Represents a single trading signal"""
    name: str
    category: str
    direction: str  # 'bullish' or 'bearish'
    strength: float  # 0-5
    confidence: float  # 0-1
    description: str
    horizon: str  # 'short', 'medium', 'long'
    
    @property
    def weighted_score(self) -> float:
        return self.strength * self.confidence

class SignalEngine:
    """Engine to generate all 40 signals from signal_definitions.md"""
    
    def __init__(self):
        self.tech_indicators = TechnicalIndicators()
    
    def generate_signals(self, symbol: str, stock_data: pd.DataFrame, fundamentals: Dict, 
                        macro_data: Dict, news: List[Dict]) -> Tuple[List[Signal], List[Signal]]:
        """
        Generate all bullish and bearish signals
        
        Returns:
            Tuple of (bullish_signals, bearish_signals)
        """
        # Calculate technical indicators
        tech_ind = self.tech_indicators.calculate_all(stock_data)
        
        bullish_signals = []
        bearish_signals = []
        
        # === MACRO SIGNALS (5 bullish, 5 bearish) ===
        bullish_signals.extend(self._generate_macro_bullish(macro_data, fundamentals))
        bearish_signals.extend(self._generate_macro_bearish(macro_data, fundamentals))
        
        # === TECHNICAL SIGNALS (5 bullish, 5 bearish) ===
        bullish_signals.extend(self._generate_technical_bullish(tech_ind, stock_data))
        bearish_signals.extend(self._generate_technical_bearish(tech_ind, stock_data))
        
        # === FUNDAMENTAL SIGNALS (5 bullish, 5 bearish) ===
        bullish_signals.extend(self._generate_fundamental_bullish(fundamentals))
        bearish_signals.extend(self._generate_fundamental_bearish(fundamentals))
        
        # === SENTIMENT & FLOW SIGNALS (3 bullish, 3 bearish) ===
        bullish_sentiment, bearish_sentiment = self._generate_sentiment_signals(news, fundamentals)
        bullish_signals.extend(bullish_sentiment)
        bearish_signals.extend(bearish_sentiment)
        
        # === MANAGEMENT & STRATEGY SIGNALS (2 bullish, 2 bearish) ===
        bullish_mgmt, bearish_mgmt = self._generate_management_signals(fundamentals)
        bullish_signals.extend(bullish_mgmt)
        bearish_signals.extend(bearish_mgmt)
        
        return bullish_signals, bearish_signals
    
    def _generate_macro_bullish(self, macro_data: Dict, fundamentals: Dict) -> List[Signal]:
        """Generate 5 bullish macro signals"""
        signals = []
        
        # 1. Falling Interest Rates (check via bond ETF trend)
        interest_trend = macro_data.get('interest_rates', {}).get('change_1m', 0)
        if interest_trend < -2:  # Bond prices rising = rates falling
            signals.append(Signal(
                name="Falling Interest Rates",
                category="Macro",
                direction="bullish",
                strength=min(5, abs(interest_trend)),
                confidence=0.7,
                description="Central banks reducing rates → supports equity valuations",
                horizon="medium-long"
            ))
        
        # 2. Liquidity Expansion (using dollar weakness as proxy)
        dollar_trend = macro_data.get('dollar', {}).get('change_1m', 0)
        if dollar_trend < -1:
            signals.append(Signal(
                name="Liquidity Expansion",
                category="Macro",
                direction="bullish",
                strength=min(5, abs(dollar_trend) * 2),
                confidence=0.6,
                description="Increase in money supply / QE / credit growth",
                horizon="medium"
            ))
        
        # 3. Sector Macro Tailwind (based on sector)
        sector = fundamentals.get('sector', '')
        if sector in ['Technology', 'Healthcare', 'Consumer Discretionary']:
            signals.append(Signal(
                name="Sector Macro Tailwind",
                category="Macro",
                direction="bullish",
                strength=4,
                confidence=0.6,
                description=f"Sector aligned with growth cycle ({sector})",
                horizon="medium-long"
            ))
        
        # 4. Currency Advantage (for exporters - simplified)
        if dollar_trend < -2:
            signals.append(Signal(
                name="Currency Advantage",
                category="Macro",
                direction="bullish",
                strength=3,
                confidence=0.5,
                description="Favorable currency trend for exporters",
                horizon="medium"
            ))
        
        # 5. Fiscal Stimulus (placeholder - would need news analysis)
        signals.append(Signal(
            name="Fiscal Stimulus",
            category="Macro",
            direction="bullish",
            strength=2,
            confidence=0.3,
            description="Government spending boosts economic activity",
            horizon="medium-long"
        ))
        
        return signals
    
    def _generate_macro_bearish(self, macro_data: Dict, fundamentals: Dict) -> List[Signal]:
        """Generate 5 bearish macro signals"""
        signals = []
        
        # 1. Rising Interest Rates
        interest_trend = macro_data.get('interest_rates', {}).get('change_1m', 0)
        if interest_trend > 2:  # Bond prices falling = rates rising
            signals.append(Signal(
                name="Rising Interest Rates",
                category="Macro",
                direction="bearish",
                strength=min(5, interest_trend),
                confidence=0.7,
                description="Central banks increasing rates → pressure on equities",
                horizon="medium-long"
            ))
        
        # 2. Liquidity Tightening
        dollar_trend = macro_data.get('dollar', {}).get('change_1m', 0)
        if dollar_trend > 1:
            signals.append(Signal(
                name="Liquidity Tightening",
                category="Macro",
                direction="bearish",
                strength=min(5, dollar_trend * 2),
                confidence=0.6,
                description="Decrease in money supply / QT",
                horizon="medium"
            ))
        
        # 3. Recession Indicators (simplified)
        if interest_trend > 3 and dollar_trend > 2:
            signals.append(Signal(
                name="Recession Indicators",
                category="Macro",
                direction="bearish",
                strength=4,
                confidence=0.5,
                description="Economic slowdown indicators present",
                horizon="medium"
            ))
        
        # 4. Currency Pressure
        if dollar_trend > 2:
            signals.append(Signal(
                name="Currency Pressure",
                category="Macro",
                direction="bearish",
                strength=3,
                confidence=0.5,
                description="Unfavorable currency trend",
                horizon="medium"
            ))
        
        # 5. Geopolitical Instability (placeholder)
        signals.append(Signal(
            name="Geopolitical Instability",
            category="Macro",
            direction="bearish",
            strength=2,
            confidence=0.3,
            description="Global tensions affecting markets",
            horizon="short-medium"
        ))
        
        return signals
    
    def _generate_technical_bullish(self, tech_ind: Dict, df: pd.DataFrame) -> List[Signal]:
        """Generate 5 bullish technical signals"""
        signals = []
        
        # 1. Golden Cross
        is_golden, strength = self.tech_indicators.golden_cross(tech_ind)
        if is_golden:
            signals.append(Signal(
                name="Golden Cross (50MA > 200MA)",
                category="Technical",
                direction="bullish",
                strength=strength,
                confidence=0.8,
                description="Long-term bullish trend confirmation",
                horizon="medium"
            ))
        
        # 2. RSI Oversold Reversal
        is_oversold, strength = self.tech_indicators.rsi_oversold(tech_ind)
        if is_oversold:
            signals.append(Signal(
                name="RSI Oversold Reversal",
                category="Technical",
                direction="bullish",
                strength=strength,
                confidence=0.7,
                description="Price potentially oversold, reversal likely",
                horizon="short"
            ))
        
        # 3. MACD Bullish Crossover
        is_macd_bull, strength = self.tech_indicators.macd_bullish(tech_ind)
        if is_macd_bull:
            signals.append(Signal(
                name="MACD Bullish Crossover",
                category="Technical",
                direction="bullish",
                strength=strength,
                confidence=0.7,
                description="Momentum turning bullish",
                horizon="short-medium"
            ))
        
        # 4. Breakout Above Resistance
        is_breakout, strength = self.tech_indicators.breakout_above_resistance(tech_ind)
        if is_breakout:
            signals.append(Signal(
                name="Breakout Above Resistance",
                category="Technical",
                direction="bullish",
                strength=strength,
                confidence=0.6,
                description="Price breaking above key resistance",
                horizon="short"
            ))
        
        # 5. Strong Trend
        is_trend, strength = self.tech_indicators.strong_trend(tech_ind)
        if is_trend:
            signals.append(Signal(
                name="Strong Trend (ADX > 25)",
                category="Technical",
                direction="bullish",
                strength=strength,
                confidence=0.6,
                description="Strong directional momentum",
                horizon="short-medium"
            ))
        
        return signals
    
    def _generate_technical_bearish(self, tech_ind: Dict, df: pd.DataFrame) -> List[Signal]:
        """Generate 5 bearish technical signals"""
        signals = []
        
        # 1. Death Cross
        is_death, strength = self.tech_indicators.death_cross(tech_ind)
        if is_death:
            signals.append(Signal(
                name="Death Cross (50MA < 200MA)",
                category="Technical",
                direction="bearish",
                strength=strength,
                confidence=0.8,
                description="Long-term bearish trend confirmation",
                horizon="medium"
            ))
        
        # 2. RSI Overbought
        is_overbought, strength = self.tech_indicators.rsi_overbought(tech_ind)
        if is_overbought:
            signals.append(Signal(
                name="RSI Overbought",
                category="Technical",
                direction="bearish",
                strength=strength,
                confidence=0.7,
                description="Price potentially overbought, correction likely",
                horizon="short"
            ))
        
        # 3. MACD Bearish Crossover
        is_macd_bear, strength = self.tech_indicators.macd_bearish(tech_ind)
        if is_macd_bear:
            signals.append(Signal(
                name="MACD Bearish Crossover",
                category="Technical",
                direction="bearish",
                strength=strength,
                confidence=0.7,
                description="Momentum turning bearish",
                horizon="short-medium"
            ))
        
        # 4. Breakdown Below Support
        is_breakdown, strength = self.tech_indicators.breakdown_below_support(tech_ind)
        if is_breakdown:
            signals.append(Signal(
                name="Breakdown Below Support",
                category="Technical",
                direction="bearish",
                strength=strength,
                confidence=0.6,
                description="Price breaking below key support",
                horizon="short"
            ))
        
        # 5. Volatility Spike
        is_vol_spike, strength = self.tech_indicators.volatility_spike(tech_ind, df)
        if is_vol_spike:
            signals.append(Signal(
                name="Volatility Spike (Risk-Off)",
                category="Technical",
                direction="bearish",
                strength=strength,
                confidence=0.6,
                description="High volatility indicating uncertainty",
                horizon="short"
            ))
        
        return signals
    
    def _generate_fundamental_bullish(self, fundamentals: Dict) -> List[Signal]:
        """Generate 5 bullish fundamental signals"""
        signals = []
        
        # 1. Revenue Growth
        revenue_growth = fundamentals.get('revenue_growth', 0) * 100
        if revenue_growth > 10:
            signals.append(Signal(
                name="Revenue Growth",
                category="Fundamental",
                direction="bullish",
                strength=min(5, revenue_growth / 10),
                confidence=0.8,
                description=f"Strong revenue growth: {revenue_growth:.1f}%",
                horizon="long"
            ))
        
        # 2. Margin Expansion
        profit_margin = fundamentals.get('profit_margin', 0)
        if profit_margin > 0.15:
            signals.append(Signal(
                name="Margin Expansion",
                category="Fundamental",
                direction="bullish",
                strength=min(5, profit_margin * 20),
                confidence=0.7,
                description=f"Healthy profit margins: {profit_margin:.1%}",
                horizon="long"
            ))
        
        # 3. Strong Free Cash Flow
        fcf = fundamentals.get('free_cash_flow', 0)
        if fcf > 0:
            signals.append(Signal(
                name="Strong Free Cash Flow",
                category="Fundamental",
                direction="bullish",
                strength=4,
                confidence=0.7,
                description="Positive free cash flow generation",
                horizon="long"
            ))
        
        # 4. Improving Leverage
        debt_to_equity = fundamentals.get('debt_to_equity', 0)
        if 0 < debt_to_equity < 1:
            signals.append(Signal(
                name="Improving Leverage",
                category="Fundamental",
                direction="bullish",
                strength=min(5, (1 - debt_to_equity) * 5),
                confidence=0.6,
                description=f"Conservative debt levels: D/E {debt_to_equity:.2f}",
                horizon="long"
            ))
        
        # 5. High ROE
        roe = fundamentals.get('return_on_equity', 0)
        if roe > 0.15:
            signals.append(Signal(
                name="High ROE / ROIC",
                category="Fundamental",
                direction="bullish",
                strength=min(5, roe * 20),
                confidence=0.7,
                description=f"Strong return on equity: {roe:.1%}",
                horizon="long"
            ))
        
        return signals
    
    def _generate_fundamental_bearish(self, fundamentals: Dict) -> List[Signal]:
        """Generate 5 bearish fundamental signals"""
        signals = []
        
        # 1. Declining Revenue
        revenue_growth = fundamentals.get('revenue_growth', 0) * 100
        if revenue_growth < -5:
            signals.append(Signal(
                name="Declining Revenue",
                category="Fundamental",
                direction="bearish",
                strength=min(5, abs(revenue_growth) / 5),
                confidence=0.8,
                description=f"Revenue declining: {revenue_growth:.1f}%",
                horizon="long"
            ))
        
        # 2. Margin Compression
        profit_margin = fundamentals.get('profit_margin', 0)
        if profit_margin < 0.05:
            signals.append(Signal(
                name="Margin Compression",
                category="Fundamental",
                direction="bearish",
                strength=min(5, (0.05 - profit_margin) * 50),
                confidence=0.7,
                description=f"Low profit margins: {profit_margin:.1%}",
                horizon="long"
            ))
        
        # 3. High Debt Levels
        debt_to_equity = fundamentals.get('debt_to_equity', 0)
        if debt_to_equity > 2:
            signals.append(Signal(
                name="High Debt Levels",
                category="Fundamental",
                direction="bearish",
                strength=min(5, debt_to_equity / 2),
                confidence=0.7,
                description=f"Elevated debt levels: D/E {debt_to_equity:.2f}",
                horizon="long"
            ))
        
        # 4. Weak Cash Flow
        fcf = fundamentals.get('free_cash_flow', 0)
        if fcf < 0:
            signals.append(Signal(
                name="Weak Cash Flow",
                category="Fundamental",
                direction="bearish",
                strength=4,
                confidence=0.7,
                description="Negative free cash flow",
                horizon="long"
            ))
        
        # 5. Poor Capital Efficiency
        roe = fundamentals.get('return_on_equity', 0)
        if roe < 0.10:
            signals.append(Signal(
                name="Poor Capital Efficiency (Low ROE)",
                category="Fundamental",
                direction="bearish",
                strength=min(5, (0.10 - roe) * 30),
                confidence=0.7,
                description=f"Low return on equity: {roe:.1%}",
                horizon="long"
            ))
        
        return signals
    
    def _generate_sentiment_signals(self, news: List[Dict], fundamentals: Dict) -> Tuple[List[Signal], List[Signal]]:
        """Generate sentiment signals (3 bullish, 3 bearish)"""
        bullish = []
        bearish = []
        
        # Aggregate enriched effective sentiment from DataLayer (headline sentiment + events + weights)
        avg_sentiment, news_count = aggregate_effective_sentiment(news)
        avg_sentiment = float(avg_sentiment)
        
        # 1. Institutional Accumulation (proxy: positive price momentum)
        if fundamentals.get('52_week_high', 0) > 0:
            current = fundamentals.get('current_price', 0)
            high_52 = fundamentals.get('52_week_high', 0)
            if current > high_52 * 0.9:
                bullish.append(Signal(
                    name="Institutional Accumulation",
                    category="Sentiment",
                    direction="bullish",
                    strength=4,
                    confidence=0.5,
                    description="Price near 52-week high suggests accumulation",
                    horizon="short-medium"
                ))
        
        # 2. Positive Earnings Revisions (proxy: positive growth)
        if fundamentals.get('earnings_growth', 0) > 0.1:
            bullish.append(Signal(
                name="Positive Earnings Revisions",
                category="Sentiment",
                direction="bullish",
                strength=4,
                confidence=0.6,
                description="Positive earnings growth trajectory",
                horizon="medium"
            ))
        
        # 3. Bullish Positioning (placeholder)
        if avg_sentiment > 0.15 and news_count >= 3:
            bullish.append(Signal(
                name="Positive News + Event Sentiment",
                category="Sentiment",
                direction="bullish",
                strength=min(5, 2 + avg_sentiment * 6),
                confidence=min(0.85, 0.45 + news_count / 20),
                description=f"Positive weighted news/event sentiment (avg={avg_sentiment:.2f}, n={news_count})",
                horizon="short-medium"
            ))
        
        # Bearish sentiment signals
        # 1. Institutional Selling
        if fundamentals.get('52_week_low', 0) > 0:
            current = fundamentals.get('current_price', 0)
            low_52 = fundamentals.get('52_week_low', 0)
            if current < low_52 * 1.1:
                bearish.append(Signal(
                    name="Institutional Selling",
                    category="Sentiment",
                    direction="bearish",
                    strength=4,
                    confidence=0.5,
                    description="Price near 52-week low suggests selling",
                    horizon="short-medium"
                ))
        
        # 2. Fear Index Spike (placeholder)
        bearish.append(Signal(
            name="Fear Index Spike (High VIX)",
            category="Sentiment",
            direction="bearish",
            strength=2,
            confidence=0.3,
            description="Market fear elevated (placeholder)",
            horizon="short"
        ))
        
        # 3. Negative news/event sentiment (enriched)
        if avg_sentiment < -0.15 and news_count >= 3:
            bearish.append(Signal(
                name="Negative News + Event Sentiment",
                category="Sentiment",
                direction="bearish",
                strength=min(5, 2 + abs(avg_sentiment) * 6),
                confidence=min(0.85, 0.45 + news_count / 20),
                description=f"Negative weighted news/event sentiment (avg={avg_sentiment:.2f}, n={news_count})",
                horizon="short-medium"
            ))
        
        return bullish, bearish
    
    def _generate_management_signals(self, fundamentals: Dict) -> Tuple[List[Signal], List[Signal]]:
        """Generate management signals (2 bullish, 2 bearish)"""
        bullish = []
        bearish = []
        
        # Bullish management signals
        # 1. Strong Leadership Track Record (placeholder - would need historical data)
        bullish.append(Signal(
            name="Strong Leadership Track Record",
            category="Management",
            direction="bullish",
            strength=3,
            confidence=0.4,
            description="Experienced management team (placeholder)",
            horizon="long"
        ))
        
        # 2. Strategic Expansion (proxy: revenue growth)
        if fundamentals.get('revenue_growth', 0) > 0.15:
            bullish.append(Signal(
                name="Strategic Expansion / Innovation",
                category="Management",
                direction="bullish",
                strength=4,
                confidence=0.5,
                description="Company expanding into new markets",
                horizon="long"
            ))
        
        # Bearish management signals
        # 1. Leadership Instability (placeholder)
        bearish.append(Signal(
            name="Leadership Instability",
            category="Management",
            direction="bearish",
            strength=2,
            confidence=0.3,
            description="Management turnover (placeholder)",
            horizon="long"
        ))
        
        # 2. Poor Capital Allocation (proxy: low ROE)
        if fundamentals.get('return_on_equity', 0) < 0.08:
            bearish.append(Signal(
                name="Poor Capital Allocation History",
                category="Management",
                direction="bearish",
                strength=3,
                confidence=0.5,
                description="Inefficient capital deployment",
                horizon="long"
            ))
        
        return bullish, bearish
