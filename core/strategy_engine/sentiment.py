"""
Sentiment Filter

Filters trades based on market sentiment alignment.
"""

from typing import Dict
from core.data_engine.sentiment_data import SentimentAnalyzer


class SentimentFilter:
    """Sentiment-based filtering engine."""
    
    def __init__(self):
        """Initialize sentiment filter."""
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def check_sentiment_alignment(self, symbol: str, direction: str) -> bool:
        """
        Check if sentiment aligns with trade direction.
        
        Args:
            symbol: Stock symbol
            direction: Trade direction ('LONG' or 'SHORT')
            
        Returns:
            True if sentiment aligns
        """
        sentiment = self.sentiment_analyzer.get_composite_sentiment()
        sentiment_score = sentiment.get('composite_score', 50)
        classification = sentiment.get('classification', 'neutral')
        
        if direction == 'LONG':
            # For longs, want positive sentiment
            return sentiment_score > 50 or classification == 'bullish'
        else:  # SHORT
            # For shorts, want negative sentiment
            return sentiment_score < 50 or classification == 'bearish'
    
    def filter_by_sentiment(self, symbols: list, direction: str) -> list:
        """
        Filter symbols by sentiment.
        
        Args:
            symbols: List of symbols
            direction: Trade direction
            
        Returns:
            Filtered list of symbols
        """
        filtered = []
        for symbol in symbols:
            if self.check_sentiment_alignment(symbol, direction):
                filtered.append(symbol)
        return filtered
    
    def get_sentiment_score(self) -> float:
        """Get current sentiment score."""
        sentiment = self.sentiment_analyzer.get_composite_sentiment()
        return sentiment.get('composite_score', 50)
