#!/usr/bin/env python3
"""
Simple QuantVision Backtester Demo - 1 Day Signal Testing
Demonstrates comprehensive backtesting with metrics: Win Rate, Net Profit, Drawdown, Accuracy
"""

import pandas as pd
import numpy as np
import asyncio
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TradeResult:
    timestamp: datetime
    pair: str
    signal: str
    entry_price: float
    exit_price: float
    position_size: float
    result: str  # 'WIN' or 'LOSS'
    pnl: float
    confidence: float

class SimpleBacktester:
    def __init__(self, initial_capital=1000):
        self.initial_capital = initial_capital
        self.position_size = 50.0  # $50 per trade
        self.payout_rate = 0.85   # 85% payout
        self.expiry_minutes = 5
        self.trades = []
        self.equity_curve = [initial_capital]
        
        # Create database
        self.setup_database()
    
    def setup_database(self):
        """Create database for storing results"""
        conn = sqlite3.connect("simple_backtest.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_trades (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                pair TEXT,
                signal TEXT,
                entry_price REAL,
                exit_price REAL,
                result TEXT,
                pnl REAL,
                confidence REAL
            )
        ''')
        conn.commit()
        conn.close()
    
    def generate_forex_data(self, pair: str, days: int = 30) -> pd.DataFrame:
        """Generate realistic forex data"""
        np.random.seed(42 + hash(pair) % 100)
        
        # Base prices
        base_prices = {
            "EUR/USD": 1.0800, "GBP/USD": 1.2500, "USD/JPY": 150.00,
            "AUD/USD": 0.6600, "USD/CHF": 0.9000
        }
        base_price = base_prices.get(pair, 1.0000)
        
        # Generate 5-minute data for specified days (288 candles per day)  
        periods = 288 * days
        timestamps = [datetime.now() - timedelta(days=days) + timedelta(minutes=5*i) for i in range(periods)]
        
        # Generate realistic price movement
        returns = np.random.normal(0, 0.0008, periods)  # Realistic forex volatility
        trend_component = np.sin(np.arange(periods) * 2 * np.pi / 144) * 0.0003  # Intraday pattern
        
        prices = [base_price]
        for i in range(1, periods):
            new_price = prices[-1] * (1 + returns[i] + trend_component[i])
            prices.append(new_price)
        
        # Create OHLCV data
        data = []
        for i, timestamp in enumerate(timestamps):
            close = prices[i]
            open_price = close * (1 + np.random.normal(0, 0.0001))
            high = max(open_price, close) * (1 + abs(np.random.normal(0, 0.0003)))
            low = min(open_price, close) * (1 - abs(np.random.normal(0, 0.0003)))
            volume = np.random.uniform(1000, 8000)
            
            data.append({
                'timestamp': timestamp,
                'open': open_price,
                'high': high, 
                'low': low,
                'close': close,
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        df = df.copy()
        
        # Moving averages
        df['sma_10'] = df['close'].rolling(10, min_periods=1).mean()
        df['sma_20'] = df['close'].rolling(20, min_periods=1).mean()
        df['ema_9'] = df['close'].ewm(span=9).mean()
        
        # RSI with safe division
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14, min_periods=1).mean()
        # Prevent division by zero
        rs = gain / loss.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))
        df['rsi'] = df['rsi'].fillna(50)  # Fill NaN with neutral RSI value
        
        # MACD
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(20, min_periods=1).mean()
        bb_std = df['close'].rolling(20, min_periods=1).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        return df
    
    def generate_signal(self, df: pd.DataFrame, i: int) -> Dict:
        """Generate trading signal based on technical analysis"""
        if i < 30:  # Need enough data for indicators
            return {'signal': 'NEUTRAL', 'confidence': 0}
        
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        # Initialize scoring
        score = 0
        confidence = 50
        
        # Trend analysis
        if current['close'] > current['sma_10'] > current['sma_20']:
            score += 2
            confidence += 15
        elif current['close'] < current['sma_10'] < current['sma_20']:
            score -= 2
            confidence += 15
        
        # RSI signals
        if current['rsi'] < 30:  # Oversold
            score += 1
            confidence += 10
        elif current['rsi'] > 70:  # Overbought
            score -= 1
            confidence += 10
        
        # MACD signals
        if (current['macd'] > current['macd_signal'] and 
            prev['macd'] <= prev['macd_signal']):  # MACD cross up
            score += 1
            confidence += 10
        elif (current['macd'] < current['macd_signal'] and 
              prev['macd'] >= prev['macd_signal']):  # MACD cross down
            score -= 1
            confidence += 10
        
        # Bollinger Bands
        if current['close'] < current['bb_lower']:  # Oversold
            score += 1
            confidence += 8
        elif current['close'] > current['bb_upper']:  # Overbought
            score -= 1
            confidence += 8
        
        # Price momentum
        price_change = (current['close'] - prev['close']) / prev['close']
        if abs(price_change) > 0.0005:  # Significant move
            if price_change > 0:
                score += 1
            else:
                score -= 1
            confidence += 5
        
        # Determine final signal
        if score >= 2:
            signal = 'CALL'
            confidence = min(85, confidence + abs(score) * 5)
        elif score <= -2:
            signal = 'PUT'
            confidence = min(85, confidence + abs(score) * 5)
        else:
            signal = 'NEUTRAL'
            confidence = max(30, confidence - 10)
        
        return {
            'signal': signal,
            'confidence': confidence,
            'score': score,
            'indicators': {
                'rsi': current['rsi'],
                'macd': current['macd'],
                'bb_position': (current['close'] - current['bb_lower']) / (current['bb_upper'] - current['bb_lower'])
            }
        }
    
    def determine_outcome(self, entry_price: float, exit_price: float, signal: str) -> Tuple[str, float]:
        """Determine trade outcome"""
        if signal == 'CALL':
            if exit_price > entry_price:
                return 'WIN', self.position_size * self.payout_rate
            else:
                return 'LOSS', -self.position_size
        elif signal == 'PUT':
            if exit_price < entry_price:
                return 'WIN', self.position_size * self.payout_rate
            else:
                return 'LOSS', -self.position_size
        else:
            return 'LOSS', -self.position_size
    
    async def backtest_pair(self, pair: str, data: pd.DataFrame) -> List[TradeResult]:
        """Backtest a single currency pair"""
        logger.info(f"Backtesting {pair} with {len(data)} data points")
        
        # Calculate indicators
        data = self.calculate_indicators(data)
        
        trades = []
        
        # Trade every 20 candles (1.67 hours) starting from index 50 - more frequent for 30-day test
        for i in range(50, len(data) - self.expiry_minutes, 20):
            # Generate signal
            analysis = self.generate_signal(data, i)
            
            if analysis['signal'] == 'NEUTRAL' or analysis['confidence'] < 65:
                continue
            
            # Entry details
            entry_time = data.iloc[i]['timestamp']
            entry_price = data.iloc[i]['close']
            
            # Exit after 5 minutes
            exit_idx = i + self.expiry_minutes
            exit_time = data.iloc[exit_idx]['timestamp']
            exit_price = data.iloc[exit_idx]['close']
            
            # Determine outcome
            result, pnl = self.determine_outcome(entry_price, exit_price, analysis['signal'])
            
            # Create trade record
            trade = TradeResult(
                timestamp=entry_time,
                pair=pair,
                signal=analysis['signal'],
                entry_price=entry_price,
                exit_price=exit_price,
                position_size=self.position_size,
                result=result,
                pnl=pnl,
                confidence=analysis['confidence']
            )
            
            trades.append(trade)
            self.equity_curve.append(self.equity_curve[-1] + pnl)
            
            logger.debug(f"{pair} {analysis['signal']} @ {entry_price:.5f} -> {exit_price:.5f} = {result} ({pnl:+.2f})")
        
        return trades
    
    async def run_backtest(self) -> Dict:
        """Run comprehensive backtest"""
        logger.info(f"Starting {30}-day comprehensive backtest...")
        
        pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF"]
        all_trades = []
        
        for pair in pairs:
            try:
                # Generate data
                data = self.generate_forex_data(pair, days=30)
                
                # Backtest pair
                trades = await self.backtest_pair(pair, data)
                all_trades.extend(trades)
                
                logger.info(f"Completed {pair}: {len(trades)} trades")
                
            except Exception as e:
                logger.error(f"Error backtesting {pair}: {e}")
                continue
        
        # Store trades
        self.trades = all_trades
        
        # Calculate results
        results = self.calculate_results()
        
        # Save to database
        self.save_to_database()
        
        return results
    
    def calculate_results(self) -> Dict:
        """Calculate comprehensive results"""
        if not self.trades:
            return {
                'total_trades': 0, 'win_rate': 0, 'net_profit': 0, 
                'max_drawdown': 0, 'accuracy': 0
            }
        
        total_trades = len(self.trades)
        wins = sum(1 for t in self.trades if t.result == 'WIN')
        win_rate = (wins / total_trades) * 100
        
        # P&L
        net_profit = sum(t.pnl for t in self.trades)
        best_trade = max(t.pnl for t in self.trades)
        worst_trade = min(t.pnl for t in self.trades)
        
        # Drawdown calculation
        peak = self.initial_capital
        max_drawdown = 0
        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
            drawdown = peak - equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        max_drawdown_pct = (max_drawdown / self.initial_capital) * 100
        
        # Accuracy (correct direction)
        correct = 0
        for t in self.trades:
            if ((t.signal == 'CALL' and t.exit_price > t.entry_price) or
                (t.signal == 'PUT' and t.exit_price < t.entry_price)):
                correct += 1
        
        accuracy = (correct / total_trades) * 100
        
        # Per-pair performance
        pairs_perf = {}
        for pair in set(t.pair for t in self.trades):
            pair_trades = [t for t in self.trades if t.pair == pair]
            pair_wins = sum(1 for t in pair_trades if t.result == 'WIN')
            pairs_perf[pair] = {
                'trades': len(pair_trades),
                'win_rate': (pair_wins / len(pair_trades)) * 100,
                'pnl': sum(t.pnl for t in pair_trades)
            }
        
        return {
            'total_trades': total_trades,
            'winning_trades': wins,
            'losing_trades': total_trades - wins,
            'win_rate': win_rate,
            'net_profit': net_profit,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'accuracy': accuracy,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'avg_confidence': sum(t.confidence for t in self.trades) / total_trades,
            'pairs_performance': pairs_perf,
            'final_capital': self.initial_capital + net_profit
        }
    
    def save_to_database(self):
        """Save trades to database"""
        conn = sqlite3.connect("simple_backtest.db")
        cursor = conn.cursor()
        
        # Clear old data
        cursor.execute("DELETE FROM backtest_trades")
        
        # Insert new trades
        for trade in self.trades:
            cursor.execute('''
                INSERT INTO backtest_trades 
                (timestamp, pair, signal, entry_price, exit_price, result, pnl, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.timestamp.isoformat(),
                trade.pair,
                trade.signal,
                trade.entry_price,
                trade.exit_price,
                trade.result,
                trade.pnl,
                trade.confidence
            ))
        
        conn.commit()
        conn.close()
    
    def print_results(self, results: Dict):
        """Print comprehensive results"""
        print("\n" + "="*70)
        print("🎯 QUANTVISION 30-DAY SIGNAL BACKTEST RESULTS")
        print("="*70)
        
        print(f"\n💰 CAPITAL MANAGEMENT")
        print(f"   Initial Capital:  ${self.initial_capital:,.2f}")
        print(f"   Final Capital:    ${results['final_capital']:,.2f}")
        print(f"   Position Size:    ${self.position_size} per trade")
        print(f"   Payout Rate:      {self.payout_rate*100}%")
        
        print(f"\n📊 TRADING PERFORMANCE")
        print(f"   Total Trades:     {results['total_trades']}")
        print(f"   Winning Trades:   {results['winning_trades']}")
        print(f"   Losing Trades:    {results['losing_trades']}")
        print(f"   Win Rate:         {results['win_rate']:.1f}%")
        print(f"   Accuracy:         {results['accuracy']:.1f}%")
        print(f"   Avg Confidence:   {results['avg_confidence']:.1f}%")
        
        print(f"\n💵 PROFIT & LOSS")
        print(f"   Net Profit:       ${results['net_profit']:+,.2f}")
        print(f"   Return:           {(results['net_profit']/self.initial_capital)*100:+.1f}%")
        print(f"   Best Trade:       ${results['best_trade']:+,.2f}")
        print(f"   Worst Trade:      ${results['worst_trade']:+,.2f}")
        
        print(f"\n📉 RISK ANALYSIS")
        print(f"   Max Drawdown:     ${results['max_drawdown']:,.2f}")
        print(f"   Max DD %:         {results['max_drawdown_pct']:.1f}%")
        print(f"   Risk-Return:      {results['net_profit']/max(results['max_drawdown'], 1):+.2f}")
        
        if results['pairs_performance']:
            print(f"\n🌍 PAIRS PERFORMANCE")
            for pair, perf in sorted(results['pairs_performance'].items(), 
                                   key=lambda x: x[1]['pnl'], reverse=True):
                print(f"   {pair:<8} | {perf['trades']:2d} trades | {perf['win_rate']:5.1f}% WR | ${perf['pnl']:+7.2f}")
        
        print(f"\n🎯 SUMMARY")
        if results['net_profit'] > 0:
            print(f"   ✅ PROFITABLE STRATEGY")
            print(f"   Generated ${results['net_profit']:.2f} profit in 30 days")
        else:
            print(f"   ❌ UNPROFITABLE STRATEGY")
            print(f"   Lost ${abs(results['net_profit']):.2f} in 30 days")
        
        print("="*70)

async def main():
    """Run the backtester"""
    print("QuantVision Simple Signal Backtester")
    print("Testing 30 days of signals with comprehensive metrics")
    print("-" * 50)
    
    # Create backtester
    backtester = SimpleBacktester(initial_capital=1000.0)
    
    # Run backtest
    results = await backtester.run_backtest()
    
    # Print results
    backtester.print_results(results)
    
    print(f"\n📁 Results saved to: simple_backtest.db")
    print(f"Generated {len(backtester.trades)} trades for analysis")

if __name__ == "__main__":
    asyncio.run(main())