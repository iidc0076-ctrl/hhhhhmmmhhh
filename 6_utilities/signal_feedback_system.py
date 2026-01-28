"""
Signal Feedback Automation System
Executes user signals in real-time, monitors outcomes, and provides feedback for improvement
"""

import asyncio
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np

@dataclass
class SignalExecution:
    """Represents a signal execution event"""
    signal_id: str  # Unique identifier
    user_id: int
    pair: str
    direction: str  # BUY or SELL
    expiry: str  # e.g., '5m', '15m'
    entry_price: float
    entry_time: datetime
    entry_confidence: float
    analysis_summary: Dict  # Why signal was generated
    
    # Outcome fields (filled after execution)
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    outcome: Optional[str] = None  # 'WIN', 'LOSS', 'BREAKEVEN'
    pips_change: Optional[float] = None
    percent_change: Optional[float] = None
    time_to_outcome: Optional[int] = None  # seconds
    
    # Analysis fields
    root_cause: Optional[str] = None  # Why it won/lost
    confluence_at_exit: Optional[Dict] = None
    market_conditions_at_exit: Optional[Dict] = None
    signal_decay_detected: Optional[bool] = None
    

class SignalFeedbackDatabase:
    """Manages signal feedback data"""
    
    def __init__(self, db_path: str = 'signal_feedback.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize feedback database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_executions (
                signal_id TEXT PRIMARY KEY,
                user_id INTEGER,
                pair TEXT,
                direction TEXT,
                expiry TEXT,
                entry_price REAL,
                entry_time DATETIME,
                entry_confidence REAL,
                exit_price REAL,
                exit_time DATETIME,
                outcome TEXT,
                pips_change REAL,
                percent_change REAL,
                time_to_outcome INTEGER,
                root_cause TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_analysis (
                signal_id TEXT PRIMARY KEY,
                analysis_summary TEXT,  -- JSON
                confluence_at_exit TEXT,  -- JSON
                market_conditions TEXT,  -- JSON
                signal_decay BOOLEAN,
                FOREIGN KEY(signal_id) REFERENCES signal_executions(signal_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT,
                metric_name TEXT,
                metric_value REAL,
                indicator_name TEXT,
                performance_contribution REAL,  -- How much this contributed to outcome
                FOREIGN KEY(signal_id) REFERENCES signal_executions(signal_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS improvement_suggestions (
                suggestion_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                category TEXT,  -- e.g., 'confidence_threshold', 'indicator_weight', 'timing'
                description TEXT,
                affected_pairs TEXT,  -- JSON list
                expected_impact TEXT,  -- 'HIGH', 'MEDIUM', 'LOW'
                implementation TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def save_signal_execution(self, execution: SignalExecution) -> bool:
        """Save signal execution to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO signal_executions
                (signal_id, user_id, pair, direction, expiry, entry_price, entry_time, 
                 entry_confidence, exit_price, exit_time, outcome, pips_change, 
                 percent_change, time_to_outcome, root_cause)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                execution.signal_id,
                execution.user_id,
                execution.pair,
                execution.direction,
                execution.expiry,
                execution.entry_price,
                execution.entry_time.isoformat(),
                execution.entry_confidence,
                execution.exit_price,
                execution.exit_time.isoformat() if execution.exit_time else None,
                execution.outcome,
                execution.pips_change,
                execution.percent_change,
                execution.time_to_outcome,
                execution.root_cause
            ))
            
            # Save detailed analysis
            cursor.execute('''
                INSERT OR REPLACE INTO signal_analysis
                (signal_id, analysis_summary, confluence_at_exit, market_conditions, signal_decay)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                execution.signal_id,
                json.dumps(execution.analysis_summary),
                json.dumps(execution.confluence_at_exit or {}),
                json.dumps(execution.market_conditions_at_exit or {}),
                execution.signal_decay_detected
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[Feedback DB] Error saving execution: {e}")
            return False
    
    async def get_signal_history(self, pair: Optional[str] = None, 
                                days: int = 7) -> List[Dict]:
        """Get signal execution history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            if pair:
                cursor.execute('''
                    SELECT * FROM signal_executions 
                    WHERE pair = ? AND created_at > ?
                    ORDER BY created_at DESC
                ''', (pair, cutoff_date))
            else:
                cursor.execute('''
                    SELECT * FROM signal_executions 
                    WHERE created_at > ?
                    ORDER BY created_at DESC
                ''', (cutoff_date,))
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            print(f"[Feedback DB] Error retrieving history: {e}")
            return []
    
    async def get_win_rate(self, pair: Optional[str] = None, 
                          days: int = 7) -> Dict:
        """Calculate win rate and statistics"""
        try:
            history = await self.get_signal_history(pair, days)
            
            if not history:
                return {'total': 0, 'wins': 0, 'losses': 0, 'win_rate': 0}
            
            outcomes = [h['outcome'] for h in history if h['outcome']]
            
            total = len(outcomes)
            wins = outcomes.count('WIN')
            losses = outcomes.count('LOSS')
            
            return {
                'total': total,
                'wins': wins,
                'losses': losses,
                'breakeven': outcomes.count('BREAKEVEN'),
                'win_rate': (wins / total * 100) if total > 0 else 0,
                'avg_pips': np.mean([h['pips_change'] for h in history if h['pips_change']]),
                'avg_percent': np.mean([h['percent_change'] for h in history if h['percent_change']])
            }
        except Exception as e:
            print(f"[Feedback DB] Error calculating win rate: {e}")
            return {}


class SignalExecutor:
    """Executes signals and monitors outcomes in real-time"""
    
    def __init__(self, feedback_db: SignalFeedbackDatabase):
        self.feedback_db = feedback_db
        self.active_signals: Dict[str, SignalExecution] = {}
    
    async def execute_signal(self, user_id: int, pair: str, direction: str, 
                            expiry: str, entry_price: float, entry_confidence: float,
                            analysis_summary: Dict) -> SignalExecution:
        """Create and track a signal execution"""
        
        signal_id = f"{pair}_{direction}_{datetime.now().isoformat()}"
        
        execution = SignalExecution(
            signal_id=signal_id,
            user_id=user_id,
            pair=pair,
            direction=direction,
            expiry=expiry,
            entry_price=entry_price,
            entry_time=datetime.now(),
            entry_confidence=entry_confidence,
            analysis_summary=analysis_summary
        )
        
        self.active_signals[signal_id] = execution
        print(f"[Signal Executor] Signal {signal_id} created - {pair} {direction} @ {entry_price}")
        
        # Start monitoring in background
        asyncio.create_task(self._monitor_signal(signal_id, expiry))
        
        return execution
    
    async def _monitor_signal(self, signal_id: str, expiry: str):
        """Monitor signal in real-time using Twelve Data"""
        
        if signal_id not in self.active_signals:
            return
        
        execution = self.active_signals[signal_id]
        
        # Convert expiry to seconds
        expiry_seconds = self._expiry_to_seconds(expiry)
        
        try:
            from stealth_api_client import TwelveDataClient
            client = TwelveDataClient()
            
            monitoring_start = datetime.now()
            
            while True:
                elapsed = (datetime.now() - monitoring_start).total_seconds()
                
                if elapsed >= expiry_seconds:
                    # Signal expired - get final price
                    current_price = await client.get_price(execution.pair)
                    await self._close_signal(signal_id, current_price)
                    break
                
                # Check for early exit conditions (TP/SL)
                current_price = await client.get_price(execution.pair)
                outcome = self._evaluate_outcome(execution, current_price)
                
                if outcome != 'PENDING':
                    await self._close_signal(signal_id, current_price)
                    break
                
                # Monitor every 10 seconds
                await asyncio.sleep(10)
        
        except Exception as e:
            print(f"[Signal Monitor] Error monitoring {signal_id}: {e}")
    
    async def _close_signal(self, signal_id: str, exit_price: float):
        """Close signal and analyze outcome"""
        
        if signal_id not in self.active_signals:
            return
        
        execution = self.active_signals[signal_id]
        execution.exit_price = exit_price
        execution.exit_time = datetime.now()
        
        # Calculate P&L
        execution.pips_change = (exit_price - execution.entry_price) * 10000
        execution.percent_change = (exit_price - execution.entry_price) / execution.entry_price * 100
        execution.time_to_outcome = int((execution.exit_time - execution.entry_time).total_seconds())
        
        # Determine outcome
        if execution.direction == 'BUY':
            if execution.percent_change > 0.05:  # 5 pips for most pairs
                execution.outcome = 'WIN'
            elif execution.percent_change < -0.05:
                execution.outcome = 'LOSS'
            else:
                execution.outcome = 'BREAKEVEN'
        else:  # SELL
            if execution.percent_change < -0.05:
                execution.outcome = 'WIN'
            elif execution.percent_change > 0.05:
                execution.outcome = 'LOSS'
            else:
                execution.outcome = 'BREAKEVEN'
        
        # Analyze root cause
        await self._analyze_outcome(execution)
        
        # Save to database
        await self.feedback_db.save_signal_execution(execution)
        
        # Remove from active signals
        del self.active_signals[signal_id]
        
        print(f"[Signal Executor] Signal {signal_id} closed - Outcome: {execution.outcome}")
    
    async def _analyze_outcome(self, execution: SignalExecution):
        """Analyze why signal succeeded or failed"""
        
        try:
            from stealth_api_client import TwelveDataClient
            client = TwelveDataClient()
            
            # Fetch data around exit time
            df = await client.fetch_data(
                execution.pair, 
                '5min',
                candles=20
            )
            
            if df.empty:
                return
            
            # Analyze market conditions at exit
            execution.market_conditions_at_exit = {
                'volatility': float(df['high'].tail(14).max() - df['low'].tail(14).min()),
                'volume': float(df['volume'].tail(5).mean()),
                'trend': 'UPTREND' if df['close'].iloc[-1] > df['close'].iloc[-20] else 'DOWNTREND',
                'rsi': float(self._calculate_rsi(df['close'].values)[-1]) if len(df) > 14 else 50
            }
            
            # Determine root cause
            if execution.outcome == 'WIN':
                execution.root_cause = self._analyze_win(execution)
            else:
                execution.root_cause = self._analyze_loss(execution)
        
        except Exception as e:
            execution.root_cause = f"Analysis failed: {str(e)}"
    
    def _analyze_win(self, execution: SignalExecution) -> str:
        """Analyze why signal won"""
        
        conditions = execution.market_conditions_at_exit or {}
        analysis = execution.analysis_summary or {}
        
        reasons = []
        
        # Check confluence alignment
        if analysis.get('confluence_factors', 0) > 5:
            reasons.append(f"Strong confluence ({analysis.get('confluence_factors', 0)} factors)")
        
        # Check trend alignment
        trend = conditions.get('trend', '')
        direction_correct = (execution.direction == 'BUY' and trend == 'UPTREND') or \
                           (execution.direction == 'SELL' and trend == 'DOWNTREND')
        if direction_correct:
            reasons.append("Signal aligned with market trend")
        
        # Check volatility
        volatility = conditions.get('volatility', 0)
        if volatility < 0.05:
            reasons.append("Low volatility enabled clean execution")
        
        if not reasons:
            reasons.append("Signal matched market direction")
        
        return " | ".join(reasons)
    
    def _analyze_loss(self, execution: SignalExecution) -> str:
        """Analyze why signal failed"""
        
        conditions = execution.market_conditions_at_exit or {}
        analysis = execution.analysis_summary or {}
        
        reasons = []
        
        # Check for whipsaw
        if execution.time_to_outcome < 120:  # Quick reversal
            reasons.append("Quick whipsaw/reversal")
        
        # Check trend alignment
        trend = conditions.get('trend', '')
        direction_wrong = (execution.direction == 'BUY' and trend == 'DOWNTREND') or \
                         (execution.direction == 'SELL' and trend == 'UPTREND')
        if direction_wrong:
            reasons.append("Signal against market trend")
        
        # Check for low confluence
        if analysis.get('confluence_factors', 0) < 3:
            reasons.append(f"Low confluence ({analysis.get('confluence_factors', 0)} factors)")
        
        # Check high volatility
        volatility = conditions.get('volatility', 0)
        if volatility > 0.1:
            reasons.append("High volatility caused false break")
        
        # Signal decay
        if execution.signal_decay_detected:
            reasons.append("Signal decay detected")
        
        if not reasons:
            reasons.append("Market moved against signal direction")
        
        return " | ".join(reasons)
    
    def _evaluate_outcome(self, execution: SignalExecution, 
                         current_price: float) -> str:
        """Evaluate if signal has outcome (WIN/LOSS/PENDING)"""
        
        price_change = current_price - execution.entry_price
        
        if execution.direction == 'BUY':
            if price_change >= 0.0005:  # TP: 5 pips
                return 'WIN'
            elif price_change <= -0.0005:  # SL: 5 pips
                return 'LOSS'
        else:  # SELL
            if price_change <= -0.0005:
                return 'WIN'
            elif price_change >= 0.0005:
                return 'LOSS'
        
        return 'PENDING'
    
    @staticmethod
    def _expiry_to_seconds(expiry: str) -> int:
        """Convert expiry string to seconds"""
        mapping = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '30m': 1800,
            '1h': 3600,
            '4h': 14400,
            '1d': 86400
        }
        return mapping.get(expiry, 300)
    
    @staticmethod
    def _calculate_rsi(prices, period=14):
        """Calculate RSI"""
        if len(prices) < period:
            return np.array([50] * len(prices))
        
        delta = np.diff(prices)
        seed = delta[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / (down + 1e-10)
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100. / (1. + rs)
        
        for i in range(period, len(prices)):
            delta_val = prices[i] - prices[i-1]
            up = (up * (period - 1) + (delta_val if delta_val > 0 else 0)) / period
            down = (down * (period - 1) + (-delta_val if delta_val < 0 else 0)) / period
            rs = up / (down + 1e-10)
            rsi[i] = 100. - 100. / (1. + rs)
        
        return rsi


class SignalImprovementEngine:
    """Analyzes feedback data to identify improvements"""
    
    def __init__(self, feedback_db: SignalFeedbackDatabase):
        self.feedback_db = feedback_db
    
    async def generate_improvement_suggestions(self, days: int = 7) -> List[Dict]:
        """Analyze signal data and generate improvement suggestions"""
        
        suggestions = []
        
        # Get recent signal history
        history = await self.feedback_db.get_signal_history(days=days)
        
        if not history:
            return suggestions
        
        # Analyze by pair
        pair_performance = {}
        for signal in history:
            pair = signal['pair']
            if pair not in pair_performance:
                pair_performance[pair] = {'wins': 0, 'losses': 0, 'low_conf': 0}
            
            if signal['outcome'] == 'WIN':
                pair_performance[pair]['wins'] += 1
            elif signal['outcome'] == 'LOSS':
                pair_performance[pair]['losses'] += 1
            
            if signal['entry_confidence'] < 65:
                pair_performance[pair]['low_conf'] += 1
        
        # Generate suggestions for underperforming pairs
        for pair, stats in pair_performance.items():
            total = stats['wins'] + stats['losses']
            if total < 5:
                continue
            
            win_rate = stats['wins'] / total * 100
            
            if win_rate < 45:
                suggestions.append({
                    'category': 'pair_exclusion',
                    'description': f'{pair} has {win_rate:.1f}% win rate - consider excluding',
                    'affected_pairs': [pair],
                    'expected_impact': 'HIGH',
                    'implementation': f'Add {pair} to exclusion list'
                })
            
            if stats['low_conf'] > total * 0.3:
                suggestions.append({
                    'category': 'confidence_threshold',
                    'description': f'{pair} signals with <65% confidence too often',
                    'affected_pairs': [pair],
                    'expected_impact': 'MEDIUM',
                    'implementation': f'Increase minimum confidence for {pair} to 70%'
                })
        
        return suggestions
    
    async def get_indicator_performance(self, days: int = 7) -> Dict:
        """Analyze which indicators contribute most to wins/losses"""
        
        history = await self.feedback_db.get_signal_history(days=days)
        
        indicator_stats = {}
        
        for signal in history:
            analysis = signal.get('analysis_summary', {})
            
            for indicator, value in analysis.items():
                if indicator not in indicator_stats:
                    indicator_stats[indicator] = {'wins': 0, 'losses': 0}
                
                if signal['outcome'] == 'WIN':
                    indicator_stats[indicator]['wins'] += 1
                else:
                    indicator_stats[indicator]['losses'] += 1
        
        return indicator_stats
