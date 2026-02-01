"""
RapidAPI Client

Single client for all RapidAPI-hosted APIs (Yahoo Finance, Alpha Vantage, TradingView, IEX, Trading Economics).
Uses one RAPIDAPI_KEY for all hosts.
"""

import os
import requests
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

# RapidAPI hosts used in this project
RAPIDAPI_HOSTS = {
    "yahoo_finance": "yahoo-finance15.p.rapidapi.com",
    "alpha_vantage": "alpha-vantage.p.rapidapi.com",
    "tradingview": "tradingview18.p.rapidapi.com",
    "iex": "investors-exchange-iex-trading.p.rapidapi.com",
    "trading_economics": "trading-econmics-scraper.p.rapidapi.com",
}


def get_headers(host_key: str) -> Dict[str, str]:
    """Build headers for a RapidAPI host. Uses RAPIDAPI_KEY from env."""
    key = os.getenv("RAPIDAPI_KEY")
    if not key:
        return {}
    host = RAPIDAPI_HOSTS.get(host_key, "")
    if not host:
        return {}
    return {
        "x-rapidapi-host": host,
        "x-rapidapi-key": key,
    }


def get(url: str, host_key: str, params: Optional[Dict] = None, timeout: int = 15) -> Optional[Dict]:
    """
    GET request to a RapidAPI endpoint.

    Args:
        url: Full URL (e.g. https://yahoo-finance15.p.rapidapi.com/...)
        host_key: Key in RAPIDAPI_HOSTS (e.g. 'yahoo_finance')
        params: Query params
        timeout: Request timeout

    Returns:
        JSON response or None
    """
    headers = get_headers(host_key)
    if not headers:
        return None
    try:
        r = requests.get(url, headers=headers, params=params or {}, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def is_available() -> bool:
    """Return True if RAPIDAPI_KEY is set."""
    return bool(os.getenv("RAPIDAPI_KEY"))
