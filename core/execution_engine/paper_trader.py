"""
Paper Trading Engine

Simulates live trading with real-time data without real money.
"""

from datetime import datetime
from typing import Dict, Optional
from core.data_engine.market_data import MarketDataFetcher
from core.risk_engine.position_sizing import PositionSizer
from core.risk_engine.drawdown_control import DrawdownController
from core.risk_engine.exposure_limits import ExposureManager


class PaperTrader:
    """Paper trading engine."""
    
    def __init__(self, initial_capital: float = 100000):
        """
        Initialize paper trader.
        
        Args:
            initial_capital: Starting capital
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # {symbol: position_info}
        self.orders = []  # Order history
        self.trades = []  # Trade history
        
        self.position_sizer = PositionSizer()
        self.drawdown_controller = DrawdownController()
        self.exposure_manager = ExposureManager(initial_capital=initial_capital)
        self.data_fetcher = MarketDataFetcher()
    
    def initialize_account(self, initial_capital: Optional[float] = None):
        """Initialize or reset account."""
        if initial_capital:
            self.initial_capital = initial_capital
        
        self.cash = self.initial_capital
        self.positions = {}
        self.orders = []
        self.trades = []
        self.exposure_manager.update_account_value(self.initial_capital)
    
    def process_market_data(self, symbol: str, data: Dict):
        """
        Process incoming market data.
        
        Args:
            symbol: Stock symbol
            data: Market data dictionary
        """
        current_price = data.get('price', 0)
        
        # Update position P&L
        if symbol in self.positions:
            self._update_position_pnl(symbol, current_price)
        
        # Update account value
        equity = self._calculate_equity()
        self.exposure_manager.update_account_value(equity)
        self.drawdown_controller.update_equity(equity)
    
    def execute_order(self, order: Dict) -> Dict:
        """
        Execute an order (simulated).
        
        Args:
            order: Order dictionary with symbol, side, quantity, type
            
        Returns:
            Order execution result
        """
        symbol = order.get('symbol')
        side = order.get('side', 'BUY').upper()
        quantity = order.get('quantity', 0)
        order_type = order.get('type', 'MARKET').upper()
        
        # Get current price (use Indian fetcher for .NS/.BO)
        market = "india" if (symbol.endswith(".NS") or symbol.endswith(".BO")) else "us"
        quote = self.data_fetcher.get_realtime_quote(symbol, market=market)
        current_price = quote.get('price', 0)
        
        if order_type == 'MARKET':
            execution_price = current_price
        elif order_type == 'LIMIT':
            limit_price = order.get('limit_price', current_price)
            if side == 'BUY' and current_price <= limit_price:
                execution_price = limit_price
            elif side == 'SELL' and current_price >= limit_price:
                execution_price = limit_price
            else:
                return {'status': 'REJECTED', 'reason': 'Limit price not met'}
        else:
            return {'status': 'REJECTED', 'reason': 'Unsupported order type'}
        
        # Execute trade
        if side == 'BUY':
            return self._execute_buy(symbol, quantity, execution_price)
        else:
            return self._execute_sell(symbol, quantity, execution_price)
    
    def _execute_buy(self, symbol: str, quantity: int, price: float) -> Dict:
        """Execute buy order."""
        cost = quantity * price
        
        if cost > self.cash:
            return {'status': 'REJECTED', 'reason': 'Insufficient cash'}
        
        self.cash -= cost
        
        if symbol in self.positions:
            # Add to existing position
            pos = self.positions[symbol]
            total_shares = pos['shares'] + quantity
            avg_price = ((pos['shares'] * pos['entry_price']) + cost) / total_shares
            self.positions[symbol] = {
                'shares': total_shares,
                'entry_price': avg_price,
                'entry_date': pos.get('entry_date', datetime.now())
            }
        else:
            # New position
            self.positions[symbol] = {
                'shares': quantity,
                'entry_price': price,
                'entry_date': datetime.now()
            }
        
        self.orders.append({
            'symbol': symbol,
            'side': 'BUY',
            'quantity': quantity,
            'price': price,
            'cost': cost,
            'timestamp': datetime.now(),
            'status': 'FILLED'
        })
        
        return {'status': 'FILLED', 'execution_price': price}
    
    def _execute_sell(self, symbol: str, quantity: int, price: float) -> Dict:
        """Execute sell order."""
        if symbol not in self.positions:
            return {'status': 'REJECTED', 'reason': 'No position'}
        
        position = self.positions[symbol]
        if quantity > position['shares']:
            return {'status': 'REJECTED', 'reason': 'Insufficient shares'}
        
        proceeds = quantity * price
        self.cash += proceeds
        
        # Update position
        remaining_shares = position['shares'] - quantity
        if remaining_shares == 0:
            del self.positions[symbol]
        else:
            self.positions[symbol]['shares'] = remaining_shares
        
        # Calculate P&L
        pnl = (price - position['entry_price']) * quantity
        
        self.orders.append({
            'symbol': symbol,
            'side': 'SELL',
            'quantity': quantity,
            'price': price,
            'proceeds': proceeds,
            'pnl': pnl,
            'timestamp': datetime.now(),
            'status': 'FILLED'
        })
        
        self.trades.append({
            'symbol': symbol,
            'entry_price': position['entry_price'],
            'exit_price': price,
            'quantity': quantity,
            'pnl': pnl,
            'timestamp': datetime.now()
        })
        
        return {'status': 'FILLED', 'execution_price': price, 'pnl': pnl}
    
    def _update_position_pnl(self, symbol: str, current_price: float):
        """Update position P&L."""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        position['current_price'] = current_price
        position['unrealized_pnl'] = (current_price - position['entry_price']) * position['shares']
        position['unrealized_pnl_pct'] = ((current_price - position['entry_price']) / position['entry_price']) * 100
    
    def _calculate_equity(self) -> float:
        """Calculate current equity."""
        equity = self.cash
        for symbol, position in self.positions.items():
            current_price = position.get('current_price', position['entry_price'])
            equity += position['shares'] * current_price
        return equity
    
    def get_account_summary(self) -> Dict:
        """Get account summary."""
        equity = self._calculate_equity()
        total_pnl = equity - self.initial_capital
        total_pnl_pct = (total_pnl / self.initial_capital) * 100
        
        unrealized_pnl = sum(pos.get('unrealized_pnl', 0) for pos in self.positions.values())
        
        return {
            'equity': equity,
            'cash': self.cash,
            'initial_capital': self.initial_capital,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'unrealized_pnl': unrealized_pnl,
            'positions': len(self.positions),
            'num_trades': len(self.trades)
        }
    
    def get_positions(self, refresh_prices: bool = False) -> Dict:
        """Get all positions. If refresh_prices=True, fetch current price and update unrealized P&L."""
        if not refresh_prices:
            return self.positions.copy()
        result = {}
        for symbol, pos in self.positions.items():
            market = "india" if (symbol.endswith(".NS") or symbol.endswith(".BO")) else "us"
            quote = self.data_fetcher.get_realtime_quote(symbol, market=market)
            current_price = quote.get("price") or pos.get("entry_price")
            pos_copy = dict(pos)
            pos_copy["current_price"] = current_price
            pos_copy["unrealized_pnl"] = (current_price - pos["entry_price"]) * pos["shares"]
            pos_copy["unrealized_pnl_pct"] = ((current_price - pos["entry_price"]) / pos["entry_price"]) * 100
            result[symbol] = pos_copy
        return result

    def get_trades(self) -> list:
        """Return list of closed trades (realized P&L)."""
        return list(self.trades)

    def get_orders(self) -> list:
        """Return list of all orders (including open order history)."""
        return list(self.orders)

    def get_execution_preview(self, order: Dict) -> Dict:
        """
        Preview how an order would execute (price, cost, message).
        Does not execute the order.
        """
        symbol = order.get("symbol", "")
        side = order.get("side", "BUY").upper()
        quantity = int(order.get("quantity", 0))
        order_type = order.get("type", "MARKET").upper()
        if quantity <= 0:
            return {"error": "Invalid quantity", "would_execute_at": None}
        quote = self.data_fetcher.get_realtime_quote(
            symbol,
            market="india" if (symbol.endswith(".NS") or symbol.endswith(".BO")) else "us",
        )
        price = quote.get("price") or 0
        if not price:
            return {"error": "Could not get current price", "would_execute_at": None}
        if order_type == "LIMIT":
            limit_price = order.get("limit_price", price)
            if side == "BUY" and price > limit_price:
                price = limit_price  # would fill at limit
            elif side == "SELL" and price < limit_price:
                price = limit_price
        cost_or_proceeds = quantity * price
        return {
            "would_execute_at": price,
            "quantity": quantity,
            "side": side,
            "estimated_value": cost_or_proceeds,
            "error": None,
        }
