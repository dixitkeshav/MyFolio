"""
Intermarket Analyzer

Analyzes intermarket relationships and confirms trades.
"""

import yfinance as yf
from typing import Dict
from core.regime_engine.macro_regime import MacroRegimeDetector


class IntermarketAnalyzer:
    """Intermarket analysis engine."""
    
    def __init__(self):
        """Initialize intermarket analyzer."""
        self.regime_detector = MacroRegimeDetector()
    
    def check_bond_equity_correlation(self) -> Dict:
        """Check bond-equity correlation."""
        try:
            # Get 10Y Treasury yield
            bond = yf.Ticker("^TNX")
            bond_data = bond.history(period="5d")
            
            # Get SPY
            spy = yf.Ticker("SPY")
            spy_data = spy.history(period="5d")
            
            if bond_data.empty or spy_data.empty:
                return {'correlation': 'neutral', 'interpretation': 'Insufficient data'}
            
            bond_change = (bond_data['Close'].iloc[-1] - bond_data['Close'].iloc[-2]) / bond_data['Close'].iloc[-2] * 100
            spy_change = (spy_data['Close'].iloc[-1] - spy_data['Close'].iloc[-2]) / spy_data['Close'].iloc[-2] * 100
            
            # Negative correlation: bonds up, equities down (risk-off)
            # Positive correlation: bonds up, equities up (risk-on)
            if bond_change > 0 and spy_change < 0:
                return {'correlation': 'negative', 'interpretation': 'Risk-off: bonds up, equities down'}
            elif bond_change < 0 and spy_change > 0:
                return {'correlation': 'positive', 'interpretation': 'Risk-on: bonds down, equities up'}
            else:
                return {'correlation': 'neutral', 'interpretation': 'Mixed signals'}
        except Exception as e:
            print(f"Error checking bond-equity correlation: {e}")
            return {'correlation': 'neutral', 'interpretation': 'Error'}
    
    def check_usd_impact(self) -> Dict:
        """Check USD impact on equities."""
        try:
            dxy = yf.Ticker("DX-Y.NYB")
            dxy_data = dxy.history(period="5d")
            
            spy = yf.Ticker("SPY")
            spy_data = spy.history(period="5d")
            
            if dxy_data.empty or spy_data.empty:
                return {'impact': 'neutral'}
            
            dxy_change = (dxy_data['Close'].iloc[-1] - dxy_data['Close'].iloc[-2]) / dxy_data['Close'].iloc[-2] * 100
            spy_change = (spy_data['Close'].iloc[-1] - spy_data['Close'].iloc[-2]) / spy_data['Close'].iloc[-2] * 100
            
            # Strong USD typically pressures equities
            if dxy_change > 0.5 and spy_change < 0:
                return {'impact': 'negative', 'interpretation': 'Strong USD pressuring equities'}
            elif dxy_change < -0.5 and spy_change > 0:
                return {'impact': 'positive', 'interpretation': 'Weak USD supporting equities'}
            else:
                return {'impact': 'neutral', 'interpretation': 'USD impact neutral'}
        except Exception as e:
            print(f"Error checking USD impact: {e}")
            return {'impact': 'neutral'}
    
    def check_gold_correlation(self) -> Dict:
        """Check gold correlation with risk sentiment."""
        try:
            gold = yf.Ticker("GC=F")
            gold_data = gold.history(period="5d")
            
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="5d")
            
            if gold_data.empty or vix_data.empty:
                return {'correlation': 'neutral'}
            
            gold_change = (gold_data['Close'].iloc[-1] - gold_data['Close'].iloc[-2]) / gold_data['Close'].iloc[-2] * 100
            vix_change = (vix_data['Close'].iloc[-1] - vix_data['Close'].iloc[-2]) / vix_data['Close'].iloc[-2] * 100
            
            # Gold up + VIX up = defensive/risk-off
            if gold_change > 0.5 and vix_change > 5:
                return {'correlation': 'defensive', 'interpretation': 'Gold and VIX up: defensive regime'}
            else:
                return {'correlation': 'neutral', 'interpretation': 'Normal correlation'}
        except Exception as e:
            print(f"Error checking gold correlation: {e}")
            return {'correlation': 'neutral'}
    
    def check_credit_spreads(self) -> Dict:
        """Check credit spread conditions."""
        # Placeholder - would require credit spread data
        return {'spreads': 'normal', 'interpretation': 'Credit spreads normal'}
    
    def confirm_trade(self, symbol: str, direction: str) -> bool:
        """
        Confirm trade with intermarket analysis.
        
        Args:
            symbol: Stock symbol
            direction: Trade direction ('LONG' or 'SHORT')
            
        Returns:
            True if intermarket confirms the trade
        """
        # Get regime
        regime_data = self.regime_detector.detect_regime()
        regime = regime_data.get('regime', 'NEUTRAL')
        
        # Check bond-equity correlation
        bond_equity = self.check_bond_equity_correlation()
        
        # Check USD impact
        usd_impact = self.check_usd_impact()
        
        if direction == 'LONG':
            # For longs, want risk-on regime
            if regime == 'RISK_OFF':
                return False
            
            # Don't want strong USD pressuring equities
            if usd_impact.get('impact') == 'negative':
                return False
            
            return True
        else:  # SHORT
            # For shorts, can work in risk-off or with USD pressure
            return True
