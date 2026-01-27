#!/usr/bin/env python3
"""
Parameter grid search for top pairs using walk-forward evaluation
Targets: USD/CAD and EUR/GBP

Saves results to `parameter_search_results.json` and `parameter_search_results.csv`.
"""

import pandas as pd
import numpy as np
import itertools
import json
import os
from datetime import datetime

DATA_DIR = 'data'
PAIRS = ['USD/CAD', 'EUR/GBP']

# Walk-forward settings (match backtester)
TRAIN_DAYS = 90
TEST_DAYS = 30
MIN_TRADE_CANDLES = 100
EXIT_OFFSET = 5  # candles after entry to check exit

# Parameter grid
RSI_PERIODS = [7, 14, 21]
RSI_OVERSOLD = [25, 30]
RSI_OVERBOUGHT = [70, 75]
SMA_SHORT = [10, 20]
SMA_LONG = [50, 100]
MACD_FAST = [8, 12]
MACD_SLOW = [26, 34]
VOTE_THRESHOLD = [50]  # total vote threshold (fixed for now)

# Weights (fixed)
WEIGHTS = {
    'rsi': 40,
    'macd': 30,
    'ma': 30
}


def _calculate_rsi(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def _ema(series, span):
    return series.ewm(span=span).mean()


def evaluate_params_on_pair(pair, params):
    """Run walk-forward evaluation on a single pair with given params."""
    fname = f"{pair.replace('/', '_')}_5min.csv"
    path = os.path.join(DATA_DIR, fname)
    if not os.path.exists(path):
        return None

    df = pd.read_csv(path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime').reset_index(drop=True)

    # compute candles per day estimate: use 22 hours/day -> 22*60/5 = 264 candles/day
    candles_per_day = int(22 * 60 / 5)
    train_size = TRAIN_DAYS * candles_per_day
    test_size = TEST_DAYS * candles_per_day
    step = test_size

    all_trades = []

    for start in range(0, len(df) - train_size - test_size + 1, step):
        train_df = df.iloc[start:start+train_size].reset_index(drop=True)
        test_df = df.iloc[start+train_size:start+train_size+test_size].reset_index(drop=True)

        # Precompute indicators on test_df using params
        rsi = _calculate_rsi(pd.concat([train_df['close'], test_df['close']]), params['rsi_period'])
        rsi_test = rsi.iloc[len(train_df):].reset_index(drop=True)

        ema_fast = _ema(pd.concat([train_df['close'], test_df['close']]), params['macd_fast'])
        ema_slow = _ema(pd.concat([train_df['close'], test_df['close']]), params['macd_slow'])
        macd = (ema_fast - ema_slow).iloc[len(train_df):].reset_index(drop=True)

        sma_short = pd.concat([train_df['close'], test_df['close']]).rolling(window=params['sma_short']).mean().iloc[len(train_df):].reset_index(drop=True)
        sma_long = pd.concat([train_df['close'], test_df['close']]).rolling(window=params['sma_long']).mean().iloc[len(train_df):].reset_index(drop=True)

        # iterate candles in test_df
        for i in range(MIN_TRADE_CANDLES, len(test_df)-EXIT_OFFSET):
            votes_call = 0
            votes_put = 0

            # RSI vote
            r = rsi_test.iloc[i]
            if pd.notna(r):
                if r < params['rsi_oversold']:
                    votes_call += WEIGHTS['rsi']
                elif r > params['rsi_overbought']:
                    votes_put += WEIGHTS['rsi']

            # MACD vote
            m = macd.iloc[i]
            if pd.notna(m):
                if m > 0:
                    votes_call += WEIGHTS['macd']
                else:
                    votes_put += WEIGHTS['macd']

            # MA vote
            s = sma_short.iloc[i]
            l = sma_long.iloc[i]
            price = test_df['close'].iloc[i]
            if pd.notna(s) and pd.notna(l):
                if price > s > l:
                    votes_call += WEIGHTS['ma']
                elif price < s < l:
                    votes_put += WEIGHTS['ma']

            # Decide
            if votes_call == votes_put or max(votes_call, votes_put) < params['vote_threshold']:
                continue

            signal = 'CALL' if votes_call > votes_put else 'PUT'
            entry = test_df['close'].iloc[i]
            exit_price = test_df['close'].iloc[i+EXIT_OFFSET]
            win = (exit_price > entry) if signal == 'CALL' else (exit_price < entry)
            pnl = 85 if win else -100

            all_trades.append({'signal': signal, 'win': win, 'pnl': pnl})

    # compute metrics
    if not all_trades:
        return {'total_trades': 0}

    wins = sum(1 for t in all_trades if t['win'])
    losses = sum(1 for t in all_trades if not t['win'])
    total_pnl = sum(t['pnl'] for t in all_trades)
    profit_factor = (sum(t['pnl'] for t in all_trades if t['pnl']>0) / (abs(sum(t['pnl'] for t in all_trades if t['pnl']<0)) + 1e-10))
    win_rate = wins / len(all_trades) * 100

    return {
        'total_trades': len(all_trades),
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'total_pnl': total_pnl
    }


if __name__ == '__main__':
    combos = list(itertools.product(RSI_PERIODS, RSI_OVERSOLD, RSI_OVERBOUGHT, SMA_SHORT, SMA_LONG, MACD_FAST, MACD_SLOW, VOTE_THRESHOLD))
    results = []

    for pair in PAIRS:
        print(f"\n=== GRID SEARCH: {pair} ===")
        best = []
        pair_results = []

        for idx, combo in enumerate(combos, 1):
            rsi_period, rsi_oversold, rsi_overbought, sma_s, sma_l, macd_f, macd_s, vote_th = combo
            if sma_s >= sma_l:
                continue  # invalid
            if macd_f >= macd_s:
                continue
            params = {
                'rsi_period': rsi_period,
                'rsi_oversold': rsi_oversold,
                'rsi_overbought': rsi_overbought,
                'sma_short': sma_s,
                'sma_long': sma_l,
                'macd_fast': macd_f,
                'macd_slow': macd_s,
                'vote_threshold': vote_th
            }
            res = evaluate_params_on_pair(pair, params)
            if res is None:
                continue
            pair_results.append({'params': params, 'metrics': res})

            if idx % 50 == 0:
                print(f"  Processed {idx}/{len(combos)} combos")

        # sort by win_rate primary, profit_factor secondary
        pair_results_sorted = [p for p in sorted(pair_results, key=lambda x: (x['metrics'].get('win_rate',0), x['metrics'].get('profit_factor',0)), reverse=True)]
        top = pair_results_sorted[:10]
        results.append({'pair': pair, 'top': top})

        # Save per-pair results
        with open(f'parameter_search_{pair.replace('/', '_')}.json', 'w') as f:
            json.dump(pair_results_sorted, f, default=str, indent=2)

        print(f"Top results for {pair}:")
        for t in top:
            print(f"  win_rate={t['metrics'].get('win_rate',0):.2f}% trades={t['metrics'].get('total_trades',0)} pf={t['metrics'].get('profit_factor',0):.2f} params={t['params']}")

    # Save combined results
    with open('parameter_search_results.json', 'w') as f:
        json.dump(results, f, default=str, indent=2)

    # Flatten and save CSV
    rows = []
    for r in results:
        pair = r['pair']
        for t in r['top']:
            row = t['params'].copy()
            row.update(t['metrics'])
            row['pair'] = pair
            rows.append(row)
    if rows:
        pd.DataFrame(rows).to_csv('parameter_search_results.csv', index=False)

    print('\nGrid search complete. Results saved to parameter_search_results.json and .csv')
