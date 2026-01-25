"""
Advanced Volume Profile Analysis for Trading Bot
Provides volume-at-price analysis, POC identification, and institutional flow detection
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import statistics
from safe_math_utils import safe_mean, safe_std, safe_divide

# Remove duplicate safe_mean definition since we're importing from safe_math_utils
# # Using safe_mean from safe_math_utils

# Using safe_divide from safe_math_utils

def safe_std(arr, default=0.0):
    """Calculate standard deviation safely, handling empty arrays"""
    if len(arr) == 0:
        return default
    clean_arr = np.array(arr)
    clean_arr = clean_arr[~np.isnan(clean_arr)]
    if len(clean_arr) == 0:
        return default
    return np.std(clean_arr)

def safe_corrcoef(x, y):
    """Calculate correlation coefficient safely"""
    try:
        if len(x) == 0 or len(y) == 0 or len(x) != len(y):
            return 0
        if safe_std(x) == 0 or safe_std(y) == 0:
            return 0
        corr = np.corrcoef(x, y)[0, 1]
        return corr if not np.isnan(corr) else 0
    except:
        return 0

@dataclass
class VolumeNode:
    price: float
    volume: float
    percentage: float
    is_poc: bool = False
    is_high_volume_node: bool = False

@dataclass
class VolumeProfileData:
    nodes: List[VolumeNode]
    poc_price: float
    value_area_high: float
    value_area_low: float
    total_volume: float
    profile_type: str  # 'Normal', 'P-shaped', 'b-shaped', 'D-shaped'

class AdvancedVolumeAnalyzer:
    """Advanced volume profile and smart money flow analysis"""
    
    def __init__(self):
        self.volume_threshold_multiplier = 1.5  # For identifying high volume nodes
        self.value_area_percentage = 70  # 70% value area
        
    def calculate_volume_profile(self, df: pd.DataFrame, price_levels: int = 50) -> VolumeProfileData:
        """Calculate comprehensive volume profile with POC and value area"""
        try:
            if len(df) < 20 or 'volume' not in df.columns:
                return self._empty_volume_profile()
            
            # Handle missing volume data
            volume_series = df['volume']
            if volume_series.isna().all() or (volume_series == 0).all():
                # Use tick volume estimation based on price movements
                df = df.copy()  # Avoid modifying original dataframe
                df['volume'] = self._estimate_tick_volume(df)
            
            # Determine price range
            high_price = df['high'].max()
            low_price = df['low'].min()
            price_range = high_price - low_price
            
            if price_range == 0:
                return self._empty_volume_profile()
            
            # Create price levels
            level_size = price_range / price_levels
            price_levels_array = np.linspace(low_price, high_price, price_levels + 1)
            
            # Initialize volume tracking
            volume_at_price = defaultdict(float)
            
            # Calculate volume at each price level
            for _, row in df.iterrows():
                candle_high = row['high']
                candle_low = row['low']
                candle_volume = row['volume']
                
                # Distribute volume across price levels within the candle
                for i in range(len(price_levels_array) - 1):
                    level_low = price_levels_array[i]
                    level_high = price_levels_array[i + 1]
                    level_mid = (level_low + level_high) / 2
                    
                    # Check if this price level intersects with the candle
                    if level_low <= candle_high and level_high >= candle_low:
                        # Calculate intersection ratio
                        intersection_low = max(level_low, candle_low)
                        intersection_high = min(level_high, candle_high)
                        intersection_range = intersection_high - intersection_low
                        candle_range = candle_high - candle_low
                        
                        if candle_range > 0:
                            volume_ratio = intersection_range / candle_range
                            volume_at_price[level_mid] += candle_volume * volume_ratio
            
            # Convert to sorted list
            total_volume = sum(volume_at_price.values())
            if total_volume == 0:
                return self._empty_volume_profile()
            
            # Create volume nodes
            nodes = []
            for price, volume in volume_at_price.items():
                percentage = (volume / total_volume) * 100
                nodes.append(VolumeNode(
                    price=price,
                    volume=volume,
                    percentage=percentage
                ))
            
            # Sort by volume (descending)
            nodes.sort(key=lambda x: x.volume, reverse=True)
            
            # Identify Point of Control (highest volume)
            poc_price = nodes[0].price
            nodes[0].is_poc = True
            
            # Identify high volume nodes
            if len(nodes) > 0:
                avg_volume = total_volume / len(nodes)
                threshold = avg_volume * self.volume_threshold_multiplier
                
                for node in nodes:
                    if node.volume >= threshold:
                        node.is_high_volume_node = True
            
            # Calculate value area (70% of volume)
            value_area_high, value_area_low = self._calculate_value_area(nodes, total_volume)
            
            # Determine profile type
            profile_type = self._classify_profile_type(nodes, poc_price, value_area_high, value_area_low)
            
            # Sort nodes by price for final output
            nodes.sort(key=lambda x: x.price)
            
            return VolumeProfileData(
                nodes=nodes,
                poc_price=poc_price,
                value_area_high=value_area_high,
                value_area_low=value_area_low,
                total_volume=total_volume,
                profile_type=profile_type
            )
            
        except Exception as e:
            print(f"Error calculating volume profile: {e}")
            return self._empty_volume_profile()
    
    def _estimate_tick_volume(self, df: pd.DataFrame) -> pd.Series:
        """Estimate tick volume when actual volume is not available"""
        try:
            if len(df) == 0:
                return pd.Series([1000], dtype=float)
            
            # Use price movement and volatility to estimate volume
            price_change = abs(df['close'] - df['open'])
            high_low_range = df['high'] - df['low']
            
            # Handle any NaN values that might cause issues
            price_change = price_change.where(price_change.notna(), 0)
            high_low_range = high_low_range.where(high_low_range.notna(), 0.0001)
            
            # Base volume on price movement intensity
            estimated_volume = (price_change + high_low_range) * 1000
            
            # Add some randomness to make it more realistic
            np.random.seed(42)  # For reproducible results
            if len(estimated_volume) > 0:
                noise = np.random.normal(1, 0.1, len(estimated_volume))
                estimated_volume = estimated_volume * noise
            
            # Ensure minimum volume and handle any remaining NaN values
            estimated_volume = estimated_volume.where(estimated_volume.notna(), 1000)
            return estimated_volume.clip(lower=1)
            
        except Exception as e:
            print(f"Error estimating tick volume: {e}")
            return pd.Series([1000] * max(1, len(df)), dtype=float)
    
    def _empty_volume_profile(self) -> VolumeProfileData:
        """Return empty volume profile data"""
        return VolumeProfileData(
            nodes=[],
            poc_price=0,
            value_area_high=0,
            value_area_low=0,
            total_volume=0,
            profile_type='Unknown'
        )
    
    def _calculate_value_area(self, nodes: List[VolumeNode], total_volume: float) -> Tuple[float, float]:
        """Calculate value area containing 70% of volume"""
        try:
            if not nodes or total_volume == 0:
                return 0, 0
            
            # Find POC node
            poc_node = next((node for node in nodes if node.is_poc), nodes[0])
            poc_volume = poc_node.volume
            
            # Sort nodes by price
            price_sorted_nodes = sorted(nodes, key=lambda x: x.price)
            poc_index = next(i for i, node in enumerate(price_sorted_nodes) if node.price == poc_node.price)
            
            # Expand from POC until we reach 70% of volume
            target_volume = total_volume * (self.value_area_percentage / 100)
            current_volume = poc_volume
            
            low_index = poc_index
            high_index = poc_index
            
            while current_volume < target_volume and (low_index > 0 or high_index < len(price_sorted_nodes) - 1):
                # Decide whether to expand up or down
                up_volume = price_sorted_nodes[high_index + 1].volume if high_index < len(price_sorted_nodes) - 1 else 0
                down_volume = price_sorted_nodes[low_index - 1].volume if low_index > 0 else 0
                
                if up_volume >= down_volume and high_index < len(price_sorted_nodes) - 1:
                    high_index += 1
                    current_volume += up_volume
                elif low_index > 0:
                    low_index -= 1
                    current_volume += down_volume
                else:
                    break
            
            value_area_low = price_sorted_nodes[low_index].price
            value_area_high = price_sorted_nodes[high_index].price
            
            return value_area_high, value_area_low
            
        except Exception as e:
            print(f"Error calculating value area: {e}")
            return 0, 0
    
    def _classify_profile_type(self, nodes: List[VolumeNode], poc_price: float, 
                              value_area_high: float, value_area_low: float) -> str:
        """Classify the volume profile type"""
        try:
            if not nodes:
                return 'Unknown'
            
            # Sort nodes by price
            price_sorted_nodes = sorted(nodes, key=lambda x: x.price)
            
            # Calculate position of POC within the profile
            price_range = price_sorted_nodes[-1].price - price_sorted_nodes[0].price
            if price_range == 0:
                return 'Normal'
            
            poc_position = (poc_price - price_sorted_nodes[0].price) / price_range
            
            # Classify based on POC position and volume distribution
            if 0.4 <= poc_position <= 0.6:
                return 'Normal'  # POC in middle
            elif poc_position > 0.7:
                return 'P-shaped'  # POC near top
            elif poc_position < 0.3:
                return 'b-shaped'  # POC near bottom
            else:
                # Check for D-shaped (double POC)
                high_volume_nodes = [node for node in nodes if node.is_high_volume_node]
                if len(high_volume_nodes) >= 2:
                    return 'D-shaped'
                return 'Normal'
                
        except Exception as e:
            print(f"Error classifying profile type: {e}")
            return 'Unknown'
    
    def analyze_smart_money_flow(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze smart money flow patterns"""
        try:
            if len(df) < 20:
                return {'error': 'Insufficient data for smart money analysis'}
            
            # Calculate various smart money indicators
            analysis = {
                'large_order_detection': self._detect_large_orders(df),
                'accumulation_distribution': self._analyze_accumulation_distribution(df),
                'institutional_footprint': self._analyze_institutional_footprint(df),
                'volume_spread_analysis': self._analyze_volume_spread(df),
                'smart_money_index': 0,
                'flow_direction': 'Neutral'
            }
            
            # Calculate overall smart money index
            analysis['smart_money_index'] = self._calculate_smart_money_index(analysis)
            
            # Determine flow direction
            if analysis['smart_money_index'] > 0.3:
                analysis['flow_direction'] = 'Bullish'
            elif analysis['smart_money_index'] < -0.3:
                analysis['flow_direction'] = 'Bearish'
            else:
                analysis['flow_direction'] = 'Neutral'
            
            return analysis
            
        except Exception as e:
            print(f"Error in smart money flow analysis: {e}")
            return {'error': str(e), 'smart_money_index': 0, 'flow_direction': 'Neutral'}
    
    def _detect_large_orders(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect potential large institutional orders"""
        try:
            if 'volume' not in df.columns:
                df = df.copy()
                df['volume'] = self._estimate_tick_volume(df)
            
            # Calculate volume statistics
            volume_mean = safe_mean(df['volume'].values)
            volume_std = safe_std(df['volume'].values)
            volume_threshold = volume_mean + (2 * volume_std)  # 2 standard deviations
            
            # Identify large volume candles
            large_volume_candles = df[df['volume'] > volume_threshold]
            
            if len(large_volume_candles) == 0:
                return {
                    'large_order_count': 0,
                    'large_order_percentage': 0,
                    'average_large_order_size': 0,
                    'bullish_large_orders': 0,
                    'bearish_large_orders': 0
                }
            
            # Analyze direction of large orders - use .loc to avoid SettingWithCopyWarning
            large_volume_candles = large_volume_candles.copy()
            large_volume_candles.loc[:, 'direction'] = np.where(
                large_volume_candles['close'] > large_volume_candles['open'], 
                'bullish', 'bearish'
            )
            
            bullish_count = len(large_volume_candles[large_volume_candles['direction'] == 'bullish'])
            bearish_count = len(large_volume_candles[large_volume_candles['direction'] == 'bearish'])
            
            return {
                'large_order_count': len(large_volume_candles),
                'large_order_percentage': (len(large_volume_candles) / len(df)) * 100,
                'average_large_order_size': safe_mean(large_volume_candles['volume'].values),
                'bullish_large_orders': bullish_count,
                'bearish_large_orders': bearish_count,
                'volume_threshold': volume_threshold
            }
            
        except Exception as e:
            print(f"Error detecting large orders: {e}")
            return {'large_order_count': 0, 'large_order_percentage': 0}
    
    def _analyze_accumulation_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze accumulation/distribution patterns"""
        try:
            if len(df) < 10:
                return {'trend': 'Unknown', 'strength': 0}
            
            # Calculate Money Flow Multiplier
            mf_multiplier = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
            mf_multiplier = mf_multiplier.where(mf_multiplier.notna(), 0)
            
            # Handle division by zero
            mf_multiplier = np.where(df['high'] == df['low'], 0, mf_multiplier)
            
            # Calculate Money Flow Volume
            if 'volume' not in df.columns:
                df = df.copy()
                df['volume'] = self._estimate_tick_volume(df)
            
            mf_volume = mf_multiplier * df['volume']
            
            # Calculate Accumulation/Distribution Line
            ad_line = mf_volume.cumsum()
            
            # Analyze trend with safe operations
            recent_trend = 0
            if len(ad_line) >= 10:
                try:
                    recent_diff = ad_line.iloc[-10:].diff()
                    recent_trend = safe_mean(recent_diff.dropna())
                    overall_trend = ad_line.iloc[-1] - ad_line.iloc[0]
                    
                    if recent_trend > 0 and overall_trend > 0:
                        trend = 'Accumulation'
                        ad_std = safe_std(ad_line.values)
                        strength = min(safe_divide(abs(recent_trend), ad_std, 0), 1)
                    elif recent_trend < 0 and overall_trend < 0:
                        trend = 'Distribution'
                        ad_std = safe_std(ad_line.values)
                        strength = min(safe_divide(abs(recent_trend), ad_std, 0), 1)
                    else:
                        trend = 'Neutral'
                        strength = 0
                except Exception:
                    trend = 'Unknown'
                    strength = 0
            else:
                trend = 'Unknown'
                strength = 0
            
            return {
                'trend': trend,
                'strength': strength,
                'ad_line_current': ad_line.iloc[-1] if len(ad_line) > 0 else 0,
                'ad_line_change': recent_trend
            }
            
        except Exception as e:
            print(f"Error in accumulation/distribution analysis: {e}")
            return {'trend': 'Unknown', 'strength': 0}
    
    def _analyze_institutional_footprint(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze institutional trading footprint"""
        try:
            if len(df) < 20:
                return {'institutional_presence': 0, 'confidence': 0}
            
            # Create a working copy to avoid modifying original data
            df_work = df.copy()
            
            # Ensure we have volume data
            if 'volume' not in df_work.columns:
                df_work['volume'] = self._estimate_tick_volume(df_work)
            elif len(df_work['volume'].dropna()) == 0:
                df_work['volume'] = self._estimate_tick_volume(df_work)
            
            # Validate volume data exists and is numeric
            if 'volume' not in df_work.columns:
                return {'institutional_presence': 0, 'confidence': 0, 'error': 'No volume data available'}
            
            # Calculate indicators of institutional presence
            indicators = []
            volume_consistency = 0
            efficiency = 0
            correlation = 0
            
            # 1. Volume consistency (institutions trade consistently)
            try:
                volume_mean = safe_mean(df_work['volume'].values)
                if not pd.isna(volume_mean) and volume_mean > 0:
                    volume_std = safe_std(df_work['volume'].values)
                    if not pd.isna(volume_std) and volume_std > 0:
                        volume_cv = safe_divide(volume_std, volume_mean, 1)
                        volume_consistency = max(0, 1 - volume_cv)
                        indicators.append(volume_consistency * 0.3)
            except Exception:
                pass
            
            # 2. Price efficiency (institutions move price efficiently)
            try:
                price_changes = df_work['close'].pct_change().dropna()
                if len(price_changes) > 1:
                    abs_sum = abs(price_changes).sum()
                    if abs_sum > 0:
                        efficiency = safe_divide(abs(price_changes.sum()), abs_sum, 0)
                        indicators.append(efficiency * 0.3)
            except Exception:
                pass
            
            # 3. Volume-price correlation (strong moves on high volume)
            try:
                # Calculate price changes and volume normalization with proper alignment
                price_changes = df_work['close'].pct_change()
                volume_ma = df_work['volume'].rolling(20, min_periods=1).mean() if len(window_data) > 0 else 0.0
                
                # Safe volume normalization - handle Series properly
                try:
                    volume_ma_safe = volume_ma.where(volume_ma.notna(), 1)
                except AttributeError:
                    volume_ma_safe = np.where(pd.isna(volume_ma), 1, volume_ma)
                volume_ma_safe = np.where(volume_ma_safe <= 0, 1, volume_ma_safe)
                volume_normalized = df_work['volume'] / volume_ma_safe
                
                # Remove NaN values and ensure alignment
                valid_indices = ~(price_changes.isna() | volume_normalized.isna())
                valid_count = valid_indices.sum()
                
                if valid_count > 10:  # Need at least 10 valid observations
                    price_clean = abs(price_changes[valid_indices])
                    volume_clean = volume_normalized[valid_indices]
                    
                    if len(price_clean) == len(volume_clean) and len(price_clean) > 1:
                        # Use safe correlation calculation - handle both Series and arrays
                        price_array = price_clean.values if hasattr(price_clean, 'values') else price_clean
                        volume_array = volume_clean.values if hasattr(volume_clean, 'values') else volume_clean
                        correlation = safe_corrcoef(price_array, volume_array)
                        if correlation != 0:
                            indicators.append(abs(correlation) * 0.4)
            except Exception as corr_error:
                # Skip volume-price correlation if it fails
                pass
            
            # Calculate overall institutional presence
            institutional_presence = sum(indicators) if indicators else 0
            confidence = len(indicators) / 3  # Based on how many indicators we could calculate
            
            return {
                'institutional_presence': min(institutional_presence, 1),
                'confidence': confidence,
                'volume_consistency': volume_consistency,
                'price_efficiency': efficiency,
                'volume_price_correlation': correlation if not np.isnan(correlation) else 0
            }
            
        except Exception as e:
            print(f"Error in institutional footprint analysis: {e}")
            return {'institutional_presence': 0, 'confidence': 0}
    
    def _analyze_volume_spread(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume spread relationship"""
        try:
            if len(df) < 10:
                return {'vs_analysis': 'Unknown', 'strength': 0}
            
            # Calculate spread (range) and volume for each candle
            df['spread'] = df['high'] - df['low']
            
            if 'volume' not in df.columns:
                df['volume'] = self._estimate_tick_volume(df)
            
            # Analyze recent candles for volume-spread patterns
            recent_data = df.tail(10)
            
            patterns = {
                'high_volume_narrow_spread': 0,  # Accumulation/Distribution
                'low_volume_wide_spread': 0,     # Weakness
                'high_volume_wide_spread': 0,    # Strength
                'low_volume_narrow_spread': 0    # Normal
            }
            
            # Define thresholds
            volume_median = recent_data['volume'].median()
            spread_median = recent_data['spread'].median()
            
            for _, row in recent_data.iterrows():
                is_high_volume = row['volume'] > volume_median
                is_wide_spread = row['spread'] > spread_median
                
                if is_high_volume and not is_wide_spread:
                    patterns['high_volume_narrow_spread'] += 1
                elif not is_high_volume and is_wide_spread:
                    patterns['low_volume_wide_spread'] += 1
                elif is_high_volume and is_wide_spread:
                    patterns['high_volume_wide_spread'] += 1
                else:
                    patterns['low_volume_narrow_spread'] += 1
            
            # Determine dominant pattern
            if patterns:
                dominant_pattern = max(patterns.keys(), key=lambda k: patterns[k])
                pattern_strength = patterns[dominant_pattern] / len(recent_data) if len(recent_data) > 0 else 0
            else:
                dominant_pattern = 'low_volume_narrow_spread'
                pattern_strength = 0
            
            # Interpret pattern
            if dominant_pattern == 'high_volume_narrow_spread':
                vs_analysis = 'Accumulation/Distribution'
            elif dominant_pattern == 'low_volume_wide_spread':
                vs_analysis = 'Weakness'
            elif dominant_pattern == 'high_volume_wide_spread':
                vs_analysis = 'Strength'
            else:
                vs_analysis = 'Normal'
            
            return {
                'vs_analysis': vs_analysis,
                'strength': pattern_strength,
                'patterns': patterns,
                'dominant_pattern': dominant_pattern
            }
            
        except Exception as e:
            print(f"Error in volume spread analysis: {e}")
            return {'vs_analysis': 'Unknown', 'strength': 0}
    
    def _calculate_smart_money_index(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall smart money index from component analyses"""
        try:
            index = 0
            weight_sum = 0
            
            # Large orders component
            large_orders = analysis.get('large_order_detection', {})
            if large_orders.get('large_order_count', 0) > 0:
                bullish = large_orders.get('bullish_large_orders', 0)
                bearish = large_orders.get('bearish_large_orders', 0)
                total = bullish + bearish
                if total > 0:
                    large_order_bias = (bullish - bearish) / total
                    index += large_order_bias * 0.3
                    weight_sum += 0.3
            
            # Accumulation/Distribution component
            ad_analysis = analysis.get('accumulation_distribution', {})
            ad_trend = ad_analysis.get('trend', 'Unknown')
            ad_strength = ad_analysis.get('strength', 0)
            
            if ad_trend == 'Accumulation':
                index += ad_strength * 0.3
                weight_sum += 0.3
            elif ad_trend == 'Distribution':
                index -= ad_strength * 0.3
                weight_sum += 0.3
            
            # Institutional footprint component
            institutional = analysis.get('institutional_footprint', {})
            inst_presence = institutional.get('institutional_presence', 0)
            inst_confidence = institutional.get('confidence', 0)
            
            if inst_confidence > 0.5:  # Only use if we have reasonable confidence
                index += (inst_presence - 0.5) * 0.2  # Centered around 0.5
                weight_sum += 0.2
            
            # Volume spread component
            vs_analysis = analysis.get('volume_spread_analysis', {})
            vs_type = vs_analysis.get('vs_analysis', 'Unknown')
            vs_strength = vs_analysis.get('strength', 0)
            
            if vs_type == 'Strength':
                index += vs_strength * 0.2
                weight_sum += 0.2
            elif vs_type == 'Weakness':
                index -= vs_strength * 0.2
                weight_sum += 0.2
            elif vs_type == 'Accumulation/Distribution':
                index += vs_strength * 0.1  # Neutral to slightly positive
                weight_sum += 0.1
            
            # Normalize by actual weights used
            if weight_sum > 0:
                index = index / weight_sum
            
            # Clamp to [-1, 1] range
            return max(-1, min(1, index))
            
        except Exception as e:
            print(f"Error calculating smart money index: {e}")
            return 0

# Global analyzer instance
volume_analyzer = AdvancedVolumeAnalyzer()

def get_volume_profile_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Get comprehensive volume profile analysis"""
    try:
        profile = volume_analyzer.calculate_volume_profile(df)
        smart_money = volume_analyzer.analyze_smart_money_flow(df)
        
        return {
            'volume_profile': {
                'poc_price': profile.poc_price,
                'value_area_high': profile.value_area_high,
                'value_area_low': profile.value_area_low,
                'total_volume': profile.total_volume,
                'profile_type': profile.profile_type,
                'high_volume_nodes': [node.price for node in profile.nodes if node.is_high_volume_node]
            },
            'smart_money_flow': smart_money,
            'analysis_summary': {
                'volume_strength': 'High' if profile.total_volume > 0 else 'Low',
                'institutional_activity': smart_money.get('flow_direction', 'Neutral'),
                'key_levels': [profile.poc_price, profile.value_area_high, profile.value_area_low]
            }
        }
        
    except Exception as e:
        print(f"Error in volume profile analysis: {e}")
        return {
            'volume_profile': {'error': str(e)},
            'smart_money_flow': {'error': str(e)},
            'analysis_summary': {'error': str(e)}
        }