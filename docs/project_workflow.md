# Project Workflow Documentation

Complete guide to understanding **what** happens, **how** it happens, and **why** it happens in the Quant Edge trading platform.

---

## 🎯 System Overview: The Decision Engine

The Quant Edge platform is **NOT a simple strategy bot**. It's a **multi-layer decision engine** that ensures every trade passes through multiple filters before execution.

### Core Philosophy

> **"Every trade must satisfy ALL layers. If ANY layer fails → NO TRADE."**

This ensures that trades are only taken when:
1. The macro environment supports it
2. Fundamentals align
3. Sentiment confirms
4. Intermarket relationships agree
5. Technical entry is present
6. Risk rules allow it

---

## 🔄 Complete System Workflow

### Phase 1: Data Collection & Processing

**WHAT**: System continuously collects market data from multiple sources

**HOW**:
1. **Market Data Engine** (`data_engine/market_data.py`)
   - Fetches OHLCV (Open, High, Low, Close, Volume) data
   - Updates every minute (configurable)
   - Sources: Yahoo Finance, Alpha Vantage, Polygon
   - Stores in `data/raw/` directory

2. **Economic Data Engine** (`data_engine/economic_data.py`)
   - Fetches economic indicators (CPI, GDP, unemployment, Fed rates)
   - Tracks economic calendar events
   - Calculates "surprise" factors (actual vs expected)
   - Assesses policy impact (hawkish/dovish)
   - Updates daily or on event release

3. **News Data Engine** (`data_engine/news_data.py`)
   - Fetches news headlines and articles
   - Filters relevant news by keywords
   - Updates every 15 minutes (configurable)

4. **Sentiment Data Engine** (`data_engine/sentiment_data.py`)
   - Fetches Fear & Greed Index
   - Gets VIX (volatility index)
   - Calculates Put/Call ratio
   - Analyzes news sentiment using NLP
   - Updates every 5 minutes (configurable)

**WHY**: 
- **Multi-source data** ensures reliability (if one API fails, others work)
- **Real-time updates** allow quick reaction to market changes
- **Historical data** enables backtesting and pattern recognition
- **Sentiment analysis** captures market psychology that price alone doesn't show

**Data Flow**:
```
External APIs → Data Engine → Cleaning & Normalization → Feature Engineering → Processed Data Storage
```

---

### Phase 2: Market Regime Detection

**WHAT**: System determines if market is in "risk-on" or "risk-off" mode

**HOW**:
1. **Regime Engine** (`regime_engine/macro_regime.py`)
   - Analyzes multiple indicators:
     - VIX level (fear gauge)
     - Bond yields (10Y Treasury)
     - USD strength (DXY index)
     - Equity performance (SPY)
     - Gold price
     - Credit spreads
   - Calculates composite "risk score" (-1 to +1)
   - Classifies regime: RISK_ON, RISK_OFF, or NEUTRAL
   - Provides confidence level (0-1)

2. **Risk-On/Off Analyzer** (`regime_engine/risk_on_off.py`)
   - Detailed analysis of risk sentiment
   - Determines if environment favors risk-taking or risk-aversion

**WHY**:
- **Risk-on regime**: Favorable for equity longs, growth stocks
- **Risk-off regime**: Favorable for defensive assets, shorts, hedges
- **Prevents fighting the market**: No point buying stocks in a risk-off environment
- **Institutional approach**: Large funds use regime detection - this levels the playing field

**Example**:
```
VIX > 30 + Bonds ↑ + USD ↑ + Equities ↓ = RISK_OFF
→ System filters out equity long strategies
→ Only allows defensive trades or shorts
```

**Data Flow**:
```
Market Indicators → Regime Engine → Risk Score Calculation → Regime Classification → Strategy Filtering
```

---

### Phase 3: Strategy Evaluation (Multi-Layer Filtering)

**WHAT**: Each strategy evaluates potential trades through multiple layers

**HOW**: Every strategy inherits from `BaseStrategy` and must pass these checks:

#### Layer 1: Macro Regime Check ✅
- **WHAT**: Checks if current regime allows this type of trade
- **HOW**: `check_regime()` method queries regime engine
- **WHY**: Prevents trading against macro environment
- **Example**: Equity long strategy requires RISK_ON regime

#### Layer 2: Fundamental Filter ✅
- **WHAT**: Checks if fundamentals support the trade
- **HOW**: `check_fundamentals()` analyzes:
  - Central bank policy (hawkish/dovish)
  - Economic data alignment
  - Policy impact on asset class
- **WHY**: Ensures trade aligns with economic fundamentals
- **Example**: Long stocks requires dovish Fed policy or strong economic data

#### Layer 3: Sentiment Alignment ✅
- **WHAT**: Checks if market sentiment confirms the trade direction
- **HOW**: `check_sentiment()` analyzes:
  - Fear & Greed Index
  - VIX level
  - News sentiment
  - Put/Call ratio
- **WHY**: Sentiment can override fundamentals short-term
- **Example**: Long trade requires positive sentiment (Fear & Greed > 50)

#### Layer 4: Intermarket Confirmation ✅
- **WHAT**: Checks if related markets confirm the trade
- **HOW**: `check_intermarket()` analyzes:
  - Bond-equity correlation
  - USD impact
  - Gold correlation
  - Credit spreads
- **WHY**: Markets are interconnected - confirmation reduces false signals
- **Example**: Long stocks requires bonds stable/rising (not crashing)

#### Layer 5: Technical Entry Signal ✅
- **WHAT**: Checks if technical analysis shows entry opportunity
- **HOW**: `check_technical_entry()` analyzes:
  - Moving averages (EMA crossovers)
  - RSI (overbought/oversold)
  - Market structure (HH/HL, LH/LL)
  - Support/resistance levels
- **WHY**: Timing matters - even good fundamentals need good entry
- **Example**: Long signal when price > EMA(50) > EMA(200) and RSI < 70

#### Layer 6: Risk Rules ✅
- **WHAT**: Final check if risk management allows the trade
- **HOW**: `check_risk_rules()` checks:
  - Account drawdown limits
  - Position size limits
  - Exposure limits
  - Daily loss limits
- **WHY**: Protects capital - no trade is worth blowing up account
- **Example**: Trade rejected if drawdown > 10% or daily loss limit reached

**Decision Flow**:
```
Strategy Idea → Regime Check → Fundamental Check → Sentiment Check → 
Intermarket Check → Technical Check → Risk Check → EXECUTE or REJECT
```

**If ANY layer fails**: Trade is rejected, no execution

**If ALL layers pass**: Trade signal generated, sent to execution engine

---

### Phase 4: Risk Management

**WHAT**: System calculates position size and manages risk before execution

**HOW**:
1. **Position Sizing** (`risk_engine/position_sizing.py`)
   - Calculates position size based on:
     - Account value
     - Risk per trade (e.g., 1%)
     - Stop loss distance
   - Formula: `Position Size = (Account × Risk%) / Stop Loss Distance`
   - Example: $100k account, 1% risk, 5% stop = $20k position

2. **Drawdown Control** (`risk_engine/drawdown_control.py`)
   - Monitors peak-to-trough drawdown
   - Reduces position sizes if drawdown increases
   - Activates "kill switch" if max drawdown exceeded

3. **Exposure Limits** (`risk_engine/exposure_limits.py`)
   - Checks total portfolio exposure
   - Limits sector concentration
   - Prevents over-correlation
   - Limits single position size

**WHY**:
- **Position sizing**: Ensures losses are controlled (1% loss per trade = 100 trades to lose account)
- **Drawdown control**: Prevents death spiral (losing more when already down)
- **Exposure limits**: Prevents over-concentration risk (don't put all eggs in one basket)

**Risk Flow**:
```
Trade Signal → Position Size Calculation → Risk Checks → Exposure Checks → Approved/Rejected
```

---

### Phase 5: Trade Execution

**WHAT**: System executes trades through backtesting, paper trading, or live trading

**HOW**: Three execution modes:

#### Mode 1: Backtesting (`execution_engine/backtester.py`)
- **WHAT**: Simulates trading on historical data
- **HOW**:
  1. Loads historical data for date range
  2. Processes each bar/event chronologically
  3. Applies strategy logic at each bar
  4. Executes trades when signals generated
  5. Applies slippage and commission
  6. Tracks P&L and positions
  7. Calculates performance metrics
- **WHY**: Test strategies before risking real money
- **Output**: Performance report with metrics (CAGR, Sharpe, drawdown, etc.)

#### Mode 2: Paper Trading (`execution_engine/paper_trader.py`)
- **WHAT**: Simulates live trading with real-time data
- **HOW**:
  1. Initializes virtual account with capital
  2. Receives real-time market data
  3. Processes strategy signals
  4. Executes orders (simulated, no real money)
  5. Tracks positions and P&L
  6. Updates account in real-time
- **WHY**: Test strategies with real-time data before going live
- **Output**: Real-time account status, positions, P&L

#### Mode 3: Live Trading (`execution_engine/live_trader.py`)
- **WHAT**: Executes real trades via broker API
- **HOW**:
  1. Connects to broker API (Groww via growwapi, or Zerodha/Upstox)
  2. Gets real account status
  3. Receives real-time market data
  4. Processes strategy signals
  5. Places orders via broker API:
     - Market orders (immediate execution)
     - Limit orders (execute at price or better)
     - Stop orders (risk management)
  6. Monitors positions and manages exits
  7. Applies risk rules (kill switch if needed)
- **WHY**: Actual trading with real money (use only after thorough testing)
- **Output**: Real account status, executed orders, live P&L

**Execution Flow**:
```
Strategy Signal → Risk Approval → Order Type Selection → Broker API → Order Execution → Position Tracking
```

---

### Phase 6: Analytics & Monitoring

**WHAT**: System tracks performance and generates analytics

**HOW**:
1. **Performance Tracking** (`analytics/performance.py`)
   - Calculates metrics:
     - CAGR (Compound Annual Growth Rate)
     - Sharpe Ratio (risk-adjusted returns)
     - Sortino Ratio (downside risk-adjusted)
     - Max Drawdown (worst peak-to-trough loss)
     - Win Rate (% of winning trades)
     - Expectancy (average profit per trade)
     - Profit Factor (gross profit / gross loss)

2. **Trade Logging** (`analytics/trade_logger.py`)
   - Logs every trade:
     - Entry/exit prices and times
     - Position size
     - P&L
     - Reason for entry/exit
     - Regime at time of trade
   - Stores in database or CSV
   - Enables trade analysis

3. **Dashboard** (`ui/dashboard.py`)
   - Real-time visualization:
     - Account value chart
     - P&L chart
     - Open positions
     - Performance metrics
     - Trade log

**WHY**:
- **Performance metrics**: Understand if strategy is working
- **Trade logging**: Learn from wins and losses
- **Dashboard**: Monitor system in real-time
- **Analysis**: Improve strategies based on data

**Analytics Flow**:
```
Trade Execution → Trade Logging → Performance Calculation → Metrics Update → Dashboard Display
```

---

## 🤖 AI Strategy Chatbot Workflow

**WHAT**: Natural language interface for strategy creation and backtesting

**HOW**:
1. **User Input**: User provides natural language prompt
   - Example: "Create a strategy that buys SPY when RSI < 30 and VIX > 25"

2. **Strategy Generation** (`ai_chatbot/strategy_chatbot.py`)
   - Uses AI (Google Gemini) to convert prompt to strategy code
   - Generates Python code following `BaseStrategy` pattern
   - Includes all required layers (regime, fundamental, sentiment, etc.)

3. **Code Validation**: Validates generated code syntax and structure

4. **Automatic Backtesting**:
   - Loads historical data
   - Runs backtest on generated strategy
   - Calculates performance metrics

5. **Results Display**:
   - Shows backtest results (PnL, metrics)
   - Explains strategy logic
   - Provides optimization suggestions

**WHY**:
- **Accessibility**: Non-programmers can create strategies
- **Speed**: Generate and test strategies quickly
- **Learning**: Understand what makes strategies work

**Chatbot Flow**:
```
User Prompt → AI Code Generation → Code Validation → Backtest Execution → Results Display → User Feedback
```

---

## 🎨 UI Workflow

**WHAT**: TradingView-style interface for monitoring and control

**HOW**:
1. **Dashboard** (`ui/dashboard.py`)
   - Account summary (equity, cash, P&L)
   - Open positions table
   - Performance charts
   - Trade log

2. **Charts** (`ui/charting.py`)
   - Price charts with candlesticks
   - Technical indicators overlay
   - Strategy signals visualization
   - Drawing tools (trend lines, support/resistance)

3. **Strategy Builder** (`ui/strategy_builder_ui.py`)
   - Visual drag-and-drop interface
   - Component configuration
   - Strategy testing

4. **Chatbot Interface** (`ui/chatbot_ui.py`)
   - Chat interface for strategy chatbot
   - Backtest results display
   - Strategy code viewer

**WHY**:
- **Visualization**: Charts help understand market and strategy
- **Monitoring**: Real-time dashboard for live trading
- **Control**: Easy strategy creation and modification

---

## 🔄 Complete End-to-End Workflow Example

### Scenario: Equity Long Strategy Signal

1. **Data Collection** (Continuous)
   - Market data: SPY price = $450, EMA(50) = $445, EMA(200) = $440
   - Economic data: Fed rate = 5.25%, CPI = 3.2% (dovish)
   - Sentiment: Fear & Greed = 65 (greed), VIX = 15 (low)
   - Intermarket: Bonds stable, USD neutral

2. **Regime Detection**
   - Risk score = +0.7 → RISK_ON regime (confidence: 0.85)

3. **Strategy Evaluation** (Equity Trend Following Strategy)
   - ✅ **Regime Check**: RISK_ON → PASS
   - ✅ **Fundamental Check**: Dovish Fed, stable economy → PASS
   - ✅ **Sentiment Check**: Positive sentiment (65) → PASS
   - ✅ **Intermarket Check**: Bonds stable, no USD pressure → PASS
   - ✅ **Technical Check**: Price > EMA(50) > EMA(200) → PASS
   - ✅ **Risk Check**: Drawdown < 5%, daily loss < 2% → PASS
   - **Result**: ALL LAYERS PASS → Generate LONG signal

4. **Risk Management**
   - Account value: $100,000
   - Risk per trade: 1%
   - Stop loss: 5% below entry
   - Position size: ($100k × 1%) / 5% = $20,000
   - Shares: $20,000 / $450 = 44 shares

5. **Execution** (Paper Trading Mode)
   - Place market order: BUY 44 shares SPY @ $450
   - Order executed (simulated)
   - Position opened: 44 shares SPY @ $450

6. **Monitoring**
   - Track position P&L in real-time
   - Monitor for exit signals
   - Update dashboard

7. **Exit** (When exit conditions met)
   - Technical exit: Price crosses below EMA(50)
   - Place market order: SELL 44 shares SPY @ $460
   - Position closed
   - P&L: ($460 - $450) × 44 = $440 profit

8. **Analytics**
   - Log trade: Entry $450, Exit $460, P&L $440
   - Update performance metrics
   - Display on dashboard

---

## 🚨 Error Handling & Safety

**WHAT**: System handles errors and prevents catastrophic failures

**HOW**:
- **API Failures**: Falls back to backup data sources
- **Data Errors**: Validates data before processing
- **Risk Violations**: Rejects trades that violate risk rules
- **Kill Switch**: Stops all trading if drawdown exceeds limit
- **Order Failures**: Retries with exponential backoff
- **Connection Loss**: Reconnects automatically

**WHY**: Protects capital and ensures system reliability

---

## 📊 Performance Optimization

**WHAT**: System optimizes for speed and efficiency

**HOW**:
- **Data Caching**: Caches API responses to reduce calls
- **Batch Processing**: Processes multiple symbols together
- **Async Operations**: Non-blocking data fetching
- **Database Storage**: Efficient data storage and retrieval

**WHY**: Faster execution, lower API costs, better user experience

---

## 🎓 Key Takeaways

1. **Multi-Layer Filtering**: Every trade must pass ALL layers
2. **Regime Awareness**: Don't fight the market environment
3. **Risk First**: Risk management is non-negotiable
4. **Data-Driven**: Decisions based on data, not emotions
5. **Continuous Learning**: System learns from every trade
6. **Safety First**: Multiple safety mechanisms protect capital

This workflow ensures that trades are taken only when **everything aligns** - macro environment, fundamentals, sentiment, intermarket relationships, technical setup, and risk rules. This is how institutions trade, and now you have the same framework.
