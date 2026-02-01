# Code Functionality Documentation

Complete documentation of all modules, classes, and functions in the Quant Edge trading platform.

## 📁 Project Structure

```
quant-edge/
├── core/
│   ├── data_engine/          # Data collection and processing
│   ├── regime_engine/         # Market regime detection
│   ├── strategy_engine/       # Strategy logic and execution
│   ├── risk_engine/           # Risk management
│   ├── execution_engine/      # Trade execution (backtest/live)
│   └── analytics/             # Performance tracking
├── strategies/                # Strategy implementations
├── config/                    # Configuration files
├── data/                      # Data storage
├── notebooks/                 # Jupyter notebooks
└── docs/                      # Documentation
```

---

## 🔵 Core Data Engine (`core/data_engine/`)

### `market_data.py`

**Purpose**: Fetch and process market price data (OHLCV)

**Classes**:
- `MarketDataFetcher`: Main class for fetching market data
  - `get_historical_data(symbol, period, interval)`: Get historical OHLCV data
  - `get_realtime_quote(symbol)`: Get real-time price quote
  - `get_multiple_symbols(symbols, period)`: Batch fetch multiple symbols
  - `clean_data(df)`: Clean and normalize price data
  - `add_technical_indicators(df)`: Add basic technical indicators

**Data Sources**:
- Primary: Yahoo Finance (yfinance)
- Backup: Alpha Vantage, Polygon.io

**Returns**: pandas DataFrame with OHLCV + indicators

---

### `economic_data.py`

**Purpose**: Fetch economic indicators and calendar events

**Classes**:
- `EconomicDataFetcher`: Fetch economic data
  - `get_fed_funds_rate()`: Get Federal Reserve interest rates
  - `get_unemployment_rate()`: Get unemployment data
  - `get_cpi_data()`: Get Consumer Price Index
  - `get_gdp_data()`: Get GDP data
  - `get_economic_calendar(start_date, end_date)`: Get economic events
  - `calculate_surprise(actual, expected)`: Calculate surprise factor
  - `assess_policy_impact(event)`: Determine hawkish/dovish impact

**Data Sources**:
- FRED API (Federal Reserve Economic Data)
- Trading Economics API (optional)

**Returns**: Economic indicators with policy impact assessment

---

### `news_data.py`

**Purpose**: Fetch and process news headlines

**Classes**:
- `NewsFetcher`: Fetch news articles
  - `get_market_news(symbol, limit)`: Get news for a symbol
  - `get_general_news(query, limit)`: Get general market news
  - `filter_relevant_news(news_list, keywords)`: Filter relevant articles

**Data Sources**:
- NewsAPI
- Finnhub

**Returns**: List of news articles with metadata

---

### `sentiment_data.py`

**Purpose**: Calculate market sentiment indicators

**Classes**:
- `SentimentAnalyzer`: Analyze market sentiment
  - `get_fear_greed_index()`: Get CNN Fear & Greed Index
  - `get_vix_level()`: Get VIX (volatility index)
  - `get_put_call_ratio()`: Get Put/Call ratio
  - `analyze_news_sentiment(news_list)`: Analyze news sentiment using NLP
  - `get_composite_sentiment()`: Get overall sentiment score

**Methods**:
- Uses Hugging Face transformers for NLP sentiment analysis
- Combines multiple sentiment indicators into composite score

**Returns**: Sentiment scores (0-100 scale)

---

## 🟢 Regime Engine (`core/regime_engine/`)

### `macro_regime.py`

**Purpose**: Detect current market regime (risk-on vs risk-off)

**Classes**:
- `MacroRegimeDetector`: Detect macro regime
  - `detect_regime()`: Main method to detect current regime
  - `calculate_risk_score()`: Calculate risk-on/risk-off score
  - `get_regime_label()`: Return regime label (RISK_ON, RISK_OFF, NEUTRAL)
  - `get_regime_confidence()`: Return confidence level (0-1)

**Logic**:
- Analyzes: VIX, bond yields, USD strength, equity performance
- Returns: RISK_ON, RISK_OFF, or NEUTRAL

**Returns**: Regime classification with confidence score

---

### `risk_on_off.py`

**Purpose**: Detailed risk-on/risk-off analysis

**Classes**:
- `RiskOnOffAnalyzer`: Analyze risk sentiment
  - `analyze_risk_indicators()`: Analyze all risk indicators
  - `get_risk_score()`: Get composite risk score (-1 to +1)
  - `is_risk_on()`: Boolean check if risk-on
  - `is_risk_off()`: Boolean check if risk-off

**Indicators Used**:
- VIX level
- Bond yields (10Y Treasury)
- USD Index (DXY)
- Equity performance (SPY)
- Gold price
- Credit spreads

**Returns**: Risk score and classification

---

## 🟡 Strategy Engine (`core/strategy_engine/`)

### `base_strategy.py`

**Purpose**: Base class for all strategies

**Classes**:
- `BaseStrategy`: Abstract base strategy class
  - `check_regime()`: Check if regime allows trading
  - `check_fundamentals()`: Check fundamental filters
  - `check_sentiment()`: Check sentiment alignment
  - `check_intermarket()`: Check intermarket confirmation
  - `check_technical_entry()`: Check technical entry signals
  - `check_risk_rules()`: Check risk management rules
  - `generate_signals()`: Generate trading signals (abstract)
  - `should_enter()`: Main entry logic (all layers must pass)
  - `should_exit()`: Exit logic

**Pattern**: All strategies inherit from this base class

---

### `technical.py`

**Purpose**: Technical analysis indicators and signals

**Classes**:
- `TechnicalAnalyzer`: Technical analysis engine
  - `calculate_ema(period)`: Calculate Exponential Moving Average
  - `calculate_rsi(period)`: Calculate Relative Strength Index
  - `calculate_atr(period)`: Calculate Average True Range
  - `calculate_vwap()`: Calculate Volume Weighted Average Price
  - `detect_market_structure()`: Detect HH/HL, LH/LL patterns
  - `identify_support_resistance()`: Identify S/R levels
  - `calculate_bollinger_bands()`: Calculate Bollinger Bands
  - `detect_divergence()`: Detect RSI/price divergence

**Functions**:
- `generate_entry_signals(df)`: Generate buy/sell signals
- `generate_exit_signals(df, position)`: Generate exit signals

**Returns**: Technical signals and indicators

---

### `fundamental.py`

**Purpose**: Fundamental analysis filters

**Classes**:
- `FundamentalAnalyzer`: Fundamental analysis engine
  - `check_central_bank_policy()`: Check central bank stance
  - `assess_rate_environment()`: Assess interest rate environment
  - `check_economic_data_alignment()`: Check if economic data supports trade
  - `calculate_policy_impact()`: Calculate policy impact score
  - `filter_by_fundamentals(symbols)`: Filter symbols by fundamentals

**Methods**:
- Tracks Fed policy (hawkish/dovish)
- Assesses economic data surprises
- Determines policy impact on asset classes

**Returns**: Fundamental filters and scores

---

### `sentiment.py`

**Purpose**: Sentiment-based filters

**Classes**:
- `SentimentFilter`: Sentiment filtering engine
  - `check_sentiment_alignment(symbol, direction)`: Check if sentiment aligns
  - `filter_by_sentiment(symbols, direction)`: Filter by sentiment
  - `get_sentiment_score()`: Get current sentiment score

**Logic**:
- For LONG: Requires positive sentiment
- For SHORT: Requires negative sentiment
- Uses composite sentiment score

**Returns**: Sentiment alignment checks

---

### `intermarket.py`

**Purpose**: Intermarket analysis and confirmation

**Classes**:
- `IntermarketAnalyzer`: Intermarket analysis engine
  - `check_bond_equity_correlation()`: Check bond-equity relationship
  - `check_usd_impact()`: Check USD impact on assets
  - `check_gold_correlation()`: Check gold correlation
  - `check_credit_spreads()`: Check credit spread conditions
  - `confirm_trade(symbol, direction)`: Confirm trade with intermarket

**Rules**:
- Bonds ↑ → Risk Off → Filter equity longs
- USD ↑ + Yields ↑ → Pressure on equities
- Gold ↑ + VIX ↑ → Defensive regime

**Returns**: Intermarket confirmation signals

---

### `strategy_builder.py`

**Purpose**: Build composite strategies from components

**Classes**:
- `StrategyBuilder`: Strategy composition engine
  - `create_strategy(name, components)`: Create custom strategy
  - `add_technical_component(strategy, component)`: Add technical component
  - `add_fundamental_filter(strategy, filter)`: Add fundamental filter
  - `add_sentiment_filter(strategy, filter)`: Add sentiment filter
  - `add_intermarket_confirmation(strategy, confirmation)`: Add intermarket logic

**Usage**: Allows building custom strategies from components

---

## 🔴 Risk Engine (`core/risk_engine/`)

### `position_sizing.py`

**Purpose**: Calculate position sizes based on risk

**Classes**:
- `PositionSizer`: Position sizing calculator
  - `calculate_position_size(account_value, risk_per_trade, stop_loss_pct)`: Calculate position size
  - `calculate_shares(price, position_size)`: Calculate number of shares
  - `apply_kelly_criterion()`: Apply Kelly Criterion (optional)
  - `apply_fixed_fractional()`: Apply fixed fractional sizing

**Formulas**:
- Position Size = (Account Value × Risk %) / Stop Loss Distance
- Shares = Position Size / Stock Price

**Returns**: Position size in dollars and shares

---

### `drawdown_control.py`

**Purpose**: Monitor and control drawdowns

**Classes**:
- `DrawdownController`: Drawdown monitoring
  - `calculate_drawdown(equity_curve)`: Calculate current drawdown
  - `check_max_drawdown()`: Check against max drawdown limit
  - `should_reduce_risk()`: Determine if risk should be reduced
  - `activate_kill_switch()`: Activate kill switch if needed

**Rules**:
- Monitors peak-to-trough drawdown
- Reduces position sizes if drawdown exceeds threshold
- Activates kill switch if max drawdown exceeded

**Returns**: Drawdown status and risk reduction signals

---

### `exposure_limits.py`

**Purpose**: Manage portfolio exposure and correlation

**Classes**:
- `ExposureManager`: Exposure management
  - `calculate_total_exposure()`: Calculate total portfolio exposure
  - `check_sector_exposure(sector)`: Check sector concentration
  - `check_correlation_exposure()`: Check correlated positions
  - `check_max_position_size(symbol)`: Check individual position limits
  - `can_add_position(symbol, size)`: Check if new position allowed

**Limits**:
- Max total exposure: 100% (configurable)
- Max sector exposure: 25% (configurable)
- Max single position: 10% (configurable)
- Max correlated exposure: 30% (configurable)

**Returns**: Exposure checks and limits

---

## 🟣 Execution Engine (`core/execution_engine/`)

### `backtester.py`

**Purpose**: Event-driven backtesting engine

**Classes**:
- `Backtester`: Main backtesting engine
  - `run_backtest(strategy, start_date, end_date)`: Run backtest
  - `process_bar(bar_data)`: Process each bar/event
  - `execute_trade(signal)`: Execute trade in backtest
  - `apply_slippage(price, direction)`: Apply slippage model
  - `apply_commission(quantity, price)`: Apply commission
  - `calculate_metrics()`: Calculate performance metrics

**Features**:
- Event-driven simulation
- Slippage modeling
- Commission calculation
- Regime-based filtering
- Position sizing logic

**Returns**: Backtest results with metrics

---

### `paper_trader.py`

**Purpose**: Paper trading (simulated live trading)

**Classes**:
- `PaperTrader`: Paper trading engine
  - `initialize_account(initial_capital)`: Initialize paper account
  - `process_market_data(symbol, data)`: Process incoming market data
  - `execute_order(order)`: Execute order (simulated)
  - `update_positions()`: Update position P&L
  - `get_account_summary()`: Get account status

**Features**:
- Simulates live trading without real money
- Tracks P&L, positions, orders
- Uses real-time data feeds

**Returns**: Paper trading account status

---

### `live_trader.py`

**Purpose**: Live trading via broker API

**Classes**:
- `LiveTrader`: Live trading engine
  - `connect_to_broker()`: Connect to broker API
  - `get_account_status()`: Get real account status
  - `place_market_order(symbol, quantity, side)`: Place market order
  - `place_limit_order(symbol, quantity, price, side)`: Place limit order
  - `place_stop_order(symbol, quantity, stop_price)`: Place stop order
  - `cancel_order(order_id)`: Cancel order
  - `get_positions()`: Get current positions
  - `monitor_positions()`: Monitor and manage positions

**Brokers Supported**:
- Groww (growwapi, primary)
- Zerodha Kite
- Upstox

**Safety Features**:
- Pre-trade risk checks
- Kill switch activation
- Order validation

**Returns**: Order status and execution results

---

## 🟠 Analytics (`core/analytics/`)

### `performance.py`

**Purpose**: Calculate performance metrics

**Classes**:
- `PerformanceAnalyzer`: Performance analysis
  - `calculate_cagr(start_value, end_value, years)`: Calculate CAGR
  - `calculate_sharpe_ratio(returns, risk_free_rate)`: Calculate Sharpe ratio
  - `calculate_sortino_ratio(returns)`: Calculate Sortino ratio
  - `calculate_max_drawdown(equity_curve)`: Calculate max drawdown
  - `calculate_win_rate(trades)`: Calculate win rate
  - `calculate_expectancy(trades)`: Calculate trade expectancy
  - `generate_performance_report()`: Generate full report

**Metrics Calculated**:
- CAGR (Compound Annual Growth Rate)
- Sharpe Ratio
- Sortino Ratio
- Max Drawdown
- Win Rate
- Expectancy
- Profit Factor

**Returns**: Performance metrics dictionary

---

### `metrics.py`

**Purpose**: Additional trading metrics

**Classes**:
- `MetricsCalculator`: Metrics calculation
  - `calculate_time_in_market()`: Calculate time in market
  - `calculate_avg_holding_period()`: Calculate average holding period
  - `calculate_avg_win_loss()`: Calculate average win/loss
  - `calculate_recovery_factor()`: Calculate recovery factor
  - `calculate_ulcer_index()`: Calculate Ulcer Index

**Returns**: Additional metrics

---

### `trade_logger.py`

**Purpose**: Log and track all trades

**Classes**:
- `TradeLogger`: Trade logging system
  - `log_trade(trade)`: Log a trade
  - `get_trade_history(start_date, end_date)`: Get trade history
  - `export_trades(format)`: Export trades (CSV, JSON)
  - `analyze_trades()`: Analyze trade patterns

**Data Stored**:
- Entry/exit prices
- Entry/exit times
- Position size
- P&L
- Reason for entry/exit
- Regime at time of trade

**Returns**: Trade logs and analysis

---

## 🟦 Strategies (`strategies/`)

### `equity_trend_following.py`

**Purpose**: Trend-following strategy for equities

**Classes**:
- `EquityTrendFollowing`: Trend-following strategy
  - Inherits from `BaseStrategy`
  - Uses EMA crossovers
  - Requires risk-on regime
  - Filters by fundamentals

**Logic**:
- Long when EMA(50) > EMA(200) and price > EMA(50)
- Short when EMA(50) < EMA(200) and price < EMA(50)
- Requires all layers to pass

---

### `options_volatility.py`

**Purpose**: Options volatility trading strategy

**Classes**:
- `OptionsVolatilityStrategy`: Options strategy
  - Trades based on IV (Implied Volatility)
  - Uses Greeks (Delta, Gamma, Theta)
  - Manages options positions

**Logic**:
- Sell options when IV is high
- Buy options when IV is low
- Manages Greeks exposure

---

### `macro_event_trades.py`

**Purpose**: Trade around macro events

**Classes**:
- `MacroEventStrategy`: Event-driven strategy
  - Trades around economic releases
  - Uses surprise factor
  - Manages event risk

**Logic**:
- Enters before events based on positioning
- Exits after events based on surprise
- Manages event risk

---

## 🤖 AI Strategy Chatbot (`core/ai_chatbot/`)

### `strategy_chatbot.py`

**Purpose**: AI-powered strategy generation and backtesting chatbot

**Classes**:
- `StrategyChatbot`: AI chatbot for strategies
  - `process_user_query(query)`: Process user prompt
  - `generate_strategy_code(prompt)`: Generate strategy code from prompt
  - `backtest_strategy(strategy_code)`: Backtest generated strategy
  - `explain_strategy(strategy_code)`: Explain strategy logic
  - `optimize_strategy(strategy_code, params)`: Optimize strategy parameters

**Features**:
- Natural language to strategy code
- Automatic backtesting
- Strategy explanation
- Parameter optimization

**Returns**: Strategy code, backtest results, explanations

---

## 🎨 UI Components (`ui/`)

### `dashboard.py`

**Purpose**: Main trading dashboard

**Components**:
- Account summary
- Open positions
- P&L chart
- Performance metrics
- Trade log

---

### `charting.py`

**Purpose**: TradingView-style charts

**Components**:
- Price charts with indicators
- Volume charts
- Technical indicators overlay
- Drawing tools
- Strategy signals visualization

**Libraries**: Plotly, TradingView Lightweight Charts

---

### `strategy_builder_ui.py`

**Purpose**: Visual strategy builder

**Components**:
- Drag-and-drop strategy components
- Parameter configuration
- Strategy testing interface

---

## 📊 Configuration (`config/`)

### `settings.yaml`

**Purpose**: General system settings

**Settings**:
- Data refresh intervals
- Default timeframes
- Logging levels
- UI preferences

---

### `broker.yaml`

**Purpose**: Broker configuration

**Settings**:
- Broker type
- API endpoints
- Order types
- Rate limits

---

### `risk.yaml`

**Purpose**: Risk management settings

**Settings**:
- Risk per trade
- Max daily loss
- Max position size
- Drawdown limits
- Kill switch thresholds

---

## 🔄 Main Application (`app.py`)

**Purpose**: Main application entry point

**Functions**:
- Initialize all engines
- Start data feeds
- Run strategy engine
- Launch UI
- Handle shutdown

---

## 📝 Usage Examples

See `notebooks/` for Jupyter notebook examples of using each module.
