"""
Sentiment Data Analyzer

Calculates market sentiment indicators from multiple sources.
"""

import yfinance as yf
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()


class SentimentAnalyzer:
    """Analyzes market sentiment from multiple indicators."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')
        self.cache = {}
    
    def get_fear_greed_index(self) -> Dict:
        """
        Get CNN Fear & Greed Index.
        
        Returns:
            Dictionary with Fear & Greed Index data
        """
        try:
            # Scrape from CNN or use API if available
            # For now, return a placeholder that would be implemented with web scraping
            # or API integration
            
            # Placeholder implementation
            return {
                'value': 50,  # 0-100 scale
                'classification': 'neutral',  # extreme_fear, fear, neutral, greed, extreme_greed
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {e}")
            return {}
    
    def get_vix_level(self) -> Dict:
        """
        Get VIX (Volatility Index) level.
        
        Returns:
            Dictionary with VIX data
        """
        try:
            vix = yf.Ticker("^VIX")
            data = vix.history(period="5d")
            
            if data.empty:
                return {}
            
            current_vix = float(data['Close'].iloc[-1])
            
            # Classify VIX level
            if current_vix < 15:
                regime = 'low_volatility'
            elif current_vix < 20:
                regime = 'normal_volatility'
            elif current_vix < 30:
                regime = 'elevated_volatility'
            else:
                regime = 'high_volatility'
            
            return {
                'value': current_vix,
                'regime': regime,
                'previous_close': float(data['Close'].iloc[-2]) if len(data) > 1 else current_vix,
                'change': float(data['Close'].iloc[-1] - data['Close'].iloc[-2]) if len(data) > 1 else 0,
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error fetching VIX: {e}")
            return {}
    
    def get_put_call_ratio(self) -> Dict:
        """
        Get Put/Call ratio (options market sentiment).
        
        Returns:
            Dictionary with Put/Call ratio data
        """
        try:
            # This would typically come from CBOE or broker API
            # Placeholder implementation
            
            return {
                'ratio': 0.8,  # Put/Call ratio
                'interpretation': 'bullish',  # > 1.0 = bearish, < 1.0 = bullish
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error fetching Put/Call ratio: {e}")
            return {}
    
    def analyze_news_sentiment(self, news_list: List[Dict]) -> Dict:
        """
        Analyze sentiment of news articles using NLP.
        
        Args:
            news_list: List of news articles
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not news_list:
            return {'sentiment_score': 0, 'classification': 'neutral'}
        
        # Simple keyword-based sentiment (can be enhanced with transformers)
        positive_keywords = [
            'bullish', 'rally', 'surge', 'gain', 'profit', 'growth', 'positive',
            'strong', 'beat', 'exceed', 'outperform', 'rise', 'up', 'higher'
        ]
        negative_keywords = [
            'bearish', 'crash', 'plunge', 'loss', 'decline', 'negative', 'weak',
            'miss', 'below', 'underperform', 'fall', 'down', 'lower', 'concern'
        ]
        
        sentiment_scores = []
        
        for article in news_list:
            text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in text)
            negative_count = sum(1 for keyword in negative_keywords if keyword in text)
            
            if positive_count > negative_count:
                sentiment_scores.append(1)
            elif negative_count > positive_count:
                sentiment_scores.append(-1)
            else:
                sentiment_scores.append(0)
        
        avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
        
        # Convert to 0-100 scale
        sentiment_score = 50 + (avg_sentiment * 25)  # Scale -1 to +1 to 25-75
        
        classification = 'neutral'
        if sentiment_score > 60:
            classification = 'positive'
        elif sentiment_score < 40:
            classification = 'negative'
        
        return {
            'sentiment_score': sentiment_score,
            'classification': classification,
            'article_count': len(news_list),
            'timestamp': datetime.now()
        }
    
    def get_composite_sentiment(self) -> Dict:
        """
        Get composite sentiment score from all indicators.
        
        Returns:
            Dictionary with composite sentiment score
        """
        # Get individual sentiment indicators
        fear_greed = self.get_fear_greed_index()
        vix_data = self.get_vix_level()
        put_call = self.get_put_call_ratio()
        
        # Normalize to 0-100 scale
        fear_greed_score = fear_greed.get('value', 50)
        
        # VIX: lower is more bullish (invert for sentiment)
        vix_value = vix_data.get('value', 20)
        vix_score = max(0, min(100, 100 - (vix_value * 2)))  # Invert and scale
        
        # Put/Call: < 1.0 is bullish
        put_call_ratio = put_call.get('ratio', 1.0)
        put_call_score = max(0, min(100, (1.0 / put_call_ratio) * 50)) if put_call_ratio > 0 else 50
        
        # Weighted composite score
        composite_score = (
            fear_greed_score * 0.4 +  # 40% weight
            vix_score * 0.4 +          # 40% weight
            put_call_score * 0.2        # 20% weight
        )
        
        # Classify
        if composite_score > 60:
            classification = 'bullish'
        elif composite_score < 40:
            classification = 'bearish'
        else:
            classification = 'neutral'
        
        return {
            'composite_score': composite_score,
            'classification': classification,
            'components': {
                'fear_greed': fear_greed_score,
                'vix': vix_score,
                'put_call': put_call_score
            },
            'timestamp': datetime.now()
        }
