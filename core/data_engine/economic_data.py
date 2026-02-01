"""
Economic Data Fetcher

Fetches economic indicators and calendar events from FRED and other sources.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from fredapi import Fred
import os
from dotenv import load_dotenv
import requests

load_dotenv()


class EconomicDataFetcher:
    """Fetches and processes economic data."""
    
    def __init__(self):
        """Initialize economic data fetcher."""
        fred_api_key = os.getenv('FRED_API_KEY')
        if fred_api_key:
            self.fred = Fred(api_key=fred_api_key)
        else:
            self.fred = None
            print("Warning: FRED_API_KEY not set. Economic data features limited.")
    
    def get_fed_funds_rate(self) -> Dict:
        """
        Get Federal Reserve interest rates.
        
        Returns:
            Dictionary with current rate and historical data
        """
        if not self.fred:
            return {}
        
        try:
            # Federal Funds Effective Rate
            series_id = 'FEDFUNDS'
            data = self.fred.get_series(series_id, observation_start='2020-01-01')
            
            return {
                'current_rate': float(data.iloc[-1]) if not data.empty else None,
                'previous_rate': float(data.iloc[-2]) if len(data) > 1 else None,
                'change': float(data.iloc[-1] - data.iloc[-2]) if len(data) > 1 else None,
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error fetching Fed funds rate: {e}")
            return {}
    
    def get_unemployment_rate(self) -> Dict:
        """
        Get unemployment rate data.
        
        Returns:
            Dictionary with unemployment rate information
        """
        if not self.fred:
            return {}
        
        try:
            # Unemployment Rate
            series_id = 'UNRATE'
            data = self.fred.get_series(series_id, observation_start='2020-01-01')
            
            return {
                'current_rate': float(data.iloc[-1]) if not data.empty else None,
                'previous_rate': float(data.iloc[-2]) if len(data) > 1 else None,
                'change': float(data.iloc[-1] - data.iloc[-2]) if len(data) > 1 else None,
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error fetching unemployment rate: {e}")
            return {}
    
    def get_cpi_data(self) -> Dict:
        """
        Get Consumer Price Index (CPI) data.
        
        Returns:
            Dictionary with CPI information
        """
        if not self.fred:
            return {}
        
        try:
            # CPI for All Urban Consumers
            series_id = 'CPIAUCSL'
            data = self.fred.get_series(series_id, observation_start='2020-01-01')
            
            # Calculate YoY change
            current = data.iloc[-1]
            year_ago = data.iloc[-12] if len(data) >= 12 else data.iloc[0]
            yoy_change = ((current - year_ago) / year_ago) * 100
            
            return {
                'current_cpi': float(current) if not data.empty else None,
                'yoy_change': float(yoy_change),
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error fetching CPI data: {e}")
            return {}
    
    def get_gdp_data(self) -> Dict:
        """
        Get GDP data.
        
        Returns:
            Dictionary with GDP information
        """
        if not self.fred:
            return {}
        
        try:
            # Real GDP
            series_id = 'GDPC1'
            data = self.fred.get_series(series_id, observation_start='2020-01-01')
            
            # Calculate QoQ change
            current = data.iloc[-1]
            previous = data.iloc[-2] if len(data) > 1 else data.iloc[0]
            qoq_change = ((current - previous) / previous) * 100
            
            return {
                'current_gdp': float(current) if not data.empty else None,
                'qoq_change': float(qoq_change),
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error fetching GDP data: {e}")
            return {}
    
    def calculate_surprise(self, actual: float, expected: float) -> Dict:
        """
        Calculate surprise factor for economic data.
        
        Args:
            actual: Actual economic data value
            expected: Expected/forecasted value
            
        Returns:
            Dictionary with surprise calculation
        """
        if expected == 0:
            return {'surprise': 0, 'surprise_pct': 0, 'direction': 'neutral'}
        
        surprise = actual - expected
        surprise_pct = (surprise / abs(expected)) * 100
        
        direction = 'neutral'
        if surprise > 0:
            direction = 'positive'
        elif surprise < 0:
            direction = 'negative'
        
        return {
            'surprise': surprise,
            'surprise_pct': surprise_pct,
            'direction': direction,
            'actual': actual,
            'expected': expected
        }
    
    def assess_policy_impact(self, event: Dict) -> str:
        """
        Assess policy impact of economic event (hawkish/dovish).
        
        Args:
            event: Dictionary with event data (name, actual, expected, etc.)
            
        Returns:
            Policy impact: 'hawkish', 'dovish', or 'neutral'
        """
        event_name = event.get('name', '').upper()
        surprise = event.get('surprise', 0)
        
        # CPI/Inflation events
        if 'CPI' in event_name or 'INFLATION' in event_name:
            if surprise > 0:  # Higher than expected inflation
                return 'hawkish'  # Fed may raise rates
            elif surprise < 0:  # Lower than expected inflation
                return 'dovish'  # Fed may lower rates
        
        # Employment events
        if 'UNEMPLOYMENT' in event_name or 'NFP' in event_name:
            if surprise < 0:  # Lower unemployment (good for economy)
                return 'hawkish'  # Strong economy, may raise rates
            elif surprise > 0:  # Higher unemployment
                return 'dovish'  # Weak economy, may lower rates
        
        # GDP events
        if 'GDP' in event_name:
            if surprise > 0:  # Higher GDP
                return 'hawkish'
            elif surprise < 0:  # Lower GDP
                return 'dovish'
        
        # Fed rate decisions
        if 'FED' in event_name or 'RATE' in event_name:
            if surprise > 0:  # Rate hike
                return 'hawkish'
            elif surprise < 0:  # Rate cut
                return 'dovish'
        
        return 'neutral'
    
    def get_economic_calendar(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Get economic calendar events.
        Uses RapidAPI Trading Economics scraper when RAPIDAPI_KEY is set.
        """
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=30)

        rapidapi_key = os.getenv("RAPIDAPI_KEY")
        if rapidapi_key:
            try:
                return self._get_trading_economics_news_rapidapi(start_date)
            except Exception as e:
                print(f"Error fetching Trading Economics via RapidAPI: {e}")
        return []

    def _get_trading_economics_news_rapidapi(self, for_date: Optional[datetime] = None) -> List[Dict]:
        """
        Get Trading Economics news via RapidAPI.
        GET get_trading_economics_news?year=2024&month=4&day=12
        """
        import requests
        for_date = for_date or datetime.now()
        key = os.getenv("RAPIDAPI_KEY")
        if not key:
            return []
        url = "https://trading-econmics-scraper.p.rapidapi.com/get_trading_economics_news"
        params = {"year": for_date.year, "month": for_date.month, "day": for_date.day}
        headers = {
            "x-rapidapi-host": "trading-econmics-scraper.p.rapidapi.com",
            "x-rapidapi-key": key,
        }
        r = requests.get(url, headers=headers, params=params, timeout=15)
        if r.status_code != 200:
            return []
        data = r.json()
        items = data if isinstance(data, list) else data.get("news", data.get("data", [])) or []
        out = []
        for item in (items if isinstance(items, list) else []):
            if isinstance(item, dict):
                out.append({
                    "name": item.get("title", item.get("event", "")),
                    "date": item.get("date", item.get("published_at", "")),
                    "actual": item.get("actual"),
                    "expected": item.get("expected"),
                    "surprise": item.get("surprise"),
                    "country": item.get("country"),
                })
        return out
