"""
QuantVision Trade Manager 0V
Advanced Binary Options Trading Management System

This system provides sophisticated money management for binary options trading,
calculating precise trade amounts to reach profit targets even with losses.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import math
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeManagerSystem:
    """
    QuantVision Trade Manager 0V - Advanced Binary Options Money Management
    
    Core Features:
    - Dynamic session calculation based on capital and gain target
    - Precise trade amount calculation with loss recovery
    - Multi-win target support for low win rate strategies
    - Mathematical position sizing for consistent profitability
    """
    
    def __init__(self, db_path: str = "trade_manager.db"):
        self.db_path = db_path
        self._init_database()
        self.active_sessions = {}
        logger.info("TradeManagerSystem initialized")
    
    def _init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id TEXT PRIMARY KEY,
                capital REAL NOT NULL,
                total_trades INTEGER NOT NULL,
                win_trades_wanted INTEGER NOT NULL,
                payout_percentage REAL NOT NULL,
                gain_target_value REAL NOT NULL,
                gain_target_type TEXT NOT NULL,
                sessions_required INTEGER NOT NULL,
                session_profit_target REAL NOT NULL,
                trading_mode TEXT DEFAULT 'balanced',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trading sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_number INTEGER NOT NULL,
                capital REAL NOT NULL,
                profit_target REAL NOT NULL,
                total_trades INTEGER NOT NULL,
                win_trades_wanted INTEGER NOT NULL,
                payout_percentage REAL NOT NULL,
                current_trade INTEGER DEFAULT 0,
                current_pl REAL DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                is_completed BOOLEAN DEFAULT FALSE,
                session_result TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES user_settings (user_id)
            )
        ''')
        
        # Individual trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                trade_number INTEGER NOT NULL,
                trade_amount REAL NOT NULL,
                trade_result TEXT NOT NULL,
                profit_loss REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES trading_sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def calculate_session_requirements(self, capital: float, gain_target_value: float, 
                                     gain_target_type: str, total_trades: int = 10, win_trades_wanted: int = 1, 
                                     payout_percentage: float = 92.0) -> Tuple[int, float]:
        """
        Enhanced session requirements calculation with improved multiple-win logic
        Higher win requirements allow for larger session targets (fewer sessions)
        
        Args:
            capital: Initial capital amount
            gain_target_value: Target gain value
            gain_target_type: 'percent' or 'dollar'
            total_trades: Total trades per session (max 20)
            win_trades_wanted: Win trades target (max half of total trades)
            
        Returns:
            Tuple of (sessions_required, session_profit_target)
        """
        if gain_target_type == 'percent':
            total_profit_target = capital * (gain_target_value / 100)
        else:
            total_profit_target = gain_target_value
        
        payout_rate = payout_percentage / 100.0
        win_rate = win_trades_wanted / total_trades
        
        # DYNAMIC SESSION TARGET OPTIMIZATION
        # Test different session target percentages to find the highest safe one
        session_target = self._find_optimal_session_target(
            capital, total_profit_target, total_trades, win_trades_wanted, payout_rate
        )
        
        sessions_required = math.ceil(total_profit_target / session_target)
        
        logger.info(f"Enhanced calculation: {sessions_required} sessions with ${session_target:.2f} target each")
        logger.info(f"Win strategy: {win_trades_wanted}/{total_trades} ({win_rate:.1%} win rate)")
        
        # Calculate max trade amount for logging purposes
        max_trade_amount = self._calculate_max_trade_amount(session_target, capital, total_trades, win_trades_wanted, payout_rate)
        logger.info(f"Max trade in sequence: ${max_trade_amount:.2f} ({(max_trade_amount/capital)*100:.1f}% of capital)")
        
        return int(sessions_required), round(session_target, 2)
    
    def _find_optimal_session_target(self, capital: float, total_profit_target: float, 
                                   total_trades: int, win_trades_wanted: int, 
                                   payout_rate: float) -> float:
        """
        Find the highest session target that doesn't exceed capital in worst-case trading sequence
        
        Tests session targets from high to low until finding one where all trades stay under 90% of capital
        """
        # Start with aggressive targets and work down - more granular testing
        test_percentages = [10.0, 9.0, 8.0, 7.0, 6.0, 5.9, 5.5, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
        
        for percentage in test_percentages:
            session_target = capital * (percentage / 100)
            
            # Don't test targets larger than total profit needed
            if session_target > total_profit_target:
                session_target = total_profit_target
            
            # Test if this session target is safe
            if self._is_session_target_safe(session_target, capital, total_trades, win_trades_wanted, payout_rate):
                logger.info(f"Optimal session target found: ${session_target:.2f} ({percentage:.1f}% of capital)")
                return session_target
        
        # Fallback to minimum safe target
        min_target = capital * 0.001  # 0.1% minimum
        logger.info(f"Using minimum fallback session target: ${min_target:.2f}")
        return min_target
    
    def _is_session_target_safe(self, session_target: float, capital: float, 
                               total_trades: int, win_trades_wanted: int, 
                               payout_rate: float) -> bool:
        """
        Test if a session target is safe by simulating worst-case martingale sequence
        
        Returns True if all trade amounts stay under 90% of capital
        """
        profit_per_win = session_target / win_trades_wanted
        cumulative_loss = 0.0
        
        # Simulate worst case: all losses until the last possible win
        max_losses = total_trades - win_trades_wanted
        
        for trade_num in range(1, total_trades + 1):
            if trade_num == 1:
                trade_amount = profit_per_win / payout_rate
            else:
                # Need to recover all previous losses + generate our profit
                trade_amount = (cumulative_loss + profit_per_win) / payout_rate
            
            # Check if this trade exceeds capital limit
            if trade_amount > capital * 0.90:  # 90% capital limit
                return False
            
            # Add this trade to cumulative loss for next iteration
            cumulative_loss += trade_amount
        
        return True
    
    def _calculate_max_trade_amount(self, session_target: float, capital: float, 
                                  total_trades: int, win_trades_wanted: int, 
                                  payout_rate: float) -> float:
        """Calculate the maximum trade amount in the worst-case sequence"""
        profit_per_win = session_target / win_trades_wanted
        cumulative_loss = 0.0
        max_trade_amount = 0.0
        
        for trade_num in range(1, total_trades + 1):
            if trade_num == 1:
                trade_amount = profit_per_win / payout_rate
            else:
                trade_amount = (cumulative_loss + profit_per_win) / payout_rate
            
            max_trade_amount = max(max_trade_amount, trade_amount)
            cumulative_loss += trade_amount
        
        return max_trade_amount
    
    def calculate_trade_amount(self, session_data: Dict[str, Any], current_pl: float, 
                             trade_number: int) -> float:
        """
        Calculate trade amount using improved multiple-win martingale logic
        Properly distributes profit targets across expected wins
        
        Args:
            session_data: Session configuration data
            current_pl: Current profit/loss for the session
            trade_number: Current trade number (1-based)
            
        Returns:
            Calculated trade amount
        """
        capital = session_data['capital']
        profit_target = session_data['profit_target']
        win_trades_wanted = session_data['win_trades_wanted']
        payout_percentage = session_data['payout_percentage']
        total_trades = session_data['total_trades']
        
        payout_rate = payout_percentage / 100.0
        
        # Count wins achieved so far
        wins_so_far = self._count_wins_in_session(session_data['session_id'])
        
        # IMPROVED MULTIPLE-WIN LOGIC: Each win contributes proportionally
        profit_per_win = profit_target / win_trades_wanted
        
        # Calculate losses to recover (only actual losses, not excess profits)
        losses_to_recover = abs(min(0, current_pl))
        
        # MARTINGALE WITH DISTRIBUTED PROFITS: 
        # Trade amount must recover all losses + contribute our share of session profit
        total_recovery_needed = losses_to_recover + profit_per_win
        
        # Calculate trade amount using Martingale principle
        if trade_number == 1:
            # First trade: just our profit contribution
            trade_amount = profit_per_win / payout_rate
        else:
            # Subsequent trades: recover all losses + our profit contribution
            trade_amount = total_recovery_needed / payout_rate
        
        # Set reasonable minimums and maximums
        min_trade_amount = capital * 0.001  # 0.1% of capital minimum
        max_trade_amount = capital * 0.90   # 90% of capital maximum
        
        trade_amount = max(min_trade_amount, trade_amount)
        trade_amount = min(max_trade_amount, trade_amount)
        
        logger.info(f"Enhanced trade calculation: ${trade_amount:.2f} for trade {trade_number}")
        logger.info(f"  - Profit per win: ${profit_per_win:.2f}")
        logger.info(f"  - Losses to recover: ${losses_to_recover:.2f}")
        logger.info(f"  - Current P/L: ${current_pl:.2f}")
        logger.info(f"  - Wins achieved: {wins_so_far}/{win_trades_wanted}")
        
        return round(trade_amount, 2)
    
    def _get_user_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user settings from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'user_id': row[0],
                    'capital': row[1],
                    'total_trades': row[2],
                    'win_trades_wanted': row[3],
                    'payout_percentage': row[4],
                    'gain_target_value': row[5],
                    'gain_target_type': row[6],
                    'sessions_required': row[7],
                    'session_profit_target': row[8],
                    'trading_mode': row[9]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting user settings: {e}")
            return None
    
    def get_last_session_result(self, user_id: str) -> Dict[str, Any]:
        """
        Get the result of the last completed session to determine if we should auto-update capital
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Dictionary with session result info
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the most recent completed session
            cursor.execute('''
                SELECT session_id, capital, current_pl, is_completed, session_result, completed_at
                FROM trading_sessions 
                WHERE user_id = ? AND is_completed = TRUE
                ORDER BY session_number DESC LIMIT 1
            ''', (user_id,))
            
            last_session = cursor.fetchone()
            conn.close()
            
            if last_session:
                session_id, original_capital, final_pl, is_completed, session_result, completed_at = last_session
                final_capital = original_capital + final_pl
                
                return {
                    "success": True,
                    "has_completed_session": True,
                    "session_id": session_id,
                    "original_capital": original_capital,
                    "final_pl": final_pl,
                    "final_capital": final_capital,
                    "session_result": session_result,
                    "completed_at": completed_at
                }
            else:
                return {
                    "success": True,
                    "has_completed_session": False
                }
                
        except Exception as e:
            logger.error(f"Error getting last session result: {e}")
            return {"success": False, "error": str(e)}

    def reset_session_counter(self, user_id: str) -> Dict[str, Any]:
        """
        Reset the session counter for a user and clear performance statistics
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Result dictionary with success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete all trades for this user (clears trade performance stats)
            cursor.execute('''
                DELETE FROM trades WHERE session_id IN (
                    SELECT session_id FROM trading_sessions WHERE user_id = ?
                )
            ''', (user_id,))
            
            # Delete all sessions for this user (clears session performance stats)
            cursor.execute('''
                DELETE FROM trading_sessions WHERE user_id = ?
            ''', (user_id,))
            
            # Remove from active sessions cache
            if user_id in self.active_sessions:
                del self.active_sessions[user_id]
            
            conn.commit()
            conn.close()
            
            logger.info(f"Session counter and performance statistics reset for user {user_id}")
            return {
                "success": True,
                "message": "Session counter and performance statistics have been reset. You can start fresh with Session #1 and clean performance data."
            }
            
        except Exception as e:
            logger.error(f"Error resetting session counter: {e}")
            return {"success": False, "error": str(e)}
    
    def create_user_settings(self, user_id: str, capital: float, total_trades: int,
                           win_trades_wanted: int, payout_percentage: float,
                           gain_target_value: float, gain_target_type: str,
                           trading_mode: str = "balanced") -> Dict[str, Any]:
        """
        Create or update user settings for the trade manager
        
        Args:
            user_id: Discord user ID
            capital: Initial trading capital
            total_trades: Total trades per session
            win_trades_wanted: Target number of wins
            payout_percentage: Broker payout percentage
            gain_target_value: Target gain value
            gain_target_type: 'percent' or 'dollar'
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            # Validate inputs
            if capital <= 0:
                return {"success": False, "error": "Capital must be positive"}
            if total_trades <= 0 or total_trades > 20:
                return {"success": False, "error": "Total trades must be between 1 and 20"}
            max_wins = total_trades // 2
            if win_trades_wanted <= 0 or win_trades_wanted > max_wins:
                return {"success": False, "error": f"Win trades must be between 1 and {max_wins} (maximum half of total trades)"}
            if payout_percentage <= 0 or payout_percentage > 100:
                return {"success": False, "error": "Payout percentage must be between 1 and 100"}
            if gain_target_value <= 0:
                return {"success": False, "error": "Gain target must be positive"}
            if gain_target_type not in ['percent', 'dollar']:
                return {"success": False, "error": "Gain target type must be 'percent' or 'dollar'"}
            
            # Calculate enhanced session requirements with user settings
            sessions_required, session_profit_target = self.calculate_session_requirements(
                capital, gain_target_value, gain_target_type, total_trades, win_trades_wanted, payout_percentage
            )
            
            # Store user settings
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_settings 
                (user_id, capital, total_trades, win_trades_wanted, payout_percentage,
                 gain_target_value, gain_target_type, sessions_required, session_profit_target,
                 trading_mode, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, capital, total_trades, win_trades_wanted, payout_percentage,
                  gain_target_value, gain_target_type, sessions_required, session_profit_target,
                  trading_mode))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User settings created for {user_id}")
            return {
                "success": True,
                "message": "Settings saved successfully",
                "sessions_required": sessions_required,
                "session_profit_target": session_profit_target
            }
            
        except Exception as e:
            logger.error(f"Error creating user settings: {e}")
            return {"success": False, "error": str(e)}
    
    def start_new_session(self, user_id: str, updated_capital: Optional[float] = None) -> Dict[str, Any]:
        """
        Start a new trading session for the user
        
        Args:
            user_id: Discord user ID
            updated_capital: Optional new capital amount
            
        Returns:
            Result dictionary with session details
        """
        try:
            # Get user settings
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
            settings = cursor.fetchone()
            
            if not settings:
                conn.close()
                return {"success": False, "error": "No settings found. Please configure settings first."}
            
            # Update capital if provided
            if updated_capital is not None:
                cursor.execute('''
                    UPDATE user_settings SET capital = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                ''', (updated_capital, user_id))
                conn.commit()
                capital = updated_capital
            else:
                capital = settings[1]  # capital column
            
            # Get current session number
            cursor.execute('''
                SELECT COALESCE(MAX(session_number), 0) + 1 FROM trading_sessions 
                WHERE user_id = ?
            ''', (user_id,))
            session_number = cursor.fetchone()[0]
            
            # Create session ID
            session_id = f"{user_id}_{session_number}_{int(datetime.now().timestamp())}"
            
            # Recalculate session profit target if capital changed
            if updated_capital is not None:
                sessions_required, session_profit_target = self.calculate_session_requirements(
                    capital, settings[5], settings[6], settings[2], settings[3], settings[4]  # gain_target_value, gain_target_type, total_trades, win_trades_wanted, payout_percentage
                )
                cursor.execute('''
                    UPDATE user_settings SET sessions_required = ?, session_profit_target = ?
                    WHERE user_id = ?
                ''', (sessions_required, session_profit_target, user_id))
                conn.commit()
            else:
                session_profit_target = settings[8]  # session_profit_target
            
            # Create new session
            cursor.execute('''
                INSERT INTO trading_sessions 
                (session_id, user_id, session_number, capital, profit_target, total_trades,
                 win_trades_wanted, payout_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, user_id, session_number, capital, session_profit_target,
                  settings[2], settings[3], settings[4]))  # total_trades, win_trades_wanted, payout_percentage
            
            conn.commit()
            conn.close()
            
            # Store in active sessions
            self.active_sessions[user_id] = session_id
            
            logger.info(f"New session started for {user_id}: {session_id}")
            return {
                "success": True,
                "message": f"Session #{session_number} started successfully",
                "session_id": session_id,
                "session_number": session_number,
                "capital": capital,
                "profit_target": session_profit_target
            }
            
        except Exception as e:
            logger.error(f"Error starting new session: {e}")
            return {"success": False, "error": str(e)}
    
    def get_session_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get current session status for a user
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Session status dictionary
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)  # Add timeout to prevent hangs
            cursor = conn.cursor()
            
            # Get active session
            cursor.execute('''
                SELECT * FROM trading_sessions 
                WHERE user_id = ? AND is_active = TRUE 
                ORDER BY session_number DESC LIMIT 1
            ''', (user_id,))
            
            session = cursor.fetchone()
            
            if not session:
                conn.close()
                logger.warning(f"No active session found for user {user_id}")
                return {"success": False, "error": "No active session found. Please start a new session first."}
            
            # Get session data
            session_data = {
                "session_id": session[0],
                "user_id": session[1],
                "session_number": session[2],
                "capital": session[3],
                "profit_target": session[4],
                "total_trades": session[5],
                "win_trades_wanted": session[6],
                "payout_percentage": session[7],
                "current_trade": session[8],
                "current_pl": session[9],
                "is_active": bool(session[10]),
                "is_completed": bool(session[11]),
                "session_result": session[12]
            }
            
            # Calculate next trade amount - handle first trade properly
            next_trade_number = session_data['current_trade'] + 1 if session_data['current_trade'] > 0 else 1
            next_trade_amount = self.calculate_trade_amount(
                session_data, session_data['current_pl'], next_trade_number
            )
            
            # Get trade history
            cursor.execute('''
                SELECT trade_number, trade_amount, trade_result, profit_loss 
                FROM trades WHERE session_id = ? ORDER BY trade_number
            ''', (session_data['session_id'],))
            
            trades = cursor.fetchall()
            
            conn.close()
            
            return {
                "success": True,
                "session_active": session_data['is_active'],
                "session_data": session_data,
                "next_trade_amount": next_trade_amount,
                "trades": trades
            }
            
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return {"success": False, "error": str(e)}
    
    def record_trade_result(self, user_id: str, result: str, trade_amount: float) -> Dict[str, Any]:
        """
        Record a trade result for the active session
        
        Args:
            user_id: Discord user ID
            result: 'win' or 'loss'
            trade_amount: Amount traded
            
        Returns:
            Result dictionary
        """
        try:
            # Get active session
            session_status = self.get_session_status(user_id)
            if not session_status.get('success'):
                logger.warning(f"Cannot record trade for {user_id}: {session_status.get('error', 'Unknown error')}")
                return {"success": False, "error": f"Session error: {session_status.get('error', 'No active session')}"}
            
            if not session_status.get('session_active'):
                logger.warning(f"Session not active for user {user_id}")
                return {"success": False, "error": "Session is not currently active. Please start a new session."}
            
            session_data = session_status['session_data']
            session_id = session_data['session_id']
            
            # Calculate profit/loss
            if result == 'win':
                profit_loss = trade_amount * (session_data['payout_percentage'] / 100)
            else:
                profit_loss = -trade_amount
            
            # Update session
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            new_trade_number = session_data['current_trade'] + 1
            new_pl = session_data['current_pl'] + profit_loss
            
            # Record trade
            trade_id = f"{session_id}_{new_trade_number}"
            cursor.execute('''
                INSERT INTO trades (trade_id, session_id, trade_number, trade_amount, 
                                  trade_result, profit_loss)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (trade_id, session_id, new_trade_number, trade_amount, result, profit_loss))
            
            # Check if session is complete - either hit total trades OR win target
            current_wins = self._count_wins_in_session(session_id)
            if result == 'win':
                current_wins += 1
            
            is_completed = (new_trade_number >= session_data['total_trades'] or 
                          current_wins >= session_data['win_trades_wanted'])
            session_result = 'active'
            
            if is_completed:
                # Session completes when win target is reached OR max trades hit
                if current_wins >= session_data['win_trades_wanted']:
                    session_result = 'success'  # Won enough trades
                elif new_pl >= session_data['profit_target']:
                    session_result = 'success'  # Hit profit target 
                else:
                    session_result = 'failure'  # Hit max trades without success
            
            # Update session
            cursor.execute('''
                UPDATE trading_sessions 
                SET current_trade = ?, current_pl = ?, is_active = ?, is_completed = ?,
                    session_result = ?, completed_at = ?
                WHERE session_id = ?
            ''', (new_trade_number, new_pl, not is_completed, is_completed,
                  session_result, datetime.now() if is_completed else None, session_id))
            
            conn.commit()
            conn.close()
            
            # Remove from active sessions if completed
            if is_completed and user_id in self.active_sessions:
                del self.active_sessions[user_id]
            
            logger.info(f"Trade recorded: {result} for ${trade_amount} (P/L: ${profit_loss})")
            
            # Get sessions_required from user settings, not session data
            try:
                conn2 = sqlite3.connect(self.db_path, timeout=10.0)
                cursor2 = conn2.cursor()
                cursor2.execute('SELECT sessions_required FROM user_settings WHERE user_id = ?', (user_id,))
                settings_row = cursor2.fetchone()
                sessions_required = settings_row[0] if settings_row else 1
                conn2.close()
            except Exception as e:
                logger.warning(f"Could not fetch sessions_required for {user_id}: {e}")
                sessions_required = 1
            
            return {
                "success": True,
                "trade_number": new_trade_number,
                "profit_loss": profit_loss,
                "new_pl": new_pl,
                "is_completed": is_completed,
                "session_result": session_result,
                "current_wins": current_wins,
                "sessions_completed": self._get_completed_sessions_count(user_id),
                "sessions_required": sessions_required
            }
            
        except Exception as e:
            logger.error(f"Error recording trade result: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_performance(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics for a user
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Performance statistics dictionary
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user settings
            cursor.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
            settings = cursor.fetchone()
            
            if not settings:
                conn.close()
                return {"success": False, "error": "No user settings found"}
            
            # Get session statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(CASE WHEN session_result = 'success' THEN 1 ELSE 0 END) as successful_sessions,
                    SUM(CASE WHEN is_completed = TRUE THEN current_pl ELSE 0 END) as total_profit,
                    AVG(CASE WHEN is_completed = TRUE THEN current_pl ELSE NULL END) as avg_session_pl
                FROM trading_sessions WHERE user_id = ?
            ''', (user_id,))
            
            session_stats = cursor.fetchone()
            
            # Get trade statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN trade_result = 'win' THEN 1 ELSE 0 END) as total_wins,
                    SUM(profit_loss) as total_pl
                FROM trades t
                JOIN trading_sessions s ON t.session_id = s.session_id
                WHERE s.user_id = ?
            ''', (user_id,))
            
            trade_stats = cursor.fetchone()
            
            conn.close()
            
            # Calculate performance metrics
            total_sessions = session_stats[0] or 0
            successful_sessions = session_stats[1] or 0
            success_rate = (successful_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            total_trades = trade_stats[0] or 0
            total_wins = trade_stats[1] or 0
            win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
            
            return {
                "success": True,
                "user_settings": {
                    "capital": settings[1],
                    "total_trades": settings[2],
                    "win_trades_wanted": settings[3],
                    "payout_percentage": settings[4],
                    "gain_target_value": settings[5],
                    "gain_target_type": settings[6],
                    "sessions_required": settings[7],
                    "session_profit_target": settings[8]
                },
                "session_performance": {
                    "total_sessions": total_sessions,
                    "successful_sessions": successful_sessions,
                    "success_rate": round(success_rate, 2),
                    "total_profit": round(session_stats[2] or 0, 2),
                    "avg_session_pl": round(session_stats[3] or 0, 2)
                },
                "trade_performance": {
                    "total_trades": total_trades,
                    "total_wins": total_wins,
                    "win_rate": round(win_rate, 2),
                    "total_pl": round(trade_stats[2] or 0, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user performance: {e}")
            return {"success": False, "error": str(e)}
    
    def reset_user_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Reset all user settings and data
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Result dictionary
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete all user data
            cursor.execute('DELETE FROM trades WHERE session_id IN (SELECT session_id FROM trading_sessions WHERE user_id = ?)', (user_id,))
            cursor.execute('DELETE FROM trading_sessions WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM user_settings WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            # Remove from active sessions
            if user_id in self.active_sessions:
                del self.active_sessions[user_id]
            
            logger.info(f"User settings reset for {user_id}")
            return {"success": True, "message": "All settings and data reset successfully"}
            
        except Exception as e:
            logger.error(f"Error resetting user settings: {e}")
            return {"success": False, "error": str(e)}
    
    def _count_wins_in_session(self, session_id: str) -> int:
        """Count wins in current session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM trades 
                WHERE session_id = ? AND trade_result = 'win'
            ''', (session_id,))
            
            wins = cursor.fetchone()[0]
            conn.close()
            return wins
        except Exception:
            return 0
    
    def _get_completed_sessions_count(self, user_id: str) -> int:
        """Get count of completed sessions for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM trading_sessions 
                WHERE user_id = ? AND is_completed = 1
            ''', (user_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0


# Legacy compatibility functions for existing UI components
def get_trade_manager_status(user_id: str) -> Dict[str, Any]:
    """Legacy compatibility function"""
    tm = TradeManagerSystem()
    return tm.get_session_status(user_id)

def create_trading_session(user_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy compatibility function"""
    tm = TradeManagerSystem()
    return tm.create_user_settings(
        user_id=user_id,
        capital=settings['capital'],
        total_trades=settings['total_trades'],
        win_trades_wanted=settings['win_trades_wanted'],
        payout_percentage=settings['payout_percentage'],
        gain_target_value=settings['gain_target_value'],
        gain_target_type=settings['gain_target_type']
    )

def record_trade_result(user_id: str, result: str, amount: float) -> Dict[str, Any]:
    """Legacy compatibility function"""
    tm = TradeManagerSystem()
    return tm.record_trade_result(user_id, result, amount)

def get_user_performance(user_id: str) -> Dict[str, Any]:
    """Legacy compatibility function"""
    tm = TradeManagerSystem()
    return tm.get_user_performance(user_id)

def calculate_session_plan(user_id: str) -> Dict[str, Any]:
    """Legacy compatibility function"""
    tm = TradeManagerSystem()
    return tm.get_session_status(user_id)