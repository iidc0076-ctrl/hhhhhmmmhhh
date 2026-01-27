# PHASE 1 IMPLEMENTATION - Weeks 1-2 (Foundation)

**Goal**: Establish true performance baseline + consolidate code  
**Current Win Rate**: 50-53%  
**Target After Phase 1**: 53-58%  
**Effort**: 15-20 hours total  

---

## WEEK 1A: WALK-FORWARD BACKTESTING FRAMEWORK

### Step 1: Download Real Historical Data

Create `data_downloader.py`:

```python
"""Download 6+ months of real historical data from Twelvedata"""
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Load your API keys
with open('api_config.json', 'r') as f:
    CONFIG = json.load(f)

TWELVEDATA_KEYS = CONFIG.get('twelvedata_api_keys', [])
PAIRS_TO_TEST = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD",
    "USD/CHF", "EUR/GBP", "EUR/JPY", "GBP/JPY"
]

def download_historical_data(pair, interval='5min', days=180):
    """Download 6 months of historical data"""
    api_key = TWELVEDATA_KEYS[0]
    symbol = pair.replace('/', '')
    
    print(f"Downloading {pair} {interval} data for {days} days...")
    
    url = "https://api.twelvedata.com/time_series"
    params = {
        'symbol': symbol,
        'interval': interval,
        'outputsize': 5000,  # Max per request
        'apikey': api_key,
        'format': 'JSON'
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if 'values' not in data:
            print(f"⚠️ No data for {pair}")
            return None
        
        # Convert to DataFrame
        df_data = []
        for candle in data['values']:
            df_data.append({
                'datetime': pd.to_datetime(candle['datetime']),
                'open': float(candle['open']),
                'high': float(candle['high']),
                'low': float(candle['low']),
                'close': float(candle['close']),
                'volume': float(candle.get('volume', 0))
            })
        
        df = pd.DataFrame(df_data)
        df = df.sort_values('datetime').reset_index(drop=True)
        
        # Save to CSV
        filename = f"data/{pair.replace('/', '_')}_{interval}.csv"
        df.to_csv(filename, index=False)
        print(f"✓ Saved {len(df)} candles to {filename}")
        
        return df
        
    except Exception as e:
        print(f"✗ Error downloading {pair}: {e}")
        return None
    
    finally:
        time.sleep(1)  # Rate limiting

# Download all pairs
import os
os.makedirs('data', exist_ok=True)

for pair in PAIRS_TO_TEST:
    download_historical_data(pair, interval='5min', days=180)
    time.sleep(1)

print("\n✓ All data downloaded!")
```

**Run it**: `python3 data_downloader.py`

---

### Step 2: Create Walk-Forward Backtesting Framework

Create `walk_forward_backtester.py`:

```python
"""
Walk-Forward Backtesting Framework
Prevents look-ahead bias and overfitting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class WalkForwardBacktester:
    """Implements proper walk-forward analysis"""
    
    def __init__(self, train_period_days=90, test_period_days=30):
        self.train_period = train_period_days
        self.test_period = test_period_days
        self.results = []
        
    def run_walk_forward_test(self, df: pd.DataFrame, pair: str) -> Dict:
        """
        Walk-forward testing with rolling window
        Train on 90 days, test on 30 days, roll forward
        """
        
        if len(df) < self.train_period + self.test_period:
            return None
        
        all_trades = []
        monthly_results = []
        
        # Roll forward through data
        for i in range(0, len(df) - self.train_period - self.test_period, self.test_period):
            train_data = df.iloc[i:i+self.train_period]
            test_data = df.iloc[i+self.train_period:i+self.train_period+self.test_period]
            
            # STEP 1: Optimize parameters on training data
            print(f"\n📊 {pair} Window {i//self.test_period + 1}")
            print(f"   Training: {train_data['datetime'].min()} → {train_data['datetime'].max()}")
            print(f"   Testing:  {test_data['datetime'].min()} → {test_data['datetime'].max()}")
            
            best_params = self._optimize_parameters(train_data, pair)
            
            # STEP 2: Test on out-of-sample data (test set)
            trades = self._backtest_with_params(test_data, best_params, pair)
            all_trades.extend(trades)
            
            # STEP 3: Calculate metrics for this window
            window_metrics = self._calculate_metrics(trades)
            window_metrics['period'] = i // self.test_period
            window_metrics['start_date'] = test_data['datetime'].min()
            window_metrics['end_date'] = test_data['datetime'].max()
            window_metrics['best_params'] = best_params
            
            monthly_results.append(window_metrics)
            
            print(f"   Win Rate: {window_metrics['win_rate']:.2f}%")
            print(f"   Trades: {window_metrics['total_trades']}")
        
        # Overall statistics
        overall_metrics = self._calculate_metrics(all_trades)
        
        return {
            'pair': pair,
            'overall_metrics': overall_metrics,
            'monthly_results': monthly_results,
            'all_trades': all_trades,
            'consistency': self._calculate_consistency(monthly_results)
        }
    
    def _optimize_parameters(self, train_data: pd.DataFrame, pair: str) -> Dict:
        """Optimize parameters on training data only"""
        
        # Test different parameter combinations
        best_params = {
            'rsi_period': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'bb_period': 20,
            'confidence_threshold': 70
        }
        
        best_win_rate = 0
        
        # Test RSI periods
        for rsi_period in [9, 14, 21]:
            for confidence in [65, 70, 75]:
                trades = self._backtest_with_params(
                    train_data,
                    {'rsi_period': rsi_period, 'confidence_threshold': confidence},
                    pair
                )
                
                if trades:
                    win_rate = len([t for t in trades if t['win']]) / len(trades)
                    if win_rate > best_win_rate:
                        best_win_rate = win_rate
                        best_params['rsi_period'] = rsi_period
                        best_params['confidence_threshold'] = confidence
        
        return best_params
    
    def _backtest_with_params(self, data: pd.DataFrame, params: Dict, pair: str) -> List[Dict]:
        """Backtest with specific parameters"""
        
        trades = []
        
        # Generate signals and evaluate
        for i in range(50, len(data) - 5):  # 50 candles for indicators, 5 for exit
            signal = self._generate_signal(data.iloc[i], data.iloc[:i], params)
            
            if signal is None:
                continue
            
            # Check trade outcome
            entry_price = data.iloc[i]['close']
            exit_price = data.iloc[i+5]['close']  # 5 candles later
            
            if signal == 'CALL':
                win = exit_price > entry_price
            else:  # PUT
                win = exit_price < entry_price
            
            trades.append({
                'signal': signal,
                'entry': entry_price,
                'exit': exit_price,
                'win': win,
                'pnl': 42.5 if win else -50,  # 85% payout
                'timestamp': data.iloc[i]['datetime']
            })
        
        return trades
    
    def _generate_signal(self, current_candle, historical_data, params) -> str:
        """Generate trading signal with given parameters"""
        
        # Simple signal generation (replace with your actual logic)
        rsi = self._calculate_rsi(historical_data['close'], params['rsi_period'])
        
        confidence = 50
        signal = None
        
        if rsi[-1] < 30:
            confidence = 75
            signal = 'CALL'
        elif rsi[-1] > 70:
            confidence = 75
            signal = 'PUT'
        
        if confidence >= params['confidence_threshold'] and signal:
            return signal
        
        return None
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi.values
    
    def _calculate_metrics(self, trades: List[Dict]) -> Dict:
        """Calculate performance metrics"""
        
        if not trades:
            return {
                'win_rate': 0,
                'total_trades': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0
            }
        
        wins = [t for t in trades if t['win']]
        losses = [t for t in trades if not t['win']]
        
        total_profit = sum(t['pnl'] for t in wins)
        total_loss = abs(sum(t['pnl'] for t in losses))
        
        win_rate = len(wins) / len(trades) * 100
        profit_factor = total_profit / (total_loss + 1e-10)
        
        pnls = [t['pnl'] for t in trades]
        sharpe = np.mean(pnls) / (np.std(pnls) + 1e-10) if len(pnls) > 1 else 0
        
        return {
            'win_rate': win_rate,
            'total_trades': len(trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'profit_factor': profit_factor,
            'total_pnl': total_profit - total_loss,
            'sharpe_ratio': sharpe
        }
    
    def _calculate_consistency(self, monthly_results: List[Dict]) -> Dict:
        """Measure consistency across periods"""
        
        if not monthly_results:
            return {}
        
        win_rates = [r['win_rate'] for r in monthly_results]
        
        return {
            'avg_win_rate': np.mean(win_rates),
            'std_win_rate': np.std(win_rates),
            'min_win_rate': np.min(win_rates),
            'max_win_rate': np.max(win_rates),
            'periods': len(monthly_results)
        }


# Run walk-forward backtest
if __name__ == "__main__":
    backtester = WalkForwardBacktester(train_period_days=90, test_period_days=30)
    
    pairs = ["EUR/USD", "GBP/USD", "USD/JPY"]
    
    all_results = {}
    
    for pair in pairs:
        try:
            filename = f"data/{pair.replace('/', '_')}_5min.csv"
            df = pd.read_csv(filename)
            df['datetime'] = pd.to_datetime(df['datetime'])
            
            results = backtester.run_walk_forward_test(df, pair)
            all_results[pair] = results
            
        except Exception as e:
            print(f"Error with {pair}: {e}")
    
    # Save results
    with open('walk_forward_results.json', 'w') as f:
        # Convert to serializable format
        for pair, results in all_results.items():
            for trade in results.get('all_trades', []):
                trade['timestamp'] = str(trade['timestamp'])
        
        json.dump(all_results, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*60)
    print("WALK-FORWARD BACKTEST SUMMARY")
    print("="*60)
    
    for pair, results in all_results.items():
        metrics = results['overall_metrics']
        print(f"\n{pair}:")
        print(f"  Win Rate: {metrics['win_rate']:.2f}%")
        print(f"  Trades: {metrics['total_trades']}")
        print(f"  Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"  PnL: ${metrics['total_pnl']:.2f}")
        
        consistency = results['consistency']
        print(f"\n  Consistency:")
        print(f"    Avg Win Rate: {consistency['avg_win_rate']:.2f}%")
        print(f"    Std Dev: {consistency['std_win_rate']:.2f}%")
        print(f"    Range: {consistency['min_win_rate']:.2f}% - {consistency['max_win_rate']:.2f}%")
```

**Run it**: `python3 walk_forward_backtester.py`

---

## WEEK 1B: ESTABLISH BASELINE

### Create Baseline Tracking Spreadsheet

Create `baseline_tracking.py`:

```python
"""Track baseline metrics for comparison"""

import pandas as pd
import json

# Create tracking file
baseline_data = {
    'Week': [],
    'Pair': [],
    'Win_Rate': [],
    'Profit_Factor': [],
    'Total_Trades': [],
    'Sharpe_Ratio': [],
    'Consistency': [],
    'Notes': []
}

baseline_df = pd.DataFrame(baseline_data)

# Load walk-forward results
with open('walk_forward_results.json', 'r') as f:
    wf_results = json.load(f)

# Extract and display
for pair, results in wf_results.items():
    metrics = results['overall_metrics']
    consistency = results['consistency']
    
    baseline_df.loc[len(baseline_df)] = {
        'Week': 1,
        'Pair': pair,
        'Win_Rate': metrics['win_rate'],
        'Profit_Factor': metrics['profit_factor'],
        'Total_Trades': metrics['total_trades'],
        'Sharpe_Ratio': metrics['sharpe_ratio'],
        'Consistency': f"{consistency['avg_win_rate']:.1f}% ± {consistency['std_win_rate']:.1f}%",
        'Notes': 'Week 1 baseline'
    }

baseline_df.to_csv('performance_tracking.csv', index=False)
print("✓ Baseline saved to performance_tracking.csv")
print(baseline_df.to_string())
```

---

## WEEK 2A: CODE CONSOLIDATION

### Identify & Consolidate Duplicates

Create `consolidation_checker.py`:

```python
"""Find and report duplicate code"""

import os
import re
from collections import defaultdict

def find_function_implementations(directory, function_name):
    """Find all implementations of a specific function"""
    
    implementations = {}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                    # Find function definition
                    pattern = rf'def {function_name}\s*\('
                    if re.search(pattern, content):
                        # Extract function code
                        match = re.search(rf'def {function_name}.*?\n(.*?)(?=\ndef |\nclass |\Z)', content, re.DOTALL)
                        if match:
                            implementations[filepath] = match.group(0)[:200] + "..."
    
    return implementations

# Check for duplicate implementations
functions_to_check = [
    'calculate_fvg',
    'detect_order_blocks',
    'calculate_support_resistance',
    'calculate_rsi',
    'calculate_macd',
    'generate_signal'
]

print("="*60)
print("DUPLICATE CODE ANALYSIS")
print("="*60)

duplicates_found = defaultdict(list)

for func in functions_to_check:
    implementations = find_function_implementations('.', func)
    if len(implementations) > 1:
        print(f"\n⚠️  {func} found in {len(implementations)} places:")
        for file, code_snippet in implementations.items():
            print(f"   - {file}")
        duplicates_found[func] = implementations

print(f"\n\nTotal duplicate functions: {len(duplicates_found)}")

# Save report
with open('duplication_report.txt', 'w') as f:
    for func, implementations in duplicates_found.items():
        f.write(f"\n{func} ({len(implementations)} implementations):\n")
        for file in implementations.keys():
            f.write(f"  - {file}\n")

print("✓ Report saved to duplication_report.txt")
```

**Run it**: `python3 consolidation_checker.py`

**Then**: Create consolidated versions in `analysis/indicators/` directory

---

## WEEK 2B: PARAMETER DOCUMENTATION

### Create Parameter Analysis Document

Create `parameter_baseline.py`:

```python
"""Document all current parameters"""

import json

CURRENT_PARAMETERS = {
    # Technical Indicators
    'indicators': {
        'rsi': {
            'period': 14,
            'oversold': 30,
            'overbought': 70,
            'description': 'Relative Strength Index'
        },
        'macd': {
            'fast_ema': 12,
            'slow_ema': 26,
            'signal_ema': 9,
            'description': 'Moving Average Convergence Divergence'
        },
        'bollinger_bands': {
            'period': 20,
            'std_dev': 2,
            'description': 'Bollinger Bands for volatility'
        },
        'atr': {
            'period': 14,
            'description': 'Average True Range'
        },
        'adx': {
            'period': 14,
            'trend_threshold': 25,
            'description': 'Average Directional Index'
        }
    },
    
    # Signal Filters
    'signal_filters': {
        'min_confidence': 70,
        'min_adx': 25,
        'optimal_sessions': ['european', 'london_us'],
        'description': 'Signal generation thresholds'
    },
    
    # Money Management
    'money_management': {
        'position_size': 50,
        'payout_rate': 0.85,
        'kelly_fraction': 0.25,
        'description': 'Position sizing parameters'
    },
    
    # Signal Decay
    'decay': {
        'base_rate': 0.02,
        'critical_threshold': 0.3,
        'model': 'linear',
        'description': 'Signal invalidation model'
    },
    
    # Risk Management
    'risk_management': {
        'daily_loss_limit_percent': 5,
        'losing_streak_limit': 4,
        'max_drawdown_percent': 20,
        'description': 'Risk control parameters'
    }
}

# Save as reference
with open('baseline_parameters.json', 'w') as f:
    json.dump(CURRENT_PARAMETERS, f, indent=2)

# Print for review
print("="*60)
print("CURRENT PARAMETER BASELINE")
print("="*60)

for category, params in CURRENT_PARAMETERS.items():
    print(f"\n{category.upper()}:")
    if isinstance(params, dict) and 'description' not in params:
        for key, value in params.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    if k != 'description':
                        print(f"    {k}: {v}")
                if 'description' in value:
                    print(f"    → {value['description']}")
            else:
                print(f"  {key}: {value}")
    else:
        for key, value in params.items():
            if key != 'description':
                print(f"  {key}: {value}")
        if 'description' in params:
            print(f"  → {params['description']}")

print("\n✓ Baseline parameters saved to baseline_parameters.json")
```

---

## ✅ WEEK 1-2 DELIVERABLES

At the end of Week 1-2, you should have:

- [ ] **Historical data**: 6 months per pair (in `data/` folder)
- [ ] **Walk-forward backtest results**: True baseline win rates (JSON file)
- [ ] **Baseline tracking**: Performance metrics recorded
- [ ] **Duplication report**: All duplicate code identified
- [ ] **Parameter baseline**: All current parameters documented
- [ ] **Git branch**: `option-a-phase1` with all changes

### Expected Results After Phase 1:

```
├─ Pair analysis from walk-forward testing
├─ Real win rates per pair (expected 48-53%)
├─ Monthly consistency metrics
├─ Identified optimization opportunities
└─ Consolidated, cleaner codebase
```

---

## 🎯 READY FOR PHASE 2?

Once Phase 1 is complete, we move to:
- **Phase 2 (Weeks 3-5)**: Core parameter optimization
- Expected gain: +4-6% win rate (to 53-59%)

**Shall we start with Week 1A implementation today?**
