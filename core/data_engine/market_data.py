"""
Market Data Fetcher

Fetches and processes market price data (OHLCV) from multiple sources.
Indian symbols (.NS, .BO, NSE indices) use IndianMarketDataFetcher (yfinance with correct tickers).
US/other use RapidAPI when RAPIDAPI_KEY is set; else yfinance.
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

# Optional: yfinance as fallback when RapidAPI not used or fails
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

try:
    from core.data_engine.stock_search import is_indian_symbol
except Exception:
    def is_indian_symbol(symbol: str) -> bool:
        return bool(symbol and (symbol.upper().endswith(".NS") or symbol.upper().endswith(".BO")))

try:
    from core.data_engine.indian_market_data import IndianMarketDataFetcher
    INDIAN_FETCHER_AVAILABLE = True
except Exception:
    INDIAN_FETCHER_AVAILABLE = False
    IndianMarketDataFetcher = None


class MarketDataFetcher:
    """Fetches and processes market data from multiple sources."""

    def __init__(self, primary_source: str = "auto"):
        """
        Initialize market data fetcher.

        Args:
            primary_source: 'auto' (RapidAPI if key set, else yfinance), 'rapidapi', 'yfinance'
        """
        self.primary_source = primary_source
        self.cache = {}
        self._rapidapi_available = self._check_rapidapi()
        self._indian_fetcher = IndianMarketDataFetcher(exchange="NSE") if INDIAN_FETCHER_AVAILABLE else None

    def _check_rapidapi(self) -> bool:
        try:
            from core.data_engine.rapidapi_client import is_available
            return is_available()
        except Exception:
            return bool(os.getenv("RAPIDAPI_KEY"))

    def get_historical_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        use_cache: bool = True,
        market: str = "us",
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data for a symbol.
        Indian symbols use IndianMarketDataFetcher (yfinance .NS/.BO). US/other use RapidAPI or yfinance.
        """
        cache_key = f"{symbol}_{period}_{interval}"
        if use_cache and cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(minutes=5):
                return cached_data.copy()

        # Indian market: use Indian fetcher (correct NSE/BSE tickers)
        if (market == "india" or is_indian_symbol(symbol)) and self._indian_fetcher:
            try:
                df = self._indian_fetcher.get_historical_data(symbol, period=period, interval=interval)
                if df is not None and not df.empty:
                    df = self.clean_data(df)
                    self.cache[cache_key] = (df.copy(), datetime.now())
                    return df
            except Exception as e:
                print(f"Indian market data fallback for {symbol}: {e}")

        use_rapidapi = (self.primary_source == "rapidapi" or (self.primary_source == "auto" and self._rapidapi_available))
        if use_rapidapi:
            df = self._get_historical_rapidapi(symbol, period, interval)
            if df is not None and not df.empty:
                df = self.clean_data(df)
                self.cache[cache_key] = (df.copy(), datetime.now())
                return df

        if YF_AVAILABLE:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, interval=interval)
                if df.empty:
                    raise ValueError(f"No data returned for {symbol}")
                df = self.clean_data(df)
                self.cache[cache_key] = (df.copy(), datetime.now())
                return df
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                raise
        raise RuntimeError("No data source available. Set RAPIDAPI_KEY or install yfinance.")

    def _get_historical_rapidapi(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        """Fetch historical data via RapidAPI Alpha Vantage."""
        try:
            key = os.getenv("RAPIDAPI_KEY")
            if not key:
                return None
            # Alpha Vantage via RapidAPI: function=TIME_SERIES_DAILY, symbol=MSFT, outputsize=compact/full
            outputsize = "full" if period in ("2y", "5y", "10y", "max") else "compact"
            url = "https://alpha-vantage.p.rapidapi.com/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol.replace(".NS", "").replace(".BO", ""),
                "outputsize": outputsize,
                "datatype": "json",
            }
            headers = {"x-rapidapi-host": "alpha-vantage.p.rapidapi.com", "x-rapidapi-key": key}
            r = requests.get(url, headers=headers, params=params, timeout=15)
            if r.status_code != 200:
                return None
            data = r.json()
            ts = data.get("Time Series (Daily)") or data.get("time_series_daily")
            if not ts:
                return None
            rows = []
            for date_str, ohlcv in ts.items():
                rows.append({
                    "date": date_str,
                    "open": float(ohlcv.get("1. open", ohlcv.get("open", 0))),
                    "high": float(ohlcv.get("2. high", ohlcv.get("high", 0))),
                    "low": float(ohlcv.get("3. low", ohlcv.get("low", 0))),
                    "close": float(ohlcv.get("4. close", ohlcv.get("close", 0))),
                    "volume": int(float(ohlcv.get("5. volume", ohlcv.get("volume", 0)))),
                })
            df = pd.DataFrame(rows)
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index()
            return df
        except Exception as e:
            print(f"RapidAPI Alpha Vantage error for {symbol}: {e}")
            return None
    
    def get_realtime_quote(self, symbol: str, market: str = "us") -> Dict:
        """
        Get real-time price quote for a symbol.
        Indian symbols use IndianMarketDataFetcher. US/other use RapidAPI or yfinance.
        """
        # Indian market: use Indian fetcher so .NS/.BO tickers work
        if (market == "india" or is_indian_symbol(symbol)) and self._indian_fetcher:
            q = self._indian_fetcher.get_realtime_quote(symbol)
            if q and q.get("price"):
                return q
        if self._rapidapi_available:
            q = self._get_quote_rapidapi(symbol)
            if q:
                return q
        if YF_AVAILABLE:
            try:
                # For Indian symbols ensure we pass normalized symbol to yf
                sym = symbol
                if (market == "india" or is_indian_symbol(symbol)) and self._indian_fetcher:
                    sym = self._indian_fetcher.normalize_symbol(symbol)
                ticker = yf.Ticker(sym)
                info = ticker.info
                return {
                    "symbol": symbol,
                    "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                    "bid": info.get("bid", 0),
                    "ask": info.get("ask", 0),
                    "volume": info.get("volume", 0),
                    "previous_close": info.get("previousClose", 0),
                    "timestamp": datetime.now(),
                }
            except Exception as e:
                print(f"Error fetching real-time quote for {symbol}: {e}")
        return {}

    def _get_quote_rapidapi(self, symbol: str) -> Optional[Dict]:
        """Get quote via RapidAPI Alpha Vantage GLOBAL_QUOTE."""
        try:
            key = os.getenv("RAPIDAPI_KEY")
            if not key:
                return None
            url = "https://alpha-vantage.p.rapidapi.com/query"
            params = {"function": "GLOBAL_QUOTE", "symbol": symbol.replace(".NS", "").replace(".BO", "")}
            headers = {"x-rapidapi-host": "alpha-vantage.p.rapidapi.com", "x-rapidapi-key": key}
            r = requests.get(url, headers=headers, params=params, timeout=10)
            if r.status_code != 200:
                return None
            data = r.json()
            gq = data.get("Global Quote") or data.get("global_quote") or {}
            price = float(gq.get("05. price", gq.get("price", 0)) or 0)
            if not price:
                return None
            return {
                "symbol": symbol,
                "price": price,
                "bid": float(gq.get("09. bid", 0) or 0),
                "ask": float(gq.get("10. ask", 0) or 0),
                "volume": int(float(gq.get("06. volume", 0) or 0)),
                "previous_close": float(gq.get("08. previous close", 0) or 0),
                "timestamp": datetime.now(),
            }
        except Exception:
            return None
    
    def get_multiple_symbols(
        self, 
        symbols: List[str], 
        period: str = "1y",
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            period: Time period
            interval: Data interval
            
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        data = {}
        for symbol in symbols:
            try:
                data[symbol] = self.get_historical_data(symbol, period, interval)
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue
        return data
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize price data.
        
        Args:
            df: Raw DataFrame from data source
            
        Returns:
            Cleaned DataFrame with standardized columns
        """
        # Standardize column names
        df.columns = [col.replace(' ', '_').lower() for col in df.columns]
        
        # Ensure we have required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                # Try alternative column names
                if col == 'open' and 'Open' in df.columns:
                    df['open'] = df['Open']
                elif col == 'high' and 'High' in df.columns:
                    df['high'] = df['High']
                elif col == 'low' and 'Low' in df.columns:
                    df['low'] = df['Low']
                elif col == 'close' and 'Close' in df.columns:
                    df['close'] = df['Close']
                elif col == 'volume' and 'Volume' in df.columns:
                    df['volume'] = df['Volume']
        
        # Remove rows with missing data
        df = df.dropna(subset=['open', 'high', 'low', 'close'])
        
        # Fill missing volume with 0
        if 'volume' in df.columns:
            df['volume'] = df['volume'].fillna(0)
        
        # Ensure data is sorted by date
        df = df.sort_index()
        
        return df
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add basic technical indicators to DataFrame.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added technical indicators
        """
        df = df.copy()
        
        # Simple Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # ATR (Average True Range)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr'] = true_range.rolling(window=14).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        return df
    
    def detect_market_structure(self, df: pd.DataFrame) -> Dict:
        """
        Detect market structure (higher highs, lower lows, etc.).
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with market structure information
        """
        df = df.copy()
        
        # Find local highs and lows
        df['local_high'] = (df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1))
        df['local_low'] = (df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1))
        
        highs = df[df['local_high']]['high'].tail(5).tolist()
        lows = df[df['local_low']]['low'].tail(5).tolist()
        
        structure = {
            'trend': 'neutral',
            'higher_highs': len([h for i, h in enumerate(highs[1:]) if h > highs[i]]) > len(highs) / 2,
            'lower_lows': len([l for i, l in enumerate(lows[1:]) if l < lows[i]]) > len(lows) / 2,
            'recent_high': highs[-1] if highs else None,
            'recent_low': lows[-1] if lows else None
        }
        
        if structure['higher_highs'] and not structure['lower_lows']:
            structure['trend'] = 'uptrend'
        elif structure['lower_lows'] and not structure['higher_highs']:
            structure['trend'] = 'downtrend'
        
        return structure
