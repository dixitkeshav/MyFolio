"""
Currency display: INR (default) and optional conversion to USD.
Values are stored in base currency (INR for Indian market, USD for US).
"""

from typing import Optional

# Approximate INR/USD for display only (update via API or config if needed)
DEFAULT_INR_PER_USD = 83.0


def get_inr_per_usd() -> float:
    """Return INR per 1 USD for display conversion."""
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        v = os.getenv("INR_PER_USD")
        if v:
            return float(v)
    except Exception:
        pass
    return DEFAULT_INR_PER_USD


def convert_to_display(
    amount: float,
    from_currency: str,
    display_currency: str,
) -> float:
    """
    Convert amount for display.
    from_currency / display_currency: 'INR' | 'USD'
    """
    if from_currency == display_currency:
        return amount
    rate = get_inr_per_usd()
    if from_currency == "INR" and display_currency == "USD":
        return amount / rate
    if from_currency == "USD" and display_currency == "INR":
        return amount * rate
    return amount


def format_currency(amount: float, currency: str = "INR") -> str:
    """Format number as currency string."""
    if currency == "INR":
        return f"₹{amount:,.2f}"
    return f"${amount:,.2f}"
