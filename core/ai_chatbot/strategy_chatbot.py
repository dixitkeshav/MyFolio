"""
Strategy Chatbot

AI-powered chatbot for strategy generation and backtesting.
Uses Google Gemini when GEMINI_API_KEY is set; otherwise rule-based generation.
"""

import os
import re
from typing import Dict, Optional
from dotenv import load_dotenv
from core.execution_engine.backtester import Backtester
from core.data_engine.market_data import MarketDataFetcher

load_dotenv()


class StrategyChatbot:
    """AI chatbot for strategy generation and backtesting (Gemini or rule-based)."""

    def __init__(self):
        """Initialize strategy chatbot. Uses GEMINI_API_KEY for Gemini."""
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.backtester = Backtester()
        self.data_fetcher = MarketDataFetcher()
        
        # Strategy template: backtest uses only technical + risk so user's condition (e.g. RSI < 30) can produce trades
        # Use {{ and }} for literal braces so .format() only replaces {entry_logic} and {exit_logic}
        self.strategy_template = """
from core.strategy_engine.base_strategy import BaseStrategy
from core.strategy_engine.technical import TechnicalAnalyzer
import pandas as pd

class GeneratedStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="Generated Strategy", require_all_layers=False)
        self.technical_analyzer = TechnicalAnalyzer()
    
    def check_technical_entry(self, df: pd.DataFrame) -> dict:
        {entry_logic}
    
    def should_enter(self, symbol: str, df: pd.DataFrame, direction: str, required_regime=None):
        # Backtest: only technical + risk (so RSI/EMA condition alone can generate trades)
        technical_signal = self.check_technical_entry(df)
        if not technical_signal.get('signal', False):
            return {{'enter': False, 'position_size': 0, 'checks': {{}}, 'reasons': ['Technical not met'], 'technical_signal': technical_signal}}
        account_value = self.exposure_manager.get_account_value()
        res = self.position_sizer.calculate_position_size(account_value, 0.01, 0.05)
        position_size_dollars = res.get('position_size', 0) if isinstance(res, dict) else float(res or 0)
        if not self.check_risk_rules(symbol, position_size_dollars):
            return {{'enter': False, 'position_size': 0, 'checks': {{'technical': True, 'risk': False}}, 'reasons': ['Risk rules'], 'technical_signal': technical_signal}}
        return {{'enter': True, 'position_size': position_size_dollars, 'checks': {{'technical': True, 'risk': True}}, 'reasons': [], 'technical_signal': technical_signal}}
    
    def should_exit(self, symbol: str, df: pd.DataFrame, position: dict) -> dict:
        {exit_logic}
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.technical_analyzer.generate_entry_signals(df)
"""
    
    def process_user_query(self, query: str) -> Dict:
        """
        Process user query and generate/backtest strategy.
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary with response and results
        """
        # Parse query to determine action
        if 'backtest' in query.lower() or 'test' in query.lower():
            # Extract strategy description and parameters
            strategy_desc = self._extract_strategy_description(query)
            symbol = self._extract_symbol(query) or 'SPY'
            start_date = self._extract_date(query, 'start') or '2023-01-01'
            end_date = self._extract_date(query, 'end') or '2024-01-01'
            
            # Generate strategy code
            strategy_code = self.generate_strategy_code(strategy_desc)
            
            # Backtest strategy
            backtest_results = self.backtest_strategy(strategy_code, symbol, start_date, end_date)
            
            return {
                'action': 'backtest',
                'strategy_code': strategy_code,
                'backtest_results': backtest_results,
                'explanation': self.explain_strategy(strategy_code)
            }
        else:
            # Just generate strategy
            strategy_desc = query
            strategy_code = self.generate_strategy_code(strategy_desc)
            
            return {
                'action': 'generate',
                'strategy_code': strategy_code,
                'explanation': self.explain_strategy(strategy_code)
            }
    
    def generate_strategy_code(self, prompt: str) -> str:
        """
        Generate strategy code from natural language prompt.
        Uses Gemini when GEMINI_API_KEY is set; else rule-based.
        """
        if self.gemini_key:
            code = self._generate_strategy_code_gemini(prompt)
            if code:
                return code
        entry_logic = self._generate_entry_logic(prompt)
        exit_logic = self._generate_exit_logic(prompt)
        return self.strategy_template.format(
            entry_logic=entry_logic,
            exit_logic=exit_logic,
        )
    
    def _generate_entry_logic(self, prompt: str) -> str:
        """Generate entry logic from prompt."""
        prompt_lower = prompt.lower()
        
        # Detect indicators mentioned
        if 'rsi' in prompt_lower:
            if ('oversold' in prompt_lower or 'below 30' in prompt_lower or
                'less than 30' in prompt_lower or 'under 30' in prompt_lower or
                '< 30' in prompt_lower or 'rsi 30' in prompt_lower):
                return """
        if len(df) < 14:
            return {'signal': False, 'reason': 'Insufficient data'}
        
        rsi = self.technical_analyzer.calculate_rsi(df)
        current_price = df['close'].iloc[-1]
        
        if rsi.iloc[-1] < 30:
            return {
                'signal': True,
                'direction': 'LONG',
                'entry_price': current_price,
                'stop_loss': current_price * 0.95,
                'take_profit': current_price * 1.10
            }
        return {'signal': False, 'reason': 'RSI not oversold'}
"""
            elif 'overbought' in prompt_lower or 'above 70' in prompt_lower or '> 70' in prompt_lower:
                return """
        if len(df) < 14:
            return {'signal': False, 'reason': 'Insufficient data'}
        
        rsi = self.technical_analyzer.calculate_rsi(df)
        current_price = df['close'].iloc[-1]
        
        if rsi.iloc[-1] > 70:
            return {
                'signal': True,
                'direction': 'SHORT',
                'entry_price': current_price,
                'stop_loss': current_price * 1.05,
                'take_profit': current_price * 0.90
            }
        return {'signal': False, 'reason': 'RSI not overbought'}
"""
        
        # Default: EMA crossover
        return """
        if len(df) < 200:
            return {'signal': False, 'reason': 'Insufficient data'}
        
        ema_50 = self.technical_analyzer.calculate_ema(df, 50)
        ema_200 = self.technical_analyzer.calculate_ema(df, 200)
        current_price = df['close'].iloc[-1]
        
        if current_price > ema_50.iloc[-1] and ema_50.iloc[-1] > ema_200.iloc[-1]:
            return {
                'signal': True,
                'direction': 'LONG',
                'entry_price': current_price,
                'stop_loss': ema_50.iloc[-1] * 0.95,
                'take_profit': current_price * 1.10
            }
        return {'signal': False, 'reason': 'No signal'}
"""
    
    def _generate_exit_logic(self, prompt: str) -> str:
        """Generate exit logic from prompt."""
        return """
        exit_signal = self.technical_analyzer.generate_exit_signals(df, position)
        return exit_signal
"""
    
    def backtest_strategy(
        self,
        strategy_code: str,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Backtest a strategy from code.
        
        Args:
            strategy_code: Strategy Python code
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            
        Returns:
            Backtest results dictionary
        """
        try:
            # Execute strategy code to create strategy class
            namespace = {}
            exec(strategy_code, namespace)
            
            # Get the strategy class
            StrategyClass = namespace.get('GeneratedStrategy')
            if not StrategyClass:
                return {'error': 'Could not find GeneratedStrategy class'}
            
            # Create strategy instance
            strategy = StrategyClass()
            
            # Run backtest
            results = self.backtester.run_backtest(
                strategy=strategy,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )
            
            return results
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_strategy_code_gemini(self, prompt: str) -> Optional[str]:
        """Generate strategy code using Google Gemini. Returns None on failure."""
        if not self.gemini_key:
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash-002")
            system = (
                "You are a Python trading strategy coder. Output ONLY valid Python code for a class named GeneratedStrategy "
                "that inherits from BaseStrategy. It must have: check_technical_entry(df) returning a dict with 'signal' (bool), "
                "'direction' ('LONG' or 'SHORT'), 'entry_price', 'stop_loss', 'take_profit'; should_exit(symbol, df, position) "
                "returning a dict with 'exit' (bool); generate_signals(df). Use self.technical_analyzer (TechnicalAnalyzer) for "
                "calculate_rsi, calculate_ema, generate_exit_signals. Imports: from core.strategy_engine.base_strategy import BaseStrategy; "
                "from core.strategy_engine.technical import TechnicalAnalyzer; import pandas as pd. No markdown, no explanation, only code."
            )
            response = model.generate_content(f"{system}\n\nUser request: {prompt}")
            if response and response.text:
                text = response.text.strip()
                if "```python" in text:
                    text = text.split("```python")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                if "class GeneratedStrategy" in text:
                    return text
        except Exception as e:
            print(f"Gemini strategy generation failed: {e}")
        return None

    def explain_strategy(self, strategy_code: str) -> str:
        """
        Explain strategy logic. Uses Gemini when GEMINI_API_KEY is set; else rule-based.
        """
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash-002")
                response = model.generate_content(
                    "Explain this trading strategy code in 3-5 short bullet points. "
                    "Focus on entry conditions, exit conditions, and risk. Be concise.\n\n" + strategy_code[:4000]
                )
                if response and response.text:
                    return "Strategy Explanation:\n\n" + response.text.strip()
            except Exception as e:
                print(f"Gemini explain failed: {e}")
        explanation = "Strategy Explanation:\n\n"
        if "rsi" in strategy_code.lower():
            if "rsi.iloc[-1] < 30" in strategy_code:
                explanation += "- Entry: Buy when RSI is below 30 (oversold)\n"
            elif "rsi.iloc[-1] > 70" in strategy_code:
                explanation += "- Entry: Sell when RSI is above 70 (overbought)\n"
        if "ema" in strategy_code.lower():
            explanation += "- Uses EMA (Exponential Moving Average) for trend detection\n"
        explanation += "- Exit: Based on technical exit signals\n"
        explanation += "- Risk Management: Stop loss and take profit levels set"
        return explanation
    
    def _extract_symbol(self, query: str) -> Optional[str]:
        """Extract stock symbol from query. Maps NIFTY/SENSEX to Yahoo symbols."""
        q = query.upper()
        # Indian indices (Yahoo Finance symbols)
        if 'NIFTY' in q or 'NSEI' in q:
            return '^NSEI'  # Nifty 50
        if 'BANK NIFTY' in q or 'BANKNIFTY' in q:
            return '^NSEBANK'
        if 'SENSEX' in q or 'BSESN' in q:
            return '^BSESN'
        # US symbols
        for symbol in ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'DIA']:
            if symbol in q:
                return symbol
        return None
    
    def _extract_date(self, query: str, date_type: str) -> Optional[str]:
        """Extract date from query."""
        # Simple date extraction (can be enhanced)
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        dates = re.findall(date_pattern, query)
        if dates:
            return dates[0] if date_type == 'start' else dates[-1]
        return None
    
    def _extract_strategy_description(self, query: str) -> str:
        """Extract strategy description from query."""
        # Remove backtest-related keywords
        keywords_to_remove = ['backtest', 'test', 'run', 'on', 'from', 'to', 'between']
        words = query.split()
        filtered = [w for w in words if w.lower() not in keywords_to_remove]
        return ' '.join(filtered)
