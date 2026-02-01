# Architecture Documentation

## System Architecture Overview

The Quant Edge trading platform follows a modular, layered architecture designed for scalability and maintainability.

## Component Layers

### 1. Data Layer
- **Purpose**: Data collection and processing
- **Components**: Market data, economic data, news data, sentiment data
- **Responsibilities**: Fetch, clean, normalize, and store data

### 2. Regime Detection Layer
- **Purpose**: Market regime classification
- **Components**: Macro regime detector, risk-on/off analyzer
- **Responsibilities**: Detect market conditions and risk sentiment

### 3. Strategy Layer
- **Purpose**: Trading strategy logic
- **Components**: Base strategy, technical, fundamental, sentiment, intermarket analyzers
- **Responsibilities**: Generate trading signals with multi-layer filtering

### 4. Risk Management Layer
- **Purpose**: Risk control and position management
- **Components**: Position sizing, drawdown control, exposure limits
- **Responsibilities**: Calculate position sizes, monitor drawdowns, enforce limits

### 5. Execution Layer
- **Purpose**: Trade execution
- **Components**: Backtester, paper trader, live trader
- **Responsibilities**: Execute trades in different modes (backtest/paper/live)

### 6. Analytics Layer
- **Purpose**: Performance tracking
- **Components**: Performance analyzer, metrics calculator, trade logger
- **Responsibilities**: Calculate metrics, log trades, generate reports

### 7. UI Layer
- **Purpose**: User interface
- **Components**: Streamlit dashboard, charts, chatbot interface
- **Responsibilities**: Visualize data, interact with system, display results

## Data Flow

```
External APIs → Data Engine → Regime Engine → Strategy Engine → Risk Engine → Execution Engine → Analytics
```

## Design Patterns

- **Strategy Pattern**: BaseStrategy with multiple strategy implementations
- **Factory Pattern**: Strategy creation and execution
- **Observer Pattern**: Real-time data updates
- **Singleton Pattern**: Shared resources (data fetchers, analyzers)

## Technology Stack

- **Backend**: Python 3.9+
- **Data Processing**: pandas, numpy
- **APIs**: yfinance, FRED, NewsAPI, Finnhub
- **ML/AI**: scikit-learn, transformers, Google Gemini (optional, for chatbot)
- **UI**: Streamlit, Plotly
- **Database**: SQLite (default), PostgreSQL (optional)

## Scalability Considerations

- Modular design allows easy addition of new strategies
- API abstraction allows switching data providers
- Configurable risk parameters
- Support for multiple brokers
- Caching for API responses

## Security

- API keys stored in environment variables
- No hardcoded credentials
- Paper trading mode by default
- Kill switch for risk management
- Order validation before execution
