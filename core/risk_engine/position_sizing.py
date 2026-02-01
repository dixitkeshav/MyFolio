"""
Position Sizing Calculator

Calculates position sizes based on risk management rules.
"""

from typing import Dict, Optional
import yaml
import os


class PositionSizer:
    """Position sizing calculator."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize position sizer.
        
        Args:
            config_path: Path to risk configuration file
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '../../config/risk.yaml')
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.risk_per_trade = self.config.get('position_sizing', {}).get('risk_per_trade', 0.01)
        self.max_position_size_pct = self.config.get('position_sizing', {}).get('max_position_size_pct', 0.10)
    
    def calculate_position_size(
        self,
        account_value: float,
        risk_per_trade: Optional[float] = None,
        stop_loss_pct: float = 0.05
    ) -> Dict:
        """
        Calculate position size based on risk.
        
        Args:
            account_value: Total account value
            risk_per_trade: Risk per trade as decimal (e.g., 0.01 for 1%)
            stop_loss_pct: Stop loss percentage as decimal (e.g., 0.05 for 5%)
            
        Returns:
            Dictionary with position size information
        """
        if risk_per_trade is None:
            risk_per_trade = self.risk_per_trade
        
        # Risk amount in dollars
        risk_amount = account_value * risk_per_trade
        
        # Position size = Risk Amount / Stop Loss Distance
        position_size = risk_amount / stop_loss_pct
        
        # Apply maximum position size limit
        max_position_size = account_value * self.max_position_size_pct
        position_size = min(position_size, max_position_size)
        
        return {
            'position_size': position_size,
            'risk_amount': risk_amount,
            'risk_per_trade': risk_per_trade,
            'stop_loss_pct': stop_loss_pct,
            'max_position_size': max_position_size
        }
    
    def calculate_shares(self, price: float, position_size: float) -> int:
        """
        Calculate number of shares for a position.
        
        Args:
            price: Stock price
            position_size: Position size in dollars
            
        Returns:
            Number of shares (integer)
        """
        if price <= 0:
            return 0
        
        shares = int(position_size / price)
        return max(1, shares)  # At least 1 share
    
    def apply_kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Apply Kelly Criterion for position sizing.
        
        Args:
            win_rate: Win rate (0 to 1)
            avg_win: Average win amount
            avg_loss: Average loss amount
            
        Returns:
            Kelly percentage (fraction of capital to risk)
        """
        if avg_loss == 0:
            return 0
        
        win_loss_ratio = avg_win / abs(avg_loss)
        kelly_pct = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Kelly should be between 0 and 1
        kelly_pct = max(0, min(1, kelly_pct))
        
        # Use fractional Kelly (half Kelly is safer)
        fractional_kelly = kelly_pct * 0.5
        
        return fractional_kelly
    
    def apply_fixed_fractional(
        self,
        account_value: float,
        risk_per_trade: float = 0.01
    ) -> float:
        """
        Apply fixed fractional position sizing.
        
        Args:
            account_value: Account value
            risk_per_trade: Risk per trade as decimal
            
        Returns:
            Position size as fraction of account
        """
        return risk_per_trade
