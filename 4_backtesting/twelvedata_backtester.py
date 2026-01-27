#!/usr/bin/env python3
"""
Comprehensive Binary Options Backtester using Twelvedata API
Tests win rates across 1m, 5m, and 15m expiry times
Integrates with the project's unified signal system
"""

import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import time
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum

# Load API configuration
with open('api_config.json', 'r') as f:
    API_CONFIG = json.load(f)

TWELVEDATA_KEYS = API_CONFIG.get('twelvedata_api_keys', [])
CURRENT_KEY_INDEX = 0

# Constants
TWELVEDATA_BASE_URL = "https://api.twelvedata.com"
PAYOUT_RATE = 0.85  # 85% payout on winning trades
INITIAL_CAPITAL = 1000
POSITION_SIZE = 50  # Fixed position size per trade
MIN_CONFIDENCE_THRESHOLD = 70

# Trading pairs optimized for binary options
TRADING_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD",
    "USD/CHF", "EUR/GBP", "EUR/JPY", "GBP/JPY",
    "NZD/USD", "USD/CAD"
]


class ExpiryType(Enum):
    """Binary options expiry times"""
    ONE_MINUTE = "1m"
    FIVE_MINUTE = "5m"
    FIFTEEN_MINUTE = "15m"


@dataclass
class TradeSignal:
    """Represents a trading signal"""
    timestamp: datetime
    pair: str
    direction: str  # 'CALL' or 'PUT'
    confidence: float
    entry_price: float
    expiry: ExpiryType


@dataclass
class TradeResult:
    """Represents a completed trade"""
    signal: TradeSignal
    exit_price: float
    exit_timestamp: datetime
    profit: float
    loss: float
    pnl: float
    win: bool
    duration_seconds: int


@dataclass
class BacktestMetrics:
    """Comprehensive backtest metrics"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    total_profit: float
    total_loss: float
    net_pnl: float
    final_capital: float
    return_percent: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    sharpe_ratio: float
    max_drawdown: float
    recovery_factor: float


class TwelveDataBacktester:
    """
    Professional backtester for binary options using real Twelvedata data
    """
    
    def __init__(self, initial_capital: float = INITIAL_CAPITAL):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.trades = []
        self.equity_curve = [initial_capital]
        self.api_key_index = 0
        self.rate_limit_delay = 0.5  # seconds between API calls
        
    def _get_next_api_key(self):
        """Rotate through API keys to avoid rate limits"""
        global CURRENT_KEY_INDEX
        if not TWELVEDATA_KEYS:
            raise Exception("No Twelvedata API keys found in api_config.json")
        key = TWELVEDATA_KEYS[CURRENT_KEY_INDEX % len(TWELVEDATA_KEYS)]
        CURRENT_KEY_INDEX = (CURRENT_KEY_INDEX + 1) % len(TWELVEDATA_KEYS)
        return key
    
    def _generate_synthetic_data(self, pair: str, num_candles: int = 1000, 
                               interval_minutes: int = 5) -> pd.DataFrame:
        """
        Generate realistic synthetic OHLCV data for testing
        Uses random walk with trend and mean reversion
        """
        np.random.seed(42)
        
        # Starting parameters
        start_price = 1.0800
        dates = pd.date_range(end=datetime.now(), periods=num_candles, freq=f'{interval_minutes}min')
        
        # Generate price data with trend and volatility
        returns = []
        current_price = start_price
        
        for i in range(num_candles):
            # Random walk with mean reversion
            drift = 0.0001 if i > num_candles // 2 else -0.00005
            volatility = np.random.normal(0, 0.001)
            mean_reversion = -(current_price - start_price) * 0.0001
            
            price_change = drift + volatility + mean_reversion
            current_price = current_price * (1 + price_change)
            returns.append(current_price)
        
        # Create OHLC from returns
        data = []
        for i, (date, close) in enumerate(zip(dates, returns)):
            # Create realistic OHLC
            daily_open = close * (1 + np.random.normal(0, 0.0005))
            daily_high = max(close, daily_open) * (1 + abs(np.random.normal(0, 0.0005)))
            daily_low = min(close, daily_open) * (1 - abs(np.random.normal(0, 0.0005)))
            volume = np.random.uniform(1000000, 5000000)
            
            data.append({
                'datetime': date,
                'open': daily_open,
                'high': daily_high,
                'low': daily_low,
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('datetime').reset_index(drop=True)
        
        print(f"✓ Generated {len(df)} synthetic candles for {pair}")
        
        # Add technical indicators
        df = self._add_technical_indicators(df)
        
        return df
    
    def _fetch_historical_data(self, pair: str, interval: str, lookback_bars: int = 1000, use_synthetic: bool = False) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data from Twelvedata or generate synthetic data
        
        Args:
            pair: Currency pair (e.g., "EUR/USD")
            interval: Time interval (e.g., "1min", "5min", "15min")
            lookback_bars: Number of bars to fetch
            use_synthetic: If True, generate synthetic data instead of API call
        
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        
        # Try synthetic data first for testing/demo
        if use_synthetic:
            interval_minutes = {
                '1min': 1,
                '5min': 5,
                '15min': 15
            }.get(interval, 5)
            return self._generate_synthetic_data(pair, num_candles=lookback_bars, interval_minutes=interval_minutes)
        
        try:
            api_key = self._get_next_api_key()
            time.sleep(self.rate_limit_delay)  # Respect rate limits
            
            # Convert pair format for Twelvedata
            # Twelvedata uses format like EURUSD or EUR/USD
            symbol = pair.replace('/', '')
            
            url = f"{TWELVEDATA_BASE_URL}/time_series"
            params = {
                'symbol': symbol,
                'interval': interval,
                'outputsize': min(lookback_bars, 5000),  # API limit
                'apikey': api_key,
                'format': 'JSON'
            }
            
            print(f"Fetching from: {url} with params: symbol={symbol}, interval={interval}")
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for errors in response
            if 'error' in data:
                print(f"API Error: {data.get('error', {}).get('description', 'Unknown error')}")
                print(f"Full response: {data}")
                return None
            
            if 'values' not in data or not data['values']:
                print(f"No data available for {pair} with interval {interval}")
                print(f"Response: {data}")
                return None
            
            # Convert to DataFrame
            df_data = []
            for candle in data['values']:
                try:
                    df_data.append({
                        'datetime': pd.to_datetime(candle['datetime']),
                        'open': float(candle['open']),
                        'high': float(candle['high']),
                        'low': float(candle['low']),
                        'close': float(candle['close']),
                        'volume': float(candle.get('volume', 0))
                    })
                except (KeyError, ValueError, TypeError) as e:
                    print(f"Error parsing candle: {e}")
                    continue
            
            if not df_data:
                print(f"No valid data could be parsed for {pair}")
                return None
            
            df = pd.DataFrame(df_data)
            df = df.sort_values('datetime').reset_index(drop=True)
            
            print(f"✓ Loaded {len(df)} candles for {pair}")
            
            # Add technical indicators
            df = self._add_technical_indicators(df)
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Request error fetching data for {pair}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error fetching data for {pair}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add essential technical indicators"""
        try:
            # Simple Moving Averages
            df['sma_9'] = df['close'].rolling(window=9).mean()
            df['sma_21'] = df['close'].rolling(window=21).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            
            # RSI (Relative Strength Index)
            df['rsi'] = self._calculate_rsi(df['close'], 14)
            
            # MACD
            df['macd'], df['macd_signal'], df['macd_hist'] = self._calculate_macd(df['close'])
            
            # Bollinger Bands
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = self._calculate_bollinger_bands(df['close'], 20)
            
            # ATR (Average True Range) for volatility
            df['atr'] = self._calculate_atr(df, 14)
            
            return df
            
        except Exception as e:
            print(f"Error adding indicators: {e}")
            return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, num_std: int = 2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)
        return upper, sma, lower
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(period).mean()
        return atr
    
    def _generate_signal(self, df: pd.DataFrame, idx: int) -> Optional[TradeSignal]:
        """
        Generate trading signal using integrated analysis
        Similar to the project's unified confidence system
        """
        if idx < 50 or len(df) - idx < 10:  # Need enough data for indicators
            return None
        
        current = df.iloc[idx]
        signal_direction = None
        confidence = 50
        
        try:
            # Technical Analysis Scoring System
            score = 0
            
            # 1. Moving Average Trend Analysis (25% weight)
            if current['close'] > current['sma_9'] > current['sma_21']:
                score += 2
                confidence += 15
            elif current['close'] < current['sma_9'] < current['sma_21']:
                score -= 2
                confidence += 15
            
            # 2. RSI Analysis (20% weight)
            if current['rsi'] < 30:  # Oversold - CALL signal
                score += 1.5
                confidence += 12
            elif current['rsi'] > 70:  # Overbought - PUT signal
                score -= 1.5
                confidence += 12
            
            # 3. MACD Analysis (20% weight)
            if current['macd'] > current['macd_signal'] and df.iloc[idx-1]['macd'] <= df.iloc[idx-1]['macd_signal']:
                score += 1.5  # Bullish crossover
                confidence += 10
            elif current['macd'] < current['macd_signal'] and df.iloc[idx-1]['macd'] >= df.iloc[idx-1]['macd_signal']:
                score -= 1.5  # Bearish crossover
                confidence += 10
            
            # 4. Bollinger Bands Position (15% weight)
            bb_position = (current['close'] - current['bb_lower']) / (current['bb_upper'] - current['bb_lower'] + 1e-10)
            if bb_position < 0.2:  # Near lower band
                score += 1
                confidence += 8
            elif bb_position > 0.8:  # Near upper band
                score -= 1
                confidence += 8
            
            # 5. Price Action / Momentum (20% weight)
            if len(df) > 5:
                recent_high = df['high'].iloc[idx-5:idx].max()
                recent_low = df['low'].iloc[idx-5:idx].min()
                
                if current['close'] == recent_high:
                    score += 0.5
                    confidence += 5
                elif current['close'] == recent_low:
                    score -= 0.5
                    confidence += 5
            
            # Determine final signal
            if score >= 2:
                signal_direction = "CALL"
                confidence = min(90, confidence + (score * 3))
            elif score <= -2:
                signal_direction = "PUT"
                confidence = min(90, confidence + (abs(score) * 3))
            else:
                return None  # Neutral signal - skip trade
            
            # Apply confidence threshold
            confidence = min(95, max(confidence, 20))
            
            if confidence < MIN_CONFIDENCE_THRESHOLD:
                return None
            
            return TradeSignal(
                timestamp=current['datetime'],
                pair="MULTI",
                direction=signal_direction,
                confidence=confidence,
                entry_price=current['close'],
                expiry=ExpiryType.FIVE_MINUTE  # Default to 5m
            )
            
        except Exception as e:
            print(f"Error generating signal: {e}")
            return None
    
    def _check_trade_outcome(self, df: pd.DataFrame, entry_idx: int, 
                            signal: TradeSignal, expiry_bars: int) -> Optional[TradeResult]:
        """
        Determine trade outcome based on expiry time
        
        Args:
            df: Price data
            entry_idx: Index of entry
            signal: The trading signal
            expiry_bars: Number of bars until expiry
        """
        try:
            exit_idx = min(entry_idx + expiry_bars, len(df) - 1)
            
            if exit_idx == entry_idx:
                return None
            
            exit_price = df.iloc[exit_idx]['close']
            exit_timestamp = df.iloc[exit_idx]['datetime']
            
            # Determine win/loss
            if signal.direction == "CALL":
                win = exit_price > signal.entry_price
            else:  # PUT
                win = exit_price < signal.entry_price
            
            # Calculate P&L
            if win:
                profit = POSITION_SIZE * PAYOUT_RATE
                loss = 0
                pnl = profit - POSITION_SIZE
            else:
                profit = 0
                loss = POSITION_SIZE
                pnl = -POSITION_SIZE
            
            duration = int((exit_timestamp - signal.timestamp).total_seconds())
            
            return TradeResult(
                signal=signal,
                exit_price=exit_price,
                exit_timestamp=exit_timestamp,
                profit=profit,
                loss=loss,
                pnl=pnl,
                win=win,
                duration_seconds=duration
            )
            
        except Exception as e:
            print(f"Error checking trade outcome: {e}")
            return None
    
    def _backtest_data(self, df: pd.DataFrame, expiry_type: ExpiryType, 
                      pair: str = "MULTI") -> List[TradeResult]:
        """
        Execute backtest on data with specific expiry time
        
        Args:
            df: Price data with indicators
            expiry_type: Expiry time (1m, 5m, 15m)
            pair: Trading pair name
        
        Returns:
            List of trade results
        """
        trades = []
        expiry_bars_map = {
            ExpiryType.ONE_MINUTE: 1,
            ExpiryType.FIVE_MINUTE: 5,
            ExpiryType.FIFTEEN_MINUTE: 15
        }
        expiry_bars = expiry_bars_map.get(expiry_type, 5)
        
        # Scan through data
        for idx in range(50, len(df) - expiry_bars - 1):
            signal = self._generate_signal(df, idx)
            
            if signal is None:
                continue
            
            # Update expiry for signal
            signal.expiry = expiry_type
            signal.pair = pair
            
            # Check trade outcome
            result = self._check_trade_outcome(df, idx, signal, expiry_bars)
            
            if result is not None:
                trades.append(result)
                
                # Update capital
                self.current_capital += result.pnl
                self.equity_curve.append(self.current_capital)
        
        return trades
    
    def _calculate_metrics(self, trades: List[TradeResult]) -> BacktestMetrics:
        """Calculate comprehensive backtest metrics"""
        if not trades:
            return BacktestMetrics(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0,
                profit_factor=0,
                total_profit=0,
                total_loss=0,
                net_pnl=0,
                final_capital=self.initial_capital,
                return_percent=0,
                avg_win=0,
                avg_loss=0,
                largest_win=0,
                largest_loss=0,
                consecutive_wins=0,
                consecutive_losses=0,
                sharpe_ratio=0,
                max_drawdown=0,
                recovery_factor=0
            )
        
        winning_trades = [t for t in trades if t.win]
        losing_trades = [t for t in trades if not t.win]
        
        total_profit = sum(t.profit for t in trades)
        total_loss = sum(t.loss for t in trades)
        net_pnl = total_profit - total_loss
        
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        profit_factor = total_profit / (total_loss + 1e-10)
        
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([abs(t.pnl) for t in losing_trades]) if losing_trades else 0
        largest_win = max([t.pnl for t in winning_trades]) if winning_trades else 0
        largest_loss = min([t.pnl for t in losing_trades]) if losing_trades else 0
        
        # Consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        for trade in trades:
            if trade.win:
                consecutive_wins += 1
                consecutive_losses = 0
            else:
                consecutive_losses += 1
                consecutive_wins = 0
            max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        # Sharpe Ratio
        if len(self.equity_curve) > 1:
            returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
            sharpe = np.mean(returns) / (np.std(returns) + 1e-10) * np.sqrt(252)
        else:
            sharpe = 0
        
        # Max Drawdown
        equity_array = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
        
        # Recovery Factor
        recovery_factor = abs(net_pnl) / (abs(max_drawdown * self.initial_capital) + 1e-10)
        
        return BacktestMetrics(
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_profit=total_profit,
            total_loss=total_loss,
            net_pnl=net_pnl,
            final_capital=self.current_capital,
            return_percent=(self.current_capital - self.initial_capital) / self.initial_capital * 100,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            consecutive_wins=max_consecutive_wins,
            consecutive_losses=max_consecutive_losses,
            sharpe_ratio=sharpe,
            max_drawdown=abs(max_drawdown),
            recovery_factor=recovery_factor
        )
    
    async def run_backtest(self, test_duration_days: int = 30, use_synthetic: bool = True) -> Dict[str, any]:
        """
        Run comprehensive backtest across multiple pairs and expiry times
        
        Args:
            test_duration_days: Number of days to backtest
            use_synthetic: If True, use synthetic data for testing (default True)
        
        Returns:
            Complete backtest results
        """
        print("=" * 80)
        print("TWELVEDATA BINARY OPTIONS BACKTESTER")
        print(f"Mode: {'SYNTHETIC DATA (Demo)' if use_synthetic else 'LIVE TWELVEDATA API'}")
        print("=" * 80)
        
        all_results = {
            'metadata': {
                'backtest_date': datetime.now().isoformat(),
                'initial_capital': self.initial_capital,
                'position_size': POSITION_SIZE,
                'payout_rate': PAYOUT_RATE,
                'test_duration_days': test_duration_days,
                'min_confidence_threshold': MIN_CONFIDENCE_THRESHOLD,
                'trading_pairs_tested': len(TRADING_PAIRS)
            },
            'results_by_expiry': {},
            'overall_metrics': {},
            'summary': {}
        }
        
        # Test each expiry time
        for expiry_type in [ExpiryType.ONE_MINUTE, ExpiryType.FIVE_MINUTE, ExpiryType.FIFTEEN_MINUTE]:
            print(f"\n{'='*80}")
            print(f"Testing {expiry_type.value} Expiry")
            print(f"{'='*80}")
            
            self.current_capital = self.initial_capital
            self.equity_curve = [self.initial_capital]
            self.trades = []
            
            # Fetch data for one pair as representative
            test_pair = TRADING_PAIRS[0]
            print(f"\nFetching historical data for {test_pair}...")
            
            # Convert expiry to interval for API call
            interval_map = {
                ExpiryType.ONE_MINUTE: "1min",
                ExpiryType.FIVE_MINUTE: "5min",
                ExpiryType.FIFTEEN_MINUTE: "15min"
            }
            interval = interval_map[expiry_type]
            
            df = self._fetch_historical_data(test_pair, interval, lookback_bars=1000, use_synthetic=use_synthetic)
            
            if df is None or len(df) < 100:
                print(f"Insufficient data for {test_pair}. Skipping...")
                continue
            
            print(f"Data retrieved: {len(df)} candles from {df['datetime'].min()} to {df['datetime'].max()}")
            
            # Run backtest
            print(f"Running backtest for {test_pair}...")
            trades = self._backtest_data(df, expiry_type, test_pair)
            self.trades = trades
            
            # Calculate metrics
            metrics = self._calculate_metrics(trades)
            
            # Store results
            expiry_key = expiry_type.value
            all_results['results_by_expiry'][expiry_key] = {
                'pair': test_pair,
                'metrics': asdict(metrics),
                'trades_count': len(trades),
                'sample_trades': [
                    {
                        'timestamp': t.signal.timestamp.isoformat(),
                        'direction': t.signal.direction,
                        'entry_price': t.signal.entry_price,
                        'exit_price': t.exit_price,
                        'confidence': t.signal.confidence,
                        'pnl': t.pnl,
                        'win': t.win
                    }
                    for t in trades[:10]  # Show first 10 trades as sample
                ]
            }
            
            # Print results
            self._print_metrics(metrics, expiry_type)
        
        # Summary statistics
        all_results['summary'] = self._generate_summary(all_results['results_by_expiry'])
        
        return all_results
    
    def _print_metrics(self, metrics: BacktestMetrics, expiry_type: ExpiryType):
        """Pretty print backtest metrics"""
        print(f"\n📊 Results for {expiry_type.value} Expiry:")
        print(f"{'─'*60}")
        print(f"Total Trades:        {metrics.total_trades}")
        print(f"Winning Trades:      {metrics.winning_trades}")
        print(f"Losing Trades:       {metrics.losing_trades}")
        print(f"{'─'*60}")
        print(f"💰 Win Rate:         {metrics.win_rate:.2f}%")
        print(f"💰 Profit Factor:    {metrics.profit_factor:.2f}")
        print(f"💰 Total Profit:     ${metrics.total_profit:.2f}")
        print(f"💰 Total Loss:       ${metrics.total_loss:.2f}")
        print(f"💰 Net P&L:          ${metrics.net_pnl:.2f}")
        print(f"{'─'*60}")
        print(f"Final Capital:       ${metrics.final_capital:.2f}")
        print(f"Return %:            {metrics.return_percent:.2f}%")
        print(f"Avg Win:             ${metrics.avg_win:.2f}")
        print(f"Avg Loss:            ${metrics.avg_loss:.2f}")
        print(f"Largest Win:         ${metrics.largest_win:.2f}")
        print(f"Largest Loss:        ${metrics.largest_loss:.2f}")
        print(f"{'─'*60}")
        print(f"Consecutive Wins:    {metrics.consecutive_wins}")
        print(f"Consecutive Losses:  {metrics.consecutive_losses}")
        print(f"Sharpe Ratio:        {metrics.sharpe_ratio:.4f}")
        print(f"Max Drawdown:        {metrics.max_drawdown:.4f}")
        print(f"Recovery Factor:     {metrics.recovery_factor:.2f}")
    
    def _generate_summary(self, results_by_expiry: Dict) -> Dict:
        """Generate summary across all expiry times"""
        summary = {
            'best_winrate_expiry': None,
            'best_winrate': 0,
            'best_pnl_expiry': None,
            'best_pnl': 0,
            'average_winrate': 0,
            'total_trades_all_expiries': 0
        }
        
        winrates = []
        pnls = []
        
        for expiry, data in results_by_expiry.items():
            metrics = data['metrics']
            winrate = metrics['win_rate']
            pnl = metrics['net_pnl']
            
            winrates.append(winrate)
            pnls.append(pnl)
            
            if winrate > summary['best_winrate']:
                summary['best_winrate_expiry'] = expiry
                summary['best_winrate'] = winrate
            
            if pnl > summary['best_pnl']:
                summary['best_pnl_expiry'] = expiry
                summary['best_pnl'] = pnl
            
            summary['total_trades_all_expiries'] += metrics['total_trades']
        
        if winrates:
            summary['average_winrate'] = np.mean(winrates)
        
        return summary


async def main():
    """Main execution"""
    backtester = TwelveDataBacktester(initial_capital=INITIAL_CAPITAL)
    
    print("\n🚀 Starting Binary Options Backtester with Twelvedata API...\n")
    
    try:
        results = await backtester.run_backtest(test_duration_days=30)
        
        # Save results to JSON
        output_file = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n✅ Backtest completed! Results saved to {output_file}")
        
        # Print summary
        print("\n" + "="*80)
        print("BACKTEST SUMMARY")
        print("="*80)
        summary = results.get('summary', {})
        print(f"\nBest Win Rate Expiry:  {summary.get('best_winrate_expiry')} ({summary.get('best_winrate', 0):.2f}%)")
        print(f"Best P&L Expiry:       {summary.get('best_pnl_expiry')} (${summary.get('best_pnl', 0):.2f})")
        print(f"Average Win Rate:      {summary.get('average_winrate', 0):.2f}%")
        print(f"Total Trades Tested:   {summary.get('total_trades_all_expiries', 0)}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error during backtest: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(main())
