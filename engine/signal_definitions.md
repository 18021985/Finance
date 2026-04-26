# Signal Definitions — Adversarial Quant Model

This module defines the full set of signals used in the adversarial model.

Each signal must include:
- Category
- Indicator Name
- Description
- Direction (Bullish / Bearish)
- Typical Data Source
- Time Horizon (Short / Long)
- Default Weight Bias (0–5 guideline)

--------------------------------------------------
🟢 BULLISH SIGNALS (20)
--------------------------------------------------

## 1. MACRO (5)

1. Falling Interest Rates
- Description: Central banks reducing rates → supports equity valuations
- Horizon: Medium–Long
- Weight: 4–5

2. Liquidity Expansion
- Description: Increase in money supply / QE / credit growth
- Horizon: Medium
- Weight: 4–5

3. Fiscal Stimulus
- Description: Government spending boosts economic activity
- Horizon: Medium–Long
- Weight: 3–5

4. Currency Advantage
- Description: Favorable currency trend (e.g., weaker INR for exporters)
- Horizon: Medium
- Weight: 3–4

5. Sector Macro Tailwind
- Description: Sector aligned with macro cycle (e.g., infra in expansion)
- Horizon: Medium–Long
- Weight: 4–5

---

## 2. TECHNICAL (5)

6. Golden Cross (50MA > 200MA)
- Horizon: Medium
- Weight: 4–5

7. RSI Oversold Reversal (<30 → rising)
- Horizon: Short
- Weight: 3–4

8. MACD Bullish Crossover
- Horizon: Short–Medium
- Weight: 3–4

9. Breakout Above Resistance
- Horizon: Short
- Weight: 4–5

10. Strong Trend (ADX > 25)
- Horizon: Short–Medium
- Weight: 3–4

---

## 3. FUNDAMENTAL (5)

11. Revenue Growth (CAGR positive)
- Horizon: Long
- Weight: 4–5

12. Margin Expansion
- Horizon: Long
- Weight: 4–5

13. Strong Free Cash Flow
- Horizon: Long
- Weight: 4–5

14. Improving Leverage (Debt ↓)
- Horizon: Long
- Weight: 3–5

15. High ROE / ROIC
- Horizon: Long
- Weight: 4–5

---

## 4. SENTIMENT & FLOW (3)

16. Institutional Accumulation
- Horizon: Short–Medium
- Weight: 4–5

17. Positive Earnings Revisions
- Horizon: Medium
- Weight: 4–5

18. Bullish Positioning (Low Put/Call)
- Horizon: Short
- Weight: 3–4

---

## 5. MANAGEMENT & STRATEGY (2)

19. Strong Leadership Track Record
- Horizon: Long
- Weight: 4–5

20. Strategic Expansion / Innovation
- Horizon: Long
- Weight: 3–5

--------------------------------------------------
🔴 BEARISH SIGNALS (20)
--------------------------------------------------

## 1. MACRO (5)

1. Rising Interest Rates
- Horizon: Medium–Long
- Weight: 4–5

2. Liquidity Tightening
- Horizon: Medium
- Weight: 4–5

3. Recession Indicators
- Horizon: Medium
- Weight: 4–5

4. Currency Pressure
- Horizon: Medium
- Weight: 3–4

5. Geopolitical Instability
- Horizon: Short–Medium
- Weight: 4–5

---

## 2. TECHNICAL (5)

6. Death Cross (50MA < 200MA)
- Horizon: Medium
- Weight: 4–5

7. RSI Overbought (>70 → falling)
- Horizon: Short
- Weight: 3–4

8. MACD Bearish Crossover
- Horizon: Short–Medium
- Weight: 3–4

9. Breakdown Below Support
- Horizon: Short
- Weight: 4–5

10. Volatility Spike (Risk-Off)
- Horizon: Short
- Weight: 4–5

---

## 3. FUNDAMENTAL (5)

11. Declining Revenue
- Horizon: Long
- Weight: 4–5

12. Margin Compression
- Horizon: Long
- Weight: 4–5

13. High Debt Levels
- Horizon: Long
- Weight: 4–5

14. Weak Cash Flow
- Horizon: Long
- Weight: 4–5

15. Poor Capital Efficiency (Low ROE/ROIC)
- Horizon: Long
- Weight: 4–5

---

## 4. SENTIMENT & FLOW (3)

16. Institutional Selling
- Horizon: Short–Medium
- Weight: 4–5

17. Fear Index Spike (High VIX)
- Horizon: Short
- Weight: 4–5

18. Negative News Sentiment
- Horizon: Short
- Weight: 3–4

---

## 5. MANAGEMENT RISK (2)

19. Leadership Instability
- Horizon: Long
- Weight: 4–5

20. Poor Capital Allocation History
- Horizon: Long
- Weight: 4–5

--------------------------------------------------
⚙️ USAGE RULES

- Minimum 15 signals per side must be evaluated
- Prefer full 20 vs 20 analysis
- Assign:
  Strength (0–5)
  Confidence (0–1)

- Adjust:
  • Confidence for macro regime
  • Weight for geopolitical risk
  • Sentiment for fake news filtering

--------------------------------------------------
