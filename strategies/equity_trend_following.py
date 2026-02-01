"""
Equity Trend Following Strategy

Simple trend-following strategy for equities.
"""

import pandas as pd
from typing import Dict
from core.strategy_engine.base_strategy import BaseStrategy
from core.strategy_engine.technical import TechnicalAnalyzer


class EquityTrendFollowing(BaseStrategy):
    """Trend-following strategy for equities."""
    
    def __init__(self):
        """Initialize strategy."""
        super().__init__(
            name="Equity Trend Following",
            require_all_layers=True
        )
        self.technical_analyzer = TechnicalAnalyzer()
    
    def check_technical_entry(self, df: pd.DataFrame) -> Dict:
        """
        Check technical entry conditions.
        
        Args:
            df: DataFrame with price data
            
        Returns:
            Dictionary with signal information
        """
        if len(df) < 200:
            return {'signal': False, 'reason': 'Insufficient data'}
        
        # Calculate EMAs
        df['ema_50'] = self.technical_analyzer.calculate_ema(df, 50)
        df['ema_200'] = self.technical_analyzer.calculate_ema(df, 200)
        df['rsi'] = self.technical_analyzer.calculate_rsi(df)
        
        current_price = df['close'].iloc[-1]
        ema_50 = df['ema_50'].iloc[-1]
        ema_200 = df['ema_200'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        
        # Long signal: price > EMA50 > EMA200, RSI not overbought
        long_signal = (
            current_price > ema_50 and
            ema_50 > ema_200 and
            rsi < 70 and
            rsi > 30
        )
        
        # Short signal: price < EMA50 < EMA200, RSI not oversold
        short_signal = (
            current_price < ema_50 and
            ema_50 < ema_200 and
            rsi > 30 and
            rsi < 70
        )
        
        if long_signal:
            return {
                'signal': True,
                'direction': 'LONG',
                'entry_price': current_price,
                'stop_loss': ema_50 * 0.95,  # 5% below EMA50
                'take_profit': current_price * 1.10  # 10% profit target
            }
        elif short_signal:
            return {
                'signal': True,
                'direction': 'SHORT',
                'entry_price': current_price,
                'stop_loss': ema_50 * 1.05,  # 5% above EMA50
                'take_profit': current_price * 0.90  # 10% profit target
            }
        else:
            return {'signal': False, 'reason': 'No trend signal'}
    
    def should_exit(self, symbol: str, df: pd.DataFrame, position: Dict) -> Dict:
        """
        Check exit conditions.
        
        Args:
            symbol: Stock symbol
            df: DataFrame with price data
            position: Current position
            
        Returns:
            Dictionary with exit decision
        """
        if len(df) < 50:
            return {'exit': False}
        
        exit_signal = self.technical_analyzer.generate_exit_signals(df, position)
        return exit_signal
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals.
        
        Args:
            df: DataFrame with price data
            
        Returns:
            DataFrame with signals
        """
        return self.technical_analyzer.generate_entry_signals(df)
