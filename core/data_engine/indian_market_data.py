"""
Indian Market Data Fetcher

Fetches Indian stock market data from NSE, BSE, and other sources.
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional
from datetime import datetime
try:
    from nsepy import get_history
    NSEPY_AVAILABLE = True
except ImportError:
    NSEPY_AVAILABLE = False
    print("Warning: nsepy not installed. Install with: pip install nsepy")


class IndianMarketDataFetcher:
    """Fetches Indian market data from multiple sources."""
    
    def __init__(self, exchange: str = "NSE"):
        """
        Initialize Indian market data fetcher.
        
        Args:
            exchange: Exchange name ('NSE' or 'BSE')
        """
        self.exchange = exchange
        self.suffix = ".NS" if exchange == "NSE" else ".BO"
    
    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize Indian stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'RELIANCE.NS', 'NSE:RELIANCE')
            
        Returns:
            Normalized symbol for Yahoo Finance
        """
        # Remove exchange prefix if present
        if ':' in symbol:
            symbol = symbol.split(':')[-1]
        
        # Remove .NS or .BO suffix if present
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            symbol = symbol[:-3]
        
        # Add appropriate suffix
        if not symbol.endswith(('.NS', '.BO')):
            symbol = symbol + self.suffix
        
        return symbol
    
    def get_historical_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        use_nsepy: bool = False
    ) -> pd.DataFrame:
        """
        Get historical data for Indian stock.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            use_nsepy: Use nsepy library if available (NSE only)
            
        Returns:
            DataFrame with OHLCV data
        """
        # Try nsepy first for NSE stocks (more reliable for Indian data)
        if use_nsepy and NSEPY_AVAILABLE and self.exchange == "NSE":
            try:
                from datetime import datetime, timedelta
                
                # Calculate date range from period
                end_date = datetime.now()
                if period == "1y":
                    start_date = end_date - timedelta(days=365)
                elif period == "6mo":
                    start_date = end_date - timedelta(days=180)
                elif period == "3mo":
                    start_date = end_date - timedelta(days=90)
                elif period == "1mo":
                    start_date = end_date - timedelta(days=30)
                else:
                    start_date = end_date - timedelta(days=365)
                
                # Remove suffix for nsepy
                clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
                
                df = get_history(
                    symbol=clean_symbol,
                    start=start_date,
                    end=end_date
                )
                
                if not df.empty:
                    # Standardize column names
                    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
                    return df
            except Exception as e:
                print(f"Error fetching from nsepy: {e}, falling back to Yahoo Finance")
        
        # Fallback to Yahoo Finance
        normalized_symbol = self.normalize_symbol(symbol)
        try:
            ticker = yf.Ticker(normalized_symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data returned for {symbol}")
            
            # Standardize column names
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            raise
    
    def get_realtime_quote(self, symbol: str) -> Dict:
        """
        Get real-time quote for Indian stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with current price, bid, ask, volume, etc.
        """
        normalized_symbol = self.normalize_symbol(symbol)
        try:
            ticker = yf.Ticker(normalized_symbol)
            info = ticker.info
            
            quote = {
                'symbol': symbol,
                'normalized_symbol': normalized_symbol,
                'exchange': self.exchange,
                'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'bid': info.get('bid', 0),
                'ask': info.get('ask', 0),
                'volume': info.get('volume', 0),
                'previous_close': info.get('previousClose', 0),
                'day_high': info.get('dayHigh', 0),
                'day_low': info.get('dayLow', 0),
                'timestamp': datetime.now()
            }
            
            return quote
        except Exception as e:
            print(f"Error fetching real-time quote for {symbol}: {e}")
            return {}
    
    def get_index_data(self, index_name: str = "NIFTY") -> pd.DataFrame:
        """
        Get Indian index data.
        
        Args:
            index_name: Index name ('NIFTY', 'SENSEX', 'NIFTY50', etc.)
            
        Returns:
            DataFrame with index data
        """
        # Map index names to Yahoo Finance symbols
        index_map = {
            'NIFTY': '^NSEI',
            'NIFTY50': '^NSEI',
            'SENSEX': '^BSESN',
            'BANKNIFTY': '^NSEBANK',
            'NIFTYIT': '^CNXIT'
        }
        
        yahoo_symbol = index_map.get(index_name.upper(), f'^{index_name}')
        
        try:
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(period="1y")
            return df
        except Exception as e:
            print(f"Error fetching index data for {index_name}: {e}")
            return pd.DataFrame()
    
    def get_top_stocks(self, exchange: str = "NSE", limit: int = 10) -> list:
        """
        Get list of top stocks by market cap.
        
        Args:
            exchange: Exchange name
            limit: Number of stocks to return
            
        Returns:
            List of stock symbols
        """
        # Common Indian stocks
        nse_stocks = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
            'ICICIBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'BAJFINANCE.NS', 'KOTAKBANK.NS'
        ]
        
        bse_stocks = [
            'RELIANCE.BO', 'TCS.BO', 'HDFCBANK.BO', 'INFY.BO', 'HINDUNILVR.BO',
            'ICICIBANK.BO', 'SBIN.BO', 'BHARTIARTL.BO', 'BAJFINANCE.BO', 'KOTAKBANK.BO'
        ]
        
        if exchange == "NSE":
            return nse_stocks[:limit]
        else:
            return bse_stocks[:limit]
