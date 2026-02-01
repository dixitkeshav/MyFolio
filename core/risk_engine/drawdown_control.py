"""
Drawdown Controller

Monitors and controls drawdowns to protect capital.
"""

from typing import List, Dict, Optional
import yaml
import os
import pandas as pd
import numpy as np


class DrawdownController:
    """Drawdown monitoring and control."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize drawdown controller.
        
        Args:
            config_path: Path to risk configuration file
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '../../config/risk.yaml')
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        drawdown_config = self.config.get('drawdown', {})
        self.max_drawdown_pct = drawdown_config.get('max_drawdown_pct', 0.15)
        self.reduce_risk_at_drawdown = drawdown_config.get('reduce_risk_at_drawdown', 0.10)
        self.kill_switch_drawdown = drawdown_config.get('kill_switch_drawdown', 0.20)
        self.reduce_risk_multiplier = drawdown_config.get('reduce_risk_multiplier', 0.5)
        
        self.equity_curve = []
        self.peak_equity = None
        self.kill_switch_active = False
    
    def update_equity(self, equity: float):
        """
        Update equity curve.
        
        Args:
            equity: Current account equity
        """
        self.equity_curve.append(equity)
        
        if self.peak_equity is None or equity > self.peak_equity:
            self.peak_equity = equity
    
    def calculate_drawdown(self, equity_curve: Optional[List[float]] = None) -> Dict:
        """
        Calculate current drawdown.
        
        Args:
            equity_curve: List of equity values (optional, uses internal if None)
            
        Returns:
            Dictionary with drawdown information
        """
        if equity_curve is None:
            equity_curve = self.equity_curve
        
        if not equity_curve or len(equity_curve) < 2:
            return {
                'current_drawdown': 0,
                'max_drawdown': 0,
                'drawdown_pct': 0
            }
        
        equity_series = pd.Series(equity_curve)
        peak = equity_series.expanding().max()
        drawdown = equity_series - peak
        drawdown_pct = (drawdown / peak) * 100
        
        current_drawdown = abs(drawdown.iloc[-1])
        current_drawdown_pct = abs(drawdown_pct.iloc[-1])
        max_drawdown = abs(drawdown.min())
        max_drawdown_pct = abs(drawdown_pct.min())
        
        return {
            'current_drawdown': current_drawdown,
            'current_drawdown_pct': current_drawdown_pct,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'peak_equity': peak.iloc[-1]
        }
    
    def check_max_drawdown(self) -> bool:
        """
        Check if current drawdown exceeds maximum allowed.
        
        Returns:
            True if drawdown is acceptable, False if exceeded
        """
        if not self.equity_curve:
            return True
        
        drawdown_info = self.calculate_drawdown()
        current_drawdown_pct = drawdown_info.get('current_drawdown_pct', 0)
        
        if current_drawdown_pct > self.max_drawdown_pct:
            return False
        
        return True
    
    def should_reduce_risk(self) -> bool:
        """
        Determine if risk should be reduced.
        
        Returns:
            True if risk should be reduced
        """
        if not self.equity_curve:
            return False
        
        drawdown_info = self.calculate_drawdown()
        current_drawdown_pct = drawdown_info.get('current_drawdown_pct', 0)
        
        return current_drawdown_pct > self.reduce_risk_at_drawdown
    
    def get_risk_multiplier(self) -> float:
        """
        Get risk multiplier based on drawdown.
        
        Returns:
            Risk multiplier (1.0 = normal, < 1.0 = reduced risk)
        """
        if self.should_reduce_risk():
            return self.reduce_risk_multiplier
        return 1.0
    
    def activate_kill_switch(self) -> bool:
        """
        Activate kill switch if drawdown exceeds threshold.
        
        Returns:
            True if kill switch activated
        """
        if not self.equity_curve:
            return False
        
        drawdown_info = self.calculate_drawdown()
        current_drawdown_pct = drawdown_info.get('current_drawdown_pct', 0)
        
        if current_drawdown_pct > self.kill_switch_drawdown:
            self.kill_switch_active = True
            return True
        
        return False
    
    def is_kill_switch_active(self) -> bool:
        """Check if kill switch is active."""
        return self.kill_switch_active
    
    def reset_kill_switch(self):
        """Reset kill switch (manual override)."""
        self.kill_switch_active = False
