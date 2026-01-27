#!/usr/bin/env python3
"""
Extended validation: USD/CAD Phase 3 performance on full dataset
Tests if 64.71% win rate holds on larger sample (avoiding overfitting on 34 trades)
"""

import pandas as pd
import numpy as np
import json
import os
from phase3_enhanced_signals import Phase3SignalEngine

# Load USD/CAD parameters (optimized from grid search)
with open('selected_params.json') as f:
    params_all = json.load(f)
    usd_cad_params = params_all['USD/CAD']

# Load USD/CAD data
df = pd.read_csv('data/USD_CAD_5min.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.sort_values('datetime').reset_index(drop=True)

print("=" * 70)
print("USD/CAD PHASE 3 VALIDATION (Full Dataset)")
print("=" * 70)
print(f"Data loaded: {len(df)} candles")
print(f"Date range: {df['datetime'].min()} → {df['datetime'].max()}")
print(f"Parameters: {usd_cad_params}")
print()

# Initialize Phase 3 engine
engine = Phase3SignalEngine(usd_cad_params)

# Generate trades across entire dataset
trades = []
for i in range(100, len(df) - 5):
    signal = engine.generate_signal(df, i, 'USD/CAD')
    
    if signal is None:
        continue
    
    entry_price = df['close'].iloc[i]
    exit_price = df['close'].iloc[i + 5]  # 5 candles (25 min) later
    
    win = (exit_price > entry_price) if signal == 'CALL' else (exit_price < entry_price)
    pnl = 85 if win else -100
    
    trades.append({
        'datetime': df['datetime'].iloc[i],
        'signal': signal,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'win': win,
        'pnl': pnl
    })

# Calculate metrics
if trades:
    wins = sum(1 for t in trades if t['win'])
    losses = sum(1 for t in trades if not t['win'])
    total_pnl = sum(t['pnl'] for t in trades)
    win_rate = wins / len(trades) * 100
    profit_factor = (sum(t['pnl'] for t in trades if t['pnl'] > 0) / 
                     (abs(sum(t['pnl'] for t in trades if t['pnl'] < 0)) + 1e-10))
    
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\n📊 OVERALL:")
    print(f"   Total Trades: {len(trades)}")
    print(f"   Winning Trades: {wins}")
    print(f"   Losing Trades: {losses}")
    print(f"   Win Rate: {win_rate:.2f}%")
    print(f"   Profit Factor: {profit_factor:.2f}x")
    print(f"   Total P&L: ${total_pnl:.2f}")
    
    print(f"\n📈 SAMPLE COMPARISON:")
    print(f"   Small sample (filtered): 34 trades, 64.71% win")
    print(f"   Full validation: {len(trades)} trades, {win_rate:.2f}% win")
    
    if win_rate >= 55:
        print(f"\n✅ VALIDATED: {win_rate:.2f}% is PROFITABLE (≥55% threshold)")
    else:
        print(f"\n⚠️  BELOW THRESHOLD: {win_rate:.2f}% < 55% (may need refinement)")
    
    # Save detailed results
    trades_df = pd.DataFrame(trades)
    trades_df.to_csv('usd_cad_phase3_validation.csv', index=False)
    
    results = {
        'pair': 'USD/CAD',
        'total_trades': len(trades),
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'total_pnl': total_pnl,
        'parameters': usd_cad_params,
        'timestamp': str(pd.Timestamp.now())
    }
    
    with open('usd_cad_phase3_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to usd_cad_phase3_validation.csv and .json")
else:
    print("❌ No trades generated (filters may be too tight)")
