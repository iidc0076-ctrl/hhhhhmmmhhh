#!/usr/bin/env python3
"""
Download real data from Twelvedata API + fallback to synthetic data
Hybrid approach for backtesting foundation
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from typing import Optional
import sys
import requests
import time

# Pairs to generate data for
PAIRS_TO_TEST = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD",
    "USD/CHF", "EUR/GBP", "EUR/JPY", "GBP/JPY",
    "NZD/USD", "USD/CAD"
]

# Load Twelvedata API keys
try:
    with open('api_config.json', 'r') as f:
        CONFIG = json.load(f)
    TWELVEDATA_KEYS = CONFIG.get('twelvedata_api_keys', [])
except:
    TWELVEDATA_KEYS = []

CURRENT_KEY_INDEX = 0

# Intervals to generate
INTERVALS = ['1min', '5min', '15min']

# Realistic starting prices and volatility for each pair
PAIR_PROPERTIES = {
    "EUR/USD": {"price": 1.0850, "daily_vol": 0.0080, "spread": 0.0001},
    "GBP/USD": {"price": 1.2650, "daily_vol": 0.0095, "spread": 0.0001},
    "USD/JPY": {"price": 145.50, "daily_vol": 1.5, "spread": 0.01},
    "AUD/USD": {"price": 0.6850, "daily_vol": 0.0070, "spread": 0.0001},
    "USD/CHF": {"price": 0.8950, "daily_vol": 0.0065, "spread": 0.0001},
    "EUR/GBP": {"price": 0.8580, "daily_vol": 0.0045, "spread": 0.0001},
    "EUR/JPY": {"price": 157.30, "daily_vol": 1.2, "spread": 0.01},
    "GBP/JPY": {"price": 183.80, "daily_vol": 1.5, "spread": 0.01},
    "NZD/USD": {"price": 0.5950, "daily_vol": 0.0075, "spread": 0.0001},
    "USD/CAD": {"price": 1.3550, "daily_vol": 0.0065, "spread": 0.0001}
}

def rotate_api_key():
    """Move to next API key"""
    global CURRENT_KEY_INDEX
    CURRENT_KEY_INDEX = (CURRENT_KEY_INDEX + 1) % len(TWELVEDATA_KEYS)
    return TWELVEDATA_KEYS[CURRENT_KEY_INDEX]

def get_current_api_key():
    """Get current API key"""
    if CURRENT_KEY_INDEX < len(TWELVEDATA_KEYS):
        return TWELVEDATA_KEYS[CURRENT_KEY_INDEX]
    return None

def download_from_twelvedata(pair: str, interval: str = '5min', limit: int = 1000) -> Optional[pd.DataFrame]:
    """
    Try multiple approaches to get real data from Twelvedata API
    Returns None if all fail (will fall back to synthetic)
    """
    
    if not TWELVEDATA_KEYS:
        return None
    
    api_key = get_current_api_key()
    symbol = pair.replace('/', '')  # EUR/USD -> EURUSD
    
    print(f"   🔗 Trying Twelvedata API... (key: {api_key[:6]}...)")
    
    # Try multiple endpoints/approaches
    attempts = [
        # Attempt 1: Standard time_series with forex symbol
        {
            'url': 'https://api.twelvedata.com/time_series',
            'params': {
                'symbol': symbol,
                'interval': interval,
                'outputsize': min(limit, 5000),
                'apikey': api_key,
                'format': 'JSON'
            }
        },
        # Attempt 2: With =X suffix (sometimes required)
        {
            'url': 'https://api.twelvedata.com/time_series',
            'params': {
                'symbol': f'{symbol}X',
                'interval': interval,
                'outputsize': min(limit, 5000),
                'apikey': api_key,
                'format': 'JSON'
            }
        },
        # Attempt 3: Using quote endpoint first to validate symbol
        {
            'url': 'https://api.twelvedata.com/quote',
            'params': {
                'symbol': symbol,
                'apikey': api_key,
                'format': 'JSON'
            },
            'is_quote': True
        }
    ]
    
    for attempt_num, attempt in enumerate(attempts, 1):
        try:
            response = requests.get(attempt['url'], params=attempt['params'], timeout=10)
            data = response.json()
            
            # For quote endpoint, just check if symbol is valid
            if attempt.get('is_quote'):
                if isinstance(data, dict) and 'code' not in data and 'symbol' in data:
                    print(f"   ✓ Symbol {symbol} is valid on Twelvedata")
                    # Try time_series again with validated symbol
                    continue
                else:
                    continue
            
            # Check for errors
            if isinstance(data, dict) and 'code' in data:
                error_msg = data.get('message', 'Unknown error')
                print(f"   ⚠️  Attempt {attempt_num}: {error_msg[:50]}")
                continue
            
            if isinstance(data, dict) and 'values' not in data:
                print(f"   ⚠️  Attempt {attempt_num}: No data in response")
                continue
            
            values = data.get('values', []) if isinstance(data, dict) else data
            if not values or len(values) < 10:
                print(f"   ⚠️  Attempt {attempt_num}: Insufficient data ({len(values)} candles)")
                continue
            
            print(f"   ✓ Attempt {attempt_num}: Got {len(values)} candles")
            
            # Parse data
            df_data = []
            for candle in values:
                try:
                    df_data.append({
                        'datetime': pd.to_datetime(candle['datetime']),
                        'open': float(candle['open']),
                        'high': float(candle['high']),
                        'low': float(candle['low']),
                        'close': float(candle['close']),
                        'volume': float(candle.get('volume', 0))
                    })
                except (ValueError, KeyError, TypeError):
                    continue
            
            if not df_data or len(df_data) < 10:
                print(f"   ⚠️  Attempt {attempt_num}: Could not parse enough data")
                continue
            
            df = pd.DataFrame(df_data).sort_values('datetime').reset_index(drop=True)
            print(f"   ✅ SUCCESS: Parsed {len(df)} valid candles")
            return df
            
        except requests.exceptions.Timeout:
            print(f"   ⚠️  Attempt {attempt_num}: Timeout")
            continue
        except Exception as e:
            print(f"   ⚠️  Attempt {attempt_num}: {type(e).__name__}")
            continue
    
    # Try next API key if available
    if len(TWELVEDATA_KEYS) > 1:
        rotate_api_key()
    
    return None

def generate_realistic_ohlcv_data(pair: str, start_price: float, daily_volatility: float, 
                                 num_candles: int, interval_minutes: int) -> pd.DataFrame:
    """
    Generate realistic synthetic OHLCV data using market microstructure
    
    Includes:
    - Volatility clustering
    - Mean reversion
    - Trends with pullbacks
    - Volume patterns matching market hours
    """
    
    np.random.seed(hash(pair) % 2**32)  # Deterministic but pair-specific
    
    timestamps = []
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    
    # Generate realistic price movements
    current_price = start_price
    current_volatility = daily_volatility
    
    for i in range(num_candles):
        # Volatility clustering - volatility tends to persist
        current_volatility = 0.7 * current_volatility + 0.3 * daily_volatility * np.random.uniform(0.5, 1.5)
        
        # Generate candle movements
        # Higher volatility = larger candles
        candle_range = current_volatility * current_price / np.sqrt(252) * np.sqrt(interval_minutes / 60)
        
        # Random walk with mean reversion
        drift = -0.0001 * (current_price - start_price)  # Small mean reversion
        price_change = drift + np.random.normal(0, candle_range)
        
        open_price = current_price
        close_price = current_price + price_change
        
        # High/low with realistic wicks
        high_price = max(open_price, close_price) + np.abs(np.random.normal(0, candle_range * 0.3))
        low_price = min(open_price, close_price) - np.abs(np.random.normal(0, candle_range * 0.3))
        
        # Volume patterns (higher in active hours, lower in quiet hours)
        hour_of_day = (i * interval_minutes) % (24 * 60)
        if 8 * 60 <= hour_of_day < 17 * 60:  # Active hours
            volume = np.random.uniform(1000, 5000)
        else:
            volume = np.random.uniform(100, 1000)
        
        # Store data
        timestamps.append(datetime(2025, 6, 1) + timedelta(minutes=i * interval_minutes))
        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
        closes.append(close_price)
        volumes.append(volume)
        
        current_price = close_price
    
    df = pd.DataFrame({
        'datetime': timestamps,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    })
    
    return df

def generate_historical_data(pair: str, interval: str = '5min', days: int = 180) -> Optional[pd.DataFrame]:
    """
    Generate synthetic historical data for backtesting
    Uses realistic market microstructure patterns
    """
    
    print(f"📊 Generating {pair} {interval} synthetic data for {days} days...")
    
    # Get pair properties
    if pair not in PAIR_PROPERTIES:
        print(f"   ⚠️  Unknown pair: {pair}")
        return None
    
    props = PAIR_PROPERTIES[pair]
    
    # Calculate number of candles needed
    if interval == '1min':
        minutes_per_candle = 1
    elif interval == '5min':
        minutes_per_candle = 5
    elif interval == '15min':
        minutes_per_candle = 15
    else:
        minutes_per_candle = 5
    
    # Assuming forex trades 5 days/week, ~22 hours/day = 6600 minutes/week
    minutes_per_week = 5 * 22 * 60  # 6600 minutes
    num_candles = int(days / 7 * minutes_per_week / minutes_per_candle)
    
    print(f"   📈 Generating {num_candles} candles ({interval} interval)")
    
    try:
        df = generate_realistic_ohlcv_data(
            pair,
            start_price=props['price'],
            daily_volatility=props['daily_vol'],
            num_candles=num_candles,
            interval_minutes=minutes_per_candle
        )
        
        print(f"   ✓ Generated {len(df)} candles")
        print(f"   📅 Date range: {df['datetime'].min()} → {df['datetime'].max()}")
        print(f"   💹 Price range: {df['low'].min():.4f} → {df['high'].max():.4f}")
        
        # Save to CSV
        os.makedirs('data', exist_ok=True)
        filename = f"data/{pair.replace('/', '_')}_{interval}.csv"
        df.to_csv(filename, index=False)
        print(f"   💾 Saved to {filename}")
        
        return df
        
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return None

def main():
    """Hybrid downloader: Real Twelvedata first, synthetic fallback"""
    
    print("=" * 70)
    print("HYBRID DATA ACQUISITION: TWELVEDATA + SYNTHETIC FALLBACK")
    print("=" * 70)
    print(f"API keys available: {len(TWELVEDATA_KEYS)}")
    print(f"Pairs to download: {len(PAIRS_TO_TEST)}")
    print(f"Intervals: {INTERVALS}")
    print(f"Total files: {len(PAIRS_TO_TEST) * len(INTERVALS)}")
    print("=" * 70)
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    download_summary = {
        'successful': 0,
        'failed': 0,
        'real_data': 0,
        'synthetic_data': 0,
        'by_pair': {},
        'timestamp': datetime.now().isoformat(),
        'api_keys_count': len(TWELVEDATA_KEYS)
    }
    
    total_files = len(PAIRS_TO_TEST) * len(INTERVALS)
    current = 0
    
    for pair in PAIRS_TO_TEST:
        download_summary['by_pair'][pair] = {
            '1min': {'source': None},
            '5min': {'source': None},
            '15min': {'source': None}
        }
        
        for interval in INTERVALS:
            current += 1
            print(f"\n[{current}/{total_files}] {pair} {interval}")
            
            # Try real data first
            df = None
            source = None
            
            if TWELVEDATA_KEYS:
                df = download_from_twelvedata(pair, interval, limit=5000)
                if df is not None and len(df) > 100:
                    print(f"   ✅ Using REAL Twelvedata")
                    source = 'twelvedata'
                    download_summary['real_data'] += 1
            
            # Fallback to synthetic if real data failed
            if df is None or len(df) < 100:
                print(f"   ↓ Falling back to synthetic data...")
                df = generate_historical_data(pair, interval, days=180)
                if df is not None:
                    source = 'synthetic'
                    download_summary['synthetic_data'] += 1
            
            # Save result
            if df is not None and len(df) > 100:
                download_summary['successful'] += 1
                download_summary['by_pair'][pair][interval]['source'] = source
                
                # Save to CSV
                filename = f"data/{pair.replace('/', '_')}_{interval}.csv"
                df.to_csv(filename, index=False)
                print(f"   💾 Saved {len(df)} candles ({source})")
            else:
                download_summary['failed'] += 1
                download_summary['by_pair'][pair][interval]['source'] = 'failed'
                print(f"   ❌ Failed to get data")
            
            # Rate limiting for API
            if source == 'twelvedata':
                time.sleep(1)
    
    # Summary
    print("\n" + "=" * 70)
    print("ACQUISITION SUMMARY")
    print("=" * 70)
    print(f"✓ Successful: {download_summary['successful']}/{total_files}")
    print(f"✗ Failed: {download_summary['failed']}/{total_files}")
    print(f"  └─ Real Twelvedata: {download_summary['real_data']}")
    print(f"  └─ Synthetic Fallback: {download_summary['synthetic_data']}")
    print(f"Success rate: {download_summary['successful']/total_files*100:.1f}%")
    
    print("\nBy Pair:")
    for pair, statuses in download_summary['by_pair'].items():
        real_count = sum(1 for v in statuses.values() if v.get('source') == 'twelvedata')
        synth_count = sum(1 for v in statuses.values() if v.get('source') == 'synthetic')
        print(f"  {pair}: {real_count} real + {synth_count} synthetic")
    
    # Save summary
    with open('data_download_summary.json', 'w') as f:
        json.dump(download_summary, f, indent=2)
    
    print(f"\n✓ Summary saved to data_download_summary.json")
    
    # List files
    print("\n" + "=" * 70)
    print("DATA FILES")
    print("=" * 70)
    
    if os.path.exists('data'):
        files = sorted([f for f in os.listdir('data') if f.endswith('.csv')])
        if files:
            total_size = 0
            for f in files:
                filepath = os.path.join('data', f)
                size = os.path.getsize(filepath)
                total_size += size
                df_check = pd.read_csv(filepath)
                print(f"✓ {f:<40} {len(df_check):>5} candles  {size/1024:>8.1f} KB")
            print(f"\nTotal: {len(files)} files, {total_size/1024/1024:.1f} MB")
        else:
            print("No CSV files found")
    
    return download_summary

if __name__ == "__main__":
    summary = main()
    sys.exit(0 if summary['failed'] == 0 else 1)
