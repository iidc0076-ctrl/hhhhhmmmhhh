#!/usr/bin/env python3
"""
QuantVision Signal Backtester - 1 Day Historical Testing
Comprehensive backtesting system with detailed performance metrics

Features:
- 1-day signal backtesting with real market data
- Detailed performance analytics: Win rate, Net profit, Maximum drawdown, Accuracy
- Binary options simulation with configurable payouts
- Risk management with position sizing
- Comprehensive reporting and visualization
"""

import pandas as pd
import numpy as np
import asyncio
import sqlite3
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path

# Import bot's actual working analysis systems
analysis_pipeline = None
get_market_data = None

try:
    # Import the main.py analysis function that's actually working in your Discord bot
    import sys
    import os
    
    # Import the working analysis function from main.py
    from main import generate_comprehensive_analysis
    
    # Create a simple wrapper that mimics the expected interface
    class BotAnalysisWrapper:
        async def process_comprehensive_analysis(self, df, pair, timeframe):
            try:
                # Use the bot's actual working analysis function
                result = await generate_comprehensive_analysis(pair, timeframe)
                
                # The main.py function returns analysis data, we need to extract signal
                if result and isinstance(result, dict):
                    # Look for signal indicators in the analysis
                    analysis_data = result.get('analysis_data', result)
                    
                    # Extract signal from various possible fields
                    signal = None
                    confidence = 55.0
                    
                    # Check for direct signal field
                    if 'signal' in analysis_data:
                        signal = analysis_data['signal']
                    elif 'recommendation' in analysis_data:
                        signal = analysis_data['recommendation']
                    elif 'main_signal' in analysis_data:
                        signal = analysis_data['main_signal']
                    
                    # Extract confidence
                    if 'confidence' in analysis_data:
                        confidence = analysis_data['confidence']
                    elif 'entry_confidence' in analysis_data:
                        confidence = analysis_data['entry_confidence']
                    elif 'timing_score' in analysis_data:
                        confidence = analysis_data['timing_score']
                    
                    # Return structured result
                    return {
                        'signal': signal or 'NEUTRAL',
                        'confidence': confidence,
                        'analysis_data': analysis_data,
                        'pair': pair,
                        'timeframe': timeframe
                    }
                
                return {'signal': 'NEUTRAL', 'confidence': 50.0}
                
            except Exception as e:
                print(f"Error in bot analysis wrapper: {e}")
                return {'signal': 'NEUTRAL', 'confidence': 50.0}
    
    analysis_pipeline = BotAnalysisWrapper()
    print("Successfully created bot analysis wrapper using main.py")
    
    # Try to get the market data function
    try:
        from alternative_data_source import AlternativeDataProvider
        
        # Create a simple wrapper for get_market_data
        async def get_market_data(pair, timeframe, limit=100):
            try:
                async with AlternativeDataProvider() as provider:
                    return await provider.get_forex_data(pair, timeframe, limit)
            except Exception as e:
                print(f"Error getting market data: {e}")
                return None
                
        print("Successfully created market data wrapper")
    except ImportError:
        print("Market data provider not available")
        get_market_data = None
        
except ImportError as e:
    print(f"Failed to import bot analysis functions: {e}")
    analysis_pipeline = None
    get_market_data = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backtest.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BacktestTrade:
    """Individual trade result"""
    timestamp: datetime
    pair: str
    signal: str
    entry_price: float
    exit_price: float
    position_size: float
    payout_rate: float
    expiry_minutes: int
    confidence: float
    result: str  # 'WIN' or 'LOSS'
    profit_loss: float
    analysis_data: Dict[str, Any]
    trade_duration: timedelta

@dataclass
class BacktestResults:
    """Complete backtest results"""
    start_date: datetime
    end_date: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_profit_loss: float
    max_drawdown: float
    max_drawdown_percent: float
    accuracy: float
    average_confidence: float
    best_trade: float
    worst_trade: float
    average_trade: float
    sharpe_ratio: float
    profit_factor: float
    recovery_factor: float
    trades: List[BacktestTrade]
    daily_pnl: List[float]
    equity_curve: List[float]
    pairs_performance: Dict[str, Dict[str, Any]]

class SignalBacktester:
    """1-Day Signal Backtester with comprehensive analytics"""
    
    def __init__(self, initial_capital: float = 1000.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.db_path = "backtest_results.db"
        self.setup_database()
        
        # Default backtesting parameters
        self.position_size = 50.0  # Fixed position size per trade
        self.payout_rate = 0.85    # 85% payout on win
        self.expiry_minutes = 5    # 5-minute expiry
        self.min_confidence = 70   # Minimum confidence threshold (same as bot)
        
        # Trading pairs to backtest
        self.pairs = [
            "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", 
            "USD/CHF", "EUR/GBP", "EUR/JPY", "GBP/JPY"
        ]
        
        self.trades = []
        self.equity_curve = [initial_capital]
        
    def setup_database(self):
        """Initialize database for storing backtest results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                start_time TEXT,
                end_time TEXT,
                initial_capital REAL,
                final_capital REAL,
                total_trades INTEGER,
                win_rate REAL,
                max_drawdown REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                pair TEXT,
                signal TEXT,
                entry_price REAL,
                exit_price REAL,
                position_size REAL,
                payout_rate REAL,
                expiry_minutes INTEGER,
                confidence REAL,
                result TEXT,
                profit_loss REAL,
                analysis_data TEXT,
                FOREIGN KEY (session_id) REFERENCES backtest_sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def get_historical_data(self, pair: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get historical market data for backtesting"""
        try:
            if get_market_data:
                # Convert pair format for the market data system
                formatted_pair = pair.replace("/", "")  # EUR/USD -> EURUSD
                
                # Calculate required data points (30 days * 288 candles per day)
                days_diff = (end_date - start_date).days
                required_points = days_diff * 288  # 5-minute candles per day
                
                # Get real market data from the bot's system
                data = await get_market_data(formatted_pair, "5m", limit=min(required_points, 8000))
                if data is not None and not data.empty:
                    logger.info(f"Retrieved real market data for {pair}: {len(data)} points for {days_diff} days")
                    return data
                    
        except Exception as e:
            logger.error(f"Error getting real market data for {pair}: {e}")
        
        # Generate realistic synthetic data as fallback
        days_diff = (end_date - start_date).days
        logger.warning(f"Using synthetic data for {pair} - generating {days_diff} days")
        return self.generate_realistic_data(pair, start_date, end_date)
    
    def generate_realistic_data(self, pair: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate realistic forex data for backtesting"""
        np.random.seed(42 + hash(pair) % 100)
        
        # Base prices for different pairs
        base_prices = {
            "EUR/USD": 1.0800, "GBP/USD": 1.2500, "USD/JPY": 150.00,
            "AUD/USD": 0.6600, "USD/CHF": 0.9000, "EUR/GBP": 0.8640,
            "EUR/JPY": 162.00, "GBP/JPY": 187.50
        }
        
        base_price = base_prices.get(pair, 1.0000)
        
        # Calculate periods for the entire date range
        days_diff = (end_date - start_date).days
        periods = days_diff * 288  # 24 hours * 60 minutes / 5 minutes per day
        timestamps = [start_date + timedelta(minutes=5*i) for i in range(periods)]
        
        # Generate realistic price movement with multi-day trends
        returns = np.random.normal(0, 0.0005, periods)  # Small returns
        
        # Add multi-timeframe patterns
        daily_trend = np.sin(np.arange(periods) * 2 * np.pi / 288) * 0.0002  # Daily pattern
        weekly_trend = np.sin(np.arange(periods) * 2 * np.pi / (288 * 7)) * 0.0001  # Weekly pattern
        trend = daily_trend + weekly_trend
        
        prices = [base_price]
        for i in range(1, periods):
            new_price = prices[-1] * (1 + returns[i] + trend[i])
            prices.append(new_price)
        
        # Generate OHLCV
        data = []
        for i, timestamp in enumerate(timestamps):
            close = prices[i]
            open_price = close * (1 + np.random.normal(0, 0.0001))
            high = max(open_price, close) * (1 + abs(np.random.normal(0, 0.0002)))
            low = min(open_price, close) * (1 - abs(np.random.normal(0, 0.0002)))
            volume = np.random.uniform(1000, 5000)
            
            data.append({
                'time': timestamp,  # Use 'time' to match API format
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('time', inplace=True)
        return df
    
    async def run_signal_analysis(self, pair: str, data: pd.DataFrame, timestamp: datetime) -> Optional[Dict]:
        """Run signal analysis using the bot's actual analysis pipeline"""
        try:
            if analysis_pipeline:
                # Convert pair format for the analysis system
                formatted_pair = pair.replace("/", "")  # EUR/USD -> EURUSD
                
                # Use the bot's real analysis integration pipeline
                result = await analysis_pipeline.process_comprehensive_analysis(data, formatted_pair, "5m")
                
                # Check if we got a valid result with signal
                if (result and isinstance(result, dict) and 
                    "signal" in result and 
                    result.get("signal") in ["CALL", "PUT", "BUY", "SELL"]):
                    
                    # Normalize signal format for binary options
                    signal = result["signal"]
                    if signal == "BUY":
                        signal = "CALL"
                    elif signal == "SELL":
                        signal = "PUT"
                    
                    confidence = result.get("confidence", 50)
                    
                    # Only return signals above our confidence threshold
                    if confidence >= self.min_confidence:
                        logger.info(f"Bot analysis: {pair} {signal} @ {confidence:.1f}% confidence")
                        return {
                            "signal": signal,
                            "confidence": confidence,
                            "analysis": result,
                            "pair": pair,
                            "timestamp": timestamp,
                            "source": "bot_analysis"
                        }
                    else:
                        logger.debug(f"Bot signal for {pair} below confidence threshold: {confidence:.1f}%")
                        return None
                        
        except Exception as e:
            logger.error(f"Error in bot signal analysis for {pair}: {e}")
            import traceback
            logger.debug(f"Full traceback: {traceback.format_exc()}")
        
        # Only use fallback if bot analysis completely fails
        logger.warning(f"Using fallback analysis for {pair} - bot analysis unavailable")
        fallback_result = self.simple_signal_analysis(data, timestamp)
        if fallback_result:
            fallback_result["source"] = "fallback_analysis"
        return fallback_result
    
    def simple_signal_analysis(self, data: pd.DataFrame, timestamp: datetime) -> Dict:
        """Simplified signal analysis as fallback"""
        if len(data) < 20:
            return {"signal": "NEUTRAL", "confidence": 0}
        
        # Get recent data
        recent = data.tail(20)
        current_price = recent['close'].iloc[-1]
        sma_10 = recent['close'].tail(10).mean()
        sma_20 = recent['close'].mean()
        
        # Simple trend analysis
        if current_price > sma_10 > sma_20:
            signal = "CALL"
            confidence = min(85, 60 + abs((current_price - sma_20) / sma_20 * 1000))
        elif current_price < sma_10 < sma_20:
            signal = "PUT"  
            confidence = min(85, 60 + abs((sma_20 - current_price) / sma_20 * 1000))
        else:
            signal = "NEUTRAL"
            confidence = 30 + np.random.uniform(0, 20)
        
        return {
            "signal": signal,
            "confidence": confidence,
            "analysis": {
                "current_price": current_price,
                "sma_10": sma_10,
                "sma_20": sma_20,
                "trend": "bullish" if signal == "CALL" else "bearish" if signal == "PUT" else "neutral"
            }
        }
    
    def determine_trade_outcome(self, entry_price: float, exit_price: float, signal: str) -> Tuple[str, float]:
        """Determine if trade was profitable"""
        if signal == "CALL":
            if exit_price > entry_price:
                return "WIN", self.position_size * self.payout_rate
            else:
                return "LOSS", -self.position_size
        elif signal == "PUT":
            if exit_price < entry_price:
                return "WIN", self.position_size * self.payout_rate
            else:
                return "LOSS", -self.position_size
        else:
            return "LOSS", -self.position_size  # Neutral signals lose
    
    async def backtest_pair(self, pair: str, data: pd.DataFrame) -> List[BacktestTrade]:
        """Backtest a single currency pair"""
        pair_trades = []
        logger.info(f"Backtesting {pair} with {len(data)} data points")
        
        # Skip first 50 candles to allow for indicator calculation
        start_idx = 50
        
        for i in range(start_idx, len(data) - self.expiry_minutes, 24):  # Trade every 24 candles (2 hours)
            try:
                # Handle different data formats
                if 'timestamp' in data.columns:
                    current_time = data.iloc[i]['timestamp']
                elif 'time' in data.columns:
                    current_time = data.iloc[i]['time']
                elif hasattr(data.index, 'to_pydatetime'):
                    current_time = data.index[i].to_pydatetime()
                else:
                    current_time = data.index[i] if isinstance(data.index[i], datetime) else datetime.now()
                
                entry_data = data.iloc[:i+1]  # Data available at entry time
                
                # Run signal analysis
                analysis = await self.run_signal_analysis(pair, entry_data, current_time)
                
                if not analysis or analysis.get("signal") == "NEUTRAL" or "signal" not in analysis:
                    continue
                
                confidence = analysis.get("confidence", 0)
                if confidence < self.min_confidence:
                    continue
                
                # Entry details
                entry_price = data.iloc[i]['close']
                entry_time = current_time
                
                # Exit after expiry minutes
                exit_idx = min(i + self.expiry_minutes, len(data) - 1)
                exit_price = data.iloc[exit_idx]['close']
                
                # Handle different timestamp formats for exit time
                if 'timestamp' in data.columns:
                    exit_time = data.iloc[exit_idx]['timestamp']
                elif 'time' in data.columns:
                    exit_time = data.iloc[exit_idx]['time']
                else:
                    exit_time = current_time + timedelta(minutes=self.expiry_minutes)
                
                # Determine outcome
                result, pnl = self.determine_trade_outcome(entry_price, exit_price, analysis["signal"])
                
                # Create trade record
                trade = BacktestTrade(
                    timestamp=entry_time,
                    pair=pair,
                    signal=analysis["signal"],
                    entry_price=entry_price,
                    exit_price=exit_price,
                    position_size=self.position_size,
                    payout_rate=self.payout_rate,
                    expiry_minutes=self.expiry_minutes,
                    confidence=confidence,
                    result=result,
                    profit_loss=pnl,
                    analysis_data=analysis,
                    trade_duration=exit_time - entry_time
                )
                
                pair_trades.append(trade)
                self.current_capital += pnl
                self.equity_curve.append(self.current_capital)
                
                logger.debug(f"{pair} {analysis['signal']} @ {entry_price:.5f} -> {exit_price:.5f} = {result} ({pnl:+.2f})")
                
            except Exception as e:
                logger.error(f"Error processing trade for {pair} at index {i}: {e}")
                continue
        
        return pair_trades
    
    async def run_backtest(self, backtest_date: Optional[datetime] = None, days: int = 30) -> BacktestResults:
        """Run comprehensive multi-day backtest"""
        if backtest_date is None:
            backtest_date = datetime.now() - timedelta(days=days)
        
        start_date = backtest_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=days)
        
        logger.info(f"Starting {days}-day backtest from {start_date} to {end_date}")
        logger.info(f"Initial capital: ${self.initial_capital:,.2f}")
        logger.info(f"Position size: ${self.position_size}")
        logger.info(f"Payout rate: {self.payout_rate*100}%")
        logger.info(f"Minimum confidence: {self.min_confidence}%")
        
        # Reset state
        self.trades = []
        self.current_capital = self.initial_capital
        self.equity_curve = [self.initial_capital]
        
        # Backtest each pair
        for pair in self.pairs:
            try:
                logger.info(f"Getting historical data for {pair}")
                data = await self.get_historical_data(pair, start_date, end_date)
                
                if data.empty:
                    logger.warning(f"No data available for {pair}")
                    continue
                
                pair_trades = await self.backtest_pair(pair, data)
                self.trades.extend(pair_trades)
                
                logger.info(f"Completed {pair}: {len(pair_trades)} trades")
                
            except Exception as e:
                logger.error(f"Error backtesting {pair}: {e}")
                continue
        
        # Calculate comprehensive results
        results = self.calculate_results(start_date, end_date)
        
        # Save to database
        await self.save_results(results)
        
        return results
    
    def calculate_results(self, start_date: datetime, end_date: datetime) -> BacktestResults:
        """Calculate comprehensive backtest results"""
        if not self.trades:
            return BacktestResults(
                start_date=start_date, end_date=end_date, total_trades=0,
                winning_trades=0, losing_trades=0, win_rate=0.0,
                total_profit_loss=0.0, max_drawdown=0.0, max_drawdown_percent=0.0,
                accuracy=0.0, average_confidence=0.0, best_trade=0.0, worst_trade=0.0,
                average_trade=0.0, sharpe_ratio=0.0, profit_factor=0.0, recovery_factor=0.0,
                trades=[], daily_pnl=[], equity_curve=[], pairs_performance={}
            )
        
        # Basic metrics
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.result == "WIN")
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # P&L metrics
        total_pnl = sum(t.profit_loss for t in self.trades)
        best_trade = max(t.profit_loss for t in self.trades)
        worst_trade = min(t.profit_loss for t in self.trades)
        average_trade = total_pnl / total_trades if total_trades > 0 else 0
        
        # Drawdown calculation
        peak = self.initial_capital
        max_drawdown = 0
        max_drawdown_percent = 0
        
        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
            drawdown = peak - equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_drawdown_percent = (drawdown / peak) * 100 if peak > 0 else 0
        
        # Accuracy (correct direction prediction)
        correct_predictions = 0
        for trade in self.trades:
            if trade.signal == "CALL" and trade.exit_price > trade.entry_price:
                correct_predictions += 1
            elif trade.signal == "PUT" and trade.exit_price < trade.entry_price:
                correct_predictions += 1
        
        accuracy = (correct_predictions / total_trades) * 100 if total_trades > 0 else 0
        average_confidence = sum(t.confidence for t in self.trades) / total_trades if total_trades > 0 else 0
        
        # Advanced metrics
        positive_pnl = sum(t.profit_loss for t in self.trades if t.profit_loss > 0)
        negative_pnl = abs(sum(t.profit_loss for t in self.trades if t.profit_loss < 0))
        
        profit_factor = positive_pnl / negative_pnl if negative_pnl > 0 else float('inf')
        recovery_factor = total_pnl / max_drawdown if max_drawdown > 0 else float('inf')
        
        # Sharpe ratio (simplified)
        returns = [self.equity_curve[i] - self.equity_curve[i-1] for i in range(1, len(self.equity_curve))]
        avg_return = np.mean(returns) if returns else 0
        std_return = np.std(returns) if returns and len(returns) > 1 else 1
        sharpe_ratio = (avg_return / std_return) * np.sqrt(288) if std_return > 0 else 0  # Annualized
        
        # Per-pair performance
        pairs_performance = {}
        for pair in set(t.pair for t in self.trades):
            pair_trades = [t for t in self.trades if t.pair == pair]
            pair_wins = sum(1 for t in pair_trades if t.result == "WIN")
            pair_pnl = sum(t.profit_loss for t in pair_trades)
            
            pairs_performance[pair] = {
                'trades': len(pair_trades),
                'wins': pair_wins,
                'win_rate': (pair_wins / len(pair_trades)) * 100,
                'pnl': pair_pnl,
                'avg_confidence': sum(t.confidence for t in pair_trades) / len(pair_trades)
            }
        
        return BacktestResults(
            start_date=start_date,
            end_date=end_date,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_profit_loss=total_pnl,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            accuracy=accuracy,
            average_confidence=average_confidence,
            best_trade=best_trade,
            worst_trade=worst_trade,
            average_trade=average_trade,
            sharpe_ratio=sharpe_ratio,
            profit_factor=profit_factor,
            recovery_factor=recovery_factor,
            trades=self.trades,
            daily_pnl=[total_pnl],
            equity_curve=self.equity_curve,
            pairs_performance=pairs_performance
        )
    
    async def save_results(self, results: BacktestResults):
        """Save backtest results to database"""
        session_id = f"backtest_{int(results.start_date.timestamp())}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save session summary
        cursor.execute('''
            INSERT OR REPLACE INTO backtest_sessions 
            (session_id, start_time, end_time, initial_capital, final_capital, 
             total_trades, win_rate, max_drawdown)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            results.start_date.isoformat(),
            results.end_date.isoformat(),
            self.initial_capital,
            self.current_capital,
            results.total_trades,
            results.win_rate,
            results.max_drawdown
        ))
        
        # Save individual trades
        for trade in results.trades:
            cursor.execute('''
                INSERT INTO backtest_trades 
                (session_id, timestamp, pair, signal, entry_price, exit_price,
                 position_size, payout_rate, expiry_minutes, confidence, result, profit_loss, analysis_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                trade.timestamp.isoformat(),
                trade.pair,
                trade.signal,
                trade.entry_price,
                trade.exit_price,
                trade.position_size,
                trade.payout_rate,
                trade.expiry_minutes,
                trade.confidence,
                trade.result,
                trade.profit_loss,
                json.dumps(trade.analysis_data, default=str)
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Results saved with session ID: {session_id}")
    
    def print_results(self, results: BacktestResults):
        """Print comprehensive backtest results"""
        print("\n" + "="*80)
        print("🎯 QUANTVISION 1-DAY SIGNAL BACKTEST RESULTS")
        print("="*80)
        
        print(f"\n📅 TEST PERIOD")
        print(f"   Start: {results.start_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   End:   {results.end_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Duration: 1 trading day")
        
        print(f"\n💰 CAPITAL & POSITION SIZING")
        print(f"   Initial Capital: ${self.initial_capital:,.2f}")
        print(f"   Final Capital:   ${self.current_capital:,.2f}")
        print(f"   Position Size:   ${self.position_size}")
        print(f"   Payout Rate:     {self.payout_rate*100}%")
        
        print(f"\n📊 TRADING PERFORMANCE")
        print(f"   Total Trades:    {results.total_trades}")
        print(f"   Winning Trades:  {results.winning_trades}")
        print(f"   Losing Trades:   {results.losing_trades}")
        print(f"   Win Rate:        {results.win_rate:.1f}%")
        print(f"   Accuracy:        {results.accuracy:.1f}%")
        print(f"   Avg Confidence:  {results.average_confidence:.1f}%")
        
        print(f"\n💵 PROFIT & LOSS ANALYSIS")
        print(f"   Net Profit:      ${results.total_profit_loss:+,.2f}")
        print(f"   Best Trade:      ${results.best_trade:+,.2f}")
        print(f"   Worst Trade:     ${results.worst_trade:+,.2f}")
        print(f"   Average Trade:   ${results.average_trade:+,.2f}")
        print(f"   Profit Factor:   {results.profit_factor:.2f}")
        
        print(f"\n📉 RISK ANALYSIS")
        print(f"   Max Drawdown:    ${results.max_drawdown:,.2f}")
        print(f"   Max DD %:        {results.max_drawdown_percent:.1f}%")
        print(f"   Recovery Factor: {results.recovery_factor:.2f}")
        print(f"   Sharpe Ratio:    {results.sharpe_ratio:.2f}")
        
        if results.pairs_performance:
            print(f"\n🌍 PAIRS PERFORMANCE")
            for pair, perf in sorted(results.pairs_performance.items(), 
                                   key=lambda x: x[1]['pnl'], reverse=True):
                print(f"   {pair:<8} | {perf['trades']:2d} trades | {perf['win_rate']:5.1f}% WR | ${perf['pnl']:+7.2f} P&L")
        
        # Performance summary
        print(f"\n🎯 SUMMARY")
        if results.total_profit_loss > 0:
            print(f"   ✅ PROFITABLE STRATEGY")
            print(f"   Return: {(results.total_profit_loss/self.initial_capital)*100:+.1f}%")
        else:
            print(f"   ❌ UNPROFITABLE STRATEGY") 
            print(f"   Loss: {(results.total_profit_loss/self.initial_capital)*100:+.1f}%")
        
        print(f"   Risk-Adjusted Return: {results.total_profit_loss/max(results.max_drawdown, 1):+.2f}")
        
        print("\n" + "="*80)

async def main():
    """Run backtester demonstration"""
    print("🚀 QuantVision Signal Backtester - 1 Day Historical Testing")
    print("="*60)
    
    # Initialize backtester
    backtester = SignalBacktester(initial_capital=1000.0)
    
    # Run backtest for yesterday
    backtest_date = datetime.now() - timedelta(days=1)
    print(f"Running backtest for: {backtest_date.strftime('%Y-%m-%d')}")
    
    try:
        results = await backtester.run_backtest(backtest_date)
        backtester.print_results(results)
        
        print(f"\n📁 Results saved to: {backtester.db_path}")
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        print(f"❌ Backtest failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())