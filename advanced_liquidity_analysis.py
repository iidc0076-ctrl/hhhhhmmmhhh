#!/usr/bin/env python3
"""
Advanced Liquidity Analysis Module
Comprehensive liquidity concepts including zones, sweeps, pools, and smart money flow detection
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
from safe_math_utils import safe_divide, safe_mean, safe_std

class LiquidityType(Enum):
    BUY_SIDE = "buy_side"
    SELL_SIDE = "sell_side"
    INTERNAL = "internal"
    EXTERNAL = "external"

class LiquidityStrength(Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    EXTREME = "extreme"

@dataclass
class LiquidityZone:
    price_level: float
    zone_high: float
    zone_low: float
    liquidity_type: LiquidityType
    strength: LiquidityStrength
    volume_estimate: float
    creation_time: int
    last_tested: Optional[int] = None
    times_tested: int = 0
    is_swept: bool = False
    sweep_time: Optional[int] = None
    confluence_factors: List[str] = None

    def __post_init__(self):
        if self.confluence_factors is None:
            self.confluence_factors = []

@dataclass
class LiquiditySweep:
    sweep_price: float
    direction: str  # "bullish" or "bearish"
    liquidity_captured: float
    sweep_time: int
    reaction_strength: float
    follow_through: bool
    zone_swept: LiquidityZone

@dataclass
class LiquidityPool:
    center_price: float
    pool_high: float
    pool_low: float
    estimated_volume: float
    pool_type: str  # "resting", "hidden", "iceberg"
    formation_pattern: str
    magnetic_strength: float
    active: bool = True

class AdvancedLiquidityAnalyzer:
    """Advanced liquidity analysis with comprehensive concepts"""
    
    def __init__(self):
        self.liquidity_zones: List[LiquidityZone] = []
        self.liquidity_sweeps: List[LiquiditySweep] = []
        self.liquidity_pools: List[LiquidityPool] = []
        self.safe_mean = self._safe_mean
        self.safe_std = self._safe_std
        
    def _safe_mean(self, arr, default=0.0):
        """Calculate mean safely"""
        if len(arr) == 0:
            return default
        return np.nanmean(arr) if not np.isnan(arr).all() else default
    
    def _safe_std(self, arr, default=0.0):
        """Calculate standard deviation safely"""
        if len(arr) == 0:
            return default
        return np.nanstd(arr) if not np.isnan(arr).all() else default
    
    def analyze_comprehensive_liquidity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive liquidity analysis combining all concepts"""
        try:
            if df is None or len(df) < 20:
                return self._empty_liquidity_analysis()
            
            # Core liquidity analysis
            liquidity_zones = self.detect_liquidity_zones(df)
            liquidity_sweeps = self.detect_liquidity_sweeps(df)
            liquidity_pools = self.detect_liquidity_pools(df)
            
            # Advanced concepts
            order_flow_imbalance = self.analyze_order_flow_imbalance(df)
            institutional_footprint = self.detect_institutional_footprint(df)
            liquidity_gaps = self._identify_liquidity_gaps(df)
            smart_money_clusters = self._detect_smart_money_clusters(df)
            
            # Liquidity-based signals
            liquidity_signals = self.generate_liquidity_signals(df, liquidity_zones, liquidity_sweeps)
            
            # Market maker behavior
            market_maker_activity = self.analyze_market_maker_behavior(df)
            
            return {
                'liquidity_zones': liquidity_zones,
                'liquidity_sweeps': liquidity_sweeps,
                'liquidity_pools': liquidity_pools,
                'order_flow_imbalance': order_flow_imbalance,
                'institutional_footprint': institutional_footprint,
                'liquidity_gaps': liquidity_gaps,
                'smart_money_clusters': smart_money_clusters,
                'liquidity_signals': liquidity_signals,
                'market_maker_activity': market_maker_activity,
                'overall_liquidity_bias': self._calculate_overall_bias(liquidity_signals),
                'liquidity_quality': self._assess_liquidity_quality(df, liquidity_zones)
            }
            
        except Exception as e:
            print(f"Error in comprehensive liquidity analysis: {e}")
            return self._empty_liquidity_analysis()
    
    def detect_liquidity_zones(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect high-probability liquidity zones"""
        zones = []
        
        try:
            # Equal highs/lows (classic liquidity zones)
            equal_zones = self._detect_equal_highs_lows(df)
            zones.extend(equal_zones)
            
            # Previous day/week/month highs and lows
            time_based_zones = self._detect_time_based_liquidity(df)
            zones.extend(time_based_zones)
            
            # Round number zones (psychological levels)
            round_number_zones = self._detect_round_number_zones(df)
            zones.extend(round_number_zones)
            
            # Volume-based liquidity zones
            volume_zones = self._detect_volume_based_zones(df)
            zones.extend(volume_zones)
            
            # Failed breakout zones
            failed_breakout_zones = self._detect_failed_breakout_zones(df)
            zones.extend(failed_breakout_zones)
            
            # Range extremes
            range_zones = self._detect_range_extreme_zones(df)
            zones.extend(range_zones)
            
            # Sort by strength and proximity to current price
            current_price = df['close'].iloc[-1]
            
            # Add strength_score to zones that don't have it
            for zone in zones:
                if 'strength_score' not in zone:
                    strength_map = {'weak': 25, 'moderate': 50, 'strong': 75, 'extreme': 100}
                    zone['strength_score'] = strength_map.get(zone.get('strength', 'weak'), 25)
            
            zones = sorted(zones, key=lambda x: (
                x.get('strength_score', 25),
                1 / (abs(x['price_level'] - current_price) + 0.0001)
            ), reverse=True)
            
            return zones[:15]  # Return top 15 zones
            
        except Exception as e:
            print(f"Error detecting liquidity zones: {e}")
            return []
    
    def _detect_equal_highs_lows(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect equal highs and lows where liquidity rests"""
        zones = []
        
        try:
            # Find swing highs and lows
            swing_highs = self._find_swing_points(df, 'high', window=5)
            swing_lows = self._find_swing_points(df, 'low', window=5)
            
            # Detect equal highs
            for i, high1 in enumerate(swing_highs):
                for high2 in swing_highs[i+1:]:
                    price_diff = abs(high1['price'] - high2['price'])
                    if safe_divide(price_diff, high1['price']) < 0.002:  # Within 0.2%
                        zones.append({
                            'price_level': (high1['price'] + high2['price']) / 2,
                            'zone_high': max(high1['price'], high2['price']) * 1.0005,
                            'zone_low': min(high1['price'], high2['price']) * 0.9995,
                            'liquidity_type': 'sell_side',
                            'strength': self._calculate_zone_strength(
                                [high1, high2], df, 'equal_highs'
                            ),
                            'formation_pattern': 'equal_highs',
                            'confluence_factors': self._get_confluence_factors(
                                (high1['price'] + high2['price']) / 2, df
                            )
                        })
            
            # Detect equal lows
            for i, low1 in enumerate(swing_lows):
                for low2 in swing_lows[i+1:]:
                    price_diff = abs(low1['price'] - low2['price'])
                    if safe_divide(price_diff, low1['price']) < 0.002:  # Within 0.2%
                        zones.append({
                            'price_level': (low1['price'] + low2['price']) / 2,
                            'zone_high': max(low1['price'], low2['price']) * 1.0005,
                            'zone_low': min(low1['price'], low2['price']) * 0.9995,
                            'liquidity_type': 'buy_side',
                            'strength': self._calculate_zone_strength(
                                [low1, low2], df, 'equal_lows'
                            ),
                            'formation_pattern': 'equal_lows',
                            'confluence_factors': self._get_confluence_factors(
                                (low1['price'] + low2['price']) / 2, df
                            )
                        })
            
            return zones
            
        except Exception as e:
            print(f"Error detecting equal highs/lows: {e}")
            return []
    
    def _detect_time_based_liquidity(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect time-based liquidity zones (daily, weekly highs/lows)"""
        zones = []
        
        try:
            if 'datetime' in df.columns:
                df_time = df.copy()
                df_time['datetime'] = pd.to_datetime(df_time['datetime'])
                
                # Daily highs/lows
                daily_highs = df_time.groupby(df_time['datetime'].dt.date)['high'].max()
                daily_lows = df_time.groupby(df_time['datetime'].dt.date)['low'].min()
                
                # Recent daily levels (last 5 days)
                for high in daily_highs.tail(5):
                    zones.append({
                        'price_level': high,
                        'zone_high': high * 1.001,
                        'zone_low': high * 0.999,
                        'liquidity_type': 'sell_side',
                        'strength': 'moderate',
                        'formation_pattern': 'daily_high',
                        'confluence_factors': ['time_based_resistance']
                    })
                
                for low in daily_lows.tail(5):
                    zones.append({
                        'price_level': low,
                        'zone_high': low * 1.001,
                        'zone_low': low * 0.999,
                        'liquidity_type': 'buy_side',
                        'strength': 'moderate',
                        'formation_pattern': 'daily_low',
                        'confluence_factors': ['time_based_support']
                    })
            
            return zones
            
        except Exception as e:
            print(f"Error detecting time-based liquidity: {e}")
            return []
    
    def _detect_round_number_zones(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect round number psychological liquidity zones"""
        zones = []
        
        try:
            current_price = df['close'].iloc[-1]
            price_range = df['high'].max() - df['low'].min()
            
            # Determine appropriate round number intervals
            if current_price > 100:
                intervals = [1, 5, 10, 25, 50, 100]
            elif current_price > 10:
                intervals = [0.1, 0.25, 0.5, 1, 2.5, 5]
            else:
                intervals = [0.01, 0.05, 0.1, 0.25, 0.5]
            
            for interval in intervals:
                # Find round numbers near current price
                base = int(safe_divide(current_price, interval)) * interval
                
                for multiplier in [-2, -1, 0, 1, 2]:
                    round_level = base + (multiplier * interval)
                    
                    if abs(round_level - current_price) <= price_range:
                        # Determine liquidity type based on position
                        liquidity_type = 'sell_side' if round_level > current_price else 'buy_side'
                        
                        zones.append({
                            'price_level': round_level,
                            'zone_high': round_level * 1.0005,
                            'zone_low': round_level * 0.9995,
                            'liquidity_type': liquidity_type,
                            'strength': 'weak',
                            'formation_pattern': f'round_number_{interval}',
                            'confluence_factors': ['psychological_level']
                        })
            
            return zones
            
        except Exception as e:
            print(f"Error detecting round number zones: {e}")
            return []
    
    def _detect_volume_based_zones(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect liquidity zones based on volume analysis"""
        zones = []
        
        try:
            # Volume proxy calculation
            volume_proxy = (df['high'] - df['low']) + abs(df['close'] - df['open'])
            
            # High volume nodes (potential liquidity zones)
            volume_threshold = volume_proxy.quantile(0.8)
            high_volume_indices = volume_proxy[volume_proxy > volume_threshold].index
            
            for idx in high_volume_indices:
                price_level = (df.loc[idx, 'high'] + df.loc[idx, 'low']) / 2
                
                zones.append({
                    'price_level': price_level,
                    'zone_high': df.loc[idx, 'high'],
                    'zone_low': df.loc[idx, 'low'],
                    'liquidity_type': 'internal',
                    'strength': 'moderate',
                    'formation_pattern': 'high_volume_node',
                    'confluence_factors': ['volume_confluence']
                })
            
            return zones[-10:]  # Return most recent 10
            
        except Exception as e:
            print(f"Error detecting volume-based zones: {e}")
            return []
    
    def detect_liquidity_sweeps(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect liquidity sweeps and their characteristics"""
        sweeps = []
        
        try:
            # Detect stop hunt patterns
            stop_hunts = self._detect_stop_hunts(df)
            sweeps.extend(stop_hunts)
            
            # Detect liquidity grab patterns
            liquidity_grabs = self._detect_liquidity_grabs(df)
            sweeps.extend(liquidity_grabs)
            
            # Detect false breakouts (liquidity sweeps)
            false_breakouts = self._detect_false_breakouts(df)
            sweeps.extend(false_breakouts)
            
            return sweeps
            
        except Exception as e:
            print(f"Error detecting liquidity sweeps: {e}")
            return []
    
    def _detect_stop_hunts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect stop hunt patterns"""
        stop_hunts = []
        
        try:
            for i in range(10, len(df)-5):
                current_high = df['high'].iloc[i]
                current_low = df['low'].iloc[i]
                
                # Look for recent highs/lows that might have stops
                recent_highs = df['high'].iloc[max(0, i-20):i].max()
                recent_lows = df['low'].iloc[max(0, i-20):i].min()
                
                # Check for stop hunt above recent high
                if current_high > recent_highs * 1.001:  # Break above by 0.1%
                    # Check for quick reversal (indication of stop hunt)
                    next_few_closes = df['close'].iloc[i:i+5]
                    if len(next_few_closes) > 0 and next_few_closes.min() < current_high * 0.995:
                        stop_hunts.append({
                            'sweep_price': current_high,
                            'direction': 'bearish_sweep',
                            'sweep_time': i,
                            'liquidity_captured': current_high - recent_highs,
                            'reaction_strength': (current_high - next_few_closes.min()) / current_high,
                            'pattern_type': 'stop_hunt_above'
                        })
                
                # Check for stop hunt below recent low
                if current_low < recent_lows * 0.999:  # Break below by 0.1%
                    next_few_closes = df['close'].iloc[i:i+5]
                    if len(next_few_closes) > 0 and next_few_closes.max() > current_low * 1.005:
                        stop_hunts.append({
                            'sweep_price': current_low,
                            'direction': 'bullish_sweep',
                            'sweep_time': i,
                            'liquidity_captured': recent_lows - current_low,
                            'reaction_strength': (next_few_closes.max() - current_low) / current_low,
                            'pattern_type': 'stop_hunt_below'
                        })
            
            return stop_hunts
            
        except Exception as e:
            print(f"Error detecting stop hunts: {e}")
            return []
    
    def detect_liquidity_pools(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect liquidity pools and accumulation zones"""
        pools = []
        
        try:
            # Detect consolidation zones (resting liquidity)
            consolidation_pools = self._detect_consolidation_pools(df)
            pools.extend(consolidation_pools)
            
            # Detect iceberg orders (hidden liquidity)
            iceberg_pools = self._detect_iceberg_patterns(df)
            pools.extend(iceberg_pools)
            
            # Detect institutional accumulation zones
            accumulation_pools = self._detect_accumulation_zones(df)
            pools.extend(accumulation_pools)
            
            return pools
            
        except Exception as e:
            print(f"Error detecting liquidity pools: {e}")
            return []
    
    def _detect_consolidation_pools(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect consolidation zones where liquidity pools form"""
        pools = []
        
        try:
            # Look for low volatility periods with tight price ranges
            for window_size in [10, 20, 30]:
                for i in range(window_size, len(df)):
                    window_data = df.iloc[i-window_size:i]
                    
                    price_range = window_data['high'].max() - window_data['low'].min()
                    avg_range = (window_data['high'] - window_data['low']).mean()
                    
                    # Low volatility consolidation
                    if price_range < avg_range * 1.5:
                        center_price = (window_data['high'].max() + window_data['low'].min()) / 2
                        
                        pools.append({
                            'center_price': center_price,
                            'pool_high': window_data['high'].max(),
                            'pool_low': window_data['low'].min(),
                            'estimated_volume': (window_data['high'] - window_data['low']).sum(),
                            'pool_type': 'resting',
                            'formation_pattern': f'consolidation_{window_size}',
                            'magnetic_strength': self._calculate_magnetic_strength(window_data),
                            'formation_time': i
                        })
            
            return pools
            
        except Exception as e:
            print(f"Error detecting consolidation pools: {e}")
            return []
    
    def _detect_failed_breakout_zones(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect failed breakout zones where liquidity accumulates"""
        zones = []
        
        try:
            for i in range(20, len(df)-5):
                # Look for breakout attempts that failed
                current_high = df['high'].iloc[i]
                current_low = df['low'].iloc[i]
                
                # Previous resistance/support levels
                prev_high = df['high'].iloc[i-20:i].max()
                prev_low = df['low'].iloc[i-20:i].min()
                
                # Check for failed breakout above resistance
                if current_high > prev_high * 1.002:  # Initial breakout
                    # Check if it failed (price came back)
                    next_closes = df['close'].iloc[i:i+5]
                    if len(next_closes) > 0 and next_closes.min() < prev_high:
                        zones.append({
                            'price_level': prev_high,
                            'zone_high': current_high,
                            'zone_low': prev_high * 0.999,
                            'liquidity_type': 'sell_side',
                            'strength': 'strong',
                            'formation_pattern': 'failed_breakout_above',
                            'confluence_factors': ['failed_breakout', 'resistance_rejection']
                        })
                
                # Check for failed breakdown below support
                if current_low < prev_low * 0.998:  # Initial breakdown
                    next_closes = df['close'].iloc[i:i+5]
                    if len(next_closes) > 0 and next_closes.max() > prev_low:
                        zones.append({
                            'price_level': prev_low,
                            'zone_high': prev_low * 1.001,
                            'zone_low': current_low,
                            'liquidity_type': 'buy_side',
                            'strength': 'strong',
                            'formation_pattern': 'failed_breakdown_below',
                            'confluence_factors': ['failed_breakdown', 'support_bounce']
                        })
            
            return zones[-10:]  # Return most recent 10
            
        except Exception as e:
            print(f"Error detecting failed breakout zones: {e}")
            return []
    
    def _detect_range_extreme_zones(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect range extreme zones where liquidity pools form"""
        zones = []
        
        try:
            # Identify ranging periods
            for window_size in [20, 30, 50]:
                for i in range(window_size, len(df)):
                    window_data = df.iloc[i-window_size:i]
                    
                    # Check if it's a ranging market
                    range_high = window_data['high'].max()
                    range_low = window_data['low'].min()
                    range_size = range_high - range_low
                    
                    # Calculate average candle range
                    avg_candle_range = (window_data['high'] - window_data['low']).mean()
                    
                    # If range is not too large compared to individual candles
                    if range_size < avg_candle_range * 8:
                        # Range top liquidity zone
                        zones.append({
                            'price_level': range_high,
                            'zone_high': range_high * 1.0005,
                            'zone_low': range_high * 0.9995,
                            'liquidity_type': 'sell_side',
                            'strength': 'moderate',
                            'formation_pattern': f'range_top_{window_size}',
                            'confluence_factors': ['range_resistance']
                        })
                        
                        # Range bottom liquidity zone
                        zones.append({
                            'price_level': range_low,
                            'zone_high': range_low * 1.0005,
                            'zone_low': range_low * 0.9995,
                            'liquidity_type': 'buy_side',
                            'strength': 'moderate',
                            'formation_pattern': f'range_bottom_{window_size}',
                            'confluence_factors': ['range_support']
                        })
            
            return zones[-15:]  # Return most recent 15
            
        except Exception as e:
            print(f"Error detecting range extreme zones: {e}")
            return []
    
    def _detect_liquidity_grabs(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect liquidity grab patterns"""
        grabs = []
        
        try:
            for i in range(10, len(df)-3):
                # Look for sudden spikes that grab liquidity
                current_candle = df.iloc[i]
                prev_candles = df.iloc[i-5:i]
                
                # Calculate normal range
                normal_range = (prev_candles['high'] - prev_candles['low']).mean()
                current_range = current_candle['high'] - current_candle['low']
                
                # Check for unusually large range (liquidity grab)
                if current_range > normal_range * 2.5:
                    # Check for quick reversal (indication of grab)
                    next_candles = df.iloc[i+1:i+4]
                    if len(next_candles) > 0:
                        # Upward grab followed by reversal
                        if (current_candle['high'] > prev_candles['high'].max() and
                            next_candles['close'].min() < current_candle['close']):
                            grabs.append({
                                'sweep_price': current_candle['high'],
                                'direction': 'bearish_grab',
                                'sweep_time': i,
                                'liquidity_captured': current_candle['high'] - prev_candles['high'].max(),
                                'reaction_strength': (current_candle['high'] - next_candles['close'].min()) / current_candle['high'],
                                'pattern_type': 'upward_liquidity_grab'
                            })
                        
                        # Downward grab followed by reversal
                        elif (current_candle['low'] < prev_candles['low'].min() and
                              next_candles['close'].max() > current_candle['close']):
                            grabs.append({
                                'sweep_price': current_candle['low'],
                                'direction': 'bullish_grab',
                                'sweep_time': i,
                                'liquidity_captured': prev_candles['low'].min() - current_candle['low'],
                                'reaction_strength': (next_candles['close'].max() - current_candle['low']) / current_candle['low'],
                                'pattern_type': 'downward_liquidity_grab'
                            })
            
            return grabs
            
        except Exception as e:
            print(f"Error detecting liquidity grabs: {e}")
            return []
    
    def _detect_false_breakouts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect false breakout patterns (liquidity sweeps)"""
        false_breakouts = []
        
        try:
            for i in range(15, len(df)-5):
                # Look for key levels (recent highs/lows)
                lookback_data = df.iloc[i-15:i]
                key_high = lookback_data['high'].max()
                key_low = lookback_data['low'].min()
                
                current_high = df['high'].iloc[i]
                current_low = df['low'].iloc[i]
                
                # False breakout above key high
                if current_high > key_high * 1.001:  # Break above by 0.1%
                    # Check for reversal within next few candles
                    next_data = df.iloc[i+1:i+6]
                    if len(next_data) > 0:
                        lowest_after = next_data['low'].min()
                        if lowest_after < key_high * 0.999:  # Came back below key level
                            false_breakouts.append({
                                'sweep_price': current_high,
                                'direction': 'bearish_sweep',
                                'sweep_time': i,
                                'liquidity_captured': current_high - key_high,
                                'reaction_strength': (current_high - lowest_after) / current_high,
                                'pattern_type': 'false_breakout_above',
                                'key_level': key_high
                            })
                
                # False breakdown below key low
                if current_low < key_low * 0.999:  # Break below by 0.1%
                    next_data = df.iloc[i+1:i+6]
                    if len(next_data) > 0:
                        highest_after = next_data['high'].max()
                        if highest_after > key_low * 1.001:  # Came back above key level
                            false_breakouts.append({
                                'sweep_price': current_low,
                                'direction': 'bullish_sweep',
                                'sweep_time': i,
                                'liquidity_captured': key_low - current_low,
                                'reaction_strength': (highest_after - current_low) / current_low,
                                'pattern_type': 'false_breakdown_below',
                                'key_level': key_low
                            })
            
            return false_breakouts
            
        except Exception as e:
            print(f"Error detecting false breakouts: {e}")
            return []
    
    def _detect_iceberg_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect iceberg order patterns (hidden liquidity)"""
        icebergs = []
        
        try:
            # Look for repeated rejections at same level
            for i in range(20, len(df)):
                current_price = df['close'].iloc[i]
                
                # Check recent data for repeated touches
                recent_data = df.iloc[i-20:i]
                
                # Find price levels that were touched multiple times
                for price_level in [recent_data['high'].max(), recent_data['low'].min()]:
                    touches = 0
                    for j in range(len(recent_data)):
                        candle = recent_data.iloc[j]
                        if abs(candle['high'] - price_level) / price_level < 0.002:  # Within 0.2%
                            touches += 1
                        elif abs(candle['low'] - price_level) / price_level < 0.002:
                            touches += 1
                    
                    # If level was touched multiple times (iceberg indication)
                    if touches >= 3:
                        pool_type = 'sell_side' if price_level > current_price else 'buy_side'
                        
                        icebergs.append({
                            'center_price': price_level,
                            'pool_high': price_level * 1.002,
                            'pool_low': price_level * 0.998,
                            'estimated_volume': touches * 10,  # Estimate based on touches
                            'pool_type': 'iceberg',
                            'formation_pattern': f'iceberg_{touches}_touches',
                            'magnetic_strength': touches / 10.0,
                            'liquidity_side': pool_type
                        })
            
            return icebergs[-5:]  # Return most recent 5
            
        except Exception as e:
            print(f"Error detecting iceberg patterns: {e}")
            return []
    
    def _detect_accumulation_zones(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect institutional accumulation zones"""
        accumulation_zones = []
        
        try:
            # Look for low volatility periods with increasing volume proxy
            for window_size in [15, 25, 40]:
                for i in range(window_size, len(df)):
                    window_data = df.iloc[i-window_size:i]
                    
                    # Calculate volatility (price range)
                    volatility = (window_data['high'] - window_data['low']).mean()
                    
                    # Calculate volume proxy trend
                    volume_proxy = (window_data['high'] - window_data['low']) + abs(window_data['close'] - window_data['open'])
                    early_volume = volume_proxy.iloc[:window_size//2].mean()
                    late_volume = volume_proxy.iloc[window_size//2:].mean()
                    
                    # Low volatility with increasing volume = accumulation
                    if volatility < df['high'].std() * 0.5 and late_volume > early_volume * 1.2:
                        center_price = (window_data['high'].max() + window_data['low'].min()) / 2
                        
                        accumulation_zones.append({
                            'center_price': center_price,
                            'pool_high': window_data['high'].max(),
                            'pool_low': window_data['low'].min(),
                            'estimated_volume': late_volume,
                            'pool_type': 'accumulation',
                            'formation_pattern': f'institutional_accumulation_{window_size}',
                            'magnetic_strength': (late_volume / early_volume) - 1,
                            'volatility_score': 1 - (volatility / df['high'].std())
                        })
            
            return accumulation_zones[-8:]  # Return most recent 8
            
        except Exception as e:
            print(f"Error detecting accumulation zones: {e}")
            return []
    
    def _identify_liquidity_gaps(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify liquidity gaps in the market"""
        gaps = []
        
        try:
            for i in range(1, len(df)):
                prev_candle = df.iloc[i-1]
                current_candle = df.iloc[i]
                
                # Gap up (price jumps higher)
                if current_candle['low'] > prev_candle['high']:
                    gap_size = current_candle['low'] - prev_candle['high']
                    gaps.append({
                        'gap_type': 'gap_up',
                        'gap_start': prev_candle['high'],
                        'gap_end': current_candle['low'],
                        'gap_size': gap_size,
                        'gap_index': i,
                        'filled': False,
                        'liquidity_zone': 'unfilled_gap'
                    })
                
                # Gap down (price jumps lower)
                elif current_candle['high'] < prev_candle['low']:
                    gap_size = prev_candle['low'] - current_candle['high']
                    gaps.append({
                        'gap_type': 'gap_down',
                        'gap_start': prev_candle['low'],
                        'gap_end': current_candle['high'],
                        'gap_size': gap_size,
                        'gap_index': i,
                        'filled': False,
                        'liquidity_zone': 'unfilled_gap'
                    })
            
            # Check if gaps have been filled
            for gap in gaps:
                gap_start_idx = gap['gap_index']
                for j in range(gap_start_idx + 1, len(df)):
                    candle = df.iloc[j]
                    
                    if gap['gap_type'] == 'gap_up':
                        # Gap filled if price trades back into gap
                        if candle['low'] <= gap['gap_end']:
                            gap['filled'] = True
                            gap['fill_index'] = j
                            break
                    else:  # gap_down
                        if candle['high'] >= gap['gap_end']:
                            gap['filled'] = True
                            gap['fill_index'] = j
                            break
            
            return gaps[-10:]  # Return most recent 10 gaps
            
        except Exception as e:
            print(f"Error identifying liquidity gaps: {e}")
            return []
    
    def _detect_smart_money_clusters(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect smart money clustering patterns"""
        clusters = []
        
        try:
            # Look for areas with multiple smart money signatures
            for i in range(30, len(df)):
                analysis_window = df.iloc[i-30:i]
                
                smart_money_signals = 0
                signal_types = []
                
                # Large candles (institutional moves)
                volume_proxy = (analysis_window['high'] - analysis_window['low']) + abs(analysis_window['close'] - analysis_window['open'])
                large_moves = volume_proxy > volume_proxy.quantile(0.9)
                if large_moves.sum() > 3:
                    smart_money_signals += large_moves.sum()
                    signal_types.append('large_institutional_moves')
                
                # Absorption patterns (wicks)
                upper_wicks = analysis_window['high'] - analysis_window[['open', 'close']].max(axis=1)
                lower_wicks = analysis_window[['open', 'close']].min(axis=1) - analysis_window['low']
                
                significant_wicks = ((upper_wicks > (analysis_window['high'] - analysis_window['low']) * 0.4) |
                                   (lower_wicks > (analysis_window['high'] - analysis_window['low']) * 0.4)).sum()
                
                if significant_wicks > 5:
                    smart_money_signals += significant_wicks
                    signal_types.append('order_absorption')
                
                # Price rejection at key levels
                window_high = analysis_window['high'].max()
                window_low = analysis_window['low'].min()
                
                rejections_at_high = 0
                rejections_at_low = 0
                
                for j in range(len(analysis_window)):
                    candle = analysis_window.iloc[j]
                    if abs(candle['high'] - window_high) / window_high < 0.002:
                        if candle['close'] < candle['high'] * 0.995:  # Rejection
                            rejections_at_high += 1
                    if abs(candle['low'] - window_low) / window_low < 0.002:
                        if candle['close'] > candle['low'] * 1.005:  # Bounce
                            rejections_at_low += 1
                
                if rejections_at_high + rejections_at_low > 2:
                    smart_money_signals += rejections_at_high + rejections_at_low
                    signal_types.append('level_rejections')
                
                # If enough smart money signals in this area
                if smart_money_signals > 8:
                    center_price = (analysis_window['high'].max() + analysis_window['low'].min()) / 2
                    
                    clusters.append({
                        'center_price': center_price,
                        'cluster_high': analysis_window['high'].max(),
                        'cluster_low': analysis_window['low'].min(),
                        'smart_money_score': smart_money_signals,
                        'signal_types': signal_types,
                        'cluster_strength': min(smart_money_signals / 15.0, 1.0),
                        'formation_index': i
                    })
            
            return clusters[-5:]  # Return most recent 5 clusters
            
        except Exception as e:
            print(f"Error detecting smart money clusters: {e}")
            return []
    
    def analyze_order_flow_imbalance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze order flow imbalances for liquidity insights"""
        try:
            # Calculate bid/ask imbalance using wick analysis
            imbalances = []
            
            for i in range(len(df)):
                upper_wick = df['high'].iloc[i] - max(df['open'].iloc[i], df['close'].iloc[i])
                lower_wick = min(df['open'].iloc[i], df['close'].iloc[i]) - df['low'].iloc[i]
                body_size = abs(df['close'].iloc[i] - df['open'].iloc[i])
                
                total_range = df['high'].iloc[i] - df['low'].iloc[i]
                if total_range > 0:
                    upper_wick_ratio = upper_wick / total_range
                    lower_wick_ratio = lower_wick / total_range
                    body_ratio = body_size / total_range
                    
                    # Calculate imbalance
                    if upper_wick_ratio > 0.4:  # Significant upper wick
                        imbalance_strength = upper_wick_ratio * body_ratio
                        imbalances.append({
                            'index': i,
                            'type': 'sell_pressure',
                            'strength': imbalance_strength
                        })
                    elif lower_wick_ratio > 0.4:  # Significant lower wick
                        imbalance_strength = lower_wick_ratio * body_ratio
                        imbalances.append({
                            'index': i,
                            'type': 'buy_pressure',
                            'strength': imbalance_strength
                        })
            
            # Recent imbalance analysis
            recent_imbalances = [i for i in imbalances if i['index'] >= len(df) - 20]
            
            buy_pressure = sum(i['strength'] for i in recent_imbalances if i['type'] == 'buy_pressure')
            sell_pressure = sum(i['strength'] for i in recent_imbalances if i['type'] == 'sell_pressure')
            
            return {
                'recent_buy_pressure': buy_pressure,
                'recent_sell_pressure': sell_pressure,
                'net_imbalance': buy_pressure - sell_pressure,
                'imbalance_direction': 'bullish' if buy_pressure > sell_pressure else 'bearish',
                'imbalance_strength': abs(buy_pressure - sell_pressure),
                'total_imbalances': len(recent_imbalances)
            }
            
        except Exception as e:
            print(f"Error analyzing order flow imbalance: {e}")
            return {
                'recent_buy_pressure': 0,
                'recent_sell_pressure': 0,
                'net_imbalance': 0,
                'imbalance_direction': 'neutral',
                'imbalance_strength': 0,
                'total_imbalances': 0
            }
    
    def detect_institutional_footprint(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect institutional trading footprint through liquidity analysis"""
        try:
            # Large candle analysis (potential institutional moves)
            volume_proxy = (df['high'] - df['low']) + abs(df['close'] - df['open'])
            large_moves = volume_proxy > volume_proxy.quantile(0.9)
            
            institutional_signals = []
            
            for i, is_large in enumerate(large_moves):
                if is_large and i > 0:
                    candle_type = 'bullish' if df['close'].iloc[i] > df['open'].iloc[i] else 'bearish'
                    
                    # Check for follow-through
                    if i < len(df) - 1:
                        next_candle_follow = (
                            (candle_type == 'bullish' and df['close'].iloc[i+1] > df['close'].iloc[i]) or
                            (candle_type == 'bearish' and df['close'].iloc[i+1] < df['close'].iloc[i])
                        )
                    else:
                        next_candle_follow = False
                    
                    institutional_signals.append({
                        'index': i,
                        'type': candle_type,
                        'strength': volume_proxy.iloc[i],
                        'follow_through': next_candle_follow,
                        'price_level': df['close'].iloc[i]
                    })
            
            # Recent institutional activity
            recent_signals = [s for s in institutional_signals if s['index'] >= len(df) - 20]
            
            bullish_institutional = [s for s in recent_signals if s['type'] == 'bullish']
            bearish_institutional = [s for s in recent_signals if s['type'] == 'bearish']
            
            return {
                'total_institutional_moves': len(recent_signals),
                'bullish_moves': len(bullish_institutional),
                'bearish_moves': len(bearish_institutional),
                'institutional_bias': 'bullish' if len(bullish_institutional) > len(bearish_institutional) else 'bearish',
                'average_move_strength': self.safe_mean([s['strength'] for s in recent_signals]),
                'follow_through_rate': self.safe_mean([s['follow_through'] for s in recent_signals]) * 100
            }
            
        except Exception as e:
            print(f"Error detecting institutional footprint: {e}")
            return {
                'total_institutional_moves': 0,
                'bullish_moves': 0,
                'bearish_moves': 0,
                'institutional_bias': 'neutral',
                'average_move_strength': 0,
                'follow_through_rate': 0
            }
    
    def generate_liquidity_signals(self, df: pd.DataFrame, zones: List[Dict], sweeps: List[Dict]) -> Dict[str, Any]:
        """Generate trading signals based on liquidity analysis"""
        try:
            current_price = df['close'].iloc[-1]
            signals = []
            
            # Zone-based signals
            for zone in zones:
                distance = abs(current_price - zone['price_level']) / current_price
                
                if distance < 0.01:  # Within 1% of zone
                    if zone['liquidity_type'] == 'buy_side':
                        signals.append({
                            'type': 'liquidity_bounce',
                            'direction': 'bullish',
                            'strength': zone.get('strength_score', 50),
                            'reason': f"Price near buy-side liquidity at {zone['price_level']:.5f}"
                        })
                    elif zone['liquidity_type'] == 'sell_side':
                        signals.append({
                            'type': 'liquidity_reversal',
                            'direction': 'bearish',
                            'strength': zone.get('strength_score', 50),
                            'reason': f"Price near sell-side liquidity at {zone['price_level']:.5f}"
                        })
            
            # Sweep-based signals
            recent_sweeps = [s for s in sweeps if s.get('sweep_time', 0) >= len(df) - 10]
            for sweep in recent_sweeps:
                if sweep.get('reaction_strength', 0) > 0.005:  # Significant reaction
                    signals.append({
                        'type': 'post_sweep_reaction',
                        'direction': sweep['direction'].replace('_sweep', ''),
                        'strength': sweep['reaction_strength'] * 1000,
                        'reason': f"Strong reaction after {sweep['direction']} liquidity sweep"
                    })
            
            # Calculate overall bias
            bullish_signals = [s for s in signals if s['direction'] == 'bullish']
            bearish_signals = [s for s in signals if s['direction'] == 'bearish']
            
            bullish_strength = sum(s['strength'] for s in bullish_signals)
            bearish_strength = sum(s['strength'] for s in bearish_signals)
            
            return {
                'signals': signals,
                'bullish_strength': bullish_strength,
                'bearish_strength': bearish_strength,
                'net_bias': bullish_strength - bearish_strength,
                'dominant_bias': 'bullish' if bullish_strength > bearish_strength else 'bearish',
                'signal_count': len(signals)
            }
            
        except Exception as e:
            print(f"Error generating liquidity signals: {e}")
            return {
                'signals': [],
                'bullish_strength': 0,
                'bearish_strength': 0,
                'net_bias': 0,
                'dominant_bias': 'neutral',
                'signal_count': 0
            }
    
    def analyze_market_maker_behavior(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market maker behavior and manipulation patterns"""
        try:
            # Detect price manipulation patterns
            manipulation_patterns = []
            
            for i in range(10, len(df)-5):
                # Look for sudden price spikes followed by quick reversals
                current_high = df['high'].iloc[i]
                current_low = df['low'].iloc[i]
                
                prev_range = df['high'].iloc[i-10:i].max() - df['low'].iloc[i-10:i].min()
                current_range = current_high - current_low
                
                # Unusually large range (potential manipulation)
                if current_range > prev_range * 2:
                    # Check for quick reversal
                    next_closes = df['close'].iloc[i+1:i+6]
                    if len(next_closes) > 0:
                        if (current_high - next_closes.min()) / current_high > 0.01:
                            manipulation_patterns.append({
                                'type': 'spike_reversal',
                                'direction': 'bearish_trap',
                                'index': i,
                                'manipulation_strength': current_range / prev_range
                            })
                        elif (next_closes.max() - current_low) / current_low > 0.01:
                            manipulation_patterns.append({
                                'type': 'spike_reversal',
                                'direction': 'bullish_trap',
                                'index': i,
                                'manipulation_strength': current_range / prev_range
                            })
            
            # Detect accumulation/distribution phases
            accumulation_score = self._detect_accumulation_phase(df)
            distribution_score = self._detect_distribution_phase(df)
            
            return {
                'manipulation_patterns': manipulation_patterns[-5:],  # Recent 5
                'accumulation_score': accumulation_score,
                'distribution_score': distribution_score,
                'market_maker_bias': 'accumulation' if accumulation_score > distribution_score else 'distribution',
                'manipulation_frequency': len(manipulation_patterns),
                'recent_manipulation': len([p for p in manipulation_patterns if p['index'] >= len(df) - 20])
            }
            
        except Exception as e:
            print(f"Error analyzing market maker behavior: {e}")
            return {
                'manipulation_patterns': [],
                'accumulation_score': 0,
                'distribution_score': 0,
                'market_maker_bias': 'neutral',
                'manipulation_frequency': 0,
                'recent_manipulation': 0
            }
    
    # Helper methods
    def _find_swing_points(self, df: pd.DataFrame, column: str, window: int = 5) -> List[Dict]:
        """Find swing points in price data"""
        swing_points = []
        
        for i in range(window, len(df) - window):
            current_value = df[column].iloc[i]
            is_swing = True
            
            # Check if it's a swing high/low
            if column == 'high':
                for j in range(i - window, i + window + 1):
                    if j != i and df[column].iloc[j] >= current_value:
                        is_swing = False
                        break
            else:  # 'low'
                for j in range(i - window, i + window + 1):
                    if j != i and df[column].iloc[j] <= current_value:
                        is_swing = False
                        break
            
            if is_swing:
                swing_points.append({
                    'index': i,
                    'price': current_value,
                    'type': column
                })
        
        return swing_points
    
    def _calculate_zone_strength(self, points: List[Dict], df: pd.DataFrame, pattern_type: str) -> str:
        """Calculate strength of liquidity zone"""
        # Simple strength calculation based on number of points and volume
        if len(points) >= 3:
            return 'strong'
        elif len(points) == 2:
            return 'moderate'
        else:
            return 'weak'
    
    def _get_confluence_factors(self, price_level: float, df: pd.DataFrame) -> List[str]:
        """Get confluence factors for a price level"""
        factors = []
        current_price = df['close'].iloc[-1]
        
        # Add basic confluence factors
        if abs(price_level - current_price) / current_price < 0.005:
            factors.append('near_current_price')
        
        return factors
    
    def _calculate_magnetic_strength(self, window_data: pd.DataFrame) -> float:
        """Calculate magnetic strength of a liquidity pool"""
        return len(window_data) / 20.0  # Simple calculation
    
    def _detect_accumulation_phase(self, df: pd.DataFrame) -> float:
        """Detect accumulation phase score"""
        # Simplified accumulation detection
        recent_data = df.tail(20)
        price_stability = 1 - (recent_data['high'].max() - recent_data['low'].min()) / recent_data['close'].mean()
        volume_increase = (recent_data['high'] - recent_data['low']).tail(10).mean() / (recent_data['high'] - recent_data['low']).head(10).mean()
        
        return (price_stability + min(volume_increase, 2)) / 2 * 100
    
    def _detect_distribution_phase(self, df: pd.DataFrame) -> float:
        """Detect distribution phase score"""
        # Simplified distribution detection
        recent_data = df.tail(20)
        price_weakness = (recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) / recent_data['close'].iloc[0]
        volatility_increase = recent_data['high'].std() / df['high'].tail(50).std()
        
        return max(0, (volatility_increase - price_weakness) * 50)
    
    def _empty_liquidity_analysis(self) -> Dict[str, Any]:
        """Return empty liquidity analysis"""
        return {
            'liquidity_zones': [],
            'liquidity_sweeps': [],
            'liquidity_pools': [],
            'order_flow_imbalance': {'net_imbalance': 0},
            'institutional_footprint': {'institutional_bias': 'neutral'},
            'liquidity_gaps': [],
            'smart_money_clusters': [],
            'liquidity_signals': {'dominant_bias': 'neutral'},
            'market_maker_activity': {'market_maker_bias': 'neutral'},
            'overall_liquidity_bias': 'neutral',
            'liquidity_quality': 'unknown'
        }
    
    def _calculate_overall_bias(self, liquidity_signals: Dict[str, Any]) -> str:
        """Calculate overall liquidity bias"""
        return liquidity_signals.get('dominant_bias', 'neutral')
    
    def _assess_liquidity_quality(self, df: pd.DataFrame, zones: List[Dict]) -> str:
        """Assess overall liquidity quality"""
        if len(zones) > 10:
            return 'high'
        elif len(zones) > 5:
            return 'moderate'
        else:
            return 'low'

# Global analyzer instance
liquidity_analyzer = AdvancedLiquidityAnalyzer()

def get_comprehensive_liquidity_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Get comprehensive liquidity analysis for a DataFrame"""
    return liquidity_analyzer.analyze_comprehensive_liquidity(df)

def get_liquidity_zones(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Get liquidity zones for a DataFrame"""
    return liquidity_analyzer.detect_liquidity_zones(df)

def get_liquidity_sweeps(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Get liquidity sweeps for a DataFrame"""
    return liquidity_analyzer.detect_liquidity_sweeps(df)

def analyze_order_flow_liquidity(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze order flow imbalances"""
    return liquidity_analyzer.analyze_order_flow_imbalance(df)