# Frontend Dashboard Blueprint

## Design Principles (Non-Negotiable)

- **Dark UI**: Low eye strain, high contrast (#0B0F14 background)
- **Information Density > Whitespace**: Bloomberg-style information density
- **Keyboard-First Navigation**: Command-based like Bloomberg terminal
- **Multi-Panel Layout**: Simultaneous context across panels
- **Color-Coded Signals**: Green (bullish), Red (bearish), Amber (neutral) - not decorative

## Layout Structure (Bloomberg-Inspired Grid)

```
+----------------------------------------------------------------------------------+
| TOP BAR (Command Input + Global Metrics)                                          |
+----------------------+----------------------+----------------------+-------------+
| LEFT PANEL           | MAIN PANEL           | RIGHT PANEL          | ALERT PANEL |
| (Navigation)         | (Charts / Analysis)  | (Insights / Signals) | (Live Feed) |
+----------------------+----------------------+----------------------+-------------+
| BOTTOM PANEL (Positions, Logs, Execution History)                                 |
+----------------------------------------------------------------------------------+
```

## Component Breakdown

### A. TOP BAR (Command Center)

**Purpose**: Fast navigation + global awareness

**Elements**:
- Command input (like Bloomberg terminal)
  - `> BTC TECH` - Analyze BTC with technical focus
  - `> AAPL FUND` - Analyze AAPL with fundamental focus
  - `> EURUSD MACRO` - Analyze EURUSD with macro context
  - `> GLOBAL` - Global market overview
  - `> ALLOC 60_40` - Get 60/40 allocation recommendation

- Global indicators (real-time):
  - S&P 500
  - BTC
  - Gold
  - USD Index
  - VIX

- Market status:
  - Risk ON / OFF indicator
  - Economic cycle phase

### B. LEFT PANEL (Navigation Tree)

**Sections**:
- Markets
  - Equities
  - Bonds
  - Commodities
  - Crypto
  - Forex
- Strategies
  - 60/40
  - Risk Parity
  - All-Weather
  - Tactical
- Portfolio
  - Holdings
  - Diversification
  - Risk Assessment
- Intelligence
  - Macro Overview
  - Scenarios
  - Correlation Matrix
  - Sector Rotation

**UX**:
- Collapsible tree
- Keyboard shortcuts (1-9)
- Search functionality

### C. MAIN PANEL (Primary Analysis View)

**Tabs**:

1. **Chart View**
   - Price chart (candlesticks)
   - Indicators overlay:
     - EMA 50 / 200
     - RSI
     - Volume
   - Support/Resistance levels
   - Chart patterns highlighted

2. **Multi-Timeframe**
   - 1H / 4H / Daily / Weekly
   - Synchronized analysis across timeframes

3. **Intelligence View**
   - Composite score (0-100)
   - Component breakdown
   - Trend and momentum indicators
   - Macro alignment

4. **Scenario View**
   - Base case / Bull case / Bear case
   - Probability distribution
   - Forward-looking implications

### D. RIGHT PANEL (Intelligence Layer)

**This is the core differentiation**

**Sections**:

1. **Composite Score**
   ```
   Score: 74 / 100
   
   Trend: Bullish ✅
   Momentum: Strong ✅
   Macro: Aligned ✅
   Fundamental: Strong ✅
   ML Probability: 68%
   ```

2. **Insight Summary**
   - Short narrative: "Trend continuation likely with moderate volatility risk"
   - Strategic consideration: "Consider increasing exposure on pullbacks"

3. **Signal Box**
   - Long / Short bias
   - Confidence level
   - Key drivers
   - Key risks

4. **Risk Factors**
   - Overbought/oversold
   - High correlation exposure
   - Macro headwinds

5. **Position Sizing**
   - Recommended shares
   - Position size %
   - Stop-loss level
   - Take-profit level

### E. ALERT PANEL (Live Intelligence Feed)

**Real-time stream**:
```
[12:01] BTC momentum spike detected
[12:03] EURUSD entering resistance zone
[12:05] Portfolio risk exceeds threshold
[12:07] Macro scenario shift: Disinflation probability rising
[12:10] Sector rotation: Technology overweight signal
```

**UX**:
- Color-coded:
  - Green = opportunity
  - Red = risk
  - Yellow = warning
- Auto-scroll with pause on hover
- Click to expand details

### F. BOTTOM PANEL (Execution & Logs)

**Tabs**:
- **Watchlist**: Tracked assets with scores
- **Scenarios**: Active scenario monitoring
- **ML Predictions**: Model outputs
- **System Logs**: System status and errors

## Visual Design System

### Colors
```css
--background: #0B0F14
--panel-bg: #111827
--border: #1F2937
--text-primary: #E5E7EB
--text-secondary: #9CA3AF
--bullish: #22C55E
--bearish: #EF4444
--neutral: #F59E0B
--accent: #3B82F6
```

### Typography
- **Monospace** (for data): JetBrains Mono, Fira Code
- **UI text**: Inter, system-ui

### Data Styling
- Heatmaps for correlation matrices
- Sparklines for trend indicators
- Micro charts for quick comparisons
- Progress bars for composite scores

## Interaction Model

### Command-Based Navigation

User types commands in top bar:
```
> BTC ML
> AAPL SCORE
> GLOBAL MACRO
> ALLOC TACTICAL
```

System loads corresponding panels and data.

### Hover Intelligence
Hover on asset → shows:
- Score
- Trend
- ML probability
- Quick insight

### Drill-Down Flow
```
Market → Asset → Signal → Scenario → Risk
```

## Intelligence UX (Where You Win)

### A. Scenario Engine
```
IF inflation rises:
→ Bonds ↓
→ USD ↑
→ Tech stocks ↓
→ Commodities ↑
```

### B. Opportunity Ranking Table
```
Asset  | Score | Trend | ML Prob | Action
-------|-------|-------|---------|-------
BTC    | 74    | Bull  | 68%     | Watch
AAPL   | 81    | Bull  | 72%     | Strong
EURUSD | 62    | Neutral| 55%     | Avoid
```

### C. Macro Dashboard
- Interest rate trends
- Inflation trajectory
- Central bank calendar
- Economic cycle indicator

## Advanced Panels (Optional but Powerful)

### A. Correlation Matrix
Heatmap of asset relationships with:
- Color coding (red = positive, blue = negative)
- Intensity = strength
- Click for detailed pair analysis

### B. Regime Detection
- Trending / Volatile / Sideways
- Regime probability
- Historical regime changes

### C. Portfolio Optimizer
- Current allocation
- Recommended allocation
- Expected improvement
- Implementation steps

## Tech Stack (Recommended)

### Frontend
- **Framework**: React + Next.js 14
- **Styling**: Tailwind CSS
- **Charts**: Recharts / TradingView Lightweight Charts
- **State**: Zustand / Redux Toolkit
- **Data Fetching**: SWR / React Query

### Backend
- **API**: Python FastAPI (already implemented)
- **Real-Time**: WebSockets for live updates
- **Database**: PostgreSQL (optional for persistence)

### Deployment
- **Frontend**: Vercel / Netlify
- **Backend**: Railway / Render / AWS Lambda

## Component Structure

```
src/
├── components/
│   ├── layout/
│   │   ├── TopBar.tsx
│   │   ├── LeftPanel.tsx
│   │   ├── MainPanel.tsx
│   │   ├── RightPanel.tsx
│   │   ├── AlertPanel.tsx
│   │   └── BottomPanel.tsx
│   ├── intelligence/
│   │   ├── CompositeScore.tsx
│   │   ├── InsightSummary.tsx
│   │   ├── SignalBox.tsx
│   │   └── RiskFactors.tsx
│   ├── charts/
│   │   ├── PriceChart.tsx
│   │   ├── CorrelationHeatmap.tsx
│   │   └── ScenarioChart.tsx
│   └── ui/
│       ├── CommandInput.tsx
│       ├── NavigationTree.tsx
│       └── AlertFeed.tsx
├── hooks/
│   ├── useIntelligence.ts
│   ├── useMacro.ts
│   └── useWebSocket.ts
├── lib/
│   ├── api.ts
│   └── types.ts
└── pages/
    ├── index.tsx
    └── _app.tsx
```

## Key Features Implementation

### 1. Command Input
```typescript
// Command parsing and execution
const executeCommand = (command: string) => {
  const [asset, focus] = command.split(' ');
  switch(focus) {
    case 'TECH': loadTechnicalAnalysis(asset);
    case 'FUND': loadFundamentalAnalysis(asset);
    case 'MACRO': loadMacroContext(asset);
    case 'ML': loadMLPrediction(asset);
    default: loadFullAnalysis(asset);
  }
};
```

### 2. Real-Time Updates
```typescript
// WebSocket connection for live data
const useWebSocket = () => {
  const ws = new WebSocket('ws://localhost:8000/ws');
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updatePanel(data.type, data.payload);
  };
};
```

### 3. Composite Score Display
```typescript
// Visual score component
const CompositeScore = ({ score, components }) => (
  <div className="score-display">
    <CircularProgress value={score.total} />
    <div className="breakdown">
      <ProgressBar label="Technical" value={score.technical} />
      <ProgressBar label="Momentum" value={score.momentum} />
      <ProgressBar label="Macro" value={score.macro} />
      <ProgressBar label="Fundamental" value={score.fundamental} />
      <ProgressBar label="ML" value={score.ml} />
    </div>
  </div>
);
```

## Performance Considerations

- **Debounce** command input (300ms)
- **Virtualize** long lists (watchlist, alerts)
- **Memoize** expensive calculations
- **Lazy load** chart components
- **Cache** API responses (SWR)

## Accessibility

- **Keyboard navigation** throughout
- **Screen reader** support for data tables
- **High contrast** color scheme
- **Focus indicators** on interactive elements

## Mobile Responsiveness

- **Collapse** panels on smaller screens
- **Stack** layout for mobile
- **Touch-friendly** command input
- **Simplified** chart view on mobile

## Security

- **API key** management (environment variables)
- **Rate limiting** on API calls
- **Input validation** on commands
- **CORS** configuration

## Future Enhancements

- **Voice commands** for hands-free operation
- **Custom layouts** saved per user
- **Collaboration** features (shared watchlists)
- **Mobile app** (React Native)
- **Desktop app** (Electron)
