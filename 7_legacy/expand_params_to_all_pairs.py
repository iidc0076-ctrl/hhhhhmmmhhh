#!/usr/bin/env python3
"""
Expand selected params to all 10 pairs using best-performing parameter combinations
This enables Phase 3 filters across all pairs.
"""
import json
import os

# Load grid search results
grid_results = {}
for fname in ['parameter_search_USD_CAD.json', 'parameter_search_EUR_GBP.json']:
    if os.path.exists(fname):
        with open(fname) as f:
            pair_data = json.load(f)
            # pair_data is a list of dicts with 'params' and 'metrics' keys
            if pair_data and isinstance(pair_data, list) and 'params' in pair_data[0]:
                pair_name = fname.replace('parameter_search_', '').replace('.json', '').replace('_', '/')
                grid_results[pair_name] = pair_data[0]['params']  # Top result's params

# For pairs without grid search, use a sensible default (balanced parameters)
default_params = {
    'rsi_period': 14,
    'rsi_oversold': 25,
    'rsi_overbought': 70,
    'sma_short': 20,
    'sma_long': 50,
    'macd_fast': 12,
    'macd_slow': 26,
    'vote_threshold': 50
}

all_pairs = [
    'AUD/USD', 'EUR/GBP', 'EUR/JPY', 'EUR/USD', 'GBP/JPY',
    'GBP/USD', 'NZD/USD', 'USD/CAD', 'USD/CHF', 'USD/JPY'
]

expanded_params = {}
for pair in all_pairs:
    if pair in grid_results:
        # Use optimized params from grid search
        expanded_params[pair] = grid_results[pair]
    else:
        # Use default for non-optimized pairs
        expanded_params[pair] = default_params

# Save expanded params
with open('selected_params.json', 'w') as f:
    json.dump(expanded_params, f, indent=2)

print(f"✓ Expanded selected params to {len(expanded_params)} pairs")
print(f"  Optimized: {list(grid_results.keys())}")
print(f"  Using defaults: {[p for p in all_pairs if p not in grid_results]}")
print(f"✓ Saved to selected_params.json")
