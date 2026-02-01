"""
Fundamental Analysis Engine

Fundamental filters based on economic data and central bank policy.
"""

from typing import Dict, Optional
from core.data_engine.economic_data import EconomicDataFetcher
from core.regime_engine.macro_regime import MacroRegimeDetector


class FundamentalAnalyzer:
    """Fundamental analysis engine."""
    
    def __init__(self):
        """Initialize fundamental analyzer."""
        self.economic_fetcher = EconomicDataFetcher()
        self.regime_detector = MacroRegimeDetector()
    
    def check_central_bank_policy(self) -> Dict:
        """Check central bank policy stance."""
        fed_data = self.economic_fetcher.get_fed_funds_rate()
        
        current_rate = fed_data.get('current_rate', 0)
        change = fed_data.get('change', 0)
        
        if change > 0:
            stance = 'hawkish'
        elif change < 0:
            stance = 'dovish'
        else:
            stance = 'neutral'
        
        return {
            'stance': stance,
            'current_rate': current_rate,
            'change': change
        }
    
    def assess_rate_environment(self) -> str:
        """Assess interest rate environment."""
        policy = self.check_central_bank_policy()
        current_rate = policy.get('current_rate', 0)
        
        if current_rate > 5:
            return 'high_rates'
        elif current_rate < 2:
            return 'low_rates'
        else:
            return 'moderate_rates'
    
    def check_economic_data_alignment(self, direction: str) -> bool:
        """
        Check if economic data aligns with trade direction.
        
        Args:
            direction: Trade direction ('LONG' or 'SHORT')
            
        Returns:
            True if economic data supports the direction
        """
        # Get economic indicators
        cpi_data = self.economic_fetcher.get_cpi_data()
        gdp_data = self.economic_fetcher.get_gdp_data()
        unemployment_data = self.economic_fetcher.get_unemployment_rate()
        
        # For LONG: want strong economy (low inflation, high GDP, low unemployment)
        # For SHORT: can tolerate weak economy
        
        if direction == 'LONG':
            # Check if economy is supportive
            cpi_yoy = cpi_data.get('yoy_change', 0)
            gdp_qoq = gdp_data.get('qoq_change', 0)
            unemployment = unemployment_data.get('current_rate', 0)
            
            # Supportive if: moderate inflation (< 4%), positive GDP, low unemployment (< 5%)
            supportive = (
                cpi_yoy < 4 and
                gdp_qoq > 0 and
                unemployment < 5
            )
            return supportive
        else:  # SHORT
            # Shorts can work in weak or strong economies
            return True
    
    def calculate_policy_impact(self) -> Dict:
        """Calculate policy impact on asset classes."""
        policy = self.check_central_bank_policy()
        stance = policy.get('stance', 'neutral')
        
        impact = {
            'equities': 'neutral',
            'bonds': 'neutral',
            'gold': 'neutral',
            'usd': 'neutral'
        }
        
        if stance == 'hawkish':
            impact['equities'] = 'negative'  # Higher rates pressure equities
            impact['bonds'] = 'negative'  # Bond prices fall
            impact['usd'] = 'positive'  # USD strengthens
            impact['gold'] = 'negative'  # Gold pressured by higher rates
        elif stance == 'dovish':
            impact['equities'] = 'positive'  # Lower rates support equities
            impact['bonds'] = 'positive'  # Bond prices rise
            impact['usd'] = 'negative'  # USD weakens
            impact['gold'] = 'positive'  # Gold supported by lower rates
        
        return impact
    
    def check_fundamentals(self, symbol: str, direction: str) -> bool:
        """
        Check if fundamentals support the trade.
        
        Args:
            symbol: Stock symbol
            direction: Trade direction ('LONG' or 'SHORT')
            
        Returns:
            True if fundamentals support the trade
        """
        # Check economic data alignment
        economic_alignment = self.check_economic_data_alignment(direction)
        
        # Check policy impact
        policy_impact = self.calculate_policy_impact()
        
        if direction == 'LONG':
            # For longs, want positive policy impact on equities
            policy_supportive = policy_impact.get('equities') in ['positive', 'neutral']
            return economic_alignment and policy_supportive
        else:  # SHORT
            # For shorts, can work with negative or neutral policy impact
            return True
    
    def filter_by_fundamentals(self, symbols: list, direction: str) -> list:
        """
        Filter symbols by fundamental criteria.
        
        Args:
            symbols: List of symbols to filter
            direction: Trade direction
            
        Returns:
            Filtered list of symbols
        """
        filtered = []
        for symbol in symbols:
            if self.check_fundamentals(symbol, direction):
                filtered.append(symbol)
        return filtered
