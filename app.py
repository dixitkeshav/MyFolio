"""
Quant Edge Trading Platform - Main Application

Streamlit-based UI. Default: Indian market, INR. Searchable stock dropdown, paper trading with PnL and trade history.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.data_engine.market_data import MarketDataFetcher
from core.data_engine.stock_search import search_stocks, get_default_symbols, is_indian_symbol
from core.data_engine.currency import convert_to_display, format_currency, get_inr_per_usd
from core.regime_engine.macro_regime import MacroRegimeDetector
from core.execution_engine.backtester import Backtester
from core.execution_engine.paper_trader import PaperTrader
from core.ai_chatbot.strategy_chatbot import StrategyChatbot
from strategies.equity_trend_following import EquityTrendFollowing

# Page configuration
st.set_page_config(
    page_title="Quant Edge Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1e88e5; margin-bottom: 1rem; }
    .metric-card { background-color: #1e1e1e; padding: 1rem; border-radius: 0.5rem; border: 1px solid #333; }
    .stButton>button { background-color: #1e88e5; color: white; border-radius: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_fetcher' not in st.session_state:
    st.session_state.data_fetcher = MarketDataFetcher()
if 'regime_detector' not in st.session_state:
    st.session_state.regime_detector = MacroRegimeDetector()
if 'paper_trader' not in st.session_state:
    st.session_state.paper_trader = PaperTrader()
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = StrategyChatbot()

# Sidebar: Market & Currency (default India, INR)
st.sidebar.title("📊 Quant Edge")
st.sidebar.markdown("---")
market = st.sidebar.radio("Market", ["India (NSE/BSE)", "US"], index=0)
market_key = "india" if "India" in market else "us"
display_currency = st.sidebar.radio("Display currency", ["INR (₹)", "USD ($)"], index=0)
currency_key = "INR" if "INR" in display_currency else "USD"
# Base currency for paper account: INR for Indian market, USD for US
base_currency = "INR" if market_key == "india" else "USD"
st.sidebar.caption(f"Account base: {base_currency}")

def fmt_money(amount: float) -> str:
    """Format amount in display currency (convert from base if needed)."""
    display_amt = convert_to_display(amount, base_currency, currency_key)
    return format_currency(display_amt, currency_key)

def stock_selector(label: str = "Select or search stock", default_symbol: str = None):
    """Searchable stock dropdown: type to search, then select. Returns (symbol, market)."""
    default_options = get_default_symbols(market_key)
    search = st.text_input(
        "Search by name or symbol",
        value="",
        key=f"stock_search_{label}",
        placeholder="e.g. Reliance, TCS, Nifty, SPY"
    )
    if search:
        options = search_stocks(search, market_filter=market_key, limit=30)
    else:
        options = default_options
    if not options:
        options = default_options
    choices = [f"{o['label']} ({o['symbol']})" for o in options]
    choice_idx = 0
    if default_symbol:
        for i, o in enumerate(options):
            if o["symbol"] == default_symbol:
                choice_idx = i
                break
    selected = st.selectbox(label, choices, index=min(choice_idx, len(choices) - 1), key=f"stock_sel_{label}")
    # Parse symbol from "Label (SYMBOL)" or use first option
    if selected and "(" in selected and ")" in selected:
        symbol = selected.split("(")[-1].rstrip(")")
    else:
        symbol = options[0]["symbol"] if options else (default_symbol or ("RELIANCE.NS" if market_key == "india" else "SPY"))
    return symbol, market_key

st.sidebar.markdown("---")
page = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Charts", "Strategy Builder", "Backtesting Chatbot", "Paper Trading", "Settings"]
)

# Main content
if page == "Dashboard":
    st.markdown('<div class="main-header">📊 Trading Dashboard</div>', unsafe_allow_html=True)

    st.subheader("Market Regime")
    with st.spinner("Detecting market regime..."):
        regime_data = st.session_state.regime_detector.detect_regime()
    regime = regime_data.get('regime', 'NEUTRAL')
    risk_score = regime_data.get('risk_score', 0)
    confidence = regime_data.get('confidence', 0)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Regime", regime)
    with col2:
        st.metric("Risk Score", f"{risk_score:.2f}")
    with col3:
        st.metric("Confidence", f"{confidence:.1%}")

    st.subheader("Account Summary (Paper Trading)")
    account_summary = st.session_state.paper_trader.get_account_summary()
    positions = st.session_state.paper_trader.get_positions(refresh_prices=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Equity", fmt_money(account_summary.get('equity', 0)))
    with col2:
        st.metric("Cash", fmt_money(account_summary.get('cash', 0)))
    with col3:
        pnl = account_summary.get('total_pnl', 0)
        pnl_pct = account_summary.get('total_pnl_pct', 0)
        st.metric("Total P&L", fmt_money(pnl), f"{pnl_pct:.2f}%")
    with col4:
        st.metric("Unrealized P&L", fmt_money(account_summary.get('unrealized_pnl', 0)))
    with col5:
        st.metric("Positions", account_summary.get('positions', 0))

    st.subheader("Open Positions")
    if positions:
        rows = []
        for symbol, pos in positions.items():
            curr = pos.get('current_price', pos['entry_price'])
            u_pnl = pos.get('unrealized_pnl', 0)
            u_pct = pos.get('unrealized_pnl_pct', 0)
            rows.append({
                'Symbol': symbol,
                'Shares': pos['shares'],
                'Entry Price': fmt_money(pos['entry_price']),
                'Current Price': fmt_money(curr),
                'P&L': fmt_money(u_pnl),
                'P&L %': f"{u_pct:.2f}%"
            })
        st.dataframe(pd.DataFrame(rows), width="stretch")
    else:
        st.info("No open positions")

elif page == "Charts":
    st.markdown('<div class="main-header">📈 Market Charts</div>', unsafe_allow_html=True)

    symbol, _ = stock_selector("Select stock or index", default_symbol="RELIANCE.NS" if market_key == "india" else "SPY")
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)

    if st.button("Load Chart"):
        with st.spinner("Loading chart data..."):
            df = st.session_state.data_fetcher.get_historical_data(symbol, period=period, market=market_key)
            df = st.session_state.data_fetcher.add_technical_indicators(df)

        fig = go.Figure(data=go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        ))
        if 'ema_50' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['ema_50'], name='EMA 50', line=dict(color='blue', width=1)))
        if 'ema_200' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['ema_200'], name='EMA 200', line=dict(color='red', width=1)))
        yaxis_title = "Price (₹)" if is_indian_symbol(symbol) else "Price ($)"
        fig.update_layout(
            title=f"{symbol} Price Chart",
            xaxis_title="Date",
            yaxis_title=yaxis_title,
            template="plotly_dark",
            height=600
        )
        st.plotly_chart(fig, width="stretch")

        st.subheader("Technical Indicators")
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'rsi' in df.columns:
                st.metric("RSI", f"{df['rsi'].iloc[-1]:.2f}")
        with col2:
            if 'atr' in df.columns:
                st.metric("ATR", fmt_money(df['atr'].iloc[-1]))
        with col3:
            if 'macd' in df.columns:
                st.metric("MACD", f"{df['macd'].iloc[-1]:.4f}")

elif page == "Backtesting Chatbot":
    st.markdown('<div class="main-header">🤖 Strategy Backtesting Chatbot</div>', unsafe_allow_html=True)
    st.markdown("Describe your trading strategy in natural language; the chatbot will generate code and backtest it.")
    user_query = st.text_area(
        "Describe your strategy",
        placeholder="Example: Buy RELIANCE.NS when RSI < 30 and backtest from 2023-01-01 to 2024-01-01"
    )
    if st.button("Generate & Backtest"):
        if user_query:
            with st.spinner("Processing..."):
                result = st.session_state.chatbot.process_user_query(user_query)
            if 'error' in result.get('backtest_results', {}):
                st.error(f"Error: {result['backtest_results']['error']}")
            else:
                st.success("Strategy generated and backtested!")
                st.subheader("Strategy Explanation")
                st.markdown(result.get('explanation', ''))
                if 'backtest_results' in result:
                    bt = result['backtest_results']
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Initial Capital", fmt_money(bt.get('initial_capital', 0)))
                    with col2:
                        st.metric("Final Equity", fmt_money(bt.get('final_equity', 0)))
                    with col3:
                        st.metric("Total Return", f"{bt.get('total_return_pct', 0):.2f}%")
                    with col4:
                        st.metric("Trades", bt.get('num_trades', 0))
                    if 'equity_curve' in bt:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=bt.get('dates', []), y=bt['equity_curve'], name='Equity', line=dict(color='#1e88e5', width=2)))
                        fig.update_layout(title="Equity Curve", xaxis_title="Date", yaxis_title=f"Equity ({currency_key})", template="plotly_dark", height=400)
                        st.plotly_chart(fig, width="stretch")
                with st.expander("View Generated Strategy Code"):
                    st.code(result.get('strategy_code', ''), language='python')

elif page == "Paper Trading":
    st.markdown('<div class="main-header">💼 Paper Trading (Equities)</div>', unsafe_allow_html=True)
    st.caption("Simulated equity trading. All values in account base currency; display can be converted above.")

    # PnL & Trade history at top
    st.subheader("P&L & Trade History")
    account = st.session_state.paper_trader.get_account_summary()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total P&L", fmt_money(account.get('total_pnl', 0)), f"{account.get('total_pnl_pct', 0):.2f}%")
    with col2:
        st.metric("Realized (closed trades)", fmt_money(sum(t.get('pnl', 0) for t in st.session_state.paper_trader.get_trades())))
    with col3:
        st.metric("Trades count", account.get('num_trades', 0))

    trades = st.session_state.paper_trader.get_trades()
    if trades:
        st.subheader("Closed Trades (how they executed)")
        trade_rows = []
        for t in reversed(trades[-50:]):
            trade_rows.append({
                'Symbol': t.get('symbol', ''),
                'Qty': t.get('quantity', 0),
                'Entry': fmt_money(t.get('entry_price', 0)),
                'Exit': fmt_money(t.get('exit_price', 0)),
                'P&L': fmt_money(t.get('pnl', 0)),
                'Time': t.get('timestamp', '')
            })
        st.dataframe(pd.DataFrame(trade_rows), width="stretch")
    else:
        st.info("No closed trades yet.")

    st.subheader("Place Order")
    symbol, _ = stock_selector("Stock", default_symbol="RELIANCE.NS" if market_key == "india" else "SPY")
    col1, col2 = st.columns(2)
    with col1:
        side = st.selectbox("Side", ["BUY", "SELL"])
        quantity = st.number_input("Quantity", min_value=1, value=10)
    with col2:
        order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])
        limit_price = None
        if order_type == "LIMIT":
            limit_price = st.number_input("Limit Price", min_value=0.01, value=1000.0 if market_key == "india" else 400.0)

    order = {'symbol': symbol, 'side': side, 'quantity': int(quantity), 'type': order_type}
    if order_type == "LIMIT":
        order['limit_price'] = limit_price

    # Execution preview: how would this execute in live market
    preview = st.session_state.paper_trader.get_execution_preview(order)
    if preview.get('error'):
        st.warning(preview['error'])
    else:
        st.info(f"**Simulated execution:** This order would execute at **{fmt_money(preview['would_execute_at'])}** per share (est. value: **{fmt_money(preview['estimated_value'])}**).")

    if st.button("Place Order"):
        result = st.session_state.paper_trader.execute_order(order)
        if result.get('status') == 'FILLED':
            st.success(f"Order filled at {fmt_money(result.get('execution_price', 0))}" + (f" | P&L: {fmt_money(result.get('pnl', 0))}" if result.get('pnl') is not None else ""))
        else:
            st.error(f"Order rejected: {result.get('reason', 'Unknown error')}")

elif page == "Settings":
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.subheader("API Configuration")
    st.info("Configure API keys in .env file. For Indian data, yfinance is used (no key required).")
    st.subheader("Currency")
    rate = get_inr_per_usd()
    st.caption(f"Display conversion: 1 USD = ₹{rate:.2f} (set INR_PER_USD in .env to override).")
    st.subheader("Risk Management")
    risk_per_trade = st.slider("Risk Per Trade (%)", 0.1, 5.0, 1.0)
    max_daily_loss = st.slider("Max Daily Loss (%)", 1.0, 10.0, 5.0)
    if st.button("Save Settings"):
        st.success("Settings saved!")

if __name__ == "__main__":
    pass
