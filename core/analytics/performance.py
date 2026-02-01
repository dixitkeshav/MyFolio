"""
Performance Analyzer

Calculates performance metrics from trading results.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional


class PerformanceAnalyzer:
    """Performance analysis engine."""
    
    def __init__(self, risk_free_rate: float = 0.04):
        """
        Initialize performance analyzer.
        
        Args:
            risk_free_rate: Risk-free rate (annual, default 4%)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_cagr(
        self,
        start_value: float,
        end_value: float,
        years: float
    ) -> float:
        """
        Calculate Compound Annual Growth Rate.
        
        Args:
            start_value: Starting value
            end_value: Ending value
            years: Number of years
            
        Returns:
            CAGR as decimal
        """
        if years <= 0 or start_value <= 0:
            return 0
        
        return (end_value / start_value) ** (1 / years) - 1
    
    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: Optional[float] = None
    ) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: Series of returns
            risk_free_rate: Risk-free rate (optional, uses instance default)
            
        Returns:
            Sharpe ratio
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        if len(returns) == 0 or returns.std() == 0:
            return 0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(252)
        
        return sharpe
    
    def calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """
        Calculate Sortino ratio (downside risk-adjusted).
        
        Args:
            returns: Series of returns
            
        Returns:
            Sortino ratio
        """
        if len(returns) == 0:
            return 0
        
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0
        
        sortino = (returns.mean() / downside_returns.std()) * np.sqrt(252)
        return sortino
    
    def calculate_max_drawdown(self, equity_curve: List[float]) -> Dict:
        """
        Calculate maximum drawdown.
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            Dictionary with drawdown information
        """
        if not equity_curve or len(equity_curve) < 2:
            return {'max_drawdown': 0, 'max_drawdown_pct': 0}
        
        equity_series = pd.Series(equity_curve)
        peak = equity_series.expanding().max()
        drawdown = equity_series - peak
        drawdown_pct = (drawdown / peak) * 100
        
        max_drawdown = abs(drawdown.min())
        max_drawdown_pct = abs(drawdown_pct.min())
        
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct
        }
    
    def calculate_win_rate(self, trades: List[Dict]) -> float:
        """
        Calculate win rate.
        
        Args:
            trades: List of trade dictionaries with 'pnl' key
            
        Returns:
            Win rate as decimal (0 to 1)
        """
        if not trades:
            return 0
        
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        return len(winning_trades) / len(trades)
    
    def calculate_expectancy(self, trades: List[Dict]) -> float:
        """
        Calculate trade expectancy.
        
        Args:
            trades: List of trade dictionaries with 'pnl' key
            
        Returns:
            Average profit per trade
        """
        if not trades:
            return 0
        
        total_pnl = sum(t.get('pnl', 0) for t in trades)
        return total_pnl / len(trades)
    
    def calculate_profit_factor(self, trades: List[Dict]) -> float:
        """
        Calculate profit factor.
        
        Args:
            trades: List of trade dictionaries with 'pnl' key
            
        Returns:
            Profit factor (gross profit / gross loss)
        """
        gross_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
        gross_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0
        
        return gross_profit / gross_loss
    
    def generate_performance_report(
        self,
        equity_curve: List[float],
        trades: List[Dict],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Generate comprehensive performance report.
        
        Args:
            equity_curve: List of equity values
            trades: List of trades
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            Dictionary with all performance metrics
        """
        if not equity_curve:
            return {}
        
        equity_series = pd.Series(equity_curve)
        returns = equity_series.pct_change().dropna()
        
        # Calculate time period
        if start_date and end_date:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            years = (end - start).days / 365.25
        else:
            years = len(equity_curve) / 252  # Assume trading days
        
        # Metrics
        initial_value = equity_curve[0]
        final_value = equity_curve[-1]
        total_return = final_value - initial_value
        total_return_pct = (total_return / initial_value) * 100
        
        cagr = self.calculate_cagr(initial_value, final_value, years)
        sharpe = self.calculate_sharpe_ratio(returns)
        sortino = self.calculate_sortino_ratio(returns)
        drawdown_info = self.calculate_max_drawdown(equity_curve)
        win_rate = self.calculate_win_rate(trades)
        expectancy = self.calculate_expectancy(trades)
        profit_factor = self.calculate_profit_factor(trades)
        
        return {
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'cagr': cagr,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown': drawdown_info['max_drawdown'],
            'max_drawdown_pct': drawdown_info['max_drawdown_pct'],
            'win_rate': win_rate,
            'expectancy': expectancy,
            'profit_factor': profit_factor,
            'num_trades': len(trades),
            'years': years
        }
