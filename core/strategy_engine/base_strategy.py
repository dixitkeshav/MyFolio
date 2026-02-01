"""
Base Strategy Class

Abstract base class for all trading strategies. Implements multi-layer filtering.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
try:
    from core.regime_engine.macro_regime import MacroRegimeDetector
    from core.data_engine.economic_data import EconomicDataFetcher
    from core.data_engine.sentiment_data import SentimentAnalyzer
    from core.strategy_engine.fundamental import FundamentalAnalyzer
    from core.strategy_engine.sentiment import SentimentFilter
    from core.strategy_engine.intermarket import IntermarketAnalyzer
    from core.risk_engine.position_sizing import PositionSizer
    from core.risk_engine.drawdown_control import DrawdownController
    from core.risk_engine.exposure_limits import ExposureManager
except ImportError:
    # Handle relative imports
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from core.regime_engine.macro_regime import MacroRegimeDetector
    from core.data_engine.economic_data import EconomicDataFetcher
    from core.data_engine.sentiment_data import SentimentAnalyzer
    from core.strategy_engine.fundamental import FundamentalAnalyzer
    from core.strategy_engine.sentiment import SentimentFilter
    from core.strategy_engine.intermarket import IntermarketAnalyzer
    from core.risk_engine.position_sizing import PositionSizer
    from core.risk_engine.drawdown_control import DrawdownController
    from core.risk_engine.exposure_limits import ExposureManager


class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, name: str, require_all_layers: bool = True):
        """
        Initialize base strategy.
        
        Args:
            name: Strategy name
            require_all_layers: If True, all layers must pass for trade
        """
        self.name = name
        self.require_all_layers = require_all_layers
        
        # Initialize engines
        self.regime_detector = MacroRegimeDetector()
        self.economic_fetcher = EconomicDataFetcher()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.sentiment_filter = SentimentFilter()
        self.intermarket_analyzer = IntermarketAnalyzer()
        
        # Risk management
        self.position_sizer = PositionSizer()
        self.drawdown_controller = DrawdownController()
        self.exposure_manager = ExposureManager()
        
        # Strategy state
        self.positions = {}
        self.trades = []
    
    def check_regime(self, required_regime: Optional[str] = None) -> bool:
        """
        Check if current regime allows trading.
        
        Args:
            required_regime: Required regime ('RISK_ON', 'RISK_OFF', or None for any)
            
        Returns:
            True if regime check passes
        """
        if required_regime is None:
            return True  # No regime requirement
        
        current_regime = self.regime_detector.get_regime_label()
        return current_regime == required_regime
    
    def check_fundamentals(self, symbol: str, direction: str) -> bool:
        """
        Check if fundamentals support the trade.
        
        Args:
            symbol: Stock symbol
            direction: Trade direction ('LONG' or 'SHORT')
            
        Returns:
            True if fundamental check passes
        """
        return self.fundamental_analyzer.check_fundamentals(symbol, direction)
    
    def check_sentiment(self, symbol: str, direction: str) -> bool:
        """
        Check if sentiment aligns with trade direction.
        
        Args:
            symbol: Stock symbol
            direction: Trade direction ('LONG' or 'SHORT')
            
        Returns:
            True if sentiment check passes
        """
        return self.sentiment_filter.check_sentiment_alignment(symbol, direction)
    
    def check_intermarket(self, symbol: str, direction: str) -> bool:
        """
        Check if intermarket relationships confirm the trade.
        
        Args:
            symbol: Stock symbol
            direction: Trade direction ('LONG' or 'SHORT')
            
        Returns:
            True if intermarket check passes
        """
        return self.intermarket_analyzer.confirm_trade(symbol, direction)
    
    @abstractmethod
    def check_technical_entry(self, df: pd.DataFrame) -> Dict:
        """
        Check if technical entry conditions are met.
        
        Args:
            df: DataFrame with price data and indicators
            
        Returns:
            Dictionary with signal information
        """
        pass
    
    def check_risk_rules(self, symbol: str, size: float) -> bool:
        """
        Check if risk management rules allow the trade.
        
        Args:
            symbol: Stock symbol
            size: Position size in dollars
            
        Returns:
            True if risk check passes
        """
        # Check drawdown
        if not self.drawdown_controller.check_max_drawdown():
            return False
        
        # Check exposure limits
        if not self.exposure_manager.can_add_position(symbol, size):
            return False
        
        return True
    
    def should_enter(
        self,
        symbol: str,
        df: pd.DataFrame,
        direction: str,
        required_regime: Optional[str] = None
    ) -> Dict:
        """
        Main entry logic - checks all layers.
        
        Args:
            symbol: Stock symbol
            df: DataFrame with price data
            direction: Trade direction ('LONG' or 'SHORT')
            required_regime: Required regime (optional)
            
        Returns:
            Dictionary with entry decision and reason
        """
        checks = {
            'regime': False,
            'fundamentals': False,
            'sentiment': False,
            'intermarket': False,
            'technical': False,
            'risk': False
        }
        
        reasons = []
        
        # Layer 1: Regime check
        if required_regime:
            checks['regime'] = self.check_regime(required_regime)
            if not checks['regime']:
                reasons.append(f"Regime check failed: required {required_regime}")
        else:
            checks['regime'] = True
        
        # Layer 2: Fundamental check
        checks['fundamentals'] = self.check_fundamentals(symbol, direction)
        if not checks['fundamentals']:
            reasons.append("Fundamental check failed")
        
        # Layer 3: Sentiment check
        checks['sentiment'] = self.check_sentiment(symbol, direction)
        if not checks['sentiment']:
            reasons.append("Sentiment check failed")
        
        # Layer 4: Intermarket check
        checks['intermarket'] = self.check_intermarket(symbol, direction)
        if not checks['intermarket']:
            reasons.append("Intermarket check failed")
        
        # Layer 5: Technical entry
        technical_signal = self.check_technical_entry(df)
        checks['technical'] = technical_signal.get('signal', False)
        if not checks['technical']:
            reasons.append("Technical entry check failed")
        
        # Layer 6: Risk rules
        # Calculate position size first (returns dict with 'position_size' key)
        account_value = self.exposure_manager.get_account_value()
        position_size_result = self.position_sizer.calculate_position_size(
            account_value, 0.01, 0.05  # 1% risk, 5% stop
        )
        position_size_dollars = position_size_result.get('position_size', 0) if isinstance(position_size_result, dict) else float(position_size_result or 0)
        checks['risk'] = self.check_risk_rules(symbol, position_size_dollars)
        if not checks['risk']:
            reasons.append("Risk rules check failed")
        
        # Decision
        if self.require_all_layers:
            all_passed = all(checks.values())
        else:
            # At least 4 out of 6 layers must pass
            passed_count = sum(checks.values())
            all_passed = passed_count >= 4
        
        return {
            'enter': all_passed,
            'checks': checks,
            'reasons': reasons,
            'technical_signal': technical_signal,
            'position_size': position_size_dollars if all_passed else 0
        }
    
    @abstractmethod
    def should_exit(self, symbol: str, df: pd.DataFrame, position: Dict) -> Dict:
        """
        Exit logic.
        
        Args:
            symbol: Stock symbol
            df: DataFrame with price data
            position: Current position information
            
        Returns:
            Dictionary with exit decision
        """
        pass
    
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals.
        
        Args:
            df: DataFrame with price data
            
        Returns:
            DataFrame with signals
        """
        pass
