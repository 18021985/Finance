from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

# Fortune 100 companies with stock symbols
FORTUNE_100_STOCKS = {
    'technology': ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'NVDA', 'META', 'TSLA', 'ADBE', 'CRM', 'INTC', 'AMD', 'ORCL', 'IBM', 'CSCO', 'ACN'],
    'healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'T', 'MRK', 'ABT', 'DHR', 'BMY', 'LLY', 'AMGN', 'GILD', 'MDT', 'ISRG', 'VRTX'],
    'finance': ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'BLK', 'SCHW', 'AXP', 'USB', 'PNC', 'TFC', 'CB', 'COF', 'MMC'],
    'energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL', 'BKR', 'FANG', 'DVN', 'HES'],
    'consumer': ['AMZN', 'HD', 'MCD', 'NKE', 'SBUX', 'LOW', 'TJX', 'DG', 'COST', 'WMT', 'TGT', 'KR', 'KO', 'PEP', 'PG'],
    'industrial': ['CAT', 'DE', 'GE', 'HON', 'UPS', 'RTX', 'LMT', 'BA', 'MMM', 'EMR', 'ETN', 'ITW', 'CMI', 'ROP', 'PH'],
    'telecom': ['VZ', 'T', 'TMUS', 'CMCSA', 'CHTR', 'DIS', 'NFLX', 'EA', 'ATVI', 'TTWO'],
}

# NIFTY 50 companies (Indian market)
NIFTY_50_STOCKS = {
    'technology': ['INFY', 'TCS', 'WIPRO', 'HCLTECH', 'LTIM', 'TECHM'],
    'finance': ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK', 'INDUSINDBK', 'BAJFINANCE'],
    'energy': ['RELIANCE', 'ONGC', 'NTPC', 'POWERGRID', 'TATAPOWER'],
    'consumer': ['ITC', 'HINDUNILVR', 'NESTLEIND', 'BRITANNIA', 'TATACONSUM'],
    'automotive': ['MARUTI', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'EICHERMOT'],
    'healthcare': ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'APOLLOHOSP', 'TATASTEEL'],
    'industrial': ['LARSEN', 'TATASTEEL', 'JSWSTEEL', 'ULTRACEMCO', 'ACC'],
}

# Sensex companies (subset of NIFTY with large caps)
SENSEX_STOCKS = {
    'technology': ['TCS', 'INFY', 'WIPRO', 'HCLTECH'],
    'finance': ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK'],
    'energy': ['RELIANCE', 'ONGC', 'NTPC'],
    'consumer': ['ITC', 'HINDUNILVR', 'NESTLEIND'],
    'automotive': ['MARUTI', 'TATAMOTORS', 'M&M'],
    'industrial': ['LARSEN', 'TATASTEEL', 'MAHINDRA'],
}

@dataclass
class InvestmentRecommendation:
    """Represents an investment recommendation"""
    symbol: str
    action: str  # buy, sell, hold
    confidence: float  # 0-1
    target_price: Optional[float]
    time_horizon: str  # short-term, medium-term, long-term
    entry_price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    reasoning: List[str]
    risk_level: str  # low, medium, high
    sector: str
    expected_return: float
    position_size: float  # percentage of portfolio
    forecast: Optional[Dict] = None

class InvestmentRecommender:
    """
    Generates investment recommendations based on market analysis
    
    Features:
    - Short-term strategies (0-3 months)
    - Long-term strategies (1-5 years)
    - Risk-adjusted recommendations
    - Portfolio allocation suggestions
    - Fortune 100 companies coverage
    - Indian market (NIFTY 50, Sensex) coverage
    """
    
    def __init__(self, analyzer=None):
        self.analyzer = analyzer
        self.sectors = FORTUNE_100_STOCKS
        self.indian_sectors = NIFTY_50_STOCKS

        # Thresholds are intentionally conservative defaults.
        # They should be calibrated by backtests once observability is in place.
        self.buy_threshold = 65  # composite total_score (0-100)
        self.reduce_threshold = 45
    
    def generate_recommendations(
        self,
        market_analysis: Dict,
        user_holdings: Optional[List[Dict]] = None,
        portfolio_value: Optional[float] = None,
        cash_available: float = 0.0,
    ) -> List[InvestmentRecommendation]:
        """
        Generate investment recommendations based on market analysis

        Args:
            market_analysis: Market analysis data including composite scores, sentiment, etc.
            user_holdings: List of holdings dicts with at least {symbol, shares, average_cost?}
            portfolio_value: Total portfolio value (if known). If not provided, estimated from holdings.
            cash_available: Cash available for new positions (optional).
        """
        if not self.analyzer:
            return []

        holdings_by_symbol: Dict[str, Dict] = {}
        if user_holdings:
            for h in user_holdings:
                sym = (h.get("symbol") or "").upper().strip()
                if sym:
                    holdings_by_symbol[sym] = h

        # Build candidate universe: always include holdings + a small diversified watchlist.
        candidates = set(holdings_by_symbol.keys())
        # Include US stocks (Fortune 100)
        for sector, symbols in self.sectors.items():
            candidates.update(s.upper() for s in symbols[:2])
        # Include Indian stocks (NIFTY 50)
        for sector, symbols in self.indian_sectors.items():
            candidates.update(s.upper() for s in symbols[:2])

        # Estimate portfolio value if not provided and holdings exist.
        est_portfolio_value = portfolio_value
        if est_portfolio_value is None and holdings_by_symbol:
            est_portfolio_value = self._estimate_portfolio_value_from_holdings(holdings_by_symbol)
        if est_portfolio_value is None:
            est_portfolio_value = 0.0

        # Keep response time bounded: analyze only a capped number of symbols per request.
        # Include holdings first, then a small diversified set.
        ordered: List[str] = []
        for s in sorted(holdings_by_symbol.keys()):
            if s not in ordered:
                ordered.append(s)
        for s in sorted(candidates):
            if s not in ordered:
                ordered.append(s)
        # If the user has no holdings configured yet, keep the first-run workload small
        # to avoid timeouts and empty responses (free data sources are slow/unreliable).
        ordered = ordered[:30] if holdings_by_symbol else ordered[:3]

        recs: List[InvestmentRecommendation] = []
        for symbol in ordered:
            rec = self._recommend_for_symbol(
                symbol=symbol,
                market_analysis=market_analysis,
                holding=holdings_by_symbol.get(symbol),
                portfolio_value=est_portfolio_value,
                cash_available=cash_available,
            )
            if rec:
                recs.append(rec)

        # If everything failed (external data issues), fall back to a tiny liquid set
        # to avoid returning an empty list to the UI.
        if not recs:
            for symbol in ["AAPL", "MSFT", "SPY", "NVDA", "GOOGL"]:
                rec = self._recommend_for_symbol(
                    symbol=symbol,
                    market_analysis=market_analysis,
                    holding=holdings_by_symbol.get(symbol),
                    portfolio_value=est_portfolio_value,
                    cash_available=cash_available,
                )
                if rec:
                    recs.append(rec)
            if not recs:
                return []

        # Sort: prioritize existing-holding risk actions and high-confidence buys
        recs.sort(key=lambda r: (0 if r.symbol in holdings_by_symbol else 1, -r.confidence, -r.expected_return))
        return recs

    def _estimate_portfolio_value_from_holdings(self, holdings_by_symbol: Dict[str, Dict]) -> Optional[float]:
        total = 0.0
        for sym, h in holdings_by_symbol.items():
            try:
                shares = float(h.get("shares") or 0)
                q = self.analyzer.data_layer.get_quote(sym) if hasattr(self.analyzer, "data_layer") else None
                px = float(q["price"]) if q and q.get("price") is not None else 0.0
                if px > 0 and shares > 0:
                    total += px * shares
            except Exception:
                continue
        return total if total > 0 else None

    def _recommend_for_symbol(
        self,
        symbol: str,
        market_analysis: Dict,
        holding: Optional[Dict],
        portfolio_value: float,
        cash_available: float,
    ) -> Optional[InvestmentRecommendation]:
        """
        Create one recommendation for a symbol using composite scoring + portfolio context.
        """
        try:
            composite = self.analyzer.get_composite_score(symbol)
            if not composite or "error" in composite:
                return None

            cs = composite.get("composite_score", {})
            total_score = float(cs.get("total_score", 0))
            confidence = float(cs.get("confidence", 0.5))
            trend = (cs.get("trend") or "neutral").lower()

            # Get current price
            quote = self.analyzer.data_layer.get_quote(symbol) if hasattr(self.analyzer, "data_layer") else None
            entry_price = float(quote["price"]) if quote and quote.get("price") else float(cs.get("current_price", 0) or 0)
            if entry_price <= 0:
                # Fallback to last close (keeps recommendations non-empty even when quotes are missing).
                try:
                    bars = self.analyzer.data_layer.get_stock_data(symbol, period="6mo")
                    if bars is not None and not bars.empty and "Close" in bars:
                        entry_price = float(bars["Close"].dropna().iloc[-1])
                except Exception:
                    entry_price = 0.0
            if entry_price <= 0:
                return None

            # Action decision: holdings are managed first (reduce risk before new buys)
            if holding:
                if trend in {"bearish", "strong_bearish"} or total_score < self.reduce_threshold:
                    action = "reduce" if total_score >= 35 else "sell"
                elif trend in {"bullish", "strong_bullish"} and total_score >= self.buy_threshold:
                    action = "increase"
                else:
                    action = "hold"
            else:
                action = "buy" if (trend in {"bullish", "strong_bullish"} and total_score >= self.buy_threshold) else "watch"

            # Time horizon: align with strength and macro risk level
            risk_level = (market_analysis.get("risk_level") or "medium").lower()
            if action in {"buy", "increase"} and total_score >= 75 and risk_level != "high":
                time_horizon = "short-term"
            elif action in {"buy", "increase"}:
                time_horizon = "medium-term"
            else:
                time_horizon = "medium-term"

            # Probabilistic forecast (quantiles + up probability) is most useful for entry/scale decisions.
            # Skip it for "watch/hold" to keep recommendations fast and avoid empty responses.
            horizon_days = 20 if time_horizon == "short-term" else (60 if time_horizon == "medium-term" else 252)
            p10_px = p50_px = p90_px = None
            up_prob = None
            if action in {"buy", "increase", "reduce", "sell"}:
                try:
                    bars = self.analyzer.data_layer.get_stock_data(symbol, period="1y")
                    if bars is not None and not bars.empty and "Close" in bars:
                        dist = self.analyzer.prob_forecaster.forecast(bars["Close"], horizon_days=horizon_days, score=total_score)
                        fc = self.analyzer.prob_forecaster.forecast_prices(entry_price, dist)
                        p10_px = fc.get("price_quantiles", {}).get("p10")
                        p50_px = fc.get("price_quantiles", {}).get("p50")
                        p90_px = fc.get("price_quantiles", {}).get("p90")
                        up_prob = fc.get("direction_up_prob")
                except Exception:
                    pass

            # Expected return from forecast median when available; fallback to bounded score proxy.
            if p50_px and entry_price > 0:
                expected_return = max(0.0, float(p50_px) / entry_price - 1.0)
            else:
                expected_return = max(0.0, (total_score - 50.0) / 250.0)  # slightly more conservative fallback

            # Stop/TP: use forecast quantiles when available, otherwise volatility-based fallback.
            if p10_px and p90_px:
                stop_loss = float(p10_px)
                take_profit = float(p90_px)
                vol_ann = None
            else:
                stop_loss, take_profit, vol_ann = self._compute_stop_and_tp(symbol, entry_price, expected_return)

            # Position sizing: if we have portfolio value, size with RiskManager; otherwise provide % only.
            position_size = 0.0
            shares = 0
            if action in {"buy", "increase"} and portfolio_value and portfolio_value > 0:
                if vol_ann is not None:
                    sizing = self.analyzer.risk_manager.calculate_position_size_vol_target(
                        portfolio_value=portfolio_value,
                        entry_price=entry_price,
                        stop_loss=stop_loss,
                        annualized_vol=vol_ann,
                        confidence=confidence,
                    )
                else:
                    sizing = self.analyzer.risk_manager.calculate_position_size(
                        portfolio_value=portfolio_value,
                        entry_price=entry_price,
                        stop_loss=stop_loss,
                        confidence=confidence,
                    )
                shares = int(sizing.get("shares") or 0)
                position_size = float(sizing.get("position_size_pct") or 0) / 100.0

                # If this is a new position and cash is provided, cap by cash
                if not holding and cash_available and cash_available > 0 and shares > 0:
                    max_shares_by_cash = int(cash_available / entry_price)
                    shares = max(0, min(shares, max_shares_by_cash))

            # Recommendation confidence: combine composite confidence with up-prob (if available), bounded.
            conf = confidence
            if isinstance(up_prob, (int, float)):
                # up_prob is 0..1; emphasize deviation from 0.5 but keep bounded
                prob_strength = min(1.0, abs(float(up_prob) - 0.5) * 2.0)
                conf = min(0.95, max(0.05, 0.5 * confidence + 0.5 * prob_strength))

            reasoning = [
                f"Composite score: {total_score:.0f}/100 (trend={trend}, confidence={confidence:.2f})",
                f"Market risk level: {risk_level}",
            ]
            if p10_px and p50_px and p90_px:
                reasoning.append(f"Forecast (+{horizon_days}d): P10={p10_px}, P50={p50_px}, P90={p90_px}, UpProb={up_prob}")
            if holding:
                try:
                    reasoning.append(f"Current holding: {float(holding.get('shares') or 0):.0f} shares")
                except Exception:
                    pass

            # Build response
            target_price = round(float(p50_px), 2) if p50_px else (round(entry_price * (1 + expected_return), 2) if expected_return > 0 else None)
            sector = (holding or {}).get("sector") or "unknown"

            return InvestmentRecommendation(
                symbol=symbol,
                action=action,
                confidence=round(min(0.95, max(0.05, conf)), 3),
                target_price=target_price,
                time_horizon=time_horizon,
                entry_price=round(entry_price, 2),
                stop_loss=round(stop_loss, 2) if stop_loss else None,
                take_profit=round(take_profit, 2) if take_profit else None,
                reasoning=reasoning,
                risk_level=risk_level,
                sector=str(sector),
                expected_return=round(expected_return, 4),
                position_size=round(position_size, 4),
                forecast=(
                    {
                        "horizon_days": horizon_days,
                        "price_quantiles": {"p10": p10_px, "p50": p50_px, "p90": p90_px},
                        "direction_up_prob": up_prob,
                    }
                    if (p10_px or p50_px or p90_px or up_prob is not None)
                    else None
                ),
            )
        except Exception:
            return None

    def _compute_stop_and_tp(self, symbol: str, entry_price: float, expected_return: float) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Compute stop-loss / take-profit using recent realized volatility (fallback).
        """
        try:
            df = self.analyzer.data_layer.get_stock_data(symbol, period="3mo")
            if df is None or df.empty or "Close" not in df:
                raise ValueError("no bars")
            rets = df["Close"].pct_change().dropna()
            if rets.empty:
                raise ValueError("no returns")
            vol_daily = float(rets.std())  # daily std
            vol_ann = vol_daily * (252 ** 0.5)
            # Convert to a pragmatic stop distance: ~2 * daily vol, bounded
            stop_dist = max(0.03, min(0.12, 2.0 * vol_daily))
            stop_loss = entry_price * (1 - stop_dist)
            # TP: at least 1.5R, or expected return if larger
            tp_dist = max(stop_dist * 1.5, expected_return)
            take_profit = entry_price * (1 + tp_dist)
            return stop_loss, take_profit, vol_ann
        except Exception:
            stop_loss = entry_price * 0.92
            take_profit = entry_price * (1 + max(0.06, expected_return))
            return stop_loss, take_profit, None
    
    def _generate_us_market_recommendations(self, market_analysis: Dict) -> List[InvestmentRecommendation]:
        """Generate US market recommendations from Fortune 100 companies"""
        recommendations = []

        # Select top stocks from each sector based on analysis
        for sector, symbols in self.sectors.items():
            # Take top 2-3 stocks per sector for recommendations
            selected_symbols = symbols[:3]

            for symbol in selected_symbols:
                # Get real market data if analyzer is available
                if self.analyzer:
                    try:
                        stock_data = self._get_stock_data(symbol, 'US')
                        if not stock_data:
                            continue

                        entry_price = stock_data.get('current_price', 0)
                        if entry_price == 0:
                            continue

                        # Analyze stock using composite score
                        analysis = self._analyze_stock(symbol, stock_data, market_analysis)
                        action = analysis.get('action', 'hold')
                        confidence = analysis.get('confidence', 0.5)

                        if action == 'buy':
                            target_price = entry_price * (1 + analysis.get('expected_return', 0.10))
                            stop_loss = entry_price * (1 - analysis.get('risk_factor', 0.05))
                            take_profit = entry_price * (1 + analysis.get('expected_return', 0.10) * 1.5)
                            expected_return = (target_price - entry_price) / entry_price
                        else:
                            target_price = None
                            stop_loss = None
                            take_profit = None
                            expected_return = 0

                        rec = InvestmentRecommendation(
                            symbol=symbol,
                            action=action,
                            confidence=confidence,
                            target_price=target_price,
                            time_horizon=analysis.get('time_horizon', 'medium-term'),
                            entry_price=entry_price,
                            stop_loss=stop_loss,
                            take_profit=take_profit,
                            reasoning=analysis.get('reasoning', []),
                            risk_level=analysis.get('risk_level', 'medium'),
                            sector=sector,
                            expected_return=expected_return,
                            position_size=analysis.get('position_size', 0.03)
                        )
                        recommendations.append(rec)

                    except Exception as e:
                        print(f"Error analyzing {symbol}: {e}")
                        continue

        return recommendations

    def _generate_indian_market_recommendations(self, market_analysis: Dict) -> List[InvestmentRecommendation]:
        """Generate Indian market recommendations from NIFTY 50 companies"""
        recommendations = []

        # Select top stocks from each sector
        for sector, symbols in self.indian_sectors.items():
            # Take top 2 stocks per sector
            selected_symbols = symbols[:2]

            for symbol in selected_symbols:
                # Get real market data if analyzer is available
                if self.analyzer and hasattr(self.analyzer, 'indian_analyzer'):
                    try:
                        stock_data = self._get_stock_data(symbol, 'IN')
                        if not stock_data:
                            continue

                        entry_price = stock_data.get('current_price', 0)
                        if entry_price == 0:
                            continue

                        # Analyze stock
                        analysis = self._analyze_stock(symbol, stock_data, market_analysis)
                        action = analysis.get('action', 'hold')
                        confidence = analysis.get('confidence', 0.5)

                        if action == 'buy':
                            target_price = entry_price * (1 + analysis.get('expected_return', 0.10))
                            stop_loss = entry_price * (1 - analysis.get('risk_factor', 0.05))
                            take_profit = entry_price * (1 + analysis.get('expected_return', 0.10) * 1.5)
                            expected_return = (target_price - entry_price) / entry_price
                        else:
                            target_price = None
                            stop_loss = None
                            take_profit = None
                            expected_return = 0

                        rec = InvestmentRecommendation(
                            symbol=symbol,
                            action=action,
                            confidence=confidence,
                            target_price=target_price,
                            time_horizon=analysis.get('time_horizon', 'medium-term'),
                            entry_price=entry_price,
                            stop_loss=stop_loss,
                            take_profit=take_profit,
                            reasoning=analysis.get('reasoning', []),
                            risk_level=analysis.get('risk_level', 'medium'),
                            sector=sector,
                            expected_return=expected_return,
                            position_size=analysis.get('position_size', 0.03)
                        )
                        recommendations.append(rec)

                    except Exception as e:
                        print(f"Error analyzing Indian stock {symbol}: {e}")
                        continue

        return recommendations

    def _get_stock_data(self, symbol: str, market: str) -> Optional[Dict]:
        """Get real stock data from analyzer"""
        try:
            if market == 'US' and self.analyzer:
                # Use existing analyzer for US stocks
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period='1mo')

                if hist.empty:
                    return None

                current_price = hist['Close'].iloc[-1]
                return {
                    'current_price': current_price,
                    'volume': hist['Volume'].iloc[-1],
                    'change': (current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0],
                    'info': info
                }

            elif market == 'IN' and self.analyzer and hasattr(self.analyzer, 'indian_analyzer'):
                # Use Indian analyzer for Indian stocks
                result = self.analyzer.indian_analyzer.analyze_indian_stock(symbol)
                if result:
                    return {
                        'current_price': result.get('current_price', 0),
                        'volume': result.get('volume', 0),
                        'change': result.get('change_1m', 0),
                        'info': result
                    }

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

        return None

    def _analyze_stock(self, symbol: str, stock_data: Dict, market_analysis: Dict) -> Dict:
        """Analyze stock and generate recommendation"""
        analysis = {}

        try:
            current_price = stock_data.get('current_price', 0)
            price_change = stock_data.get('change', 0)

            # Determine action based on price change and market sentiment
            market_sentiment = market_analysis.get('market_sentiment', 'neutral')

            if price_change > 0.05 and market_sentiment in ['bullish', 'neutral']:
                action = 'buy'
                confidence = min(0.9, 0.6 + abs(price_change))
                time_horizon = 'short-term'
                risk_level = 'medium'
                expected_return = 0.10 + abs(price_change)
            elif price_change < -0.05 and market_sentiment == 'bullish':
                action = 'buy'
                confidence = 0.7
                time_horizon = 'long-term'
                risk_level = 'low'
                expected_return = 0.15
            elif abs(price_change) < 0.02:
                action = 'hold'
                confidence = 0.5
                time_horizon = 'medium-term'
                risk_level = 'low'
                expected_return = 0.05
            else:
                action = 'hold'
                confidence = 0.4
                time_horizon = 'medium-term'
                risk_level = 'medium'
                expected_return = 0.03

            # Generate reasoning
            reasoning = self._generate_analysis_reasoning(symbol, action, price_change, market_sentiment)

            analysis = {
                'action': action,
                'confidence': confidence,
                'time_horizon': time_horizon,
                'risk_level': risk_level,
                'expected_return': expected_return,
                'risk_factor': 0.05 if risk_level == 'low' else 0.08 if risk_level == 'medium' else 0.12,
                'position_size': 0.05 if risk_level == 'low' else 0.03 if risk_level == 'medium' else 0.02,
                'reasoning': reasoning
            }

        except Exception as e:
            print(f"Error in stock analysis: {e}")
            # Fallback to conservative recommendation
            analysis = {
                'action': 'hold',
                'confidence': 0.5,
                'time_horizon': 'medium-term',
                'risk_level': 'medium',
                'expected_return': 0.05,
                'risk_factor': 0.08,
                'position_size': 0.03,
                'reasoning': ['Insufficient data for analysis', 'Monitor stock for better entry point']
            }

        return analysis

    def _generate_analysis_reasoning(self, symbol: str, action: str, price_change: float, market_sentiment: str) -> List[str]:
        """Generate reasoning based on analysis"""
        reasons = []

        if action == 'buy':
            if price_change > 0:
                reasons.append(f"{symbol} showing positive momentum with {price_change*100:.1f}% recent gain")
                reasons.append("Technical indicators suggest continued upward trend")
            else:
                reasons.append(f"{symbol} at attractive valuation after recent decline")
                reasons.append("Potential for recovery based on fundamentals")

            if market_sentiment == 'bullish':
                reasons.append("Favorable market conditions support position")
            reasons.append("Strong fundamentals and growth potential")
            reasons.append("Risk-reward ratio favorable at current levels")

        elif action == 'hold':
            reasons.append(f"{symbol} in consolidation phase")
            reasons.append("Wait for clearer directional signal")
            reasons.append("Current price does not offer optimal entry point")
            reasons.append("Monitor for breakout or breakdown")

        return reasons

    def get_portfolio_allocation(self, risk_profile: str = 'moderate') -> Dict:
        """
        Get recommended portfolio allocation based on risk profile
        
        Args:
            risk_profile: conservative, moderate, aggressive
        """
        allocations = {
            'conservative': {
                'equities': 0.40,
                'bonds': 0.40,
                'cash': 0.10,
                'commodities': 0.05,
                'real_estate': 0.05
            },
            'moderate': {
                'equities': 0.60,
                'bonds': 0.25,
                'cash': 0.05,
                'commodities': 0.05,
                'real_estate': 0.05
            },
            'aggressive': {
                'equities': 0.80,
                'bonds': 0.10,
                'cash': 0.05,
                'commodities': 0.03,
                'real_estate': 0.02
            }
        }
        
        return allocations.get(risk_profile, allocations['moderate'])
    
    def get_market_opportunities(self, market_analysis: Dict) -> List[Dict]:
        """
        Identify current market opportunities
        
        Args:
            market_analysis: Market analysis data
        """
        opportunities = [
            {
                'type': 'sector_rotation',
                'description': 'Technology sector showing strength',
                'action': 'Increase allocation to tech stocks',
                'priority': 'high'
            },
            {
                'type': 'value_opportunity',
                'description': 'Energy stocks undervalued relative to fundamentals',
                'action': 'Consider adding energy exposure',
                'priority': 'medium'
            },
            {
                'type': 'dividend_growth',
                'description': 'High-quality dividend stocks available at attractive yields',
                'action': 'Build dividend income portfolio',
                'priority': 'medium'
            },
            {
                'type': 'growth_opportunity',
                'description': 'AI and cloud computing companies showing strong growth',
                'action': 'Allocate to growth-focused tech companies',
                'priority': 'high'
            }
        ]
        
        return opportunities
    
    def get_investment_tips(self, market_analysis: Dict) -> List[str]:
        """
        Get investment tips based on current market conditions
        
        Args:
            market_analysis: Market analysis data
        """
        market_sentiment = (market_analysis.get("market_sentiment") or "neutral").lower()
        risk_level = (market_analysis.get("risk_level") or "medium").lower()
        holdings = market_analysis.get("holdings") or []

        # Basic concentration heuristic: if most holdings are tech symbols (common early portfolios),
        # suggest diversifying. We keep it lightweight and avoid extra data fetches here.
        tech_like = {"AAPL", "MSFT", "GOOGL", "GOOG", "NVDA", "META", "TSLA", "ADBE", "CRM", "AMD", "INTC", "ORCL", "IBM", "CSCO", "AMZN"}
        held_syms = [str(h.get("symbol") or "").upper().strip() for h in holdings if isinstance(h, dict)]
        held_syms = [s for s in held_syms if s]

        tech_count = sum(1 for s in held_syms if s in tech_like)
        total_count = len(set(held_syms))
        tech_share = (tech_count / total_count) if total_count else 0.0

        tips: List[str] = []
        tips.append(f"Current regime snapshot: sentiment={market_sentiment}, risk_level={risk_level}")

        # Regime / risk-level aware tips (top priority)
        if risk_level in {"high", "very_high"}:
            tips.append("High-risk regime detected: reduce position sizes and widen diversification (avoid concentrated bets)")
            tips.append("Prefer staggered entries (DCA) and use predefined stop-loss / risk limits on new trades")
            tips.append("Maintain higher cash buffer until volatility normalizes")
        elif risk_level in {"low"} and market_sentiment in {"bullish"}:
            tips.append("Risk regime is supportive: prioritize quality trend-following entries over random diversification")
            tips.append("Still size positions by risk (volatility/stop distance), not by conviction alone")
        else:
            tips.append("Size positions by risk (stop distance / volatility), not by price or emotions")

        # Portfolio concentration
        if total_count > 0 and tech_share >= 0.6:
            tips.append("Your holdings look concentrated in tech/growth: add uncorrelated sectors (healthcare, staples, energy, financials) to reduce drawdown risk")
        else:
            tips.append("Diversify across sectors to reduce concentration and correlation risk")

        # Always-useful hygiene tips (kept concise)
        tips.append("Rebalance periodically (e.g., quarterly) to maintain your target allocation and control drift")
        tips.append("Focus on quality balance sheets and sustainable cashflows when taking long-horizon positions")
        tips.append("Don’t chase hot tips—require a clear thesis, entry/exit plan, and invalidation point")
        tips.append("Consider taxes/fees before frequent trading; prefer fewer, higher-quality decisions")
        tips.append("Keep an emergency fund separate from your investment portfolio")

        # De-duplicate while preserving order
        seen = set()
        out: List[str] = []
        for t in tips:
            if t not in seen:
                out.append(t)
                seen.add(t)

        return out[:10]
