# Indian Markets Integration Guide

## Overview

This guide explains how to use the Quant Edge platform for Indian stock markets (NSE and BSE) alongside US markets.

## 🇮🇳 Indian Market Support

The platform now supports both **US** and **Indian** markets with the following features:

### Supported Markets

1. **NSE (National Stock Exchange)**
   - Equity stocks
   - Indices (Nifty 50, Bank Nifty, etc.)
   - Futures & Options (via broker APIs)

2. **BSE (Bombay Stock Exchange)**
   - Equity stocks
   - Indices (Sensex, etc.)

## 📊 Data Sources for Indian Markets

### 1. Yahoo Finance (Primary - FREE)
- **Symbol Format**: 
  - NSE: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`
  - BSE: `RELIANCE.BO`, `TCS.BO`
- **Usage**: Historical and real-time data
- **Example**:
  ```python
  from core.data_engine.market_data import MarketDataFetcher
  fetcher = MarketDataFetcher()
  data = fetcher.get_historical_data("RELIANCE.NS", period="1y")
  ```

### 2. NSEpy (NSE Only - FREE)
- **Purpose**: Direct NSE data access
- **Installation**: `pip install nsepy`
- **Usage**: More reliable for NSE historical data
- **Example**:
  ```python
  from core.data_engine.indian_market_data import IndianMarketDataFetcher
  fetcher = IndianMarketDataFetcher(exchange="NSE")
  data = fetcher.get_historical_data("RELIANCE", use_nsepy=True)
  ```

### 3. Zerodha Kite API (Trading & Real-time Data)
- **Purpose**: Real-time quotes, order placement
- **Installation**: `pip install kiteconnect`
- **Usage**: Full trading capabilities
- **Documentation**: https://kite.trade/docs/connect/v3/

### 4. Upstox API (Alternative Trading)
- **Purpose**: Trading and market data
- **Installation**: `pip install upstox-python-sdk`
- **Usage**: Alternative to Zerodha

## 🔑 Indian Broker APIs

### Groww API
- **Status**: Awaiting API documentation
- **Requirements**: See `docs/groww_integration.md`
- **Key Info Needed**:
  - Base URL
  - Authentication method
  - API endpoints
  - Rate limits

### Zerodha Kite API (Recommended Alternative)
- **Why Recommended**: Well-documented, robust, free API access
- **Features**:
  - Full trading capabilities
  - Real-time market data
  - WebSocket support
  - Historical data
- **Setup**:
  1. Sign up at https://kite.trade/
  2. Create API app
  3. Get API key and secret
  4. Implement OAuth flow
  5. Get access token

### Upstox API
- **Features**: Similar to Zerodha
- **Setup**: Sign up at https://upstox.com/

## 📈 Common Indian Stock Symbols

### NSE Top Stocks
- `RELIANCE.NS` - Reliance Industries
- `TCS.NS` - Tata Consultancy Services
- `HDFCBANK.NS` - HDFC Bank
- `INFY.NS` - Infosys
- `ICICIBANK.NS` - ICICI Bank
- `SBIN.NS` - State Bank of India
- `BHARTIARTL.NS` - Bharti Airtel
- `BAJFINANCE.NS` - Bajaj Finance
- `KOTAKBANK.NS` - Kotak Mahindra Bank
- `HINDUNILVR.NS` - Hindustan Unilever

### BSE Top Stocks
- `RELIANCE.BO` - Reliance Industries
- `TCS.BO` - Tata Consultancy Services
- `HDFCBANK.BO` - HDFC Bank

### Indices
- `^NSEI` - Nifty 50
- `^BSESN` - Sensex
- `^NSEBANK` - Bank Nifty
- `^CNXIT` - Nifty IT

## ⏰ Indian Market Hours

- **Pre-market**: 9:00 AM - 9:15 AM IST
- **Market Open**: 9:15 AM IST
- **Market Close**: 3:30 PM IST
- **After-hours**: Until 3:40 PM IST
- **Timezone**: Asia/Kolkata (IST)

## 🔧 Configuration

### Set Market Type

In `.env`:
```bash
MARKET=both  # us | india | both
```

In `config/broker.yaml`:
```yaml
broker:
  type: "groww"  # or "zerodha", "upstox"
  market: "india"
```

### Use Indian Market Data Fetcher

```python
from core.data_engine.indian_market_data import IndianMarketDataFetcher

# For NSE
nse_fetcher = IndianMarketDataFetcher(exchange="NSE")
data = nse_fetcher.get_historical_data("RELIANCE", period="1y")

# For BSE
bse_fetcher = IndianMarketDataFetcher(exchange="BSE")
data = bse_fetcher.get_historical_data("RELIANCE", period="1y")
```

## 📝 Example: Trading Indian Stocks

### Backtest Indian Stock Strategy

```python
from core.execution_engine.backtester import Backtester
from strategies.equity_trend_following import EquityTrendFollowing

strategy = EquityTrendFollowing()
backtester = Backtester(initial_capital=100000)

# Backtest on Indian stock
results = backtester.run_backtest(
    strategy=strategy,
    symbol="RELIANCE.NS",  # NSE symbol
    start_date="2023-01-01",
    end_date="2024-01-01"
)

print(f"Total Return: {results['total_return_pct']:.2f}%")
```

### Get Real-time Quote

```python
from core.data_engine.indian_market_data import IndianMarketDataFetcher

fetcher = IndianMarketDataFetcher(exchange="NSE")
quote = fetcher.get_realtime_quote("RELIANCE")
print(f"Current Price: ₹{quote['price']}")
```

## 🚨 Important Notes

1. **Symbol Format**: Always use `.NS` for NSE and `.BO` for BSE when using Yahoo Finance
2. **Currency**: Indian stocks are in INR (₹), US stocks in USD ($)
3. **Market Hours**: Indian markets operate in IST timezone
4. **Holidays**: Indian markets have different holidays than US markets
5. **Lot Sizes**: Indian derivatives have lot sizes (e.g., Nifty lot size = 50)

## 🔄 Multi-Market Support

The platform supports trading both US and Indian markets simultaneously:

```python
# US stock
us_data = fetcher.get_historical_data("SPY", market="us")

# Indian stock
indian_data = fetcher.get_historical_data("RELIANCE.NS", market="india")
```

## 📚 Additional Resources

- **NSE Website**: https://www.nseindia.com/
- **BSE Website**: https://www.bseindia.com/
- **Zerodha Kite API Docs**: https://kite.trade/docs/connect/v3/
- **Upstox API Docs**: https://upstox.com/developer/api-documentation

## 🆘 Troubleshooting

### Issue: No data returned for Indian symbol
**Solution**: 
- Check symbol format (use `.NS` or `.BO` suffix)
- Verify symbol exists on exchange
- Try using `IndianMarketDataFetcher` with `use_nsepy=True`

### Issue: API authentication fails
**Solution**:
- Verify API keys in `.env`
- Check if OAuth tokens need refresh
- Confirm API endpoint URLs

### Issue: Market hours mismatch
**Solution**:
- Set correct timezone in configuration
- Use IST timezone for Indian markets
- Check market holiday calendar

## ✅ Next Steps

1. **Choose Indian Broker**: Groww, Zerodha, or Upstox
2. **Get API Credentials**: Sign up and get API keys
3. **Configure Environment**: Add credentials to `.env`
4. **Test Data Fetching**: Verify Indian stock data access
5. **Start Trading**: Begin with paper trading

For Groww-specific integration, see `docs/groww_integration.md`.
