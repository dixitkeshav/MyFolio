"""
News Data Fetcher

Fetches and processes news headlines and articles.
Uses RapidAPI (Yahoo Finance news, Trading Economics scraper) when RAPIDAPI_KEY is set.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class NewsFetcher:
    """Fetches news articles from multiple sources."""

    def __init__(self):
        """Initialize news fetcher."""
        self.newsapi_key = os.getenv("NEWS_API_KEY")
        self.finnhub_key = os.getenv("FINNHUB_API_KEY")
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")

    def get_market_news(
        self,
        symbol: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Get market news for a symbol or general market news.
        Prefers RapidAPI Yahoo Finance / Trading Economics when RAPIDAPI_KEY is set.
        """
        articles = []

        # RapidAPI: Yahoo Finance news (ticker=AAPL,TSLA)
        if self.rapidapi_key:
            try:
                articles.extend(self._fetch_rapidapi_yahoo_news(symbol, limit))
            except Exception as e:
                print(f"Error fetching from RapidAPI Yahoo: {e}")
        if len(articles) >= limit:
            return articles[:limit]

        # RapidAPI: Trading Economics scraper (by date)
        if self.rapidapi_key:
            try:
                articles.extend(self._fetch_rapidapi_trading_economics(limit - len(articles)))
            except Exception as e:
                print(f"Error fetching from RapidAPI Trading Economics: {e}")
        if len(articles) >= limit:
            return articles[:limit]

        # NewsAPI
        if self.newsapi_key:
            try:
                articles.extend(self._fetch_newsapi(symbol, limit - len(articles)))
            except Exception as e:
                print(f"Error fetching from NewsAPI: {e}")
        if len(articles) >= limit:
            return articles[:limit]

        # Finnhub
        if self.finnhub_key and len(articles) < limit:
            try:
                articles.extend(self._fetch_finnhub(symbol, limit - len(articles)))
            except Exception as e:
                print(f"Error fetching from Finnhub: {e}")

        return articles[:limit]

    def _fetch_rapidapi_yahoo_news(self, symbol: Optional[str], limit: int) -> List[Dict]:
        """Yahoo Finance news via RapidAPI: /api/v1/markets/news?ticker=AAPL%2CTSLA"""
        if not self.rapidapi_key:
            return []
        url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/news"
        params = {}
        if symbol:
            params["ticker"] = symbol.replace(".NS", "").replace(".BO", "")
        headers = {
            "x-rapidapi-host": "yahoo-finance15.p.rapidapi.com",
            "x-rapidapi-key": self.rapidapi_key,
        }
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        body = data.get("body") or data.get("items") or data if isinstance(data, list) else []
        out = []
        for item in (body[:limit] if isinstance(body, list) else []):
            out.append({
                "title": item.get("title", ""),
                "description": item.get("summary", item.get("description", "")),
                "url": item.get("link", item.get("url", "")),
                "published_at": item.get("pubDate", item.get("published_at", "")),
                "source": item.get("publisher", item.get("source", "Yahoo")),
                "symbol": symbol,
            })
        return out

    def _fetch_rapidapi_trading_economics(self, limit: int) -> List[Dict]:
        """Trading Economics news via RapidAPI: get_trading_economics_news?year=&month=&day="""
        if not self.rapidapi_key or limit <= 0:
            return []
        now = datetime.now()
        url = "https://trading-econmics-scraper.p.rapidapi.com/get_trading_economics_news"
        params = {"year": now.year, "month": now.month, "day": now.day}
        headers = {
            "x-rapidapi-host": "trading-econmics-scraper.p.rapidapi.com",
            "x-rapidapi-key": self.rapidapi_key,
        }
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        items = data if isinstance(data, list) else data.get("news", data.get("data", [])) or []
        out = []
        for item in (items[:limit] if isinstance(items, list) else []):
            if isinstance(item, dict):
                out.append({
                    "title": item.get("title", ""),
                    "description": item.get("description", item.get("summary", "")),
                    "url": item.get("url", ""),
                    "published_at": item.get("date", item.get("published_at", "")),
                    "source": "Trading Economics",
                    "symbol": None,
                })
        return out
    
    def _fetch_newsapi(self, symbol: Optional[str], limit: int) -> List[Dict]:
        """Fetch news from NewsAPI."""
        if not self.newsapi_key:
            return []
        
        url = "https://newsapi.org/v2/everything"
        params = {
            'apiKey': self.newsapi_key,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': limit
        }
        
        if symbol:
            params['q'] = symbol
        else:
            params['q'] = 'stock market OR economy OR federal reserve'
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'symbol': symbol
                })
            return articles
        
        return []
    
    def _fetch_finnhub(self, symbol: Optional[str], limit: int) -> List[Dict]:
        """Fetch news from Finnhub."""
        if not self.finnhub_key:
            return []
        
        url = "https://finnhub.io/api/v1/news"
        params = {
            'token': self.finnhub_key,
            'category': 'general'
        }
        
        if symbol:
            url = f"https://finnhub.io/api/v1/company-news"
            params['symbol'] = symbol
            params['from'] = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            params['to'] = datetime.now().strftime('%Y-%m-%d')
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = []
            for article in data[:limit]:
                articles.append({
                    'title': article.get('headline', ''),
                    'description': article.get('summary', ''),
                    'url': article.get('url', ''),
                    'published_at': article.get('datetime', 0),
                    'source': article.get('source', ''),
                    'symbol': symbol
                })
            return articles
        
        return []
    
    def filter_relevant_news(
        self, 
        news_list: List[Dict], 
        keywords: List[str]
    ) -> List[Dict]:
        """
        Filter news articles by relevant keywords.
        
        Args:
            news_list: List of news articles
            keywords: List of keywords to filter by
            
        Returns:
            Filtered list of relevant articles
        """
        if not keywords:
            return news_list
        
        relevant = []
        keywords_lower = [k.lower() for k in keywords]
        
        for article in news_list:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            
            text = title + ' ' + description
            
            if any(keyword in text for keyword in keywords_lower):
                relevant.append(article)
        
        return relevant
