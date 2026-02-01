# Groww API SDK Reference (growwapi)

Reference extracted from the installed **growwapi** package (v1.5.0). Official docs: https://groww.in/trade-api/docs/python-sdk

---

## Installation & Package

```bash
pip install growwapi
```

- **Package**: `growwapi`
- **Version**: 1.5.0
- **Python**: 3.9–3.13
- **Dependencies**: requests, pandas, nats-py, pynacl, nkeys, certifi, colorama, protobuf, pydantic, aiohttp

---

## Authentication

### Option 1: Use access token directly

You need an **API access token**. Pass it to `GrowwAPI`:

```python
from growwapi import GrowwAPI

client = GrowwAPI("YOUR_ACCESS_TOKEN")
```

### Option 2: Get access token from API key + TOTP or secret

```python
from growwapi.groww.client import GrowwAPI

# With TOTP (from authenticator app)
token = GrowwAPI.get_access_token(api_key="YOUR_API_KEY", totp="123456")

# With approval secret
token = GrowwAPI.get_access_token(api_key="YOUR_API_KEY", secret="YOUR_SECRET")

# token is a dict with key "token"; use that string for GrowwAPI(token["token"])
client = GrowwAPI(token["token"])
```

- **Token endpoint**: `POST https://api.groww.in/v1/token/api/access`
- **Headers**: Same as below; body: `key_type` + `totp` or `key_type` + `checksum` + `timestamp` for approval.

### Required env vars (for this project)

- `GROWW_API_KEY` – API key (if using `get_access_token`)
- `GROWW_ACCESS_TOKEN` – Pre-obtained access token (if not using TOTP/secret each time)
- Optionally: `GROWW_API_SECRET` for approval-based login

---

## Base URL & Headers

- **Base URL**: `https://api.groww.in/v1`
- **Headers** (built by SDK):
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
  - `x-request-id`: UUID
  - `x-client-id`: growwapi
  - `x-client-platform`: growwapi-python-client
  - `x-client-platform-version`: 1.5.0
  - `x-api-version`: 1.0

---

## GrowwAPI – Main methods

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| `place_order(...)` | POST `/order/create` | Place order (see params below) |
| `modify_order(...)` | POST `/order/modify` | Modify by `groww_order_id` |
| `cancel_order(groww_order_id, segment, timeout)` | POST `/order/cancel` | Cancel order |
| `get_order_detail(segment, groww_order_id, timeout)` | GET `/order/detail/{id}` | Order details |
| `get_order_list(page, page_size, segment, timeout)` | GET `/order/list` | List orders |
| `get_order_status(segment, groww_order_id, timeout)` | GET `/order/status/{id}` | Order status |
| `get_order_status_by_reference(segment, order_reference_id, timeout)` | GET `/order/status/reference/{ref}` | Status by ref ID |
| `get_trade_list_for_order(groww_order_id, segment, page, page_size, timeout)` | GET `/order/trades/{id}` | Trades for an order |

**place_order** parameters:

- `validity`, `exchange`, `order_type`, `product`, `quantity`, `segment`, `trading_symbol`, `transaction_type`
- Optional: `order_reference_id`, `price`, `trigger_price`, `timeout`

### Holdings & positions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `get_holdings_for_user(timeout)` | GET `/holdings/user` | User holdings |
| `get_positions_for_user(segment, timeout)` | GET `/positions/user` | All positions |
| `get_position_for_trading_symbol(trading_symbol, segment, timeout)` | GET `/positions/trading-symbol` | Position for one symbol |

### Market data (REST)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `get_quote(trading_symbol, exchange, segment, timeout)` | GET `/live-data/quote` | Latest quote |
| `get_ltp(exchange_trading_symbols, segment, timeout)` | GET `/live-data/ltp` | LTP for symbols (tuple) |
| `get_ohlc(exchange_trading_symbols, segment, timeout)` | GET `/live-data/ohlc` | OHLC for symbols |
| `get_historical_candles(exchange, segment, groww_symbol, start_time, end_time, candle_interval, timeout)` | GET `/historical/candles` | Historical candles (V2) |
| `get_expiries(exchange, underlying_symbol, year, month, timeout)` | GET `/historical/expiries` | F&O expiries |
| `get_contracts(exchange, underlying_symbol, expiry_date, timeout)` | GET `/historical/contracts` | Contracts for expiry |
| `get_option_chain(exchange, underlying, expiry_date, timeout)` | GET `/option-chain/exchange/{ex}/underlying/{und}` | Option chain |
| `get_greeks(exchange, underlying, trading_symbol, expiry)` | GET `/live-data/greeks/...` | Option Greeks |

### Margins & user

| Method | Endpoint | Description |
|--------|----------|-------------|
| `get_available_margin_details(timeout)` | GET `/margins/detail/user` | User margin |
| `get_order_margin_details(segment, orders, timeout)` | POST `/margins/detail/orders` | Margin for order list |
| `get_user_profile(timeout)` | GET `/user/detail` | User profile |

### Instruments

| Method | Description |
|--------|-------------|
| `get_all_instruments()` | DataFrame of all instruments (from CSV) |
| `get_instrument_by_exchange_and_trading_symbol(exchange, trading_symbol)` | One instrument by exchange + symbol |
| `get_instrument_by_groww_symbol(groww_symbol)` | By groww_symbol |
| `get_instrument_by_exchange_token(exchange_token)` | By exchange_token |

- Instruments CSV: `https://growwapi-assets.groww.in/instruments/instrument.csv`

### Smart orders (GTT / OCO)

| Method | Description |
|--------|-------------|
| `create_smart_order(smart_order_type, segment, trading_symbol, quantity, product_type, exchange, duration, ...)` | Create GTT or OCO |
| `modify_smart_order(smart_order_id, smart_order_type, segment, ...)` | Modify |
| `cancel_smart_order(segment, smart_order_type, smart_order_id, timeout)` | Cancel |
| `get_smart_order(segment, smart_order_type, smart_order_id, timeout)` | Get one |
| `get_smart_order_list(smart_order_type, segment, status, page, page_size, start_date_time, end_date_time, timeout)` | List with filters |

### Socket token (for feed)

- `generate_socket_token(key_pair)` – POST to `https://api.groww.in/v1/api/apex/v1/socket/token/create/`  
- Used internally by `GrowwFeed`; requires key pair (nkeys).

---

## Constants (GrowwAPI)

Use these when calling the API:

- **Exchange**: `EXCHANGE_NSE`, `EXCHANGE_BSE`, `EXCHANGE_MCX`, `EXCHANGE_MCXSX`, `EXCHANGE_NCDEX`, `EXCHANGE_US`
- **Segment**: `SEGMENT_CASH`, `SEGMENT_FNO`, `SEGMENT_CURRENCY`, `SEGMENT_COMMODITY`
- **Order type**: `ORDER_TYPE_LIMIT`, `ORDER_TYPE_MARKET`, `ORDER_TYPE_STOP_LOSS` (`"SL"`), `ORDER_TYPE_STOP_LOSS_MARKET` (`"SL_M"`)
- **Product**: `PRODUCT_CNC`, `PRODUCT_MIS`, `PRODUCT_NRML`, `PRODUCT_CO`, `PRODUCT_BO`, `PRODUCT_MTF`, `PRODUCT_ARBITRAGE`
- **Validity**: `VALIDITY_DAY`, `VALIDITY_IOC`, `VALIDITY_EOS`, `VALIDITY_GTC`, `VALIDITY_GTD`
- **Transaction**: `TRANSACTION_TYPE_BUY`, `TRANSACTION_TYPE_SELL`
- **Candle interval**: `CANDLE_INTERVAL_MIN_1`, `CANDLE_INTERVAL_MIN_5`, …, `CANDLE_INTERVAL_DAY`, `CANDLE_INTERVAL_WEEK`, `CANDLE_INTERVAL_MONTH`
- **Smart order**: `SMART_ORDER_TYPE_GTT`, `SMART_ORDER_TYPE_OCO`; status: `SMART_ORDER_STATUS_ACTIVE`, `TRIGGERED`, `CANCELLED`, etc.

---

## GrowwFeed (live data)

- **Constructor**: `GrowwFeed(groww_api: GrowwAPI)` – takes a `GrowwAPI` instance, not the raw token.
- **WebSocket**: NATS at `wss://socket-api.groww.in`; token from `generate_socket_token`.

### Usage pattern

```python
from growwapi import GrowwAPI, GrowwFeed

api = GrowwAPI("YOUR_ACCESS_TOKEN")
feed = GrowwFeed(api)

# Subscribe to LTP for instruments (instrument_list = list of dicts with exchange, segment, exchange_token)
# Then: feed.get_ltp(), feed.get_market_depth(), feed.get_index_value()
# Order/position updates: subscribe_equity_order_updates, subscribe_fno_order_updates, subscribe_fno_position_updates
```

Feed methods include: `subscribe_ltp`, `unsubscribe_ltp`, `subscribe_market_depth`, `subscribe_index_value`, `subscribe_equity_order_updates`, `subscribe_fno_order_updates`, `subscribe_fno_position_updates`, and their get/unsubscribe counterparts.

---

## Exceptions (growwapi.groww.exceptions)

| Exception | HTTP / case |
|-----------|-------------|
| `GrowwAPIAuthenticationException` | 401 |
| `GrowwAPIAuthorisationException` | 403 |
| `GrowwAPIBadRequestException` | 400 |
| `GrowwAPINotFoundException` | 404 |
| `GrowwAPIRateLimitException` | 429 |
| `GrowwAPITimeoutException` | 504 / timeout |
| `GrowwAPIException` | API returns `status: FAILURE` or other non-OK |
| `InstrumentNotFoundException` | Instrument lookup failed |
| `GrowwFeedConnectionException` | Feed socket connection failed |
| `GrowwFeedNotSubscribedException` | Get called without subscribing |

---

## Symbol format

- **REST**: `trading_symbol` (e.g. `RELIANCE`, `SWIGGY`) with `exchange` (e.g. `NSE`, `BSE`) and `segment` (e.g. `CASH`, `FNO`).
- **Historical candles**: use `groww_symbol` (from instruments) with `start_time` / `end_time` in `yyyy-MM-dd HH:mm:ss`.
- **LTP/OHLC**: `exchange_trading_symbols` as tuple like `("NSE_RELIANCE", "NSE_INFY")` (exchange prefix + symbol).

---

## Quick example (orders + quote)

```python
from growwapi import GrowwAPI

client = GrowwAPI("YOUR_ACCESS_TOKEN")

# Quote
quote = client.get_quote("RELIANCE", "NSE", "CASH", timeout=5)

# Place limit buy
order = client.place_order(
    validity=GrowwAPI.VALIDITY_DAY,
    exchange=GrowwAPI.EXCHANGE_NSE,
    order_type=GrowwAPI.ORDER_TYPE_LIMIT,
    product=GrowwAPI.PRODUCT_CNC,
    quantity=1,
    segment=GrowwAPI.SEGMENT_CASH,
    trading_symbol="RELIANCE",
    transaction_type=GrowwAPI.TRANSACTION_TYPE_BUY,
    price=2500.0,
)

# Orders list
orders = client.get_order_list(segment=GrowwAPI.SEGMENT_CASH, timeout=5)
```

---

## Integration with Quant Edge

- Use **one** `GrowwAPI` instance (with token from env or from `get_access_token`) for all REST calls.
- Use **one** `GrowwFeed(api)` if you need live LTP/order/position updates.
- Map our internal symbol format (e.g. `RELIANCE.NS`) to Groww’s `trading_symbol` + `exchange` + `segment` using instruments or a small mapping layer.
- Keep token refresh logic (TOTP/secret) in a single place and pass the refreshed token into `GrowwAPI`.

For full integration steps and env vars, see **docs/groww_integration.md**.
