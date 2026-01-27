#!/usr/bin/env python3
"""
Multi-Pair Portfolio Optimization: Find optimal pair combinations and weights
Tests all pair combinations (2-pair, 3-pair portfolios) to maximize Sharpe ratio
"""

import pandas as pd
import numpy as np
import json
import os
import itertools
from phase3_enhanced_signals import Phase3SignalEngine

PAIRS = ['AUD/USD', 'EUR/GBP', 'EUR/JPY', 'EUR/USD', 'GBP/JPY', 'GBP/USD', 'NZD/USD', 'USD/CAD', 'USD/CHF', 'USD/JPY']
DATA_DIR = 'data'

def backtest_pair(pair: str, params: dict, data_dir: str = 'data') -> dict:
    """Single pair backtest"""
    fname = f"{pair.replace('/', '_')}_5min.csv"
    path = os.path.join(data_dir, fname)
    
    if not os.path.exists(path):
        return {'pair': pair, 'trades': 0, 'win_rate': 0, 'pnl': 0, 'sharpe': 0}
    
    df = pd.read_csv(path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime').reset_index(drop=True)
    
    engine = Phase3SignalEngine(params)
    trades = []
    
    for i in range(100, len(df) - 5):
        signal = engine.generate_signal(df, i, pair)
        if signal is None:
            continue
        
        entry = df['close'].iloc[i]
        exit_price = df['close'].iloc[i + 5]
        win = (exit_price > entry) if signal == 'CALL' else (exit_price < entry)
        pnl = 85 if win else -100
        trades.append({'signal': signal, 'win': win, 'pnl': pnl})
    
    if not trades:
        return {'pair': pair, 'trades': 0, 'win_rate': 0, 'pnl': 0, 'sharpe': 0}
    
    wins = sum(1 for t in trades if t['win'])
    total_pnl = sum(t['pnl'] for t in trades)
    pnls = np.array([t['pnl'] for t in trades])
    sharpe = np.mean(pnls) / (np.std(pnls) + 1e-10) * np.sqrt(252)
    
    return {
        'pair': pair,
        'trades': len(trades),
        'win_rate': wins / len(trades) * 100,
        'pnl': total_pnl,
        'sharpe': sharpe
    }

def test_portfolio_combination(pairs: list, params_dict: dict, data_dir: str = 'data') -> dict:
    """Test 2-3 pair portfolio combinations"""
    
    results = []
    for pair in pairs:
        pair_clean = pair.replace('_', '/')
        if pair_clean in params_dict:
            params = params_dict[pair_clean]
        else:
            # Default params
            params = {
                'rsi_period': 14, 'rsi_oversold': 25, 'rsi_overbought': 70,
                'sma_short': 20, 'sma_long': 50, 'macd_fast': 12, 'macd_slow': 26,
                'vote_threshold': 50
            }
        res = backtest_pair(pair_clean, params, data_dir)
        results.append(res)
    
    # Portfolio metrics (equal-weight combination)
    total_trades = sum(r['trades'] for r in results)
    total_pnl = sum(r['pnl'] for r in results)
    total_wins = sum(r['trades'] * r['win_rate'] / 100 for r in results)
    
    if total_trades == 0:
        portfolio_wr = 0
        sharpe = 0
    else:
        portfolio_wr = total_wins / total_trades * 100
        sharpe = np.mean([r['sharpe'] for r in results if r['trades'] > 0]) if results else 0
    
    return {
        'pairs': pairs,
        'total_trades': total_trades,
        'portfolio_win_rate': portfolio_wr,
        'total_pnl': total_pnl,
        'avg_sharpe': sharpe,
        'pair_results': results
    }

if __name__ == '__main__':
    # Load params
    with open('selected_params.json') as f:
        params = json.load(f)
    
    print("=" * 80)
    print("MULTI-PAIR PORTFOLIO OPTIMIZATION")
    print("=" * 80)
    
    # Test all 2-pair combinations
    print("\n🔍 Testing 2-Pair Portfolios (best Sharpe ratio):\n")
    two_pair_results = []
    
    for pair1, pair2 in itertools.combinations(PAIRS[:6], 2):  # Top 6 pairs for speed
        result = test_portfolio_combination([pair1, pair2], params)
        two_pair_results.append(result)
    
    # Sort by Sharpe ratio
    two_pair_results_sorted = sorted(two_pair_results, key=lambda x: x['avg_sharpe'], reverse=True)
    
    for idx, res in enumerate(two_pair_results_sorted[:5], 1):
        print(f"{idx}. {' + '.join(res['pairs'])}")
        print(f"   Trades: {res['total_trades']}, Win Rate: {res['portfolio_win_rate']:.2f}%, "
              f"P&L: ${res['total_pnl']:.0f}, Sharpe: {res['avg_sharpe']:.3f}\n")
    
    # Test 3-pair combinations (top performers)
    print("\n🔍 Testing 3-Pair Portfolios (best Sharpe ratio):\n")
    top_pairs = [r['pairs'][0] if r['pairs'][0] in PAIRS[:6] else r['pairs'][1] for r in two_pair_results_sorted[:3]]
    top_pairs = list(set(top_pairs))[:3]
    
    three_pair_results = []
    for combo in itertools.combinations(top_pairs + ['USD/CAD', 'GBP/USD'], 3):
        result = test_portfolio_combination(list(combo), params)
        three_pair_results.append(result)
    
    three_pair_results_sorted = sorted(three_pair_results, key=lambda x: x['avg_sharpe'], reverse=True)
    
    for idx, res in enumerate(three_pair_results_sorted[:3], 1):
        print(f"{idx}. {' + '.join(res['pairs'])}")
        print(f"   Trades: {res['total_trades']}, Win Rate: {res['portfolio_win_rate']:.2f}%, "
              f"P&L: ${res['total_pnl']:.0f}, Sharpe: {res['avg_sharpe']:.3f}\n")
    
    # Save results
    best_portfolio = two_pair_results_sorted[0] if two_pair_results_sorted else None
    
    with open('portfolio_optimization_results.json', 'w') as f:
        json.dump({
            'best_2pair': best_portfolio,
            'best_3pair': three_pair_results_sorted[0] if three_pair_results_sorted else None,
            'all_2pair_results': two_pair_results_sorted[:10]
        }, f, indent=2)
    
    print("\n✓ Results saved to portfolio_optimization_results.json")
    
    # Recommendation
    if best_portfolio:
        print(f"\n✅ RECOMMENDED PORTFOLIO: {' + '.join(best_portfolio['pairs'])}")
        print(f"   Expected Win Rate: {best_portfolio['portfolio_win_rate']:.2f}%")
        print(f"   Expected Sharpe Ratio: {best_portfolio['avg_sharpe']:.3f}")
