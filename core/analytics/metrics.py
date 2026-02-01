"""
Additional Metrics Calculator

Additional trading metrics beyond basic performance.
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime


class MetricsCalculator:
    """Additional metrics calculator."""
    
    def calculate_time_in_market(self, trades: List[Dict]) -> float:
        """
        Calculate percentage of time in market.
        
        Args:
            trades: List of trades with entry/exit dates
            
        Returns:
            Time in market as percentage
        """
        if not trades:
            return 0
        
        # Simplified calculation
        # Would need full trade history with dates
        return 0.5  # Placeholder
    
    def calculate_avg_holding_period(self, trades: List[Dict]) -> float:
        """
        Calculate average holding period in days.
        
        Args:
            trades: List of trades with entry/exit dates
            
        Returns:
            Average holding period in days
        """
        if not trades:
            return 0
        
        holding_periods = []
        for trade in trades:
            entry_date = trade.get('entry_date')
            exit_date = trade.get('exit_date')
            
            if entry_date and exit_date:
                if isinstance(entry_date, str):
                    entry_date = datetime.strptime(entry_date, '%Y-%m-%d')
                if isinstance(exit_date, str):
                    exit_date = datetime.strptime(exit_date, '%Y-%m-%d')
                
                days = (exit_date - entry_date).days
                holding_periods.append(days)
        
        if not holding_periods:
            return 0
        
        return sum(holding_periods) / len(holding_periods)
    
    def calculate_avg_win_loss(self, trades: List[Dict]) -> Dict:
        """
        Calculate average win and loss.
        
        Args:
            trades: List of trades with 'pnl' key
            
        Returns:
            Dictionary with average win and loss
        """
        wins = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0]
        losses = [t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0]
        
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        return {
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'win_loss_ratio': abs(avg_win / avg_loss) if avg_loss != 0 else 0
        }
    
    def calculate_recovery_factor(self, equity_curve: List[float]) -> float:
        """
        Calculate recovery factor (net profit / max drawdown).
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            Recovery factor
        """
        if not equity_curve or len(equity_curve) < 2:
            return 0
        
        net_profit = equity_curve[-1] - equity_curve[0]
        
        equity_series = pd.Series(equity_curve)
        peak = equity_series.expanding().max()
        drawdown = equity_series - peak
        max_drawdown = abs(drawdown.min())
        
        if max_drawdown == 0:
            return float('inf') if net_profit > 0 else 0
        
        return net_profit / max_drawdown
    
    def calculate_ulcer_index(self, equity_curve: List[float]) -> float:
        """
        Calculate Ulcer Index (measure of drawdown volatility).
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            Ulcer Index
        """
        if not equity_curve or len(equity_curve) < 2:
            return 0
        
        equity_series = pd.Series(equity_curve)
        peak = equity_series.expanding().max()
        drawdown_pct = ((equity_series - peak) / peak) * 100
        
        squared_drawdowns = (drawdown_pct ** 2).sum()
        ulcer_index = np.sqrt(squared_drawdowns / len(equity_curve))
        
        return ulcer_index
