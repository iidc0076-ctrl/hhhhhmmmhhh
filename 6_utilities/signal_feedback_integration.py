"""
Signal Feedback Integration
Connects signal generation to the feedback automation system
"""

import asyncio
from typing import Dict, Optional
from datetime import datetime
from signal_feedback_system import (
    SignalFeedbackDatabase, 
    SignalExecutor, 
    SignalImprovementEngine,
    SignalExecution
)

class SignalFeedbackIntegration:
    """Integrates feedback system with signal generation"""
    
    def __init__(self):
        self.feedback_db = SignalFeedbackDatabase()
        self.executor = SignalExecutor(self.feedback_db)
        self.improvement_engine = SignalImprovementEngine(self.feedback_db)
    
    async def process_user_signal(self, user_id: int, pair: str, direction: str,
                                 expiry: str, entry_price: float, 
                                 entry_confidence: float, 
                                 analysis_summary: Dict) -> SignalExecution:
        """
        Process a user signal through the feedback system
        
        Args:
            user_id: Discord user ID
            pair: Trading pair (e.g., 'EUR/USD')
            direction: 'BUY' or 'SELL'
            expiry: Expiry time (e.g., '5m')
            entry_price: Entry price from signal
            entry_confidence: Signal confidence percentage
            analysis_summary: Dict with analysis details
        
        Returns:
            SignalExecution object
        """
        
        print(f"\n[Feedback Integration] Processing signal for user {user_id}")
        print(f"  Pair: {pair} | Direction: {direction} | Expiry: {expiry}")
        print(f"  Confidence: {entry_confidence:.1f}% | Entry: {entry_price}")
        
        # Execute signal and start monitoring
        execution = await self.executor.execute_signal(
            user_id=user_id,
            pair=pair,
            direction=direction,
            expiry=expiry,
            entry_price=entry_price,
            entry_confidence=entry_confidence,
            analysis_summary=analysis_summary
        )
        
        return execution
    
    async def get_signal_report(self, pair: Optional[str] = None, 
                               days: int = 7) -> Dict:
        """Get comprehensive signal feedback report"""
        
        win_rate_data = await self.feedback_db.get_win_rate(pair, days)
        suggestions = await self.improvement_engine.generate_improvement_suggestions(days)
        indicator_perf = await self.improvement_engine.get_indicator_performance(days)
        
        return {
            'win_rate': win_rate_data,
            'improvement_suggestions': suggestions,
            'indicator_performance': indicator_perf,
            'period_days': days
        }
    
    async def get_active_signals(self) -> Dict[str, SignalExecution]:
        """Get all currently active signals"""
        return self.executor.active_signals.copy()
    
    async def get_signal_history(self, pair: Optional[str] = None, 
                                days: int = 7) -> list:
        """Get signal execution history"""
        return await self.feedback_db.get_signal_history(pair, days)


# Global instance
feedback_integration = None

def get_signal_feedback_integration() -> SignalFeedbackIntegration:
    """Get or create feedback integration instance"""
    global feedback_integration
    if feedback_integration is None:
        feedback_integration = SignalFeedbackIntegration()
    return feedback_integration


async def log_signal_with_feedback(user_id: int, pair: str, direction: str,
                                   expiry: str, entry_price: float,
                                   entry_confidence: float,
                                   analysis_summary: Dict) -> Dict:
    """
    Convenient function to log a signal and start feedback monitoring
    
    Usage in main.py:
    from signal_feedback_integration import log_signal_with_feedback
    
    await log_signal_with_feedback(
        user_id=123456,
        pair='EUR/USD',
        direction='BUY',
        expiry='5m',
        entry_price=1.0890,
        entry_confidence=75.5,
        analysis_summary={
            'confluence_factors': 6,
            'ict_signal': 'BUY',
            'volume_confirmation': True,
            'trend': 'UPTREND'
        }
    )
    """
    
    integration = get_signal_feedback_integration()
    execution = await integration.process_user_signal(
        user_id=user_id,
        pair=pair,
        direction=direction,
        expiry=expiry,
        entry_price=entry_price,
        entry_confidence=entry_confidence,
        analysis_summary=analysis_summary
    )
    
    return {
        'signal_id': execution.signal_id,
        'status': 'monitoring',
        'message': f'Signal monitoring started for {pair} {direction}'
    }
