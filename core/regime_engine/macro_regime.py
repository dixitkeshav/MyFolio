"""
Macro Regime Detector

Detects current market regime (risk-on vs risk-off) based on multiple indicators.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Optional
from core.data_engine.sentiment_data import SentimentAnalyzer


class MacroRegimeDetector:
    """Detects macro market regime."""
    
    def __init__(self):
        """Initialize regime detector."""
        self.sentiment_analyzer = SentimentAnalyzer()
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
    
    def detect_regime(self) -> Dict:
        """
        Detect current macro regime.
        
        Returns:
            Dictionary with regime classification and confidence
        """
        try:
            # Get all indicators
            vix_data = self.sentiment_analyzer.get_vix_level()
            sentiment_data = self.sentiment_analyzer.get_composite_sentiment()
            
            # Get bond yields (10Y Treasury)
            bond_data = self._get_bond_yields()
            
            # Get USD strength (DXY)
            usd_data = self._get_usd_strength()
            
            # Get equity performance (SPY)
            equity_data = self._get_equity_performance()
            
            # Calculate risk score
            risk_score = self.calculate_risk_score(
                vix_data, sentiment_data, bond_data, usd_data, equity_data
            )
            
            # Classify regime
            regime_label = self._classify_regime(risk_score)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                vix_data, sentiment_data, bond_data, usd_data, equity_data
            )
            
            return {
                'regime': regime_label,
                'risk_score': risk_score,
                'confidence': confidence,
                'indicators': {
                    'vix': vix_data,
                    'sentiment': sentiment_data,
                    'bonds': bond_data,
                    'usd': usd_data,
                    'equity': equity_data
                },
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error detecting regime: {e}")
            return {
                'regime': 'NEUTRAL',
                'risk_score': 0,
                'confidence': 0,
                'error': str(e)
            }
    
    def calculate_risk_score(
        self,
        vix_data: Dict,
        sentiment_data: Dict,
        bond_data: Dict,
        usd_data: Dict,
        equity_data: Dict
    ) -> float:
        """
        Calculate composite risk score (-1 to +1).
        
        Args:
            vix_data: VIX data
            sentiment_data: Sentiment data
            bond_data: Bond yield data
            usd_data: USD strength data
            equity_data: Equity performance data
            
        Returns:
            Risk score from -1 (risk-off) to +1 (risk-on)
        """
        scores = []
        
        # VIX component (lower VIX = more risk-on)
        vix_value = vix_data.get('value', 20)
        vix_score = (30 - vix_value) / 30  # Normalize to -1 to +1
        scores.append(vix_score * 0.25)
        
        # Sentiment component
        sentiment_score = sentiment_data.get('composite_score', 50)
        sentiment_normalized = (sentiment_score - 50) / 50  # Normalize to -1 to +1
        scores.append(sentiment_normalized * 0.25)
        
        # Bond component (rising yields = risk-on, falling yields = risk-off)
        bond_change = bond_data.get('change', 0)
        bond_score = np.tanh(bond_change * 10)  # Normalize bond change
        scores.append(bond_score * 0.20)
        
        # USD component (strong USD can pressure equities)
        usd_change = usd_data.get('change', 0)
        usd_score = -np.tanh(usd_change * 5)  # Invert: strong USD = risk-off
        scores.append(usd_score * 0.15)
        
        # Equity performance component
        equity_change = equity_data.get('change_pct', 0)
        equity_score = np.tanh(equity_change * 20)  # Normalize equity change
        scores.append(equity_score * 0.15)
        
        # Composite score
        risk_score = sum(scores)
        
        # Clamp to -1 to +1
        risk_score = max(-1, min(1, risk_score))
        
        return risk_score
    
    def _classify_regime(self, risk_score: float) -> str:
        """
        Classify regime based on risk score.
        
        Args:
            risk_score: Risk score from -1 to +1
            
        Returns:
            Regime label: 'RISK_ON', 'RISK_OFF', or 'NEUTRAL'
        """
        if risk_score > 0.3:
            return 'RISK_ON'
        elif risk_score < -0.3:
            return 'RISK_OFF'
        else:
            return 'NEUTRAL'
    
    def _calculate_confidence(
        self,
        vix_data: Dict,
        sentiment_data: Dict,
        bond_data: Dict,
        usd_data: Dict,
        equity_data: Dict
    ) -> float:
        """
        Calculate confidence level (0 to 1) in regime classification.
        
        Returns:
            Confidence score from 0 to 1
        """
        # Check if indicators agree
        agreements = 0
        total = 0
        
        # VIX and sentiment should agree
        vix_regime = 'RISK_ON' if vix_data.get('value', 20) < 20 else 'RISK_OFF'
        sentiment_regime = sentiment_data.get('classification', 'neutral')
        sentiment_regime = 'RISK_ON' if sentiment_regime == 'bullish' else 'RISK_OFF'
        
        if vix_regime == sentiment_regime:
            agreements += 1
        total += 1
        
        # Higher confidence if more indicators agree
        confidence = agreements / total if total > 0 else 0.5
        
        # Boost confidence if risk score is extreme
        risk_score = self.calculate_risk_score(
            vix_data, sentiment_data, bond_data, usd_data, equity_data
        )
        if abs(risk_score) > 0.7:
            confidence = min(1.0, confidence + 0.2)
        
        return confidence
    
    def _get_bond_yields(self) -> Dict:
        """Get 10Y Treasury yield data."""
        try:
            # Use ^TNX for 10Y Treasury yield
            bond = yf.Ticker("^TNX")
            data = bond.history(period="5d")
            
            if data.empty:
                return {'value': 0, 'change': 0}
            
            current = float(data['Close'].iloc[-1])
            previous = float(data['Close'].iloc[-2]) if len(data) > 1 else current
            
            return {
                'value': current,
                'change': current - previous,
                'change_pct': ((current - previous) / previous * 100) if previous > 0 else 0
            }
        except Exception as e:
            print(f"Error fetching bond yields: {e}")
            return {'value': 0, 'change': 0}
    
    def _get_usd_strength(self) -> Dict:
        """Get USD strength (DXY index)."""
        try:
            dxy = yf.Ticker("DX-Y.NYB")  # DXY index
            data = dxy.history(period="5d")
            
            if data.empty:
                return {'value': 100, 'change': 0}
            
            current = float(data['Close'].iloc[-1])
            previous = float(data['Close'].iloc[-2]) if len(data) > 1 else current
            
            return {
                'value': current,
                'change': current - previous,
                'change_pct': ((current - previous) / previous * 100) if previous > 0 else 0
            }
        except Exception as e:
            print(f"Error fetching USD strength: {e}")
            return {'value': 100, 'change': 0}
    
    def _get_equity_performance(self) -> Dict:
        """Get equity performance (SPY)."""
        try:
            spy = yf.Ticker("SPY")
            data = spy.history(period="5d")
            
            if data.empty:
                return {'value': 0, 'change': 0}
            
            current = float(data['Close'].iloc[-1])
            previous = float(data['Close'].iloc[-2]) if len(data) > 1 else current
            
            return {
                'value': current,
                'change': current - previous,
                'change_pct': ((current - previous) / previous * 100) if previous > 0 else 0
            }
        except Exception as e:
            print(f"Error fetching equity performance: {e}")
            return {'value': 0, 'change': 0}
    
    def get_regime_label(self) -> str:
        """
        Get current regime label.
        
        Returns:
            Regime label: 'RISK_ON', 'RISK_OFF', or 'NEUTRAL'
        """
        regime_data = self.detect_regime()
        return regime_data.get('regime', 'NEUTRAL')
    
    def get_regime_confidence(self) -> float:
        """
        Get confidence level in regime classification.
        
        Returns:
            Confidence score from 0 to 1
        """
        regime_data = self.detect_regime()
        return regime_data.get('confidence', 0.5)
