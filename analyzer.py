from typing import Dict, Optional
import pandas as pd
from data_layer import DataLayer
from signal_engine import SignalEngine
from scoring_model import ScoringModel
from decision_logic import DecisionLogic
from output_formatter import OutputFormatter
from context_integration import ContextIntegration
from momentum_predictor import MomentumPredictor
from investment_horizon_analyzer import InvestmentHorizonAnalyzer
from chart_analyzer import ChartAnalyzer
from action_advisor import ActionAdvisor
from indian_market_analyzer import IndianMarketAnalyzer
from sector_analyzer import SectorAnalyzer
from portfolio_optimizer import PortfolioOptimizer
from backtester import Backtester
from alert_system import AlertSystem
from risk_manager import RiskManager
from composite_scorer import CompositeScorer
from macro_analyzer import MacroAnalyzer
from multi_asset_analyzer import MultiAssetAnalyzer
from scenario_analyzer import ScenarioAnalyzer
from correlation_analyzer import CorrelationAnalyzer
from asset_allocator import AssetAllocator
from ml_predictor import MLPredictor
from ensemble_predictor import EnsemblePredictor
from performance_tracker import PerformanceTracker
from hyperparameter_optimizer import HyperparameterOptimizer
from online_learner import OnlineLearner
from continuous_validator import ContinuousValidator
from ml_backtester import MLBacktester
from model_explainer import ModelExplainer
from regime_detector import RegimeDetector
from probabilistic_forecast import ProbabilisticForecaster
try:
    from deep_learning_predictor import DeepLearningPredictor
    DEEP_LEARNING_AVAILABLE = True
except ImportError:
    DEEP_LEARNING_AVAILABLE = False
    print("Deep learning predictor not available. Install with: pip install tensorflow")
try:
    from social_sentiment import SocialSentimentAnalyzer
    SOCIAL_SENTIMENT_AVAILABLE = True
except ImportError:
    SOCIAL_SENTIMENT_AVAILABLE = False
    print("Social sentiment analyzer not available. Install with: pip install textblob tweepy praw")
try:
    from rl_trader import RLTrader
    RL_TRADER_AVAILABLE = True
except ImportError:
    RL_TRADER_AVAILABLE = False
    print("RL trader not available. Install with: pip install gymnasium stable-baselines3")
try:
    from auto_feature_engineer import AutoFeatureEngineer
    AUTO_FEATURE_AVAILABLE = True
except ImportError:
    AUTO_FEATURE_AVAILABLE = False
    print("Auto feature engineer not available. Install with: pip install featuretools")
try:
    from online_learner import OnlineLearner, RIVER_AVAILABLE
    ONLINE_LEARNER_AVAILABLE = RIVER_AVAILABLE
except ImportError:
    ONLINE_LEARNER_AVAILABLE = False
    print("Online learner not available. Install with: pip install river")
try:
    from realtime_pipeline import RealTimeDataPipeline
    REALTIME_PIPELINE_AVAILABLE = True
except ImportError:
    REALTIME_PIPELINE_AVAILABLE = False
    print("Realtime pipeline not available")

try:
    from model_explainer import ModelExplainer, SHAP_AVAILABLE
    MODEL_EXPLAINER_AVAILABLE = SHAP_AVAILABLE
except ImportError:
    MODEL_EXPLAINER_AVAILABLE = False
    print("Model explainer not available. Install with: pip install shap")

try:
    from multi_source_data import MultiSourceDataFetcher
    MULTI_SOURCE_AVAILABLE = True
except ImportError:
    MULTI_SOURCE_AVAILABLE = False
    print("Multi-source data fetcher not available")

try:
    from geopolitical_risk import GeopoliticalRiskAnalyzer
    GEOPOLITICAL_AVAILABLE = True
except ImportError:
    GEOPOLITICAL_AVAILABLE = False
    print("Geopolitical risk analyzer not available")


class FinancialIntelligenceSystem:
    """
    Main financial intelligence system
    
    Integrates all analysis modules:
    - Data layer
    - Chart analyzer
    - Momentum predictor
    - Macro analyzer
    - ML predictor
    - Composite scorer
    """
    
    def __init__(self):
        # Cache for macro data (expires after 5 minutes)
        self._macro_cache = None
        self._macro_cache_time = None
        # Cache for stock data (expires after 1 minute)
        self._stock_cache = {}
        self._stock_cache_time = {}
        self.data_layer = DataLayer()
        self.signal_engine = SignalEngine()
        self.scoring_model = ScoringModel()
        self.decision_logic = DecisionLogic()
        self.output_formatter = OutputFormatter()
        self.context_integration = ContextIntegration()
        self.regime_detector = RegimeDetector()
        self.prob_forecaster = ProbabilisticForecaster()
        
        # Advanced analytics modules
        self.momentum_predictor = MomentumPredictor()
        self.horizon_analyzer = InvestmentHorizonAnalyzer()
        self.chart_analyzer = ChartAnalyzer()
        self.action_advisor = ActionAdvisor()
        self.indian_analyzer = IndianMarketAnalyzer()
        self.sector_analyzer = SectorAnalyzer()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.backtester = Backtester()
        self.alert_system = AlertSystem()
        self.risk_manager = RiskManager()
        
        # New intelligence modules
        self.composite_scorer = CompositeScorer()
        self.macro_analyzer = MacroAnalyzer()
        self.multi_asset_analyzer = MultiAssetAnalyzer()
        self.scenario_analyzer = ScenarioAnalyzer()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.asset_allocator = AssetAllocator()
        self.ml_predictor = MLPredictor()
        
        # ML modules
        self.ensemble_predictor = EnsemblePredictor()
        self.ml_backtester = MLBacktester(self.ensemble_predictor)
        self.model_explainer = ModelExplainer(self.ensemble_predictor) if MODEL_EXPLAINER_AVAILABLE else None
        self.deep_learning_predictor = DeepLearningPredictor() if DEEP_LEARNING_AVAILABLE else None
        self.social_sentiment = SocialSentimentAnalyzer() if SOCIAL_SENTIMENT_AVAILABLE else None
        self.rl_trader = RLTrader() if RL_TRADER_AVAILABLE else None
        self.auto_feature_engineer = AutoFeatureEngineer() if AUTO_FEATURE_AVAILABLE else None
        self.online_learner = OnlineLearner() if ONLINE_LEARNER_AVAILABLE else None
        self.realtime_pipeline = RealTimeDataPipeline() if REALTIME_PIPELINE_AVAILABLE else None
        
        # New advanced modules
        self.multi_source_fetcher = MultiSourceDataFetcher() if MULTI_SOURCE_AVAILABLE else None
        self.geopolitical_analyzer = GeopoliticalRiskAnalyzer() if GEOPOLITICAL_AVAILABLE else None
        
        # Investment recommender
        try:
            from investment_recommender import InvestmentRecommender
            self.investment_recommender = InvestmentRecommender(analyzer=self)
        except ImportError:
            self.investment_recommender = None
            print("Investment recommender not available")
    
    def _get_cached_macro_data(self) -> Dict:
        """Get cached macro data or fetch fresh if expired"""
        import time
        current_time = time.time()
        
        # Return cached data if less than 5 minutes old
        if self._macro_cache is not None and self._macro_cache_time is not None:
            if current_time - self._macro_cache_time < 300:  # 5 minutes
                return self._macro_cache
        
        # Fetch fresh data
        self._macro_cache = self.macro_analyzer.get_macro_overview()
        self._macro_cache_time = current_time
        return self._macro_cache
    
    def _get_cached_stock_data(self, symbol: str) -> Dict:
        """Get cached stock data or fetch fresh if expired"""
        import time
        current_time = time.time()
        
        # Return cached data if less than 1 minute old
        if symbol in self._stock_cache and symbol in self._stock_cache_time:
            if current_time - self._stock_cache_time[symbol] < 60:  # 1 minute
                return self._stock_cache[symbol]
        
        # Fetch fresh data
        stock_data = self.data_layer.get_stock_data(symbol)
        self._stock_cache[symbol] = stock_data
        self._stock_cache_time[symbol] = current_time
        return stock_data
    
    def analyze_company(self, symbol: str, format: str = 'json') -> Dict:
        """
        Perform complete analysis of a company
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL', 'RELIANCE.NS')
            format: Output format ('json' or 'markdown')
        
        Returns:
            Analysis results in specified format
        """
        try:
            # Step 1: Fetch data
            stock_data = self._get_cached_stock_data(symbol)
            company_info = self.data_layer.get_company_info(symbol)
            fundamentals = self.data_layer.get_fundamental_data(symbol)
            news = self.data_layer.get_news_sentiment(symbol)
            macro_data = self._get_cached_macro_data()
            
            # Step 2: Generate signals
            bullish_signals, bearish_signals = self.signal_engine.generate_signals(
                symbol, stock_data, fundamentals, macro_data, news
            )
            
            # Step 3: Apply context adjustments
            context_summary = self.context_integration.get_context_summary()
            
            # Adjust signal confidences based on geopolitical context
            for signal in bullish_signals + bearish_signals:
                signal.confidence = self.context_integration.adjust_confidence_for_geopolitics(
                    signal.confidence
                )
            
            # Step 4: Calculate scores
            scores = self.scoring_model.calculate_scores(bullish_signals, bearish_signals)
            scores = self.scoring_model.adjust_for_conflicts(scores, bullish_signals, bearish_signals)
            
            # Step 5: Get top signals
            top_bullish = self.scoring_model.get_top_signals(bullish_signals, 10)
            top_bearish = self.scoring_model.get_top_signals(bearish_signals, 10)
            
            # Step 6: Generate forecast
            forecast = self.decision_logic.generate_forecast(scores, fundamentals)

            # Step 6b: Regime + probabilistic forecast (quantiles)
            try:
                regime = self.regime_detector.detect(stock_data, macro_data)
            except Exception:
                regime = {"volatility_regime": "medium", "trend_regime": "neutral", "correlation_regime": None}

            try:
                last_price = float(company_info.get("current_price") or fundamentals.get("current_price") or 0) or float(stock_data["Close"].iloc[-1]) if not stock_data.empty else 0
                # Use composite-ish score proxy: rescale adjusted_net_score into 0..100 band around 50
                adj = float(scores.get("adjusted_net_score", scores.get("net_score", 0)))
                score_proxy = max(0.0, min(100.0, 50.0 + adj))
                st = self.prob_forecaster.forecast(stock_data["Close"], horizon_days=20, score=score_proxy)
                lt = self.prob_forecaster.forecast(stock_data["Close"], horizon_days=252, score=score_proxy)
                forecast["probabilistic"] = {
                    "regime": regime,
                    "short_term": self.prob_forecaster.forecast_prices(last_price, st),
                    "long_term": self.prob_forecaster.forecast_prices(last_price, lt),
                }
            except Exception:
                forecast["probabilistic"] = {"regime": regime}
            
            # Step 7: Identify key drivers
            key_drivers = self.decision_logic.identify_key_drivers(bullish_signals, bearish_signals)
            
            # Step 8: Make decision
            decision = self.decision_logic.interpret_score(
                scores['adjusted_net_score'],
                scores.get('conviction', 'high')
            )
            
            # Step 9: Format output
            if format == 'markdown':
                output = self.output_formatter.format_analysis(
                    symbol, company_info, scores, top_bullish, top_bearish,
                    forecast, key_drivers, decision
                )
                return {'format': 'markdown', 'content': output}
            else:
                output = self.output_formatter.format_json(
                    symbol, company_info, scores, top_bullish, top_bearish,
                    forecast, key_drivers, decision
                )
                output['context'] = context_summary
                return output
                
        except Exception as e:
            return {
                'error': str(e),
                'symbol': symbol,
                'message': 'Analysis failed'
            }
    
    def get_market_overview(self) -> Dict:
        """Get overview of major market indices"""
        try:
            indices = self.data_layer.get_market_indices()
            macro = self.data_layer.get_macro_indicators()
            context = self.context_integration.get_context_summary()
            
            return {
                'indices': indices,
                'macro_indicators': macro,
                'context': context,
            }
        except Exception as e:
            return {'error': str(e)}
    
    def scan_opportunities(self, symbols: list) -> dict:
        """
        Scan multiple symbols for investment opportunities
        
        Returns dict with opportunities list sorted by net score
        """
        results = []
        
        for symbol in symbols:
            try:
                analysis = self.analyze_company(symbol, format='json')
                if 'error' not in analysis:
                    results.append({
                        'symbol': symbol,
                        'net_score': analysis['scores']['net_score'],
                        'verdict': analysis['verdict']['verdict'],
                        'company': analysis['company'].get('name', ''),
                    })
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue
        
        # Sort by net score (descending)
        results.sort(key=lambda x: x['net_score'], reverse=True)
        
        return {
            'opportunities': results,
            'total_analyzed': len(results)
        }
    
    def analyze_company_enhanced(self, symbol: str) -> Dict:
        """
        Enhanced analysis with momentum, chart patterns, and action advice
        """
        try:
            # Get base analysis
            base_analysis = self.analyze_company(symbol, format='json')
            if 'error' in base_analysis:
                return base_analysis
            
            # Fetch additional data
            stock_data = self.data_layer.get_stock_data(symbol)
            fundamentals = self.data_layer.get_fundamental_data(symbol)
            
            # Momentum prediction
            momentum = self.momentum_predictor.predict_momentum(
                stock_data, fundamentals.get('current_price', 0)
            )
            
            # Chart analysis
            chart = self.chart_analyzer.analyze_chart(stock_data, symbol)
            
            # Action advice
            action_advice = self.action_advisor.generate_advice(
                symbol, base_analysis, momentum, chart, fundamentals
            )
            
            # Investment horizon analysis
            technical_indicators = self.chart_analyzer._calculate_technical_indicators(stock_data)
            short_term = self.horizon_analyzer.analyze_short_term_opportunities(
                symbol, stock_data, fundamentals, technical_indicators
            )
            long_term = self.horizon_analyzer.analyze_long_term_opportunities(
                symbol, stock_data, fundamentals, technical_indicators
            )
            
            # Combine with base analysis
            base_analysis['momentum'] = momentum
            base_analysis['chart_analysis'] = chart
            base_analysis['action_advice'] = action_advice.__dict__
            base_analysis['investment_horizons'] = {
                'short_term': short_term,
                'long_term': long_term
            }
            
            return base_analysis
            
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}
    
    def analyze_indian_stock(self, symbol: str) -> Dict:
        """Analyze Indian stock using specialized Indian market analyzer"""
        return self.indian_analyzer.analyze_indian_stock(symbol)
    
    def get_indian_market_overview(self) -> Dict:
        """Get Indian market overview"""
        return self.indian_analyzer.get_indian_market_overview()
    
    def analyze_sector_rotation(self, market: str = 'US') -> Dict:
        """Analyze sector rotation and identify opportunities"""
        return self.sector_analyzer.analyze_sector_rotation(market)
    
    def get_sector_recommendations(self, market: str = 'US') -> Dict:
        """Get sector allocation recommendations"""
        return self.sector_analyzer.get_sector_recommendations(market)
    
    def optimize_portfolio(self, holdings: Dict[str, float], 
                          expected_returns: Dict[str, float]) -> Dict:
        """Optimize portfolio allocation"""
        return self.portfolio_optimizer.optimize_portfolio(holdings, expected_returns)
    
    def backtest_strategy(self, symbol: str, period: str = '1y') -> Dict:
        """Backtest a strategy on a stock"""
        try:
            data = self.data_layer.get_stock_data(symbol, period)
            signals = self.backtester.generate_signals_from_indicators(data)
            return self.backtester.backtest_strategy(data, signals)
        except Exception as e:
            return {'error': str(e)}
    
    def assess_portfolio_risk(self, holdings: Dict[str, float],
                            prices: Dict[str, float],
                            volatilities: Dict[str, float]) -> Dict:
        """Assess portfolio risk"""
        return self.risk_manager.assess_portfolio_risk(holdings, prices, volatilities)
    
    def calculate_position_size(self, portfolio_value: float, entry_price: float,
                               stop_loss: float, confidence: float = 0.5) -> Dict:
        """Calculate optimal position size"""
        return self.risk_manager.calculate_position_size(
            portfolio_value, entry_price, stop_loss, confidence
        )
    
    # New intelligence methods
    
    def get_composite_score(self, symbol: str) -> Dict:
        """
        Get composite score for an asset (0-100)
        
        Weights: 30% Technical + 25% Momentum + 20% Macro + 15% Fundamental + 10% ML
        """
        try:
            # Fetch data with caching
            stock_data = self._get_cached_stock_data(symbol)
            fundamentals = self.data_layer.get_fundamental_data(symbol)
            macro_data = self._get_cached_macro_data()  # Use cached macro data
            
            # Get component analyses
            technical = self.chart_analyzer.analyze_chart(stock_data, symbol)
            momentum = self.momentum_predictor.predict_momentum(stock_data, fundamentals.get('current_price', 0))
            
            # Get ML prediction
            ml_prediction = self.ml_predictor.predict(symbol)
            # Keep probability internally for scoring, but do NOT expose it in the API response
            # to avoid duplicate probability fields in the UI.
            ml_for_scoring = {
                "direction": ml_prediction.direction,
                "probability": ml_prediction.probability,
                "confidence": ml_prediction.confidence,
            }
            ml_for_response = {
                "direction": ml_prediction.direction,
                "confidence": ml_prediction.confidence,
            }
            
            # Calculate composite score
            composite = self.composite_scorer.calculate_composite_score(
                technical=technical,
                momentum=momentum,
                macro=macro_data,
                fundamental=fundamentals,
                ml_prediction=ml_for_scoring
            )
            
            # Generate insight
            insight = self.composite_scorer.generate_insight(composite, symbol)
            
            return {
                # Keep a single probability for UI: composite_score.ml_probability is a percent (0-100).
                # Do not duplicate the same probability in multiple scales.
                'composite_score': composite.__dict__,
                'insight': insight,
                'ml_prediction': ml_for_response
            }
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}
    
    def get_macro_intelligence(self) -> Dict:
        """Get comprehensive macro intelligence"""
        return self.macro_analyzer.get_macro_overview()
    
    def get_macro_scenarios(self) -> Dict:
        """Get forward-looking macro scenarios"""
        scenarios = self.macro_analyzer.generate_macro_scenarios()
        # `MacroAnalyzer.generate_macro_scenarios()` returns a list of dicts in this codebase.
        # Keep this endpoint tolerant in case the implementation returns dataclasses later.
        scenario_list = []
        for s in scenarios or []:
            if isinstance(s, dict):
                scenario_list.append(s)
            else:
                scenario_list.append(getattr(s, "__dict__", {"value": s}))
        return {
            'scenarios': scenario_list,
            'probability_matrix': self.scenario_analyzer.get_scenario_probability_matrix()
        }
    
    def analyze_multi_asset(self, symbol: str) -> Dict:
        """Analyze any asset class (equity, bond, commodity, crypto, forex)"""
        return self.multi_asset_analyzer.analyze_asset(symbol)
    
    def get_asset_scenarios(self, symbol: str) -> Dict:
        """Get forward-looking scenarios for a specific asset"""
        current_context = self.macro_analyzer.get_macro_overview()
        scenarios = self.scenario_analyzer.generate_scenarios(symbol, current_context)
        
        return {
            'base_case': scenarios.base_case.__dict__,
            'bull_case': scenarios.bull_case.__dict__,
            'bear_case': scenarios.bear_case.__dict__,
            'positioning': scenarios.recommended_positioning,
            'monitoring_points': scenarios.key_monitoring_points
        }
    
    def get_correlation_matrix(self, assets: list = None) -> Dict:
        """Get correlation matrix for asset universe"""
        return self.correlation_analyzer.calculate_correlation_matrix(assets)
    
    def assess_diversification(self, holdings: Dict[str, float]) -> Dict:
        """Assess portfolio diversification"""
        return self.correlation_analyzer.assess_portfolio_diversification(holdings)
    
    def get_allocation_recommendation(self, strategy: str = '60_40',
                                   signals: Dict = None) -> Dict:
        """
        Get asset allocation recommendation

        Strategies: 60_40, risk_parity, all_weather, tactical, economic_cycle
        """
        print(f"get_allocation_recommendation called with strategy: {strategy}")

        if strategy == '60_40':
            result = self.asset_allocator.get_60_40_allocation()
            print(f"60_40 result type: {type(result)}")
            return result.__dict__
        elif strategy == 'risk_parity':
            result = self.asset_allocator.get_risk_parity_allocation()
            print(f"risk_parity result type: {type(result)}")
            return result.__dict__
        elif strategy == 'all_weather':
            result = self.asset_allocator.get_all_weather_portfolio()
            print(f"all_weather result type: {type(result)}")
            return result.__dict__
        elif strategy == 'tactical':
            if signals is None:
                signals = {
                    'equity_signal': 'neutral',
                    'bond_signal': 'neutral',
                    'commodity_signal': 'neutral',
                    'risk_sentiment': 'neutral'
                }
            result = self.asset_allocator.get_tactical_allocation(signals)
            return result.__dict__
        elif strategy == 'economic_cycle':
            # Determine current cycle
            macro = self.macro_analyzer.get_macro_overview()
            cycle = macro.get('economic_cycle', {}).get('current_phase', 'expansion')
            result = self.asset_allocator.get_economic_cycle_allocation(cycle)
            return result.__dict__
        else:
            result = self.asset_allocator.get_60_40_allocation()
            return result.__dict__
    
    def compare_allocation_strategies(self) -> Dict:
        """Compare all allocation strategies"""
        return self.asset_allocator.compare_strategies()
    
    def get_risk_on_risk_off(self) -> Dict:
        """Get current risk-on/risk-off sentiment"""
        macro = self.macro_analyzer.get_macro_overview()
        risk_sentiment = macro.get('risk_sentiment', {})
        
        return {
            'sentiment': risk_sentiment.get('sentiment', 'neutral'),
            'vix': risk_sentiment.get('vix', 0),
            'interpretation': risk_sentiment.get('interpretation', ''),
            'implications': self._get_risk_sentiment_implications(risk_sentiment.get('sentiment', 'neutral'))
        }
    
    def _get_risk_sentiment_implications(self, sentiment: str) -> str:
        """Get implications of risk sentiment"""
        if sentiment == 'risk-on':
            return "Favor cyclical equities, emerging markets, commodities; reduce defensives"
        elif sentiment == 'risk-off':
            return "Favor quality bonds, defensives, cash; reduce cyclical exposure"
        else:
            return "Balanced allocation with moderate risk exposure"
