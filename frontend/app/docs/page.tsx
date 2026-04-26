'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { ChevronDown, ChevronRight, Brain, BarChart3, Globe, Zap, Activity, TrendingUp, Shield, Database, Cpu, ArrowLeft, Search, BookOpen, Code, Layers } from 'lucide-react'

interface Section {
  id: string
  title: string
  icon: any
  content: string
  subsections?: Subsection[]
}

interface Subsection {
  title: string
  content: string
  code?: string
}

export default function Documentation() {
  const router = useRouter()
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']))
  const [searchQuery, setSearchQuery] = useState('')

  const toggleSection = (id: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedSections(newExpanded)
  }

  const sections: Section[] = [
    {
      id: 'overview',
      title: 'System Overview',
      icon: Brain,
      content: 'The Financial Intelligence System is an institutional-grade market intelligence platform that combines machine learning, technical analysis, and macroeconomic insights to provide actionable investment recommendations. The system processes multiple asset classes (equities, bonds, commodities, crypto, forex) and generates probabilistic forecasts with calibrated confidence scores.',
      subsections: [
        {
          title: 'Architecture',
          content: 'The system follows a modular architecture with clear separation of concerns:\n\n1. **Data Layer** (`data_layer.py`): Handles all external data fetching with caching, rate limiting, and timeout enforcement. Supports yfinance (free) and Alpha Vantage (paid) as data providers.\n\n2. **Analyzer** (`analyzer.py`): Core intelligence system that orchestrates market analysis, composite scoring, and macro intelligence.\n\n3. **Composite Scorer** (`composite_scorer.py`): Calculates a unified 0-100 score combining technical, fundamental, and macro signals.\n\n4. **Probabilistic Forecaster** (`probabilistic_forecast.py`): Generates quantile-based return forecasts (p10, p50, p90) with calibrated direction probabilities.\n\n5. **Investment Recommender** (`investment_recommender.py`): Generates actionable buy/sell/hold recommendations with position sizing and risk management.\n\n6. **Risk Manager** (`risk_manager.py`): Implements volatility-targeted position sizing and portfolio risk controls.\n\n7. **Backtester** (`backtester.py`): Validates strategies with walk-forward evaluation and regime-specific hit rates.\n\n8. **Auto-Learning Store** (`auto_learning_store.py`): Tracks predictions and outcomes for continuous model improvement.\n\n9. **News Events** (`news_events.py`): Extracts and classifies news events with credibility weighting and sentiment analysis.'
        },
        {
          title: 'Data Flow',
          content: '1. **Data Ingestion**: Market data fetched via DataLayer with 10s timeout and quality safeguards\n2. **Signal Generation**: 40+ technical indicators computed from price/volume data\n3. **Composite Scoring**: Signals weighted and combined into 0-100 score\n4. **Probabilistic Forecasting**: Quantile-based return distribution estimated\n5. **Recommendation Generation**: Action (buy/sell/hold) determined with position sizing\n6. **Risk Management**: Volatility-targeted position sizes calculated\n7. **Persistence**: Predictions logged to AutoLearningStore for continuous learning'
        }
      ]
    },
    {
      id: 'algorithms',
      title: 'Algorithms & Calculations',
      icon: Cpu,
      content: 'The system employs a combination of statistical methods, machine learning techniques, and domain-specific financial algorithms.',
      subsections: [
        {
          title: 'Composite Score Calculation',
          content: 'The composite score (0-100) is a weighted combination of multiple signal categories:\n\n**Technical Signals (40% weight)**:\n- RSI (Relative Strength Index): Momentum oscillator measuring overbought/oversold conditions\n- MACD: Trend-following momentum indicator\n- Bollinger Bands: Volatility-based price bands\n- Moving Averages (SMA, EMA): Trend identification\n- Volume indicators: OBV, Volume Rate of Change\n\n**Fundamental Signals (30% weight)**:\n- P/E Ratio: Price-to-earnings valuation\n- P/B Ratio: Price-to-book valuation\n- Dividend Yield: Income component\n- Debt-to-Equity: Financial health\n- ROE: Return on equity\n\n**Macro Signals (30% weight)**:\n- Interest rate environment\n- Inflation trends\n- Economic cycle position\n- Market sentiment indicators\n\n**Formula**:\n```\nComposite Score = 0.4 * Technical_Score + 0.3 * Fundamental_Score + 0.3 * Macro_Score\n\nWhere each component is normalized to 0-100 range based on historical percentiles\n```'
        },
        {
          title: 'Probabilistic Forecasting',
          content: 'The system uses empirical quantile estimation for robust probabilistic forecasting:\n\n**Method**:\n1. Calculate historical returns over the forecast horizon\n2. Compute empirical quantiles (p10, p50, p90) from historical distribution\n3. Adjust direction probability based on composite score\n4. Apply calibration to reduce overconfidence\n\n**Calibration**:\n```\nCalibrated_Prob = Raw_Prob + (Avg_Actual - Avg_Predicted) * 0.3\n\nWhere:\n- Avg_Actual: Average of recent actual outcomes (0 or 1)\n- Avg_Predicted: Average of recent predicted probabilities\n- 0.3: Conservative correction factor (bounded to ±10%)\n```\n\n**Forecast Distribution**:\n- p10: 10th percentile return (bearish scenario)\n- p50: 50th percentile return (median/expected)\n- p90: 90th percentile return (bullish scenario)\n- direction_up_prob: Calibrated probability of positive return'
        },
        {
          title: 'Volatility-Targeted Position Sizing',
          content: 'Position sizes are calculated using volatility targeting to maintain consistent risk exposure:\n\n**Formula**:\n```\nVol_Scale = Target_Vol / Current_Vol\nEffective_Budget = Base_Budget * Vol_Scale * Confidence_Scale\nPosition_Size = Portfolio_Value * Effective_Budget / Entry_Price\n\nWhere:\n- Target_Vol: Target annualized volatility (default 15%)\n- Current_Vol: Current asset volatility (252 * daily_std)\n- Base_Budget: Per-trade risk budget (default 2% of portfolio)\n- Confidence_Scale: 0.75 + 0.5 * confidence (0.775 to 1.225)\n- Vol_Scale: Bounded to [0.25, 2.0] to prevent extreme sizes\n```\n\n**Risk Controls**:\n- Maximum position size: 20% of portfolio\n- Minimum position size: 1% of portfolio\n- Stop loss: Based on p10 quantile or ATR-based\n- Take profit: Based on p90 quantile or risk-reward ratio'
        },
        {
          title: 'Regime Detection',
          content: 'Market regimes are detected using volatility and trend analysis:\n\n**Regime Classification**:\n```\nRegime = f(Volatility, Trend)\n\nWhere:\n- Volatility: Rolling 63-day standard deviation of returns\n- Trend: (MA_short - MA_long) / MA_long\n\nClassification Rules:\n- Bull: Trend > 2% AND Volatility < 70th percentile\n- Bear: Trend < -2% OR (Volatility > 70th percentile AND Trend < 0)\n- Sideways: All other conditions\n```\n\n**Purpose**: Regime-specific hit rates are tracked to understand strategy performance across different market conditions.'
        },
        {
          title: 'News Event Classification',
          content: 'News headlines are classified using keyword-based event detection with severity weighting:\n\n**Event Taxonomy**:\n- Management Change (CEO, CFO resignations/appointments)\n- Earnings Guidance (raises, cuts, beats, misses)\n- M&A Activity (acquisitions, mergers)\n- Regulatory Actions (SEC, FTC investigations)\n- Litigation (lawsuits, settlements)\n- Product Launches (new product introductions)\n- R&D Breakthroughs (patents, innovations)\n- Funding Events (investment rounds)\n- Geopolitical Exposure (sanctions, tariffs)\n- Supply Chain Issues (disruptions, shortages)\n- Market Reactions (surges, crashes)\n- Dividend Changes (increases, cuts)\n- Credit Rating Changes (upgrades, downgrades)\n- Labor Issues (strikes, layoffs)\n- Commodity Impact (oil, energy prices)\n\n**Credibility Weighting**:\n- Trusted sources (Reuters, Bloomberg, WSJ): 1.0\n- Moderate sources (Yahoo Finance, MarketWatch): 0.8\n- Questionable sources (blogs, social media): 0.5\n- Unknown sources: 0.7\n\n**Effective Sentiment**:\n```\nEffective = (0.7 * Headline_Sentiment + 0.3 * Event_Score) * Credibility * Recency * Severity_Boost\n\nWhere Severity_Boost = 1.15 if high-severity events present, else 1.0\n```'
        }
      ]
    },
    {
      id: 'modules',
      title: 'Module Details',
      icon: Database,
      content: 'Detailed description of each system module and its purpose.',
      subsections: [
        {
          title: 'Data Layer (data_layer.py)',
          content: '**Purpose**: Centralized data access layer with caching, rate limiting, and timeout enforcement.\n\n**Key Features**:\n- Timeout guards: get_stock_data (10s), get_quote (5s), get_fundamental_data (8s)\n- Data quality safeguards: Missing value handling, outlier detection, consistency validation\n- Caching: TTL-based caching for all data types\n- Rate limiting: Alpha Vantage 12-second minimum between requests\n- Fallback logic: Graceful degradation when providers fail\n\n**Data Quality Safeguards**:\n- Remove rows with missing critical data (Open, High, Low, Close)\n- Forward-fill remaining missing values\n- Validate price positivity and High >= Low\n- Remove extreme outliers (>10x or <0.1x median)\n- Ensure minimum 20 data points'
        },
        {
          title: 'Composite Scorer (composite_scorer.py)',
          content: '**Purpose**: Calculate unified 0-100 score combining multiple signal categories.\n\n**Signal Categories**:\n1. **Momentum (15 points)**: RSI, MACD, Rate of Change\n2. **Trend (15 points)**: Moving averages, ADX, Parabolic SAR\n3. **Volume (10 points)**: OBV, Volume Rate of Change, Volume Profile\n4. **Volatility (10 points)**: ATR, Bollinger Bands, Historical Volatility\n5. **Fundamental (25 points)**: P/E, P/B, Dividend Yield, ROE, Debt/Equity\n6. **Macro (25 points)**: Interest rates, Inflation, Economic indicators\n\n**Scoring Logic**:\n- Each signal normalized to 0-100 based on historical percentiles\n- Signals weighted by category importance\n- Final score bounded to 0-100 range\n- Scores > 50: Bullish bias\n- Scores < 50: Bearish bias'
        },
        {
          title: 'Probabilistic Forecaster (probabilistic_forecast.py)',
          content: '**Purpose**: Generate quantile-based return forecasts with calibrated probabilities.\n\n**Method**:\n- Empirical quantile estimation from historical returns\n- No heavy ML dependencies (robust and explainable)\n- Probability calibration to reduce overconfidence\n\n**Calibration Mechanism**:\n- Tracks last 100 predictions with actual outcomes\n- Computes average prediction vs actual difference\n- Applies 30% correction factor (bounded to ±10%)\n- Prevents extreme probability shifts\n\n**Output**:\n- ForecastDistribution dataclass with:\n  - horizon_days: Forecast horizon\n  - p10, p50, p90: Return quantiles\n  - direction_up_prob: Calibrated up probability'
        },
        {
          title: 'Investment Recommender (investment_recommender.py)',
          content: '**Purpose**: Generate actionable buy/sell/hold recommendations with position sizing.\n\n**Recommendation Logic**:\n1. Calculate composite score for candidate symbols\n2. Generate probabilistic forecast\n3. Determine action based on score and probability:\n   - Score > 60 & up_prob > 0.6: BUY\n   - Score < 40 & up_prob < 0.4: SELL\n   - Otherwise: HOLD\n4. Calculate position size using volatility targeting\n5. Set stop loss at p10 or ATR-based level\n6. Set take profit at p90 or risk-reward ratio\n\n**Portfolio Context**:\n- Considers existing holdings\n- Estimates portfolio value\n- Adjusts for cash available\n- Limits concentration risk'
        },
        {
          title: 'Risk Manager (risk_manager.py)',
          content: '**Purpose**: Implement volatility-targeted position sizing and portfolio risk controls.\n\n**Key Functions**:\n- calculate_position_size_vol_target: Volatility-based sizing\n- calculate_stop_loss: ATR-based stop levels\n- calculate_take_profit: Risk-reward based targets\n- assess_portfolio_risk: Overall portfolio risk metrics\n\n**Risk Parameters**:\n- max_portfolio_risk: Maximum portfolio risk (default 2%)\n- min_risk_per_trade: Minimum per-trade risk (0.5%)\n- max_risk_per_trade: Maximum per-trade risk (3%)\n- target_annual_vol: Target volatility (15%)\n- atr_multiplier: ATR multiplier for stops (default 2.0)'
        },
        {
          title: 'Backtester (backtester.py)',
          content: '**Purpose**: Validate strategies with walk-forward evaluation and regime-specific analysis.\n\n**Backtesting Method**:\n1. Simulate trades based on historical signals\n2. Track equity curve and trade-level P&L\n3. Calculate performance metrics:\n   - Total return, annualized return\n   - Max drawdown\n   - Sharpe ratio\n   - Win rate, profit factor\n   - Average win/loss\n4. Regime-specific hit rates:\n   - Bull market hit rate\n   - Bear market hit rate\n   - Sideways market hit rate\n\n**Regime Detection**:\n- Uses 63-day rolling volatility\n- Trend based on moving average slope\n- Classifies as bull/bear/sideways'
        },
        {
          title: 'Auto-Learning Store (auto_learning_store.py)',
          content: '**Purpose**: Track predictions and outcomes for continuous model improvement.\n\n**Storage Options**:\n- Supabase Postgres (durable, production)\n- In-memory fallback (development)\n\n**Data Tracked**:\n- Prediction ID, timestamp, symbol\n- Predicted direction, probability, confidence\n- Model used, features\n- Actual direction, return (when available)\n\n**Metrics Generated**:\n- Accuracy, precision, recall, F1\n- Sharpe ratio, max drawdown\n- Win rate, total predictions\n- Rolling metrics over time window'
        },
        {
          title: 'News Events (news_events.py)',
          content: '**Purpose**: Extract and classify news events with credibility weighting.\n\n**Event Detection**:\n- Keyword-based pattern matching\n- 15 event types with severity levels\n- Directional polarity assignment\n- Confidence scoring based on keyword matches\n\n**Credibility Weighting**:\n- Source reputation assessment\n- Trusted, moderate, questionable categories\n- Recency decay (3-day half-life)\n\n**Sentiment Analysis**:\n- TextBlob-based sentiment (if available)\n- Keyword-based fallback\n- Event-polarity adjustment\n- Severity boost for high-impact events'
        }
      ]
    },
    {
      id: 'api',
      title: 'API Endpoints',
      icon: Zap,
      content: 'RESTful API endpoints for accessing system functionality.',
      subsections: [
        {
          title: 'Market Intelligence',
          content: '**GET /intelligence/{symbol}**\n- Get composite score and insight for a symbol\n- Timeout: 15 seconds\n- Returns: score, insight, confidence, signals\n\n**GET /macro**\n- Get macro intelligence overview\n- Timeout: 12 seconds\n- Returns: rates, inflation, economic indicators\n\n**GET /intelligence-feed**\n- Get live intelligence feed with alerts\n- Timeout: 10 seconds\n- Returns: list of real-time alerts'
        },
        {
          title: 'Recommendations',
          content: '**GET /recommendations**\n- Get investment recommendations\n- Parameters: limit (max 80), cash_available\n- Timeout: 15 seconds\n- Returns: list of recommendations with action, position size, stop/target\n\n**GET /opportunities**\n- Scan opportunities for multiple symbols\n- Parameters: symbols (comma-separated, max 20)\n- Returns: opportunities for each symbol'
        },
        {
          title: 'Data Access',
          content: '**GET /history/{symbol}**\n- Get historical stock data\n- Parameters: period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)\n- Returns: OHLCV data\n\n**GET /quote/{symbol}**\n- Get current quote\n- Returns: price, change, volume, market cap\n\n**GET /companies**\n- Get available companies\n- Parameters: limit (max 2000), market (US, IN, ALL)\n- Returns: list of companies with symbol, sector'
        },
        {
          title: 'Auto-Learning',
          content: '**POST /auto-learning/prediction**\n- Log a prediction\n- Body: symbol, predicted_direction, predicted_probability, confidence, model_used, features\n- Returns: prediction_id\n\n**POST /auto-learning/outcome**\n- Record outcome for a prediction\n- Body: prediction_id, actual_direction, actual_return\n- Returns: success status\n\n**GET /auto-learning/report**\n- Get learning report\n- Parameters: window_size (20-5000)\n- Returns: accuracy, precision, recall, sharpe, max_drawdown, win_rate\n\n**POST /learning/outcome**\n- Record outcome (alias for /auto-learning/outcome)\n\n**GET /learning/report**\n- Get learning report (alias for /auto-learning/report)'
        },
        {
          title: 'Health & Status',
          content: '**GET /health**\n- Lightweight health check\n- Returns: status, version, pid, uptime_s, timestamp\n- No external dependencies'
        }
      ]
    },
    {
      id: 'reliability',
      title: 'Reliability Features',
      icon: Shield,
      content: 'Production-grade reliability features implemented in Phase 1.',
      subsections: [
        {
          title: 'Timeout Enforcement',
          content: 'All external API calls have timeout guards:\n- get_stock_data: 10 seconds\n- get_quote: 5 seconds\n- get_fundamental_data: 8 seconds\n- Intelligence endpoints: 12-15 seconds\n- Returns 504 on timeout with partial data fallback'
        },
        {
          title: 'Data Layer Abstraction',
          content: 'All market data routed through DataLayer:\n- Consistent caching across all endpoints\n- Unified timeout handling\n- Graceful fallback to alternate providers\n- Data quality safeguards applied universally'
        },
        {
          title: 'Background Persistence',
          content: 'Database operations moved off request path:\n- Recommendations saved via background tasks\n- Non-blocking for user responses\n- Best-effort logging (system continues if DB fails)'
        },
        {
          title: 'Frontend Resilience',
          content: 'Dashboard uses Promise.allSettled for concurrent requests:\n- Individual panel failures don\'t break entire page\n- Per-panel error states with visual indicators\n- API connection status indicator (green/red/yellow)\n- 30-second Axios timeout'
        }
      ]
    }
  ]

  const filteredSections = sections.filter(section => {
    const query = searchQuery.toLowerCase()
    return section.title.toLowerCase().includes(query) || 
           section.content.toLowerCase().includes(query) ||
           section.subsections?.some(sub => 
             sub.title.toLowerCase().includes(query) || 
             sub.content.toLowerCase().includes(query)
           )
  })

  return (
    <div className="min-h-screen bg-background text-text-primary p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex items-center gap-4"
        >
          <button
            onClick={() => router.push('/')}
            className="p-2 hover:bg-panel-bg rounded-lg transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">System Documentation</h1>
            <p className="text-text-secondary">Comprehensive documentation of algorithms, calculations, and module purposes</p>
          </div>
        </motion.div>

        {/* Search Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-secondary" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search documentation..."
              className="w-full pl-12 pr-4 py-3 bg-panel-bg rounded-lg text-text-primary border border-white/10 focus:border-accent outline-none"
            />
          </div>
        </motion.div>

        {/* Quick Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid md:grid-cols-4 gap-4 mb-8"
        >
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="w-5 h-5 text-accent" />
              <span className="text-text-secondary text-sm">Sections</span>
            </div>
            <div className="text-2xl font-bold">{sections.length}</div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Layers className="w-5 h-5 text-accent" />
              <span className="text-text-secondary text-sm">Subsections</span>
            </div>
            <div className="text-2xl font-bold">{sections.reduce((acc, s) => acc + (s.subsections?.length || 0), 0)}</div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Code className="w-5 h-5 text-accent" />
              <span className="text-text-secondary text-sm">Code Examples</span>
            </div>
            <div className="text-2xl font-bold">{sections.reduce((acc, s) => acc + (s.subsections?.filter(sub => sub.code).length || 0), 0)}</div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Database className="w-5 h-5 text-accent" />
              <span className="text-text-secondary text-sm">Modules</span>
            </div>
            <div className="text-2xl font-bold">9</div>
          </div>
        </motion.div>

        {/* Documentation Sections */}
        <div className="space-y-4">
          {filteredSections.map((section, index) => (
            <motion.div
              key={section.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="glass rounded-xl overflow-hidden border border-transparent hover:border-accent/30 transition-all"
            >
              <button
                onClick={() => toggleSection(section.id)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-accent/5 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-accent/20 rounded-lg">
                    <section.icon className="w-5 h-5 text-accent" />
                  </div>
                  <h2 className="text-xl font-semibold">{section.title}</h2>
                </div>
                {expandedSections.has(section.id) ? (
                  <ChevronDown className="w-5 h-5 text-text-secondary" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-text-secondary" />
                )}
              </button>

              {expandedSections.has(section.id) && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="px-6 pb-6"
                >
                  <p className="text-text-secondary mb-6 whitespace-pre-line leading-relaxed">{section.content}</p>
                  
                  {section.subsections && section.subsections.map((subsection, idx) => (
                    <div key={idx} className="mb-6 last:mb-0 p-4 bg-panel-bg/50 rounded-lg">
                      <h3 className="text-lg font-semibold mb-3 text-accent flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-accent"></span>
                        {subsection.title}
                      </h3>
                      <p className="text-text-secondary whitespace-pre-line mb-3 leading-relaxed">{subsection.content}</p>
                      {subsection.code && (
                        <div className="relative">
                          <pre className="bg-black/50 rounded-lg p-4 overflow-x-auto text-sm border border-white/10">
                            <code className="text-green-400 font-mono">{subsection.code}</code>
                          </pre>
                        </div>
                      )}
                    </div>
                  ))}
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>

        {filteredSections.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20 text-text-secondary"
          >
            <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg">No results found for "{searchQuery}"</p>
          </motion.div>
        )}
      </div>
    </div>
  )
}
