#!/usr/bin/env python3
"""
Load `parameter_search_results.json`, pick the top parameter set per pair,
run the same walk-forward evaluation for those selected params, and save results.
"""
import json
import os
from parameter_search import evaluate_params_on_pair

INPUT = 'parameter_search_results.json'
OUT_JSON = 'selected_params_results.json'
OUT_SELECTED = 'selected_params.json'

if __name__ == '__main__':
    if not os.path.exists(INPUT):
        print('parameter_search_results.json not found')
        raise SystemExit(1)

    with open(INPUT) as f:
        data = json.load(f)

    selected = {}
    results = []
    for entry in data:
        pair = entry['pair']
        top = entry.get('top', [])
        if not top:
            continue
        best = top[0]
        params = best['params']
        selected[pair] = params

        print(f"Evaluating selected params for {pair}...")
        metrics = evaluate_params_on_pair(pair, params)
        results.append({'pair': pair, 'params': params, 'metrics': metrics})

    with open(OUT_SELECTED, 'w') as f:
        json.dump(selected, f, indent=2)

    with open(OUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)

    print('Selected params and results saved:', OUT_SELECTED, OUT_JSON)
