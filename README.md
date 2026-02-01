# Quant Edge – Personal Algorithmic Trading Platform

A personal institutional-grade algorithmic trading system combining:

- **Technical Analysis** (EMA, VWAP, RSI, ATR, Market Structure)
- **Fundamental Macro Analysis** (Central Bank Policy, Economic Data, Policy Impact)
- **Market Sentiment** (Fear & Greed, Put/Call Ratio, VIX Regime, News Sentiment)
- **Risk-On / Risk-Off Regimes** (Macro Regime Detection)
- **Intermarket Relationships** (Bonds, USD, Gold, VIX correlations)

## 🎯 Core Philosophy

This system is **NOT a "strategy bot"** — it is a **Decision Engine**.

Every trade must satisfy:
```
MACRO REGIME ✅ → FUNDAMENTAL BIAS ✅ → SENTIMENT ALIGNMENT ✅ → 
INTERMARKET CONFIRMATION ✅ → TECHNICAL ENTRY ✅ → RISK RULES ✅
```

If **any layer fails → no trade**.

## 🚀 Features

- **Multi-Layer Strategy Engine**: Technical + Fundamental + Sentiment + Intermarket
- **Professional Backtesting**: Event-driven, slippage, commission, regime filtering
- **Live Trading**: Paper trading and live trading via broker APIs
- **Multi-Market Support**: Indian markets (Groww primary; Zerodha, Upstox) + US data via RapidAPI
- **Risk Management**: Position sizing, drawdown control, exposure limits, kill switches
- **Modern UI**: TradingView-style interface with charts, indicators, and trade management
- **AI Strategy Chatbot**: Prompt-based backtesting and strategy generation
- **Analytics Dashboard**: PnL tracking, performance metrics, trade logs

## 📋 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Paper Trading**:
   ```bash
   python -m core.execution_engine.paper_trader
   ```

4. **Start UI**:
   ```bash
   python app.py
   ```

## 📚 Documentation

- **[API & Services Documentation](docs/api_services.md)** - All required APIs and setup
- **[Code Functionality Documentation](docs/code_functionality.md)** - Complete module documentation
- **[Project Workflow Documentation](docs/project_workflow.md)** - What/how/why of the system
- **[Architecture Documentation](docs/architecture.md)** - System design and architecture
- **[Strategy Design](docs/strategy_design.md)** - Strategy philosophy and implementation
- **[Backtesting Guide](docs/backtesting.md)** - How to backtest strategies
- **[Live Trading Guide](docs/live_trading.md)** - Live trading setup and execution
- **[Risk Management](docs/risk_management.md)** - Risk framework and rules
- **[Indian Markets Guide](docs/indian_markets_guide.md)** - NSE/BSE and Indian broker setup
- **[Groww Integration](docs/groww_integration.md)** - Groww broker setup
- **[Groww SDK Reference](docs/groww_sdk_reference.md)** - growwapi SDK reference (from installed package)

## ⚠️ Disclaimer

This system is for **personal trading only**. Trading involves substantial risk of loss. Past performance does not guarantee future results. Use at your own risk.

## 🛠️ Tech Stack

- **Backend**: Python 3.9+
- **Data**: yfinance, pandas, numpy
- **ML/AI**: scikit-learn, transformers (for sentiment analysis)
- **UI**: Streamlit / Dash (TradingView-style interface)
- **Charts**: Plotly, TradingView Lightweight Charts
- **Backtesting**: Custom event-driven engine
- **APIs**: Groww (growwapi), RapidAPI (Yahoo Finance, Alpha Vantage, TradingView, IEX, Trading Economics), Gemini (chatbot)

## 📖 License

Personal use only.
