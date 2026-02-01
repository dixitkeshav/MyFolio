"""
Stock & Index Search for Indian and US Markets

Provides searchable lists of stocks and indices with display names.
Default currency: INR for Indian, USD for US.
"""

from typing import List, Dict, Optional

# Indian indices (NSE/BSE) – symbol used for yfinance
INDIAN_INDICES = [
    ("^NSEI", "Nifty 50", "NSE"),
    ("^NSEBANK", "Nifty Bank", "NSE"),
    ("^CNXIT", "Nifty IT", "NSE"),
    ("^NSEMDCP50", "Nifty Midcap 50", "NSE"),
    ("^BSESN", "S&P BSE Sensex", "BSE"),
    ("^BSE200", "BSE 200", "BSE"),
]

# Indian stocks – (symbol_suffix, display_name). NSE = .NS, BSE = .BO
INDIAN_STOCKS = [
    ("RELIANCE.NS", "Reliance Industries"),
    ("TCS.NS", "TCS"),
    ("HDFCBANK.NS", "HDFC Bank"),
    ("INFY.NS", "Infosys"),
    ("HINDUNILVR.NS", "Hindustan Unilever"),
    ("ICICIBANK.NS", "ICICI Bank"),
    ("SBIN.NS", "State Bank of India"),
    ("BHARTIARTL.NS", "Bharti Airtel"),
    ("BAJFINANCE.NS", "Bajaj Finance"),
    ("KOTAKBANK.NS", "Kotak Mahindra Bank"),
    ("LT.NS", "Larsen & Toubro"),
    ("AXISBANK.NS", "Axis Bank"),
    ("ITC.NS", "ITC"),
    ("ASIANPAINT.NS", "Asian Paints"),
    ("MARUTI.NS", "Maruti Suzuki"),
    ("WIPRO.NS", "Wipro"),
    ("HCLTECH.NS", "HCL Technologies"),
    ("TITAN.NS", "Titan"),
    ("SUNPHARMA.NS", "Sun Pharma"),
    ("ULTRACEMCO.NS", "UltraTech Cement"),
    ("NESTLEIND.NS", "Nestle India"),
    ("TATAMOTORS.NS", "Tata Motors"),
    ("POWERGRID.NS", "Power Grid"),
    ("INDUSINDBK.NS", "IndusInd Bank"),
    ("ONGC.NS", "ONGC"),
    ("NTPC.NS", "NTPC"),
    ("TATASTEEL.NS", "Tata Steel"),
    ("DIVISLAB.NS", "Divi's Labs"),
    ("CIPLA.NS", "Cipla"),
    ("DRREDDY.NS", "Dr Reddy's"),
    ("ADANIPORTS.NS", "Adani Ports"),
    ("BRITANNIA.NS", "Britannia"),
    ("HINDALCO.NS", "Hindalco"),
    ("GRASIM.NS", "Grasim"),
    ("JSWSTEEL.NS", "JSW Steel"),
    ("EICHERMOT.NS", "Eicher Motors"),
    ("APOLLOHOSP.NS", "Apollo Hospitals"),
    ("BAJAJ-AUTO.NS", "Bajaj Auto"),
    ("M&M.NS", "Mahindra & Mahindra"),
    ("COALINDIA.NS", "Coal India"),
    ("HEROMOTOCO.NS", "Hero MotoCorp"),
]

# US symbols for dropdown
US_INDICES = [
    ("SPY", "S&P 500 ETF"),
    ("QQQ", "Nasdaq 100 ETF"),
    ("DIA", "Dow Jones ETF"),
    ("IWM", "Russell 2000 ETF"),
]

US_STOCKS = [
    ("AAPL", "Apple"),
    ("MSFT", "Microsoft"),
    ("GOOGL", "Alphabet (Google)"),
    ("AMZN", "Amazon"),
    ("NVDA", "NVIDIA"),
    ("META", "Meta"),
    ("TSLA", "Tesla"),
    ("BRK-B", "Berkshire Hathaway"),
    ("JPM", "JPMorgan Chase"),
    ("V", "Visa"),
    ("JNJ", "Johnson & Johnson"),
    ("WMT", "Walmart"),
    ("PG", "Procter & Gamble"),
    ("MA", "Mastercard"),
    ("HD", "Home Depot"),
    ("DIS", "Walt Disney"),
    ("BAC", "Bank of America"),
    ("XOM", "Exxon Mobil"),
    ("PFE", "Pfizer"),
    ("COST", "Costco"),
]

# Combined for search: (symbol, display_label, market)
def _all_entries() -> List[tuple]:
    out = []
    for sym, name, _ in INDIAN_INDICES:
        out.append((sym, f"{name} (Index)", "india"))
    for sym, name in INDIAN_STOCKS:
        out.append((sym, name, "india"))
    for sym, name in US_INDICES:
        out.append((sym, f"{name} (US)", "us"))
    for sym, name in US_STOCKS:
        out.append((sym, name, "us"))
    return out


_ALL_ENTRIES = _all_entries()


def search_stocks(
    query: str,
    market_filter: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, str]]:
    """
    Search stocks and indices by symbol or name.
    
    Args:
        query: Search string (symbol or company name).
        market_filter: 'india' | 'us' | None (both).
        limit: Max results.
    
    Returns:
        List of dicts: symbol, label, market.
    """
    q = (query or "").strip().upper()
    results = []
    for symbol, label, market in _ALL_ENTRIES:
        if market_filter and market != market_filter:
            continue
        if not q or q in symbol.upper() or q in label.upper():
            results.append({"symbol": symbol, "label": label, "market": market})
        if len(results) >= limit:
            break
    return results


def get_default_symbols(market: str = "india") -> List[Dict[str, str]]:
    """Default list for dropdown when no search (e.g. top Indian or US)."""
    if market == "india":
        entries = [(s, l) for s, l, m in _ALL_ENTRIES if m == "india"][:30]
    else:
        entries = [(s, l) for s, l, m in _ALL_ENTRIES if m == "us"][:30]
    return [{"symbol": s, "label": l, "market": market} for s, l in entries]


def is_indian_symbol(symbol: str) -> bool:
    """True if symbol is Indian (.NS, .BO or known Indian index)."""
    if not symbol:
        return False
    s = symbol.upper()
    if s.endswith(".NS") or s.endswith(".BO"):
        return True
    indian_syms = [e[0] for e in INDIAN_INDICES + [(x[0], x[1]) for x in INDIAN_STOCKS]]
    return s in [e.upper() for e in indian_syms]
