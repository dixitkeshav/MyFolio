"""
Live Trading Engine

Executes real trades via broker API. Primary broker: Groww (growwapi) for Indian markets.
"""

from typing import Dict, Optional, Tuple
import os
from dotenv import load_dotenv
from core.risk_engine.drawdown_control import DrawdownController
from core.risk_engine.exposure_limits import ExposureManager

load_dotenv()


def _symbol_to_groww(symbol: str) -> Tuple[str, str]:
    """Convert symbol (e.g. RELIANCE.NS, TCS) to (exchange, trading_symbol)."""
    symbol = (symbol or "").strip().upper()
    if not symbol:
        return "NSE", ""
    if ".NS" in symbol:
        return "NSE", symbol.replace(".NS", "")
    if ".BO" in symbol:
        return "BSE", symbol.replace(".BO", "")
    # Default NSE for plain symbols
    return "NSE", symbol


class LiveTrader:
    """Live trading engine (Groww via growwapi)."""

    def __init__(self, broker_type: str = "groww"):
        """
        Initialize live trader.

        Args:
            broker_type: Broker type ('groww', 'zerodha', 'upstox')
        """
        self.broker_type = broker_type
        self.broker = None
        self.connected = False

        self.drawdown_controller = DrawdownController()
        self.exposure_manager = ExposureManager()

        self._initialize_broker()

    def _initialize_broker(self):
        """Initialize broker connection (Groww via growwapi)."""
        if self.broker_type == "groww":
            try:
                from growwapi import GrowwAPI
                token = os.getenv("GROWW_ACCESS_TOKEN") or os.getenv("GROWW_API_KEY")
                if token:
                    self.broker = GrowwAPI(token)
                    self.connected = True
            except ImportError:
                print("growwapi not installed. Install with: pip install growwapi")
            except Exception as e:
                print(f"Error initializing Groww: {e}")
        # Add zerodha, upstox here if needed

    def connect_to_broker(self) -> bool:
        """
        Connect to broker API.

        Returns:
            True if connected successfully
        """
        if self.broker_type == "groww" and self.broker:
            try:
                _ = self.broker.get_user_profile(timeout=5)
                self.connected = True
                return True
            except Exception as e:
                print(f"Error connecting to Groww: {e}")
                return False
        return False

    def get_account_status(self) -> Dict:
        """
        Get real account status (margin/equity from Groww).

        Returns:
            Dictionary with account information
        """
        if not self.connected or not self.broker:
            return {"error": "Not connected to broker"}

        try:
            if self.broker_type == "groww":
                margins = self.broker.get_available_margin_details(timeout=10)
                # Groww returns payload with margin details; adapt keys to common shape
                equity = margins.get("equity") or margins.get("available_cash") or 0
                cash = margins.get("available_cash") or margins.get("cash") or 0
                return {
                    "equity": float(equity) if equity else 0,
                    "cash": float(cash) if cash else 0,
                    "buying_power": float(margins.get("available_margin", cash) or cash),
                    "portfolio_value": float(equity) if equity else 0,
                }
        except Exception as e:
            return {"error": str(e)}

    def place_market_order(
        self,
        symbol: str,
        quantity: int,
        side: str,
        segment: str = "CASH",
        product: str = "CNC",
    ) -> Dict:
        """
        Place market order.

        Args:
            symbol: Stock symbol (e.g. RELIANCE, RELIANCE.NS)
            quantity: Number of shares
            side: 'buy' or 'sell'
            segment: CASH or FNO
            product: CNC, MIS, NRML, etc.

        Returns:
            Order result
        """
        if not self.connected:
            return {"error": "Not connected to broker"}

        if self.drawdown_controller.is_kill_switch_active():
            return {"error": "Kill switch active - trading disabled"}

        try:
            if self.broker_type == "groww":
                exchange, trading_symbol = _symbol_to_groww(symbol)
                if not trading_symbol:
                    return {"error": "Invalid symbol"}
                trans = self.broker.TRANSACTION_TYPE_BUY if str(side).lower() == "buy" else self.broker.TRANSACTION_TYPE_SELL
                order = self.broker.place_order(
                    validity=self.broker.VALIDITY_DAY,
                    exchange=exchange,
                    order_type=self.broker.ORDER_TYPE_MARKET,
                    product=product,
                    quantity=quantity,
                    segment=segment,
                    trading_symbol=trading_symbol,
                    transaction_type=trans,
                    price=0.0,
                    timeout=30,
                )
                oid = order.get("groww_order_id") or order.get("order_id") or ""
                return {
                    "status": "SUBMITTED",
                    "order_id": oid,
                    "symbol": symbol,
                    "quantity": quantity,
                    "side": side,
                }
        except Exception as e:
            return {"error": str(e)}

    def place_limit_order(
        self,
        symbol: str,
        quantity: int,
        price: float,
        side: str,
        segment: str = "CASH",
        product: str = "CNC",
    ) -> Dict:
        """
        Place limit order.

        Args:
            symbol: Stock symbol
            quantity: Number of shares
            price: Limit price
            side: 'buy' or 'sell'
            segment: CASH or FNO
            product: CNC, MIS, etc.

        Returns:
            Order result
        """
        if not self.connected:
            return {"error": "Not connected to broker"}

        try:
            if self.broker_type == "groww":
                exchange, trading_symbol = _symbol_to_groww(symbol)
                if not trading_symbol:
                    return {"error": "Invalid symbol"}
                trans = self.broker.TRANSACTION_TYPE_BUY if str(side).lower() == "buy" else self.broker.TRANSACTION_TYPE_SELL
                order = self.broker.place_order(
                    validity=self.broker.VALIDITY_DAY,
                    exchange=exchange,
                    order_type=self.broker.ORDER_TYPE_LIMIT,
                    product=product,
                    quantity=quantity,
                    segment=segment,
                    trading_symbol=trading_symbol,
                    transaction_type=trans,
                    price=float(price),
                    timeout=30,
                )
                oid = order.get("groww_order_id") or order.get("order_id") or ""
                return {
                    "status": "SUBMITTED",
                    "order_id": oid,
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": price,
                    "side": side,
                }
        except Exception as e:
            return {"error": str(e)}

    def place_stop_order(
        self,
        symbol: str,
        quantity: int,
        stop_price: float,
        segment: str = "CASH",
        product: str = "CNC",
    ) -> Dict:
        """
        Place stop-loss order (sell).

        Args:
            symbol: Stock symbol
            quantity: Number of shares
            stop_price: Trigger price
            segment: CASH or FNO
            product: CNC, MIS, etc.

        Returns:
            Order result
        """
        if not self.connected:
            return {"error": "Not connected to broker"}

        try:
            if self.broker_type == "groww":
                exchange, trading_symbol = _symbol_to_groww(symbol)
                if not trading_symbol:
                    return {"error": "Invalid symbol"}
                order = self.broker.place_order(
                    validity=self.broker.VALIDITY_DAY,
                    exchange=exchange,
                    order_type=self.broker.ORDER_TYPE_STOP_LOSS_MARKET,
                    product=product,
                    quantity=quantity,
                    segment=segment,
                    trading_symbol=trading_symbol,
                    transaction_type=self.broker.TRANSACTION_TYPE_SELL,
                    trigger_price=float(stop_price),
                    timeout=30,
                )
                oid = order.get("groww_order_id") or order.get("order_id") or ""
                return {
                    "status": "SUBMITTED",
                    "order_id": oid,
                    "symbol": symbol,
                    "quantity": quantity,
                    "stop_price": stop_price,
                }
        except Exception as e:
            return {"error": str(e)}

    def cancel_order(self, order_id: str, segment: str = "CASH") -> Dict:
        """
        Cancel an order.

        Args:
            order_id: Groww order ID
            segment: CASH or FNO

        Returns:
            Cancellation result
        """
        if not self.connected:
            return {"error": "Not connected to broker"}

        try:
            if self.broker_type == "groww":
                self.broker.cancel_order(groww_order_id=order_id, segment=segment, timeout=10)
                return {"status": "CANCELLED", "order_id": order_id}
        except Exception as e:
            return {"error": str(e)}

    def get_positions(self, segment: Optional[str] = None) -> Dict:
        """
        Get current positions.

        Returns:
            Dictionary with positions
        """
        if not self.connected:
            return {"error": "Not connected to broker"}

        try:
            if self.broker_type == "groww":
                data = self.broker.get_positions_for_user(segment=segment, timeout=10)
                positions = data.get("positions") or data.get("position_list") or data
                if isinstance(positions, dict) and "positions" not in str(type(data)):
                    positions = list(positions.values()) if positions else []
                if not isinstance(positions, list):
                    positions = [positions] if isinstance(positions, dict) else []
                out = []
                for pos in positions:
                    if isinstance(pos, dict):
                        qty = int(pos.get("quantity") or pos.get("qty") or pos.get("net_quantity") or 0)
                        avg = float(pos.get("avg_price") or pos.get("avg_entry_price") or pos.get("average_price") or 0)
                        cur = float(pos.get("last_price") or pos.get("current_price") or pos.get("ltp") or avg)
                        out.append({
                            "symbol": pos.get("trading_symbol") or pos.get("symbol", ""),
                            "qty": qty,
                            "avg_entry_price": avg,
                            "current_price": cur,
                            "market_value": cur * qty if qty else 0,
                            "unrealized_pl": float(pos.get("pnl") or pos.get("unrealized_pl") or pos.get("profit_loss") or 0),
                        })
                return {"positions": out}
        except Exception as e:
            return {"error": str(e)}

    def monitor_positions(self):
        """Monitor and manage positions."""
        account_status = self.get_account_status()
        if "equity" in account_status:
            self.drawdown_controller.update_equity(account_status["equity"])
            self.drawdown_controller.activate_kill_switch()

        positions = self.get_positions()
        if "positions" in positions:
            total_exposure = sum(p.get("market_value", 0) for p in positions["positions"])
            self.exposure_manager.update_account_value(account_status.get("equity", 0))
