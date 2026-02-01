"""
Data Engine Module

Handles all data collection and processing:
- Market data (OHLCV)
- Economic data
- News data
- Sentiment data
"""

from .market_data import MarketDataFetcher
from .economic_data import EconomicDataFetcher
from .news_data import NewsFetcher
from .sentiment_data import SentimentAnalyzer

__all__ = [
    'MarketDataFetcher',
    'EconomicDataFetcher',
    'NewsFetcher',
    'SentimentAnalyzer'
]
