"""
Risk-On / Risk-Off Analyzer

Detailed analysis of risk sentiment and market conditions.
"""

from typing import Dict
from .macro_regime import MacroRegimeDetector


class RiskOnOffAnalyzer:
    """Analyzes risk-on vs risk-off conditions."""
    
    def __init__(self):
        """Initialize risk analyzer."""
        self.regime_detector = MacroRegimeDetector()
    
    def analyze_risk_indicators(self) -> Dict:
        """
        Analyze all risk indicators.
        
        Returns:
            Dictionary with detailed risk analysis
        """
        regime_data = self.regime_detector.detect_regime()
        
        indicators = regime_data.get('indicators', {})
        
        analysis = {
            'regime': regime_data.get('regime', 'NEUTRAL'),
            'risk_score': regime_data.get('risk_score', 0),
            'confidence': regime_data.get('confidence', 0),
            'indicators': {
                'vix': {
                    'value': indicators.get('vix', {}).get('value', 20),
                    'regime': indicators.get('vix', {}).get('regime', 'normal_volatility'),
                    'interpretation': self._interpret_vix(indicators.get('vix', {}))
                },
                'sentiment': {
                    'score': indicators.get('sentiment', {}).get('composite_score', 50),
                    'classification': indicators.get('sentiment', {}).get('classification', 'neutral'),
                    'interpretation': self._interpret_sentiment(indicators.get('sentiment', {}))
                },
                'bonds': {
                    'yield': indicators.get('bonds', {}).get('value', 0),
                    'change': indicators.get('bonds', {}).get('change', 0),
                    'interpretation': self._interpret_bonds(indicators.get('bonds', {}))
                },
                'usd': {
                    'strength': indicators.get('usd', {}).get('value', 100),
                    'change': indicators.get('usd', {}).get('change', 0),
                    'interpretation': self._interpret_usd(indicators.get('usd', {}))
                },
                'equity': {
                    'performance': indicators.get('equity', {}).get('change_pct', 0),
                    'interpretation': self._interpret_equity(indicators.get('equity', {}))
                }
            },
            'recommendations': self._generate_recommendations(regime_data)
        }
        
        return analysis
    
    def get_risk_score(self) -> float:
        """
        Get composite risk score.
        
        Returns:
            Risk score from -1 (risk-off) to +1 (risk-on)
        """
        regime_data = self.regime_detector.detect_regime()
        return regime_data.get('risk_score', 0)
    
    def is_risk_on(self) -> bool:
        """
        Check if market is in risk-on mode.
        
        Returns:
            True if risk-on, False otherwise
        """
        regime = self.regime_detector.get_regime_label()
        return regime == 'RISK_ON'
    
    def is_risk_off(self) -> bool:
        """
        Check if market is in risk-off mode.
        
        Returns:
            True if risk-off, False otherwise
        """
        regime = self.regime_detector.get_regime_label()
        return regime == 'RISK_OFF'
    
    def _interpret_vix(self, vix_data: Dict) -> str:
        """Interpret VIX level."""
        vix_value = vix_data.get('value', 20)
        if vix_value < 15:
            return "Low volatility - complacent market, risk-on environment"
        elif vix_value < 20:
            return "Normal volatility - stable market conditions"
        elif vix_value < 30:
            return "Elevated volatility - increased uncertainty"
        else:
            return "High volatility - fear-driven market, risk-off environment"
    
    def _interpret_sentiment(self, sentiment_data: Dict) -> str:
        """Interpret sentiment."""
        classification = sentiment_data.get('classification', 'neutral')
        score = sentiment_data.get('composite_score', 50)
        
        if classification == 'bullish' or score > 60:
            return "Positive sentiment - risk-on conditions"
        elif classification == 'bearish' or score < 40:
            return "Negative sentiment - risk-off conditions"
        else:
            return "Neutral sentiment - mixed signals"
    
    def _interpret_bonds(self, bond_data: Dict) -> str:
        """Interpret bond yields."""
        change = bond_data.get('change', 0)
        if change > 0:
            return "Rising yields - risk-on, growth expectations"
        elif change < 0:
            return "Falling yields - risk-off, flight to safety"
        else:
            return "Stable yields - neutral conditions"
    
    def _interpret_usd(self, usd_data: Dict) -> str:
        """Interpret USD strength."""
        change = usd_data.get('change', 0)
        if change > 0:
            return "Strong USD - can pressure equities, risk-off signal"
        elif change < 0:
            return "Weak USD - supports equities, risk-on signal"
        else:
            return "Stable USD - neutral impact"
    
    def _interpret_equity(self, equity_data: Dict) -> str:
        """Interpret equity performance."""
        change_pct = equity_data.get('change_pct', 0)
        if change_pct > 1:
            return "Strong equity performance - risk-on"
        elif change_pct < -1:
            return "Weak equity performance - risk-off"
        else:
            return "Neutral equity performance"
    
    def _generate_recommendations(self, regime_data: Dict) -> Dict:
        """Generate trading recommendations based on regime."""
        regime = regime_data.get('regime', 'NEUTRAL')
        risk_score = regime_data.get('risk_score', 0)
        
        recommendations = {
            'equity_longs': False,
            'equity_shorts': False,
            'defensive_assets': False,
            'risk_reduction': False,
            'message': ''
        }
        
        if regime == 'RISK_ON':
            recommendations['equity_longs'] = True
            recommendations['message'] = "Risk-on environment - favorable for equity longs"
        elif regime == 'RISK_OFF':
            recommendations['equity_shorts'] = True
            recommendations['defensive_assets'] = True
            recommendations['risk_reduction'] = True
            recommendations['message'] = "Risk-off environment - reduce risk, consider defensive positions"
        else:
            recommendations['message'] = "Neutral regime - selective trading, wait for clearer signals"
        
        return recommendations
