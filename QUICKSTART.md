# Quick Start Guide

## 🚀 Getting Started

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Some packages may require additional setup:
- `ta-lib`: May require system libraries. See: https://ta-lib.org/install/

### Step 2: Configure Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   # Essential (Free APIs)
   FRED_API_KEY=your_fred_key_here
   NEWS_API_KEY=your_newsapi_key_here
   FINNHUB_API_KEY=your_finnhub_key_here
   
   # Optional (for chatbot)
   GEMINI_API_KEY=your_gemini_key_here
   
   # Broker (for live trading - start with paper trading)
   GROWW_ACCESS_TOKEN=your_groww_access_token_here
   RAPIDAPI_KEY=your_rapidapi_key_here
   ```

### Step 3: Get API Keys

#### Free API Keys (Start Here):

1. **FRED API** (Economic Data)
   - Sign up: https://fred.stlouisfed.org/docs/api/api_key.html
   - Free, unlimited

2. **NewsAPI** (News Data)
   - Sign up: https://newsapi.org/
   - Free tier: 100 requests/day

3. **Finnhub** (News & Sentiment)
   - Sign up: https://finnhub.io/
   - Free tier: 60 calls/min

4. **Alpha Vantage** (Market Data Backup)
   - Sign up: https://www.alphavantage.co/support/#api-key
   - Free tier: 5 calls/min, 500 calls/day

#### Optional (Paid):

- **Gemini API**: For strategy chatbot (Google AI Studio)
- **Groww**: For Indian market trading (growwapi). **RapidAPI**: One key for Yahoo Finance, Alpha Vantage, TradingView, IEX, Trading Economics

### Step 4: Run the Application

```bash
streamlit run app.py
```

The UI will open in your browser at `http://localhost:8501`

## 📖 Usage Examples

### 1. View Market Regime

1. Open the Dashboard
2. View current market regime (RISK_ON, RISK_OFF, NEUTRAL)
3. Check risk score and confidence

### 2. View Charts

1. Go to "Charts" page
2. Enter a symbol (e.g., SPY, AAPL)
3. Select time period
4. Click "Load Chart"
5. View price chart with technical indicators

### 3. Backtest a Strategy with Chatbot

1. Go to "Backtesting Chatbot" page
2. Enter a strategy description:
   ```
   Create a strategy that buys SPY when RSI is below 30 
   and backtest it from 2023-01-01 to 2024-01-01
   ```
3. Click "Generate & Backtest"
4. View results and equity curve

### 4. Paper Trading

1. Go to "Paper Trading" page
2. Enter symbol, side (BUY/SELL), quantity
3. Select order type (MARKET or LIMIT)
4. Click "Place Order"
5. View positions on Dashboard

## 🧪 Testing the System

### Test Data Fetching

```python
from core.data_engine.market_data import MarketDataFetcher

fetcher = MarketDataFetcher()
data = fetcher.get_historical_data("SPY", period="1y")
print(data.head())
```

### Test Regime Detection

```python
from core.regime_engine.macro_regime import MacroRegimeDetector

detector = MacroRegimeDetector()
regime = detector.detect_regime()
print(f"Current Regime: {regime['regime']}")
```

### Test Backtesting

```python
from core.execution_engine.backtester import Backtester
from strategies.equity_trend_following import EquityTrendFollowing

strategy = EquityTrendFollowing()
backtester = Backtester(initial_capital=100000)

results = backtester.run_backtest(
    strategy=strategy,
    symbol="SPY",
    start_date="2023-01-01",
    end_date="2024-01-01"
)

print(f"Total Return: {results['total_return_pct']:.2f}%")
print(f"Sharpe Ratio: {results['metrics']['sharpe_ratio']:.2f}")
```

## ⚠️ Important Notes

1. **Start with Paper Trading**: Never use live trading until you've thoroughly tested in paper mode
2. **API Rate Limits**: Free APIs have rate limits - be mindful of your usage
3. **Risk Management**: Always set appropriate risk parameters before trading
4. **Data Quality**: Market data quality depends on API availability
5. **No Financial Advice**: This is a tool for personal use, not financial advice

## 🐛 Troubleshooting

### Import Errors

If you get import errors, make sure you're running from the project root:
```bash
cd /path/to/MyFolio
python -m streamlit run app.py
```

### API Errors

- Check your `.env` file has correct API keys
- Verify API keys are valid
- Check API rate limits haven't been exceeded

### Data Fetching Issues

- Check internet connection
- Verify symbol is correct (e.g., "SPY" not "spy")
- Try a different time period

## 📚 Next Steps

1. Read the full documentation:
   - `docs/api_services.md` - API setup guide
   - `docs/code_functionality.md` - Code documentation
   - `docs/project_workflow.md` - System workflow

2. Explore strategies:
   - `strategies/equity_trend_following.py` - Example strategy

3. Customize:
   - Edit `config/risk.yaml` for risk parameters
   - Create your own strategies
   - Customize UI in `app.py`

## 🆘 Support

For issues or questions:
1. Check the documentation in `docs/`
2. Review error messages carefully
3. Check API status pages
4. Verify environment setup

Happy Trading! 📈
