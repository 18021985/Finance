# Scoring Model

Each signal must include:

- Category (Macro / Technical / Fundamental / Sentiment / Management)
- Direction (Bullish / Bearish)
- Strength (0–5)
- Confidence (0–1)

Formula:

Weighted Score = Strength × Confidence

Total Scores:
- Bullish Score = sum of bullish signals
- Bearish Score = sum of bearish signals

Constraints:
- Minimum 15 signals per side
- Prefer 20 per side
