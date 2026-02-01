# Groww API Integration Guide

## Overview

Groww is integrated via the official **growwapi** Python SDK. This guide summarizes what you need for Quant Edge and points to the full SDK reference.

**SDK reference (from installed package):** [docs/groww_sdk_reference.md](groww_sdk_reference.md)  
**Official docs:** https://groww.in/trade-api/docs/python-sdk

---

## 🔑 What You Need

### 1. Authentication

- **Option A – Access token**  
  Set `GROWW_ACCESS_TOKEN` in `.env` and pass it to `GrowwAPI(token)`. You obtain the token from Groww (e.g. dashboard or auth flow).

- **Option B – API key + TOTP or secret**  
  Set `GROWW_API_KEY`. Then get a token at runtime:
  - **TOTP**: `GrowwAPI.get_access_token(api_key=KEY, totp="123456")` (code from authenticator app).
  - **Approval secret**: `GrowwAPI.get_access_token(api_key=KEY, secret=SECRET)`.

Use the returned token string to create `GrowwAPI(token)`.

### 2. Environment Variables (.env)

```bash
# At least one of:
GROWW_ACCESS_TOKEN=your_access_token_here

# If using get_access_token():
GROWW_API_KEY=your_api_key_here
# Optional, for approval-based login:
GROWW_API_SECRET=your_secret_here
```

User ID is not required by the SDK; the token identifies the user.

### 3. Base URL & Headers

- **Base URL**: `https://api.groww.in/v1`
- Headers (handled by the SDK): `Authorization: Bearer <token>`, `x-client-id: growwapi`, etc. See [groww_sdk_reference.md](groww_sdk_reference.md).

---

## 📡 Main Capabilities (from growwapi)

| Area | Methods / Features |
|------|--------------------|
| **Orders** | `place_order`, `modify_order`, `cancel_order`, `get_order_list`, `get_order_detail`, `get_order_status`, `get_trade_list_for_order` |
| **Holdings & positions** | `get_holdings_for_user`, `get_positions_for_user`, `get_position_for_trading_symbol` |
| **Market data (REST)** | `get_quote`, `get_ltp`, `get_ohlc`, `get_historical_candles`, `get_option_chain`, `get_greeks` |
| **Margins & user** | `get_available_margin_details`, `get_order_margin_details`, `get_user_profile` |
| **Instruments** | `get_all_instruments`, `get_instrument_by_exchange_and_trading_symbol`, `get_instrument_by_groww_symbol` |
| **Smart orders** | `create_smart_order`, `modify_smart_order`, `cancel_smart_order`, `get_smart_order`, `get_smart_order_list` (GTT, OCO) |
| **Live feed** | `GrowwFeed(api)` – LTP, market depth, index, order/position updates over WebSocket (NATS) |

Exchanges: NSE, BSE, MCX, etc. Segments: CASH, FNO, CURRENCY, COMMODITY. Order types: LIMIT, MARKET, SL, SL_M. See [groww_sdk_reference.md](groww_sdk_reference.md) for all constants and parameters.

---

## 📐 Symbol Format

- **REST (orders, quote, etc.)**: `trading_symbol` (e.g. `RELIANCE`, `SWIGGY`) with `exchange` (e.g. `NSE`, `BSE`) and `segment` (e.g. `CASH`).
- **Historical candles**: use `groww_symbol` from instruments; time in `yyyy-MM-dd HH:mm:ss`.
- **LTP/OHLC (REST)**: tuple like `("NSE_RELIANCE", "NSE_INFY")`.

Map our internal symbols (e.g. `RELIANCE.NS`) to `(exchange, trading_symbol)` using instruments or a small mapping layer.

---

## 🔧 Implementation Plan (Quant Edge)

1. **Groww broker adapter** (`core/execution_engine/groww_trader.py` or `core/brokers/groww_client.py`)
   - Load token from env (or get via `get_access_token`).
   - Wrap `GrowwAPI` for: place/modify/cancel order, positions, holdings, margins.
   - Map our symbol format to Groww’s `exchange` + `trading_symbol` + `segment`.
   - Handle growwapi exceptions and map to our error types.

2. **Market data** (`core/data_engine/groww_data.py` or use existing `indian_market_data.py`)
   - Use `get_quote`, `get_ltp`, `get_ohlc`, `get_historical_candles` for NSE/BSE.
   - Optionally use `GrowwFeed(api)` for live LTP/order/position updates.

3. **Config**
   - Already in `config/broker.yaml` and `.env.example` (Groww section).
   - Use `BROKER_TYPE=groww` and Indian market hours when trading on Groww.

4. **Symbol mapper**
   - `RELIANCE.NS` → NSE CASH `RELIANCE`; `RELIANCE.BO` → BSE CASH `RELIANCE`; same for FNO if needed.

---

## 📝 Status

- ✅ **growwapi** SDK installed and documented (see [groww_sdk_reference.md](groww_sdk_reference.md)).
- ✅ Config and env vars added for Groww.
- ⏳ **Next**: Implement `GrowwTrader` and optional `GrowwDataFetcher` using the SDK and this guide.
