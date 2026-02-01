"""
Backtesting Engine

Event-driven backtesting with slippage and commission modeling.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from core.data_engine.market_data import MarketDataFetcher
from core.risk_engine.position_sizing import PositionSizer
from core.risk_engine.drawdown_control import DrawdownController
from core.risk_engine.exposure_limits import ExposureManager


class Backtester:
    """Event-driven backtesting engine."""
    
    def __init__(
        self,
        initial_capital: float = 100000,
        commission: float = 0.005,
        slippage_bps: float = 5
    ):
        """
        Initialize backtester.
        
        Args:
            initial_capital: Starting capital
            commission: Commission per share
            slippage_bps: Slippage in basis points
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage_bps = slippage_bps / 10000  # Convert to decimal
        
        self.cash = initial_capital
        self.positions = {}  # {symbol: {'shares': int, 'entry_price': float}}
        self.trades = []
        self.equity_curve = [initial_capital]
        self.dates = []
        
        self.position_sizer = PositionSizer()
        self.drawdown_controller = DrawdownController()
        self.exposure_manager = ExposureManager(initial_capital=initial_capital)
        self.data_fetcher = MarketDataFetcher()
    
    def run_backtest(
        self,
        strategy,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> Dict:
        """
        Run backtest for a strategy.
        
        Args:
            strategy: Strategy instance (inherits from BaseStrategy)
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval
            
        Returns:
            Dictionary with backtest results
        """
        # Get historical data
        period = self._calculate_period(start_date, end_date)
        df = self.data_fetcher.get_historical_data(symbol, period=period, interval=interval)
        df = self.data_fetcher.add_technical_indicators(df)
        
        # Filter by date range
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        # Reset state
        self.cash = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = [self.initial_capital]
        self.dates = []
        
        # Process each bar
        for date, row in df.iterrows():
            self.dates.append(date)
            current_price = row['close']
            
            # Update equity
            equity = self._calculate_equity(current_price)
            self.equity_curve.append(equity)
            self.drawdown_controller.update_equity(equity)
            self.exposure_manager.update_account_value(equity)
            
            # Check for exit signals
            if symbol in self.positions:
                position = self.positions[symbol]
                exit_signal = strategy.should_exit(symbol, df.loc[:date], position)
                
                if exit_signal.get('exit', False):
                    self._execute_exit(symbol, current_price, exit_signal.get('reason', ''))
            
            # Check for entry signals
            if symbol not in self.positions:
                entry_decision = strategy.should_enter(symbol, df.loc[:date], 'LONG')
                
                if entry_decision.get('enter', False):
                    position_size = entry_decision.get('position_size', 0)
                    # Ensure position_size is a number (strategy may return dict from position_sizer)
                    if isinstance(position_size, dict):
                        position_size = position_size.get('position_size', 0)
                    position_size = float(position_size or 0)
                    if position_size > 0:
                        self._execute_entry(symbol, current_price, position_size)
        
        # Close any remaining positions
        if symbol in self.positions:
            final_price = df['close'].iloc[-1]
            self._execute_exit(symbol, final_price, 'End of backtest')
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        return {
            'initial_capital': self.initial_capital,
            'final_equity': self.equity_curve[-1],
            'total_return': self.equity_curve[-1] - self.initial_capital,
            'total_return_pct': ((self.equity_curve[-1] - self.initial_capital) / self.initial_capital) * 100,
            'trades': self.trades,
            'num_trades': len(self.trades),
            'metrics': metrics,
            'equity_curve': self.equity_curve,
            'dates': self.dates
        }
    
    def _execute_entry(self, symbol: str, price: float, position_size: float):
        """Execute entry trade."""
        # Apply slippage
        execution_price = price * (1 + self.slippage_bps)
        
        # Calculate shares
        shares = self.position_sizer.calculate_shares(execution_price, position_size)
        cost = shares * execution_price
        
        # Apply commission
        commission_cost = shares * self.commission
        total_cost = cost + commission_cost
        
        if total_cost > self.cash:
            return  # Not enough cash
        
        # Execute trade
        self.cash -= total_cost
        self.positions[symbol] = {
            'shares': shares,
            'entry_price': execution_price,
            'entry_date': self.dates[-1] if self.dates else datetime.now()
        }
        
        self.trades.append({
            'symbol': symbol,
            'type': 'ENTRY',
            'shares': shares,
            'price': execution_price,
            'cost': total_cost,
            'date': self.dates[-1] if self.dates else datetime.now()
        })
    
    def _execute_exit(self, symbol: str, price: float, reason: str):
        """Execute exit trade."""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        shares = position['shares']
        entry_price = position['entry_price']
        
        # Apply slippage
        execution_price = price * (1 - self.slippage_bps)
        
        # Calculate proceeds
        proceeds = shares * execution_price
        commission_cost = shares * self.commission
        net_proceeds = proceeds - commission_cost
        
        # Update cash
        self.cash += net_proceeds
        
        # Calculate P&L
        pnl = net_proceeds - (shares * entry_price)
        pnl_pct = (pnl / (shares * entry_price)) * 100
        
        self.trades.append({
            'symbol': symbol,
            'type': 'EXIT',
            'shares': shares,
            'price': execution_price,
            'proceeds': net_proceeds,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': reason,
            'date': self.dates[-1] if self.dates else datetime.now()
        })
        
        # Remove position
        del self.positions[symbol]
    
    def _calculate_equity(self, current_price: float) -> float:
        """Calculate current equity."""
        equity = self.cash
        for symbol, position in self.positions.items():
            equity += position['shares'] * current_price
        return equity
    
    def _calculate_period(self, start_date: str, end_date: str) -> str:
        """Calculate period string for data fetching."""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        days = (end - start).days
        
        if days <= 5:
            return '5d'
        elif days <= 30:
            return '1mo'
        elif days <= 90:
            return '3mo'
        elif days <= 180:
            return '6mo'
        elif days <= 365:
            return '1y'
        else:
            return '2y'
    
    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics."""
        if not self.equity_curve or len(self.equity_curve) < 2:
            return {}
        
        equity_series = pd.Series(self.equity_curve)
        returns = equity_series.pct_change().dropna()
        
        # Total return
        total_return = (equity_series.iloc[-1] - equity_series.iloc[0]) / equity_series.iloc[0]
        
        # CAGR (simplified)
        days = len(equity_series)
        years = days / 252  # Trading days
        cagr = ((equity_series.iloc[-1] / equity_series.iloc[0]) ** (1 / years) - 1) if years > 0 else 0
        
        # Sharpe ratio (simplified)
        sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        # Max drawdown
        peak = equity_series.expanding().max()
        drawdown = (equity_series - peak) / peak
        max_drawdown = abs(drawdown.min())
        
        # Win rate
        winning_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0
        
        return {
            'total_return': total_return,
            'cagr': cagr,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'num_trades': len(self.trades)
        }
