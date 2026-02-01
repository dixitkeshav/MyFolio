# API & Services Documentation

This document lists all required APIs, services, and external dependencies for the Quant Edge trading platform.

## 🔑 Required API Keys & Services

### RapidAPI (Single Key for Multiple Data Sources)

One **RAPIDAPI_KEY** is used for all RapidAPI-hosted APIs. Sign up at https://rapidapi.com and subscribe to the APIs below.

| RapidAPI Host | Purpose | Endpoint Example |
|---------------|---------|------------------|
| **yahoo-finance15.p.rapidapi.com** | Yahoo Finance news, market data | `/api/v1/markets/news?ticker=AAPL,TSLA` |
| **alpha-vantage.p.rapidapi.com** | Alpha Vantage (TIME_SERIES_DAILY, GLOBAL_QUOTE) | `/query?function=TIME_SERIES_DAILY&symbol=MSFT` |
| **tradingview18.p.rapidapi.com** | TradingView symbols, data | `/symbols/auto-complete?query=tesla` |
| **investors-exchange-iex-trading.p.rapidapi.com** | IEX short interest, stock data | `/stock/GOOG/short-interest` |
| **trading-econmics-scraper.p.rapidapi.com** | Trading Economics news | `/get_trading_economics_news?year=2024&month=4&day=12` |

- **Env var**: `RAPIDAPI_KEY`
- **Usage**: Market data (Yahoo/Alpha Vantage), news (Yahoo/Trading Economics), IEX, TradingView

### 1. Market Data APIs

#### **Yahoo Finance (yfinance)** - FREE
- **Purpose**: Historical and real-time price data (OHLCV)
- **Setup**: No API key required (or use RapidAPI Yahoo Finance with RAPIDAPI_KEY)
- **Rate Limits**: Moderate (be respectful)
- **Usage**: Primary/fallback data source for equities, ETFs, indices
- **Python Package**: `yfinance`

#### **Alpha Vantage** - FREE (with limits) / PAID / via RapidAPI
- **Purpose**: Real-time and historical market data, technical indicators
- **API Key**: Required (free tier: 5 calls/min, 500 calls/day)
- **Signup**: https://www.alphavantage.co/support/#api-key
- **Usage**: Backup data source, technical indicators
- **Python Package**: `alpha_vantage`

#### **Polygon.io** - PAID (Recommended for Production)
- **Purpose**: Professional-grade market data, real-time quotes
- **Pricing**: Starts at $29/month
- **Signup**: https://polygon.io/
- **Usage**: Production-grade real-time data
- **Python Package**: `polygon`

#### **IEX Cloud** - PAID
- **Purpose**: Real-time and historical market data
- **Pricing**: Starts at $9/month
- **Signup**: https://iexcloud.io/
- **Usage**: Alternative data provider
- **Python Package**: `iexfinance`

#### **Indian Market Data APIs**

##### **NSEpy** - FREE
- **Purpose**: NSE (National Stock Exchange) data
- **Setup**: No API key required
- **Usage**: Historical and real-time NSE data
- **Python Package**: `nsepy`
- **Features**: Equity, derivatives, indices data
- **Market**: India (NSE)

##### **BSEpy** - FREE
- **Purpose**: BSE (Bombay Stock Exchange) data
- **Setup**: No API key required
- **Usage**: Historical BSE data
- **Python Package**: `bsepy`
- **Features**: Equity, indices data
- **Market**: India (BSE)

##### **Yahoo Finance (Indian Stocks)** - FREE
- **Purpose**: Indian stock data via Yahoo Finance
- **Setup**: No API key required
- **Usage**: Use `.NS` suffix for NSE, `.BO` for BSE
- **Examples**: `RELIANCE.NS`, `TCS.NS`, `INFY.BO`
- **Python Package**: `yfinance`
- **Market**: India (via Yahoo Finance)

##### **Alpha Vantage (Indian Stocks)** - FREE/PAID
- **Purpose**: Indian stock data
- **API Key**: Required
- **Usage**: Use Indian stock symbols
- **Python Package**: `alpha_vantage`
- **Market**: India (supports Indian stocks)

### 2. Economic Data APIs

#### **US Economic Data**

##### **FRED (Federal Reserve Economic Data)** - FREE
- **Purpose**: Economic indicators, interest rates, employment data
- **API Key**: Required (free, unlimited)
- **Signup**: https://fred.stlouisfed.org/docs/api/api_key.html
- **Usage**: Central bank data, economic calendar
- **Python Package**: `fredapi`
- **Market**: US

#### **Indian Economic Data**

##### **RBI (Reserve Bank of India) API** - FREE
- **Purpose**: Indian economic indicators, interest rates, RBI policy
- **API Key**: Not required (public data)
- **Usage**: RBI policy rates, economic indicators
- **Python Package**: Custom wrapper or web scraping
- **Market**: India
- **Documentation**: https://www.rbi.org.in/scripts/Statistics.aspx

##### **Trading Economics India** - FREE/PAID
- **Purpose**: Indian economic calendar, indicators
- **API Key**: Required for API access
- **Signup**: https://tradingeconomics.com/api
- **Usage**: Indian economic events, forecasts
- **Python Package**: Custom API wrapper
- **Market**: India

#### **Trading Economics** - PAID
- **Purpose**: Comprehensive economic calendar, forecasts
- **Pricing**: Starts at $49/month
- **Signup**: https://tradingeconomics.com/api
- **Usage**: Economic calendar events, forecasts
- **Python Package**: Custom API wrapper

#### **Economic Calendar API** - FREE/PAID
- **Purpose**: Economic event calendar
- **API Key**: Required
- **Signup**: https://www.economiccalendar.com/api/
- **Usage**: Economic event tracking

### 3. News & Sentiment APIs

#### **NewsAPI** - FREE (with limits) / PAID
- **Purpose**: News headlines, articles
- **API Key**: Required (free tier: 100 requests/day)
- **Signup**: https://newsapi.org/
- **Usage**: News sentiment analysis
- **Python Package**: `newsapi-python`

#### **Finnhub** - FREE (with limits) / PAID
- **Purpose**: News, sentiment, company data
- **API Key**: Required (free tier: 60 calls/min)
- **Signup**: https://finnhub.io/
- **Usage**: News sentiment, company fundamentals
- **Python Package**: `finnhub-python`

#### **Alpha Vantage News & Sentiment** - FREE/PAID
- **Purpose**: News sentiment analysis
- **API Key**: Same as Alpha Vantage
- **Usage**: News sentiment scoring

### 4. Market Sentiment Indicators

#### **Fear & Greed Index** - FREE
- **Purpose**: Market sentiment indicator (0-100)
- **Source**: CNN Fear & Greed Index (web scraping or API)
- **Usage**: Risk-on/risk-off detection
- **Implementation**: Web scraping or API if available

#### **CBOE VIX Data** - FREE
- **Purpose**: Volatility index (fear gauge)
- **Source**: Yahoo Finance (VIX ticker)
- **Usage**: Volatility regime detection
- **Implementation**: Via yfinance

#### **Put/Call Ratio** - FREE
- **Purpose**: Options market sentiment
- **Source**: CBOE (web scraping) or broker API
- **Usage**: Sentiment confirmation

### 5. Broker APIs (Trading Execution)

#### **US / Other Brokers**

##### **Interactive Brokers (IBKR)** - PAID
- **Purpose**: Professional trading platform
- **API**: TWS API (Trader Workstation)
- **Setup**: Requires TWS installation
- **Usage**: Advanced trading, international markets
- **Python Package**: `ib_insync` or `ibapi`
- **Market**: US and International

#### **Indian Market Brokers**

##### **Groww** - FREE/PAID
- **Purpose**: Indian stock trading, mutual funds, ETFs
- **API Key**: Required (if API available)
- **Signup**: https://groww.in/
- **Usage**: Primary broker for Indian equities
- **Python Package**: Custom wrapper (to be implemented)
- **Features**: NSE/BSE trading, mutual funds
- **Market**: India (NSE/BSE)
- **Key Requirements**:
  - API Key (if Groww provides API)
  - API Secret
  - User ID
  - Access Token (OAuth if applicable)
  - Base URL (to be confirmed from Groww documentation)

##### **Zerodha Kite API** - FREE (API Access)
- **Purpose**: Indian stock trading, derivatives, commodities
- **API Key**: Required
- **Signup**: https://kite.trade/
- **Usage**: Popular Indian broker with robust API
- **Python Package**: `kiteconnect`
- **Features**: NSE/BSE/NFO/CDS/MCX trading, real-time data
- **Market**: India
- **Key Requirements**:
  - API Key
  - API Secret
  - Access Token (OAuth)
  - Request Token (for OAuth flow)
- **Documentation**: https://kite.trade/docs/connect/v3/

##### **Upstox** - FREE (API Access)
- **Purpose**: Indian stock trading, derivatives
- **API Key**: Required
- **Signup**: https://upstox.com/
- **Usage**: Indian broker with API access
- **Python Package**: `upstox-python-sdk`
- **Features**: NSE/BSE/NFO/CDS/MCX trading
- **Market**: India
- **Key Requirements**:
  - API Key
  - API Secret
  - Access Token (OAuth)
- **Documentation**: https://upstox.com/developer/api-documentation

#### **Interactive Brokers (IBKR)** - PAID
- **Purpose**: Professional trading platform
- **API**: TWS API (Trader Workstation)
- **Setup**: Requires TWS installation
- **Usage**: Advanced trading, international markets
- **Python Package**: `ib_insync` or `ibapi`

#### **TD Ameritrade (Schwab)** - FREE
- **Purpose**: Trading execution
- **API Key**: Required
- **Signup**: https://developer.tdameritrade.com/
- **Usage**: Alternative broker
- **Python Package**: `tda-api`

#### **E*TRADE** - FREE
- **Purpose**: Trading execution
- **API Key**: Required
- **Signup**: https://developer.etrade.com/
- **Usage**: Alternative broker

### 6. Options Data APIs

#### **CBOE Options Data** - PAID
- **Purpose**: Options chain data, Greeks, IV
- **Pricing**: Varies
- **Signup**: https://www.cboe.com/us/options/market_statistics/
- **Usage**: Options strategies, Greeks calculation

#### **Polygon.io Options** - PAID
- **Purpose**: Options chain, Greeks, IV
- **Usage**: Options data (included with Polygon subscription)

### 7. Machine Learning / AI Services

#### **Google Gemini API** (Optional) - FREE tier / PAID
- **Purpose**: Strategy chatbot, natural language strategy generation
- **API Key**: Required (GEMINI_API_KEY)
- **Signup**: https://aistudio.google.com/apikey or https://makersuite.google.com/
- **Usage**: AI-powered strategy generation and backtesting chatbot
- **Python Package**: `google-generativeai`

#### **Hugging Face Transformers** - FREE
- **Purpose**: Sentiment analysis models, NLP
- **Usage**: News sentiment analysis, text processing
- **Python Package**: `transformers`, `torch`

#### **scikit-learn** - FREE
- **Purpose**: ML models for regime classification, feature engineering
- **Usage**: Regime detection, pattern recognition
- **Python Package**: `scikit-learn`

## 📦 Python Package Dependencies

### Core Dependencies
```python
pandas>=2.0.0
numpy>=1.24.0
yfinance>=0.2.0
requests>=2.31.0
python-dotenv>=1.0.0
pyyaml>=6.0
```

### Data & APIs
```python
alpha-vantage>=2.3.1
fredapi>=0.5.0
newsapi-python>=0.2.7
finnhub-python>=2.4.0
growwapi>=1.5.0  # Groww (Indian broker)
```

### ML & AI
```python
scikit-learn>=1.3.0
transformers>=4.30.0
torch>=2.0.0
google-generativeai>=0.8.0  # Gemini for strategy chatbot
```

### UI & Visualization
```python
streamlit>=1.28.0
plotly>=5.17.0
dash>=2.14.0
pandas-ta>=0.3.14b0  # Technical indicators
```

### Backtesting & Analysis
```python
backtrader>=1.9.78  # Optional alternative
ta-lib>=0.4.28  # Technical analysis library (optional)
```

## 🔧 Environment Variables Setup

Create a `.env` file with the following:

```bash
# Broker Configuration
BROKER_TYPE=groww  # groww, zerodha, upstox
GROWW_ACCESS_TOKEN=your_groww_access_token
GROWW_API_KEY=your_groww_api_key  # if using get_access_token

# RapidAPI (one key for Yahoo Finance, Alpha Vantage, TradingView, IEX, Trading Economics)
RAPIDAPI_KEY=your_rapidapi_key

# Market Data APIs (optional if using RapidAPI)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
POLYGON_API_KEY=your_polygon_key  # Optional
IEX_API_KEY=your_iex_key  # Optional

# Economic Data
FRED_API_KEY=your_fred_api_key
TRADING_ECONOMICS_API_KEY=your_te_key  # Optional

# News & Sentiment
NEWS_API_KEY=your_newsapi_key
FINNHUB_API_KEY=your_finnhub_key

# AI/ML Services (Optional)
GEMINI_API_KEY=your_gemini_key  # For strategy chatbot

# Trading Configuration
MODE=paper  # paper | live
RISK_PER_TRADE=0.01  # 1% risk per trade
MAX_DAILY_LOSS=0.05  # 5% max daily loss
MAX_POSITION_SIZE=0.1  # 10% max position size

# Database (Optional)
DATABASE_URL=sqlite:///trading.db  # SQLite by default
```

## 🚀 Setup Instructions

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get API Keys
1. **Essential (Free)**:
   - FRED API Key (economic data)
   - Alpha Vantage API Key (market data backup)
   - NewsAPI Key (news sentiment)
   - Finnhub API Key (sentiment)

2. **Recommended**:
   - RapidAPI key (Yahoo Finance, Alpha Vantage, TradingView, IEX, Trading Economics)
   - Groww API/access token (Indian broker)
   - Polygon.io (production data, optional)
   - Gemini API (for strategy chatbot, optional)

### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Step 4: Test API Connections
```bash
python scripts/test_apis.py
```

## 📊 Free Tier Limitations

### Free Tier Limits:
- **Alpha Vantage**: 5 calls/min, 500 calls/day
- **NewsAPI**: 100 requests/day
- **Finnhub**: 60 calls/min
- **FRED**: Unlimited (free)

### Recommendations:
- Start with free tiers for development
- Upgrade to paid tiers for production/live trading
- Use caching to minimize API calls
- Implement rate limiting in code

## 🔒 Security Best Practices

1. **Never commit `.env` file** to git
2. **Use environment variables** for all API keys
3. **Rotate API keys** regularly
4. **Use paper trading** first before live trading
5. **Implement rate limiting** to avoid API abuse
6. **Monitor API usage** to avoid unexpected charges

## 📝 API Usage Examples

See `scripts/test_apis.py` for examples of connecting to each API.

## 🆘 Troubleshooting

### Common Issues:
1. **Rate Limit Errors**: Implement exponential backoff
2. **API Key Invalid**: Check `.env` file and API key validity
3. **Connection Timeout**: Check internet connection and API status
4. **Data Missing**: Verify API key permissions and data availability

## 🔄 API Status Monitoring

Monitor API status pages:
- Alpha Vantage: https://status.alphavantage.co/
- Polygon: https://status.polygon.io/
- RapidAPI: https://rapidapi.com/developer/dashboard
