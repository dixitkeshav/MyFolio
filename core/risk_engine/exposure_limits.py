"""
Exposure Limits Manager

Manages portfolio exposure and correlation limits.
"""

from typing import Dict, List, Optional
import yaml
import os


class ExposureManager:
    """Exposure and position limit management."""
    
    def __init__(self, config_path: Optional[str] = None, initial_capital: float = 100000):
        """
        Initialize exposure manager.
        
        Args:
            config_path: Path to risk configuration file
            initial_capital: Initial account capital
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '../../config/risk.yaml')
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        exposure_config = self.config.get('exposure', {})
        self.max_total_exposure_pct = exposure_config.get('max_total_exposure_pct', 1.0)
        self.max_sector_exposure_pct = exposure_config.get('max_sector_exposure_pct', 0.25)
        self.max_correlation_exposure_pct = exposure_config.get('max_correlation_exposure_pct', 0.30)
        self.max_single_position_pct = exposure_config.get('max_single_position_pct', 0.10)
        
        self.account_value = initial_capital
        self.positions = {}  # {symbol: position_info}
    
    def update_account_value(self, value: float):
        """Update account value."""
        self.account_value = value
    
    def get_account_value(self) -> float:
        """Get current account value."""
        return self.account_value
    
    def add_position(self, symbol: str, size: float, price: float):
        """
        Add a position.
        
        Args:
            symbol: Stock symbol
            size: Position size in dollars
            price: Entry price
        """
        self.positions[symbol] = {
            'size': size,
            'price': price,
            'value': size * price
        }
    
    def remove_position(self, symbol: str):
        """Remove a position."""
        if symbol in self.positions:
            del self.positions[symbol]
    
    def calculate_total_exposure(self) -> Dict:
        """Calculate total portfolio exposure."""
        total_exposure = sum(pos['value'] for pos in self.positions.values())
        exposure_pct = (total_exposure / self.account_value) if self.account_value > 0 else 0
        
        return {
            'total_exposure': total_exposure,
            'exposure_pct': exposure_pct,
            'max_exposure': self.account_value * self.max_total_exposure_pct,
            'max_exposure_pct': self.max_total_exposure_pct
        }
    
    def check_sector_exposure(self, sector: str) -> Dict:
        """
        Check sector exposure.
        
        Args:
            sector: Sector name
            
        Returns:
            Dictionary with sector exposure information
        """
        # Placeholder - would require sector mapping
        sector_exposure = 0
        exposure_pct = (sector_exposure / self.account_value) if self.account_value > 0 else 0
        
        return {
            'sector_exposure': sector_exposure,
            'exposure_pct': exposure_pct,
            'max_exposure': self.account_value * self.max_sector_exposure_pct,
            'within_limit': exposure_pct <= self.max_sector_exposure_pct
        }
    
    def check_correlation_exposure(self) -> Dict:
        """Check correlated positions exposure."""
        # Placeholder - would require correlation analysis
        correlated_exposure = 0
        exposure_pct = (correlated_exposure / self.account_value) if self.account_value > 0 else 0
        
        return {
            'correlated_exposure': correlated_exposure,
            'exposure_pct': exposure_pct,
            'max_exposure': self.account_value * self.max_correlation_exposure_pct,
            'within_limit': exposure_pct <= self.max_correlation_exposure_pct
        }
    
    def check_max_position_size(self, symbol: str, size: float) -> bool:
        """
        Check if position size exceeds maximum.
        
        Args:
            symbol: Stock symbol
            size: Position size in dollars
            
        Returns:
            True if within limit
        """
        max_position_size = self.account_value * self.max_single_position_pct
        return size <= max_position_size
    
    def can_add_position(self, symbol: str, size: float) -> bool:
        """
        Check if new position can be added.
        
        Args:
            symbol: Stock symbol
            size: Position size in dollars
            
        Returns:
            True if position can be added
        """
        # Check if already have position
        if symbol in self.positions:
            return False  # Already have position
        
        # Check max position size
        if not self.check_max_position_size(symbol, size):
            return False
        
        # Check total exposure
        exposure_info = self.calculate_total_exposure()
        new_total_exposure = exposure_info['total_exposure'] + size
        
        if new_total_exposure > exposure_info['max_exposure']:
            return False
        
        return True
    
    def get_positions(self) -> Dict:
        """Get all current positions."""
        return self.positions.copy()
