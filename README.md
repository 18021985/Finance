# Financial Intelligence System

An institutional-grade financial intelligence and advisory platform that generates multi-layered market intelligence, signals, and forward-looking insights using only free APIs.

## Positioning

**This is NOT a trading platform.** It is a sophisticated financial intelligence system designed to:
- Generate market insights based on technical, fundamental, and macro indicators
- Provide opportunity signals with probability-based evaluation
- Assess risk and exposure
- Generate forward-looking scenarios based on economic conditions
- Offer strategic allocation suggestions for short, medium, and long-term horizons

**All outputs use advisory language:** "consider", "potential opportunity", "risk scenario" - never "execute trade".

## Features

### Core Intelligence
- **Composite Scoring System**: Unified 0-100 score (30% Technical + 25% Momentum + 20% Macro + 15% Fundamental + 10% ML)
- **40+ Signal Analysis**: Macro, Technical, Fundamental, Sentiment, and Management categories
- **Investment Opportunities**: Scan multiple assets for high-probability setups
- **Market Overview**: Track major indices and macro indicators
- **Smart Scoring**: Weighted signal scoring with conflict detection
- **Forecasts**: Short-term (0-3 months) and long-term (1-5 years) predictions

### Advanced Analytics
- **Momentum Prediction**: ROC analysis, momentum oscillator, trend strength, velocity, volume momentum
- **Chart Pattern Recognition**: Double top/bottom, head & shoulders, triangles, flags
- **Support/Resistance Levels**: Automatic identification with strength scoring
- **Investment Horizon Analysis**: Separate short-term (3-6 months) and long-term (3-5 years) opportunities
- **Action Advisor**: Buy/sell/hold recommendations with timing advice

### Multi-Asset Coverage
- **Equities**: US and Indian stocks with full fundamental analysis
- **Bonds**: Government and corporate bonds with yield analysis
- **Commodities**: Gold, oil, metals, agriculture with seasonal patterns
- **Crypto**: Bitcoin, Ethereum with on-chain metrics
- **Forex**: Currency pairs with rate differential analysis

### Bank-Level Macro Analysis
- **Interest Rates**: Fed, ECB, BOE, BOJ policy rates and stances
- **Inflation**: CPI, PPI trends and expectations
- **Central Bank Policies**: Hawkish/dovish stances, meeting schedules
- **Yield Curve**: 2y/10y spread, recession indicators
- **Risk Sentiment**: VIX analysis, risk-on/risk-off indicators
- **Economic Cycle**: Expansion, peak, contraction, trough identification

### Scenario Analysis
- **Forward-Looking Scenarios**: Base case, bull case, bear case with probabilities
- **Macro Scenarios**: Disinflation, stagflation, growth scare, policy error
- **IF-THEN Logic**: "IF inflation rises → THEN bonds fall, USD rises"
- **Cross-Asset Implications**: Each scenario's impact on all asset classes

### Portfolio Management
- **Asset Allocation Models**: 60/40, Risk Parity, All-Weather, Tactical, Economic Cycle
- **Diversification Analysis**: Correlation matrix, concentration risk
- **Portfolio Optimization**: Mean-variance optimization, rebalancing
- **Risk Assessment**: VaR calculation, exposure analysis, position sizing

### Sector Analysis
- **US Sectors**: Technology, Financials, Healthcare, Energy, etc.
- **Indian Sectors**: NIFTY IT, Bank, FMCG, Auto, Pharma
- **Sector Rotation**: Identify overweight/underweight sectors
- **Allocation Recommendations**: Strategic sector positioning

### Monitoring
- **Alert System**: Price alerts, signal alerts, pattern detection
- **Risk Management**: Trade validation, exposure limits

### Free APIs Only
- Uses yfinance (unlimited) and Alpha Vantage (free tier)
- No paid API subscriptions required

## Architecture

### Intelligence Platform Layers

```
Data Sources
├── Market Data (price, volume) - yfinance
├── Macro Data (rates, inflation) - yfinance
├── Fundamentals (earnings) - yfinance, Alpha Vantage
└── Alternative Data (sentiment) - yfinance news
    ↓
Processing Layers
├── Technical Engine (indicators, patterns)
├── Fundamental Engine (valuation, growth)
├── Macro Engine (rates, central banks, cycle)
└── ML Prediction Layer (probabilistic signals)
    ↓
Insight Engine
├── Signal Scoring (composite 0-100)
├── Scenario Analysis (IF-THEN logic)
└── Risk Evaluation (VaR, exposure)
    ↓
Output
├── Market Insights
├── Opportunity Signals
├── Risk Alerts
└── Forward Scenarios
```

### Components

#### Core Intelligence
1. **Composite Scorer** (`composite_scorer.py`)
   - Unified 0-100 score
   - Weights: 30% Technical + 25% Momentum + 20% Macro + 15% Fundamental + 10% ML
   - Trend, momentum, macro alignment, fundamental strength assessments
   - Insight generation with strategic considerations

2. **Macro Analyzer** (`macro_analyzer.py`)
   - Interest rate analysis (Fed, ECB, BOE, BOJ)
   - Inflation trends (CPI, PPI)
   - Central bank policy stances
   - Yield curve dynamics (2y/10y spread)
   - Risk sentiment (VIX, risk-on/risk-off)
   - Economic cycle identification
   - Forward-looking macro scenarios

3. **Multi-Asset Analyzer** (`multi_asset_analyzer.py`)
   - Equities (stocks)
   - Bonds (government, corporate)
   - Commodities (gold, oil, metals, agriculture)
   - Crypto (BTC, ETH)
   - Forex (currency pairs)
   - Asset-class-specific analysis

4. **Scenario Analyzer** (`scenario_analyzer.py`)
   - Base case, bull case, bear case generation
   - Probability-based scenarios
   - IF-THEN forward logic
   - Cross-asset implications
   - Key monitoring points

5. **Correlation Analyzer** (`correlation_analyzer.py`)
   - Cross-asset correlation matrix
   - Rolling correlation analysis
   - Regime change detection
   - Diversification assessment
   - Concentration risk identification

6. **Asset Allocator** (`asset_allocator.py`)
   - 60/40 portfolio
   - Risk parity
   - All-weather portfolio
   - Tactical asset allocation
   - Economic cycle positioning
   - Strategy comparison

#### Core Analysis (Existing)
7. **Data Layer** (`data_layer.py`)
   - yfinance for stock data (unlimited, free)
   - Alpha Vantage for fundamentals (25 requests/day free tier)
   - News sentiment via yfinance news

8. **Signal Engine** (`signal_engine.py`)
   - 40 signals (20 bullish, 20 bearish)
   - Categories: Macro, Technical, Fundamental, Sentiment, Management

9. **Technical Indicators** (`technical_indicators.py`)
   - Moving averages (50/200 day)
   - RSI, MACD, ADX, Bollinger Bands
   - Support/Resistance levels
   - ATR for volatility

10. **Scoring Model** (`scoring_model.py`)
    - Weighted score = Strength × Confidence
    - Conflict detection and adjustment

11. **Decision Logic** (`decision_logic.py`)
    - Net score interpretation
    - Verdict generation (Strong Buy to Strong Sell)

12. **Context Integration** (`context_integration.py`)
    - Geopolitical context adjustments
    - Sentiment credibility weighting

#### Advanced Analytics
13. **Momentum Predictor** (`momentum_predictor.py`)
    - Rate of Change (ROC) analysis
    - Momentum oscillator
    - Trend strength and velocity
    - Volume momentum

14. **Chart Analyzer** (`chart_analyzer.py`)
    - Chart pattern recognition
    - Support/resistance level detection
    - Trend analysis
    - Volume analysis

15. **Investment Horizon Analyzer** (`investment_horizon_analyzer.py`)
    - Short-term opportunities (3-6 months)
    - Long-term opportunities (3-5 years)
    - Entry/target/stop-loss levels

16. **Action Advisor** (`action_advisor.py`)
    - Buy/sell/hold recommendations
    - Timing advice
    - Position sizing

#### Market Coverage
17. **Indian Market Analyzer** (`indian_market_analyzer.py`)
    - NSE/BSE stock analysis
    - Indian sector indices

18. **Sector Analyzer** (`sector_analyzer.py`)
    - US sector ETFs
    - Indian sector indices
    - Sector rotation signals

#### Portfolio Management
19. **Portfolio Optimizer** (`portfolio_optimizer.py`)
    - Mean-variance optimization
    - Rebalancing recommendations
    - Diversification assessment

20. **Risk Manager** (`risk_manager.py`)
    - Position sizing
    - Stop-loss calculation
    - Portfolio risk assessment
    - VaR calculation

21. **Backtester** (`backtester.py`)
    - Strategy backtesting
    - Performance metrics

22. **Alert System** (`alert_system.py`)
    - Price alerts
    - Signal alerts
    - Pattern alerts

#### API
23. **FastAPI Server** (`api.py`)
    - REST API endpoints
    - JSON and Markdown output formats
    - CORS enabled
    - Interactive Swagger documentation

## Setup

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Clone the repository:
```bash
cd quant-investment-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (optional):
```bash
cp .env.example .env
```

Edit `.env` and add your free API keys:
- **Alpha Vantage** (optional): Get free key at https://www.alphavantage.co/support/#api-key
  - Without this, the system falls back to yfinance for fundamentals
- **NewsAPI** (optional): Get free key at https://newsapi.org/register
  - Without this, uses yfinance news

Note: The system works with just yfinance (no API keys required). Alpha Vantage and NewsAPI are optional enhancements.

## Usage

### Start the Server

```bash
python api.py
```

The server will start at `http://localhost:8000`

### API Endpoints

#### 1. Analyze a Company

**POST** `/analyze`
```json
{
  "symbol": "AAPL",
  "format": "json"
}
```

**GET** `/analyze/{symbol}?format=json`
```
GET /analyze/AAPL?format=json
```

**Response:**
```json
{
  "symbol": "AAPL",
  "company": {
    "name": "Apple Inc.",
    "sector": "Technology",
    "current_price": 150.25,
    ...
  },
  "scores": {
    "bullish_score": 45.5,
    "bearish_score": 20.3,
    "net_score": 25.2,
    "signal_ratio": 0.69
  },
  "bullish_indicators": [...],
  "bearish_indicators": [...],
  "forecast": {
    "short_term": {...},
    "long_term": {...}
  },
  "key_drivers": {...},
  "verdict": {
    "verdict": "Buy",
    "direction": "Bullish",
    "probability": 0.65
  }
}
```

#### 2. Market Overview

**GET** `/market-overview`

Returns major indices (S&P 500, NASDAQ, DOW, NIFTY) and macro indicators.

#### 3. Scan Opportunities

**POST** `/scan`
```json
{
  "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA"]
}
```

**GET** `/opportunities?symbols=AAPL,GOOGL,MSFT,TSLA`

Returns symbols sorted by net score (highest first).

#### 1. Composite Intelligence (NEW)

**GET** `/intelligence/{symbol}`
```
GET /intelligence/AAPL
```

Returns composite score (0-100) with component breakdown:
- Technical score (30%)
- Momentum score (25%)
- Macro alignment (20%)
- Fundamental strength (15%)
- ML probability (10%)

**Response:**
```json
{
  "composite_score": {
    "total_score": 74,
    "technical_score": 78,
    "momentum_score": 72,
    "macro_score": 65,
    "fundamental_score": 80,
    "ml_probability": 68,
    "trend": "bullish",
    "momentum": "strong",
    "macro_alignment": "aligned",
    "fundamental_strength": "strong",
    "confidence": 0.72
  },
  "insight": {
    "assessment": "Favorable setup with moderate strength across factors",
    "strategic_consideration": "Potential opportunity exists, consider selective exposure with risk management",
    "key_drivers": ["Strong technical trend", "Positive momentum", "Solid fundamentals"],
    "key_risks": []
  }
}
```

#### 2. Macro Intelligence (NEW)

**GET** `/macro`

Returns comprehensive macro analysis:
- Interest rates (Fed, ECB, BOE, BOJ)
- Inflation trends
- Central bank policies
- Yield curve dynamics
- Risk sentiment (VIX)
- Economic cycle phase

**GET** `/macro/scenarios`

Returns forward-looking macro scenarios:
- Disinflation (40% prob)
- Stagflation (15% prob)
- Growth scare (25% prob)
- Policy error (10% prob)
- Supply shock (10% prob)

Each scenario includes cross-asset implications.

#### 3. Multi-Asset Analysis (NEW)

**GET** `/multi-asset/{symbol}`

Analyze any asset class:
- Equities: AAPL, GOOGL, etc.
- Bonds: TLT, IEF, LQD
- Commodities: GLD, USO, SLV
- Crypto: BTC-USD, ETH-USD
- Forex: EURUSD=X, GBPUSD=X

**Response:**
```json
{
  "asset": "BTC-USD",
  "asset_class": "crypto",
  "current_price": 45000,
  "technical": {...},
  "volatility": 0.85,
  "insight": "Positive trend with high volatility - size positions accordingly",
  "strategic_consideration": "High volatility asset - limit allocation, use risk management"
}
```

#### 4. Scenario Analysis (NEW)

**GET** `/scenarios/{symbol}`

Returns forward-looking scenarios for a specific asset:
- Base case (most likely)
- Bull case (optimistic)
- Bear case (pessimistic)
- Recommended positioning
- Key monitoring points

#### 5. Correlation Analysis (NEW)

**GET** `/correlation?assets=SPY,TLT,GLD,BTC-USD`

Returns cross-asset correlation matrix with:
- Average correlation
- Highest/lowest correlations
- Diversification opportunities
- Concentration risks

**POST** `/diversification`
```json
{
  "holdings": {"AAPL": 0.3, "GOOGL": 0.2, "TLT": 0.3, "GLD": 0.2}
}
```

Assesses portfolio diversification and provides recommendations.

#### 6. Asset Allocation (NEW)

**GET** `/allocation/{strategy}`

Strategies:
- `60_40` - Classic 60/40 portfolio
- `risk_parity` - Equal risk contribution
- `all_weather` - All-weather portfolio
- `tactical` - Dynamic based on signals
- `economic_cycle` - Based on current cycle

**GET** `/allocation/compare`

Compare all strategies by expected return, volatility, and Sharpe ratio.

#### 7. Risk Sentiment (NEW)

**GET** `/risk-sentiment`

Returns current risk-on/risk-off indicators:
- VIX level
- Sentiment interpretation
- Asset implications

#### 8. Enhanced Analysis

**GET** `/analyze/{symbol}/enhanced`

Comprehensive analysis including:
- Base signal analysis
- Momentum prediction
- Chart pattern recognition
- Action advice with timing
- Short-term and long-term investment opportunities

#### 9. Indian Market Analysis

**GET** `/indian/analyze/{symbol}`
```
GET /indian/analyze/RELIANCE.NS
```

**GET** `/indian/overview`
- NIFTY 50, NIFTY Bank, NIFTY IT, sector indices

#### 10. Sector Analysis

**GET** `/sectors/rotation?market=US`
- Analyze sector rotation across US or Indian markets

**GET** `/sectors/recommendations?market=US`
- Get sector allocation recommendations

#### 11. Portfolio Management

**POST** `/portfolio/optimize`
```json
{
  "holdings": {"AAPL": 0.3, "GOOGL": 0.2, "MSFT": 0.15},
  "expected_returns": {"AAPL": 0.15, "GOOGL": 0.12, "MSFT": 0.10}
}
```

**POST** `/portfolio/risk`
```json
{
  "holdings": {"AAPL": 100, "GOOGL": 50},
  "prices": {"AAPL": 150.0, "GOOGL": 120.0},
  "volatilities": {"AAPL": 0.25, "GOOGL": 0.30}
}
```

**POST** `/position-size`
```json
{
  "portfolio_value": 100000,
  "entry_price": 150.0,
  "stop_loss": 140.0,
  "confidence": 0.7
}
```

#### 12. Backtesting

**GET** `/backtest/{symbol}?period=1y`
- Backtest strategy on historical data

#### 13. Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI.

## Example Usage

### Python Script

```python
from analyzer import FinancialAnalyzer

# Initialize analyzer
analyzer = FinancialAnalyzer()

# Basic analysis
result = analyzer.analyze_company("AAPL", format="json")
print(f"Verdict: {result['verdict']['verdict']}")
print(f"Net Score: {result['scores']['net_score']}")

# Enhanced analysis with momentum and chart patterns
enhanced = analyzer.analyze_company_enhanced("AAPL")
print(f"Momentum: {enhanced['momentum']['current_momentum']['direction']}")
print(f"Action: {enhanced['action_advice']['action']}")

# Indian market analysis
indian_result = analyzer.analyze_indian_stock("RELIANCE.NS")
print(f"Indian Stock: {indian_result.get('name', 'N/A')}")

# Sector rotation
sectors = analyzer.analyze_sector_rotation(market="US")
print(f"Top Sector: {sectors['top_sectors'][0]['sector']}")

# Portfolio optimization
holdings = {"AAPL": 0.3, "GOOGL": 0.2, "MSFT": 0.15}
returns = {"AAPL": 0.15, "GOOGL": 0.12, "MSFT": 0.10}
optimization = analyzer.optimize_portfolio(holdings, returns)
print(f"Optimized Sharpe: {optimization['optimized_portfolio']['sharpe_ratio']}")

# Position sizing
position = analyzer.calculate_position_size(100000, 150, 140, 0.7)
print(f"Recommended shares: {position['shares']}")
print(f"Position size: {position['position_size_pct']}%")

# Backtesting
backtest = analyzer.backtest_strategy("AAPL", period="1y")
print(f"Strategy Return: {backtest['total_return']}%")
print(f"Sharpe Ratio: {backtest['sharpe_ratio']}")
```

### cURL

```bash
# Analyze Apple
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "format": "json"}'

# Enhanced analysis
curl "http://localhost:8000/analyze/AAPL/enhanced"

# Indian market analysis
curl "http://localhost:8000/indian/analyze/RELIANCE.NS"

# Sector rotation
curl "http://localhost:8000/sectors/rotation?market=US"

# Portfolio optimization
curl -X POST "http://localhost:8000/portfolio/optimize" \
  -H "Content-Type: application/json" \
  -d '{"holdings": {"AAPL": 0.3, "GOOGL": 0.2}, "expected_returns": {"AAPL": 0.15, "GOOGL": 0.12}}'

# Position sizing
curl -X POST "http://localhost:8000/position-size" \
  -H "Content-Type: application/json" \
  -d '{"portfolio_value": 100000, "entry_price": 150, "stop_loss": 140, "confidence": 0.7}'

# Backtesting
curl "http://localhost:8000/backtest/AAPL?period=1y"
```

## Signal Categories

### Macro (5 bullish, 5 bearish)
- Interest rates, liquidity, fiscal stimulus, currency, sector tailwinds

### Technical (5 bullish, 5 bearish)
- Golden/Death cross, RSI, MACD, breakouts, trend strength, volatility

### Fundamental (5 bullish, 5 bearish)
- Revenue growth, margins, cash flow, debt levels, ROE/ROIC

### Sentiment (3 bullish, 3 bearish)
- Institutional flow, earnings revisions, positioning, news sentiment

### Management (2 bullish, 2 bearish)
- Leadership track record, strategic expansion, capital allocation

## Scoring System

- **Strength**: 0-5 scale per signal
- **Confidence**: 0-1 scale (adjusted for geopolitical risk)
- **Weighted Score**: Strength × Confidence
- **Net Score**: Bullish Score - Bearish Score

**Verdict Scale:**
- Net Score > +25: Strong Buy
- Net Score +10 to +25: Buy
- Net Score -10 to +10: Hold
- Net Score -10 to -25: Sell
- Net Score < -25: Strong Sell

## Free API Limits

| API | Free Tier | Limit |
|-----|-----------|-------|
| yfinance | Unlimited | None |
| Alpha Vantage | Free | 25 requests/day, 5/minute |
| NewsAPI | Free | 100 requests/day |

**Note**: The system is designed to work with just yfinance. Alpha Vantage and NewsAPI are optional for enhanced data.

## Supported Markets

- US Stocks (e.g., AAPL, GOOGL, TSLA)
- Indian Stocks (e.g., RELIANCE.NS, TCS.NS)
- Global markets (use appropriate ticker suffixes)

## Project Structure

```
quant-investment-ai/
├── api.py                      # FastAPI server with 15+ endpoints
├── analyzer.py                 # Main analyzer orchestrator
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── .env.example               # Environment variables template
├── test_analyzer.py           # Test suite
│
├── Core Analysis
├── data_layer.py               # Data fetching (yfinance, Alpha Vantage)
├── signal_engine.py            # Signal generation (40 signals)
├── technical_indicators.py    # Technical calculations
├── scoring_model.py           # Scoring logic
├── decision_logic.py          # Decision making
├── output_formatter.py        # Output formatting
├── context_integration.py     # Geopolitical/sentiment context
│
├── Advanced Analytics
├── momentum_predictor.py      # Momentum prediction and change detection
├── chart_analyzer.py          # Chart pattern recognition and analysis
├── investment_horizon_analyzer.py  # Short/long-term opportunities
├── action_advisor.py          # Buy/sell/hold with timing advice
│
├── Market Coverage
├── indian_market_analyzer.py  # NSE/BSE specialized analysis
├── sector_analyzer.py         # Sector rotation and allocation
│
├── Portfolio Management
├── portfolio_optimizer.py     # Portfolio optimization and rebalancing
├── risk_manager.py            # Risk management and position sizing
├── backtester.py              # Strategy backtesting
├── alert_system.py            # Alert system for monitoring
│
├── Configuration
├── engine/                    # Signal definitions (markdown)
│   ├── signal_definitions.md
│   ├── scoring_model.md
│   └── decision_logic.md
├── data/                      # Context data
│   ├── sentiment_rules.md
│   └── geopolitical_context.md
├── templates/                 # Output templates
│   └── output_format.md
└── config/                    # Investment profile
    └── investment_profile.json
```

## Development

### Running Tests

```bash
# Test with a single company
python -c "from analyzer import FinancialAnalyzer; print(FinancialAnalyzer().analyze_company('AAPL'))"

# Test market overview
python -c "from analyzer import FinancialAnalyzer; print(FinancialAnalyzer().get_market_overview())"
```

## License

MIT

## Disclaimer

This tool is for educational and informational purposes only. Not financial advice. Always do your own research before making investment decisions.
#   F i n a n c e  
 