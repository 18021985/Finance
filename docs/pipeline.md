# System pipeline (current) + gaps

This document describes the **current end-to-end flow** in this repository and highlights where portfolio, news/events, sentiment, and “real market values” are (and are not) used.

## 1) API entrypoints

- `api.py`
  - `/analyze` and `/analyze/{symbol}` call `FinancialIntelligenceSystem.analyze_company()`
  - `/analyze/{symbol}/enhanced` calls `FinancialIntelligenceSystem.analyze_company_enhanced()`
  - `/recommendations` calls `InvestmentRecommender.generate_recommendations()` (currently not portfolio-aware)
  - `/user-holdings` reads/writes holdings from Supabase when configured (otherwise sample holdings)
  - `/portfolio` returns **hardcoded sample holdings** (not connected to `/user-holdings`)

## 2) Analysis path (per symbol)

### Orchestrator

- `analyzer.py` → `FinancialIntelligenceSystem.analyze_company(symbol)`
  1. **Data fetch**
     - `DataLayer.get_stock_data(symbol)` (yfinance historical bars)
     - `DataLayer.get_company_info(symbol)` (yfinance `ticker.info`)
     - `DataLayer.get_fundamental_data(symbol)` (Alpha Vantage if configured else yfinance)
     - `DataLayer.get_news_sentiment(symbol)` (yfinance news headlines only)
     - `DataLayer.get_macro_indicators()` (yfinance ETF proxies: TLT/TIP/UUP)
  2. **Signals**
     - `SignalEngine.generate_signals(symbol, stock_data, fundamentals, macro_data, news)`
  3. **Context adjustments**
     - `ContextIntegration.get_context_summary()`
     - `ContextIntegration.adjust_confidence_for_geopolitics()` applied to every signal
  4. **Scoring**
     - `ScoringModel.calculate_scores(bullish_signals, bearish_signals)`
     - `ScoringModel.adjust_for_conflicts(...)`
  5. **Forecast**
     - `DecisionLogic.generate_forecast(scores, fundamentals)`
  6. **Decision/verdict**
     - `DecisionLogic.interpret_score(adjusted_net_score, conviction)`
  7. **Output**
     - `OutputFormatter.format_json(...)` or `.format_analysis(...)`

### Key gap: sentiment/news/events

- `SignalEngine._generate_sentiment_signals(...)` is currently **mostly placeholder logic** and does not perform NLP on headlines, event extraction (management change, guidance, regulatory), or credibility scoring.
- `ContextIntegration` sentiment credibility weighting exists, but is **not wired** into the signal engine/news processing pipeline.

## 3) Recommendation path (multi-symbol)

- `investment_recommender.py`
  - Picks a small subset of symbols per sector (e.g., first 2–3)
  - Uses `_analyze_stock()` which is primarily a heuristic based on:
    - 1-month price change
    - high-level market sentiment string (SPY 1-month change)
  - Does **not** consume:
    - `SignalEngine` results
    - `ScoringModel` results
    - `CompositeScorer` outputs
    - portfolio holdings / cash / risk budget
    - real bid/ask quotes or corporate actions

### Key gap: portfolio integration

- `/user-holdings` supports Supabase-backed holdings, but `/portfolio` and `/recommendations` do not consistently use it.
- Without portfolio integration, the system cannot reliably output:
  - “increase shares / reduce / exit”
  - position sizing constrained by portfolio risk/exposure
  - concentration/sector risk warnings per user holdings

## 4) “Real-time” market data

- `realtime_pipeline.py` polls `yfinance` 1-minute bars.
- Important limitation: `yfinance` is not a guaranteed real-time feed (delay/coverage varies), so “real market values” require a provider abstraction and (optionally) a true quote feed.

## 5) Where to improve first (highest leverage)

1. Make the **recommender consume the same scoring stack** as `/analyze` (single source of truth).
2. Make the portfolio endpoints use **one holdings source** (Supabase when configured), then propagate holdings + cash + risk budget into recommendations.
3. Replace placeholder news/sentiment with **structured event extraction + credibility + recency decay**, and feed it into signals/scoring.
4. Introduce a **MarketDataProvider** abstraction (quotes/bars) with yfinance fallback, caching, and time/session normalization.

