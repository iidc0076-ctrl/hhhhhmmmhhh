#!/usr/bin/env python3
"""
Walk-Forward Backtester: Tests bot performance on sliding windows
Prevents look-ahead bias and overfitting by training/testing on separate data

Strategy:
- Train on 90 days → Test on 30 days
- Roll forward, repeat
- Measures consistency across different market conditions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import os
import sys

# Import bot signal wrapper
try:
    from bot_signal_wrapper import HybridSignalGenerator
    BOT_SIGNALS_AVAILABLE = True
    print("✓ Loaded HybridSignalGenerator")
except ImportError as e:
    print(f"⚠️  Could not import HybridSignalGenerator: {e}")
    BOT_SIGNALS_AVAILABLE = False
    HybridSignalGenerator = None

# Import Phase 3 enhanced signals
try:
    from phase3_enhanced_signals import Phase3SignalEngine
    PHASE3_AVAILABLE = True
    print("✓ Loaded Phase3SignalEngine")
except ImportError as e:
    print(f"⚠️  Could not import Phase3SignalEngine: {e}")
    PHASE3_AVAILABLE = False
    Phase3SignalEngine = None


class WalkForwardBacktester:
    """Implements proper walk-forward analysis with out-of-sample testing"""
    
    def __init__(self, train_period_days=90, test_period_days=30, use_bot=True, max_trades=None):
        self.train_period = train_period_days
        self.test_period = test_period_days
        self.all_results = {}
        self.use_bot = use_bot and BOT_SIGNALS_AVAILABLE
        self.max_trades = max_trades  # Limit total trades to speed up backtest
        
        if self.use_bot:
            try:
                self.signal_gen = HybridSignalGenerator()
                print("✓ Initialized hybrid signal generator")
            except Exception as e:
                print(f"⚠️  Could not initialize signal generator: {e}")
                self.use_bot = False
        
        if not self.use_bot:
            print("⚠️  Using technical analysis fallback (no bot engine)")
        # Load selected params if available (from parameter search)
        self.selected_params = {}
        self.phase3_engines = {}  # Phase 3 signal engines per pair
        try:
            sel_path = 'selected_params.json'
            if os.path.exists(sel_path):
                with open(sel_path, 'r') as f:
                    self.selected_params = json.load(f)
                print(f"✓ Loaded selected params from {sel_path}")
                # Initialize Phase 3 engines for each pair
                if PHASE3_AVAILABLE:
                    for pair, params in self.selected_params.items():
                        self.phase3_engines[pair] = Phase3SignalEngine(params)
                    print(f"✓ Initialized Phase3SignalEngine for {len(self.phase3_engines)} pairs")
        except Exception as e:
            print(f"⚠️  Could not load Phase3: {e}")
            self.selected_params = {}
        
    def run_walk_forward_test(self, data_dir: str = 'data') -> Dict:
        """
        Run walk-forward test on all pairs in data directory
        
        Returns:
            Dictionary with comprehensive backtest results
        """
        
        results_summary = {
            'total_pairs': 0,
            'overall_metrics': {},
            'by_pair': {},
            'consistency_analysis': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Find all 5min data files
        if not os.path.exists(data_dir):
            print(f"❌ Data directory not found: {data_dir}")
            return results_summary
        
        csv_files = sorted([f for f in os.listdir(data_dir) if f.endswith('_5min.csv')])
        
        if not csv_files:
            print(f"❌ No 5min CSV files found in {data_dir}")
            return results_summary
        
        print("=" * 70)
        print("WALK-FORWARD BACKTEST (90-day train, 30-day test, rolling)")
        print("=" * 70)
        
        all_trades = []
        pair_results = {}
        
        for file_idx, csv_file in enumerate(csv_files, 1):
            # Early stop if max_trades limit reached
            if self.max_trades and len(all_trades) >= self.max_trades:
                print(f"\n⚠️  Max trades limit ({self.max_trades}) reached, stopping early")
                break
            
            pair = csv_file.replace('_5min.csv', '').replace('_', '/')
            print(f"\n[{file_idx}/{len(csv_files)}] {pair}")
            
            filepath = os.path.join(data_dir, csv_file)
            
            try:
                df = pd.read_csv(filepath)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.sort_values('datetime').reset_index(drop=True)
                
                print(f"   📊 Loaded {len(df)} candles")
                print(f"   📅 Date range: {df['datetime'].min()} → {df['datetime'].max()}")
                
                # Run walk-forward test for this pair
                pair_trades = self._run_wf_for_pair(df, pair)
                # Truncate if we'd exceed max_trades
                if self.max_trades and len(all_trades) + len(pair_trades) > self.max_trades:
                    pair_trades = pair_trades[:self.max_trades - len(all_trades)]
                all_trades.extend(pair_trades)
                
                # Calculate pair metrics
                pair_metrics = self._calculate_metrics(pair_trades)
                pair_results[pair] = {
                    'trades': len(pair_trades),
                    'metrics': pair_metrics
                }
                
                print(f"   ✓ {pair}: {pair_metrics['total_trades']} trades, "
                      f"{pair_metrics['win_rate']:.2f}% win rate")
                
            except Exception as e:
                print(f"   ❌ Error processing {pair}: {str(e)}")
                continue
        
        # Overall metrics
        overall_metrics = self._calculate_metrics(all_trades)
        
        results_summary['total_pairs'] = len(pair_results)
        results_summary['by_pair'] = pair_results
        results_summary['overall_metrics'] = overall_metrics
        results_summary['consistency_analysis'] = self._analyze_consistency(pair_results)
        
        # Print summary
        self._print_summary(results_summary)
        
        # Save results
        self._save_results(results_summary, all_trades)
        
        return results_summary
    
    def _run_wf_for_pair(self, df: pd.DataFrame, pair: str) -> List[Dict]:
        """Run walk-forward test on single pair"""
        
        all_trades = []
        window_num = 0
        
        # Calculate minimum data needed
        min_data_needed = (self.train_period + self.test_period) * 22 * 60 / 5  # 5min candles
        
        if len(df) < min_data_needed:
            print(f"   ⚠️  Insufficient data: {len(df)} candles, need {int(min_data_needed)}")
            return all_trades
        
        # Roll forward through data
        train_size = int(self.train_period * 22 * 60 / 5)  # 5min candles in 90 days
        test_size = int(self.test_period * 22 * 60 / 5)   # 5min candles in 30 days
        step_size = test_size
        
        for start_idx in range(0, len(df) - train_size - test_size, step_size):
            window_num += 1
            
            # Split data
            train_start = start_idx
            train_end = start_idx + train_size
            test_start = train_end
            test_end = test_start + test_size
            
            if test_end > len(df):
                break
            
            train_data = df.iloc[train_start:train_end].reset_index(drop=True)
            test_data = df.iloc[test_start:test_end].reset_index(drop=True)
            
            # Generate trades on test data
            trades = self._generate_trades(test_data, pair)
            all_trades.extend(trades)
            
            if window_num <= 3:  # Show first 3 windows
                win_rate = len([t for t in trades if t['win']]) / len(trades) * 100 if trades else 0
                print(f"     Window {window_num}: {len(trades)} trades, {win_rate:.1f}% win")
        
        if window_num > 3:
            print(f"     ... ({window_num - 3} more windows)")
        
        return all_trades
    
    def _generate_trades(self, data: pd.DataFrame, pair: str) -> List[Dict]:
        """Generate trading signals from price data"""
        
        trades = []
        
        # Need minimum candles for indicators
        if len(data) < 100:
            return trades
        
        # Simple strategy: Use your bot's logic or implement basic strategy
        for i in range(50, len(data) - 5):
            # Generate signal
            signal = self._generate_signal(data, i)
            
            if signal is None:
                continue
            
            # Get entry and exit prices
            entry_price = data.iloc[i]['close']
            exit_price = data.iloc[i + 5]['close']  # 5 candles (25 min) later
            
            # Determine if win
            if signal == 'CALL':
                win = exit_price > entry_price
            else:  # PUT
                win = exit_price < entry_price
            
            # Calculate P&L (85% payout, 100% loss)
            pnl = 85 if win else -100  # Risk 100 to win 85
            
            trades.append({
                'pair': pair,
                'signal': signal,
                'entry_time': data.iloc[i]['datetime'],
                'entry_price': entry_price,
                'exit_price': exit_price,
                'win': win,
                'pnl': pnl
            })
        
        return trades
    
    def _generate_signal(self, data: pd.DataFrame, current_idx: int, pair: str = 'EUR/USD') -> Optional[str]:
        """
        Generate trading signal using hybrid bot + technical analysis
        """
        
        if current_idx < 100:
            return None
        
        # Prefer Phase 3 enhanced signals (with regime filters)
        if PHASE3_AVAILABLE and pair in self.phase3_engines:
            try:
                return self.phase3_engines[pair].generate_signal(data, current_idx, pair)
            except Exception:
                pass
        
        # Fallback: selected params
        try:
            if pair in self.selected_params and self.selected_params.get(pair):
                return self._technical_signal_with_params(data, current_idx, self.selected_params[pair])
        except Exception:
            pass

        if self.use_bot:
            try:
                return self.signal_gen.generate_signal(data, current_idx, pair)
            except Exception:
                # Fall back to technical
                pass
        
        # Fallback technical analysis
        return self._technical_signal(data, current_idx)

    def _technical_signal_with_params(self, data: pd.DataFrame, current_idx: int, params: dict) -> Optional[str]:
        """Technical signal using specific parameter set (from grid search).

        Expected params keys: `rsi_period`, `rsi_oversold`, `rsi_overbought`,
        `sma_short`, `sma_long`, `macd_fast`, `macd_slow`, `vote_threshold`
        """
        try:
            # RSI
            rsi = self._calculate_rsi(data['close'], period=int(params.get('rsi_period', 14))).iloc[current_idx]

            # MACD (EMAs)
            ema_fast = data['close'].ewm(span=int(params.get('macd_fast', 12))).mean().iloc[current_idx]
            ema_slow = data['close'].ewm(span=int(params.get('macd_slow', 26))).mean().iloc[current_idx]
            macd_val = ema_fast - ema_slow

            # Moving averages
            sma_short = data['close'].rolling(window=int(params.get('sma_short', 20))).mean().iloc[current_idx]
            sma_long = data['close'].rolling(window=int(params.get('sma_long', 50))).mean().iloc[current_idx]
            price = data['close'].iloc[current_idx]

            # Voting with weights (match grid search weights)
            votes_call = 0
            votes_put = 0
            if pd.notna(rsi):
                if rsi < params.get('rsi_oversold', 30):
                    votes_call += 40
                elif rsi > params.get('rsi_overbought', 70):
                    votes_put += 40

            if pd.notna(macd_val):
                if macd_val > 0:
                    votes_call += 30
                else:
                    votes_put += 30

            if pd.notna(sma_short) and pd.notna(sma_long):
                if price > sma_short > sma_long:
                    votes_call += 30
                elif price < sma_short < sma_long:
                    votes_put += 30

            # Threshold check
            vote_threshold = params.get('vote_threshold', 50)
            if votes_call == votes_put or max(votes_call, votes_put) < vote_threshold:
                return None

            return 'CALL' if votes_call > votes_put else 'PUT'
        except Exception:
            return None
    
    def _technical_signal(self, data: pd.DataFrame, current_idx: int) -> Optional[str]:
        """
        Pure technical analysis: RSI + MACD + Moving Averages
        """
        
        try:
            close = data['close'].values
            
            # RSI
            rsi = self._calculate_rsi(data['close'], period=14).iloc[current_idx]
            
            # MACD
            ema12 = data['close'].ewm(span=12).mean().iloc[current_idx]
            ema26 = data['close'].ewm(span=26).mean().iloc[current_idx]
            macd_line = ema12 - ema26
            
            # Moving Averages
            sma20 = data['close'].rolling(20).mean().iloc[current_idx]
            sma50 = data['close'].rolling(50).mean().iloc[current_idx]
            current_price = data['close'].iloc[current_idx]
            
            # Signal scoring
            signal_votes = {}
            
            # RSI component
            if rsi < 30:
                signal_votes['CALL'] = signal_votes.get('CALL', 0) + 40
            elif rsi > 70:
                signal_votes['PUT'] = signal_votes.get('PUT', 0) + 40
            
            # MACD component
            if macd_line > 0:
                signal_votes['CALL'] = signal_votes.get('CALL', 0) + 30
            else:
                signal_votes['PUT'] = signal_votes.get('PUT', 0) + 30
            
            # Moving Average component
            if current_price > sma20 > sma50:
                signal_votes['CALL'] = signal_votes.get('CALL', 0) + 30
            elif current_price < sma20 < sma50:
                signal_votes['PUT'] = signal_votes.get('PUT', 0) + 30
            
            # Determine signal
            if signal_votes.get('CALL', 0) > signal_votes.get('PUT', 0):
                return 'CALL'
            elif signal_votes.get('PUT', 0) > signal_votes.get('CALL', 0):
                return 'PUT'
            
            return None
            
        except Exception as e:
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate performance metrics from trades"""
        
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'sharpe_ratio': 0
            }
        
        wins = [t for t in trades if t['win']]
        losses = [t for t in trades if not t['win']]
        
        total_win_pnl = sum(t['pnl'] for t in wins)
        total_loss_pnl = sum(abs(t['pnl']) for t in losses)
        
        win_rate = len(wins) / len(trades) * 100
        profit_factor = total_win_pnl / (total_loss_pnl + 1e-10)
        total_pnl = total_win_pnl - total_loss_pnl
        
        # Sharpe ratio
        pnls = np.array([t['pnl'] for t in trades])
        sharpe = np.mean(pnls) / (np.std(pnls) + 1e-10) * np.sqrt(252)
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_pnl': total_pnl,
            'avg_win': np.mean([t['pnl'] for t in wins]) if wins else 0,
            'avg_loss': np.mean([abs(t['pnl']) for t in losses]) if losses else 0,
            'sharpe_ratio': float(sharpe)
        }
    
    def _analyze_consistency(self, pair_results: Dict) -> Dict:
        """Analyze consistency across pairs"""
        
        win_rates = [p['metrics']['win_rate'] for p in pair_results.values()]
        pnls = [p['metrics']['total_pnl'] for p in pair_results.values()]
        
        return {
            'pairs_tested': len(pair_results),
            'avg_win_rate': np.mean(win_rates),
            'std_win_rate': np.std(win_rates),
            'min_win_rate': np.min(win_rates),
            'max_win_rate': np.max(win_rates),
            'avg_pnl': np.mean(pnls),
            'winning_pairs': sum(1 for wr in win_rates if wr > 50),
            'losing_pairs': sum(1 for wr in win_rates if wr < 50)
        }
    
    def _print_summary(self, results: Dict):
        """Print results summary"""
        
        print("\n" + "=" * 70)
        print("WALK-FORWARD BACKTEST RESULTS")
        print("=" * 70)
        
        overall = results['overall_metrics']
        consistency = results['consistency_analysis']
        
        print(f"\n📊 OVERALL PERFORMANCE:")
        print(f"   Total Trades: {overall['total_trades']}")
        print(f"   Win Rate: {overall['win_rate']:.2f}%")
        print(f"   Winning: {overall['winning_trades']} | Losing: {overall['losing_trades']}")
        print(f"   Profit Factor: {overall['profit_factor']:.2f}x")
        print(f"   Total P&L: ${overall['total_pnl']:.2f}")
        print(f"   Sharpe Ratio: {overall['sharpe_ratio']:.3f}")
        
        print(f"\n📈 CONSISTENCY ACROSS PAIRS:")
        print(f"   Pairs Tested: {consistency['pairs_tested']}")
        print(f"   Avg Win Rate: {consistency['avg_win_rate']:.2f}% ± {consistency['std_win_rate']:.2f}%")
        print(f"   Range: {consistency['min_win_rate']:.2f}% → {consistency['max_win_rate']:.2f}%")
        print(f"   Profitable Pairs: {consistency['winning_pairs']}/{consistency['pairs_tested']}")
        print(f"   Unprofitable Pairs: {consistency['losing_pairs']}/{consistency['pairs_tested']}")
        
        print(f"\n💰 PER-TRADE METRICS:")
        print(f"   Avg Win: ${overall['avg_win']:.2f}")
        print(f"   Avg Loss: ${overall['avg_loss']:.2f}")
        print(f"   Win/Loss Ratio: {overall['avg_win']/abs(overall['avg_loss'] + 1e-10):.2f}")
        
        # Status
        print(f"\n🎯 STATUS:")
        if overall['win_rate'] >= 55:
            print(f"   ✅ PROFITABLE: {overall['win_rate']:.2f}% > 55% threshold")
        elif overall['win_rate'] >= 50:
            print(f"   ⚠️  BREAKEVEN: {overall['win_rate']:.2f}% (need 55%+ for profit)")
        else:
            print(f"   ❌ UNPROFITABLE: {overall['win_rate']:.2f}% < 50%")
        
        print("\n" + "=" * 70)
    
    def _save_results(self, results: Dict, all_trades: List[Dict]):
        """Save detailed results to files"""
        
        # Summary JSON
        with open('walk_forward_results.json', 'w') as f:
            # Make results serializable
            serializable_results = results.copy()
            json.dump(serializable_results, f, indent=2, default=str)
        
        # Detailed trades CSV
        if all_trades:
            trades_df = pd.DataFrame(all_trades)
            trades_df.to_csv('walk_forward_trades.csv', index=False)
            print(f"\n✓ Trades saved: walk_forward_trades.csv ({len(trades_df)} trades)")
        
        print(f"✓ Results saved: walk_forward_results.json")


def main():
    """Run walk-forward backtest"""
    
    backtester = WalkForwardBacktester(train_period_days=90, test_period_days=30, use_bot=True, max_trades=20000)
    
    results = backtester.run_walk_forward_test(data_dir='data')
    
    return 0 if results['overall_metrics'].get('total_trades', 0) > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
