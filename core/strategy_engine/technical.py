"""
Technical Analysis Engine

Technical indicators and signal generation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


class TechnicalAnalyzer:
    """Technical analysis engine."""
    
    def __init__(self):
        """Initialize technical analyzer."""
        pass
    
    def calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return df['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(window=period).mean()
    
    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Volume Weighted Average Price."""
        return (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    
    def detect_market_structure(self, df: pd.DataFrame) -> Dict:
        """Detect market structure (HH/HL, LH/LL)."""
        df = df.copy()
        df['local_high'] = (df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1))
        df['local_low'] = (df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1))
        
        highs = df[df['local_high']]['high'].tail(5).tolist()
        lows = df[df['local_low']]['low'].tail(5).tolist()
        
        structure = {
            'trend': 'neutral',
            'higher_highs': len([h for i, h in enumerate(highs[1:]) if h > highs[i]]) > len(highs) / 2 if len(highs) > 1 else False,
            'lower_lows': len([l for i, l in enumerate(lows[1:]) if l < lows[i]]) > len(lows) / 2 if len(lows) > 1 else False
        }
        
        if structure['higher_highs'] and not structure['lower_lows']:
            structure['trend'] = 'uptrend'
        elif structure['lower_lows'] and not structure['higher_highs']:
            structure['trend'] = 'downtrend'
        
        return structure
    
    def identify_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """Identify support and resistance levels."""
        recent = df.tail(window)
        resistance = recent['high'].max()
        support = recent['low'].min()
        
        return {
            'support': support,
            'resistance': resistance,
            'current_price': df['close'].iloc[-1]
        }
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std: float = 2) -> pd.DataFrame:
        """Calculate Bollinger Bands."""
        df = df.copy()
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        bb_std = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * std)
        df['bb_lower'] = df['bb_middle'] - (bb_std * std)
        return df[['bb_middle', 'bb_upper', 'bb_lower']]
    
    def detect_divergence(self, df: pd.DataFrame, rsi_period: int = 14) -> Dict:
        """Detect RSI/price divergence."""
        rsi = self.calculate_rsi(df, rsi_period)
        
        # Find recent peaks and troughs
        price_peaks = df['close'].rolling(window=5, center=True).max() == df['close']
        rsi_peaks = rsi.rolling(window=5, center=True).max() == rsi
        
        divergence = {
            'bullish_divergence': False,
            'bearish_divergence': False
        }
        
        # Simplified divergence detection
        if len(df) > 20:
            recent_price = df['close'].tail(10)
            recent_rsi = rsi.tail(10)
            
            if recent_price.iloc[-1] < recent_price.iloc[0] and recent_rsi.iloc[-1] > recent_rsi.iloc[0]:
                divergence['bullish_divergence'] = True
            elif recent_price.iloc[-1] > recent_price.iloc[0] and recent_rsi.iloc[-1] < recent_rsi.iloc[0]:
                divergence['bearish_divergence'] = True
        
        return divergence
    
    def generate_entry_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate entry signals based on technical indicators."""
        df = df.copy()
        
        # Add indicators
        df['ema_50'] = self.calculate_ema(df, 50)
        df['ema_200'] = self.calculate_ema(df, 200)
        df['rsi'] = self.calculate_rsi(df)
        
        # Generate signals
        df['long_signal'] = (
            (df['close'] > df['ema_50']) &
            (df['ema_50'] > df['ema_200']) &
            (df['rsi'] < 70) &
            (df['rsi'] > 30)
        )
        
        df['short_signal'] = (
            (df['close'] < df['ema_50']) &
            (df['ema_50'] < df['ema_200']) &
            (df['rsi'] > 30) &
            (df['rsi'] < 70)
        )
        
        return df
    
    def generate_exit_signals(self, df: pd.DataFrame, position: Dict) -> Dict:
        """Generate exit signals for a position."""
        df = df.copy()
        
        if len(df) < 50:
            return {'exit': False, 'reason': 'Insufficient data'}
        
        # Add indicators
        df['ema_50'] = self.calculate_ema(df, 50)
        df['rsi'] = self.calculate_rsi(df)
        
        current_price = df['close'].iloc[-1]
        position_type = position.get('type', 'LONG')
        entry_price = position.get('entry_price', current_price)
        
        exit_signal = False
        reason = ''
        
        if position_type == 'LONG':
            # Exit long if price crosses below EMA 50
            if current_price < df['ema_50'].iloc[-1]:
                exit_signal = True
                reason = 'Price crossed below EMA 50'
            # Exit if RSI becomes overbought
            elif df['rsi'].iloc[-1] > 80:
                exit_signal = True
                reason = 'RSI overbought'
        else:  # SHORT
            # Exit short if price crosses above EMA 50
            if current_price > df['ema_50'].iloc[-1]:
                exit_signal = True
                reason = 'Price crossed above EMA 50'
            # Exit if RSI becomes oversold
            elif df['rsi'].iloc[-1] < 20:
                exit_signal = True
                reason = 'RSI oversold'
        
        return {
            'exit': exit_signal,
            'reason': reason,
            'current_price': current_price
        }
