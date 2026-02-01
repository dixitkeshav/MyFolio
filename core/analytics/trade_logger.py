"""
Trade Logger

Logs and tracks all trades.
"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Optional
import os


class TradeLogger:
    """Trade logging system."""
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize trade logger.
        
        Args:
            log_file: Path to log file (optional)
        """
        if log_file is None:
            log_dir = os.path.join(os.path.dirname(__file__), '../../logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, 'trades.json')
        
        self.log_file = log_file
        self.trades = []
        
        # Load existing trades if file exists
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    self.trades = json.load(f)
            except:
                self.trades = []
    
    def log_trade(self, trade: Dict):
        """
        Log a trade.
        
        Args:
            trade: Trade dictionary
        """
        trade['logged_at'] = datetime.now().isoformat()
        self.trades.append(trade)
        
        # Save to file
        self._save_trades()
    
    def get_trade_history(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> List[Dict]:
        """
        Get trade history.
        
        Args:
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            symbol: Symbol filter
            
        Returns:
            List of trades
        """
        filtered = self.trades
        
        if symbol:
            filtered = [t for t in filtered if t.get('symbol') == symbol]
        
        if start_date:
            filtered = [t for t in filtered if t.get('date', '') >= start_date]
        
        if end_date:
            filtered = [t for t in filtered if t.get('date', '') <= end_date]
        
        return filtered
    
    def export_trades(self, format: str = 'csv', filepath: Optional[str] = None) -> str:
        """
        Export trades to file.
        
        Args:
            format: Export format ('csv' or 'json')
            filepath: Output file path (optional)
            
        Returns:
            Path to exported file
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if format == 'csv':
                filepath = f'logs/trades_export_{timestamp}.csv'
            else:
                filepath = f'logs/trades_export_{timestamp}.json'
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if format == 'csv':
            if self.trades:
                with open(filepath, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=self.trades[0].keys())
                    writer.writeheader()
                    writer.writerows(self.trades)
        else:  # JSON
            with open(filepath, 'w') as f:
                json.dump(self.trades, f, indent=2)
        
        return filepath
    
    def analyze_trades(self) -> Dict:
        """
        Analyze trade patterns.
        
        Returns:
            Dictionary with trade analysis
        """
        if not self.trades:
            return {}
        
        winning_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in self.trades if t.get('pnl', 0) < 0]
        
        total_pnl = sum(t.get('pnl', 0) for t in self.trades)
        
        return {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(self.trades) if self.trades else 0,
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / len(self.trades) if self.trades else 0
        }
    
    def _save_trades(self):
        """Save trades to file."""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump(self.trades, f, indent=2)
