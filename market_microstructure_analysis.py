"""
Market Microstructure Analysis for Trading Bot
Analyzes price ladder, order flow, gaps, and market maker behavior
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

class OrderFlowType(Enum):
    MARKET_MAKER = "market_maker"
    MARKET_TAKER = "market_taker"
    INSTITUTIONAL = "institutional"
    RETAIL = "retail"

class GapType(Enum):
    BREAKAWAY = "breakaway"
    CONTINUATION = "continuation"
    EXHAUSTION = "exhaustion"
    COMMON = "common"

@dataclass
class PriceLadderLevel:
    price: float
    volume: float
    order_count: int
    imbalance_ratio: float  # buy vs sell pressure
    significance_score: float

@dataclass
class OrderFlowSignal:
    flow_type: OrderFlowType
    direction: str  # "bullish", "bearish", "neutral"
    strength: float
    volume_profile: Dict[str, float]
    time_intensity: float
    confidence: float

@dataclass
class GapAnalysis:
    gap_type: GapType
    gap_size: float
    gap_percentage: float
    fill_probability: float
    expected_fill_time_hours: Optional[float]
    resistance_levels: List[float]
    support_levels: List[float]

@dataclass
class TickMomentumData:
    tick_direction: str  # "up", "down", "neutral"
    tick_intensity: float
    volume_per_tick: float
    price_acceleration: float
    momentum_sustainability: float

class MarketMicrostructureAnalyzer:
    """Advanced market microstructure analysis for institutional-level insights"""
    
    def __init__(self):
        self.config = {
            'price_ladder_levels': 20,
            'significant_volume_threshold': 1.5,  # 1.5x average volume
            'imbalance_threshold': 0.6,  # 60% imbalance to be significant
            'tick_analysis_window': 50,
            'gap_fill_threshold': 0.5,  # 50% gap fill considered significant
            'institutional_volume_threshold': 2.0,  # 2x average for institutional
            'market_maker_spread_threshold': 0.0005  # 0.05% spread threshold
        }
        
    async def analyze_price_ladder(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze price ladder and order clustering"""
        try:
            current_price = df['close'].iloc[-1]
            high_price = df['high'].max()
            low_price = df['low'].min()
            
            # Create price levels around current price
            price_range = high_price - low_price
            level_spacing = price_range / self.config['price_ladder_levels']
            
            price_levels = []
            for i in range(self.config['price_ladder_levels']):
                level_price = low_price + (i * level_spacing)
                
                # Calculate volume and activity at each level
                level_data = self._analyze_price_level_activity(df, level_price, level_spacing)
                
                if level_data:
                    price_levels.append(level_data)
            
            # Identify significant levels
            significant_levels = [level for level in price_levels 
                                if level.significance_score > 1.0]
            
            # Calculate overall ladder imbalance
            total_buy_volume = sum(level.volume * max(0, level.imbalance_ratio) 
                                 for level in price_levels)
            total_sell_volume = sum(level.volume * max(0, -level.imbalance_ratio) 
                                  for level in price_levels)
            
            overall_imbalance = (total_buy_volume - total_sell_volume) / max(
                total_buy_volume + total_sell_volume, 1)
            
            # Identify clustering zones
            clustering_zones = self._identify_order_clustering(price_levels, current_price)
            
            return {
                'current_price': current_price,
                'price_levels': [
                    {
                        'price': level.price,
                        'volume': level.volume,
                        'order_count': level.order_count,
                        'imbalance_ratio': level.imbalance_ratio,
                        'significance_score': level.significance_score
                    } for level in price_levels
                ],
                'significant_levels': [
                    {
                        'price': level.price,
                        'volume': level.volume,
                        'significance_score': level.significance_score,
                        'distance_from_current': abs(level.price - current_price) / current_price
                    } for level in significant_levels
                ],
                'overall_imbalance': overall_imbalance,
                'clustering_zones': clustering_zones,
                'ladder_quality': self._assess_ladder_quality(price_levels, overall_imbalance)
            }
            
        except Exception as e:
            return self._empty_price_ladder_analysis()
    
    def _analyze_price_level_activity(self, df: pd.DataFrame, target_price: float, 
                                    tolerance: float) -> Optional[PriceLadderLevel]:
        """Analyze activity at a specific price level"""
        try:
            # Find candles that touched this price level
            touched_candles = df[
                (df['low'] <= target_price + tolerance) & 
                (df['high'] >= target_price - tolerance)
            ]
            
            if len(touched_candles) == 0:
                return None
            
            # Calculate volume and activity metrics
            total_volume = touched_candles['volume'].sum() if 'volume' in df.columns else len(touched_candles)
            order_count = len(touched_candles)
            
            # Estimate buy/sell imbalance based on price action
            imbalance_ratio = self._estimate_level_imbalance(touched_candles, target_price)
            
            # Calculate significance score
            avg_volume = df['volume'].mean() if 'volume' in df.columns else 1
            significance_score = (total_volume / max(avg_volume, 1)) * (order_count / max(len(df) / 10, 1))
            
            return PriceLadderLevel(
                price=target_price,
                volume=total_volume,
                order_count=order_count,
                imbalance_ratio=imbalance_ratio,
                significance_score=significance_score
            )
            
        except Exception as e:
            return None
    
    def _estimate_level_imbalance(self, candles: pd.DataFrame, target_price: float) -> float:
        """Estimate buy/sell imbalance at a price level"""
        try:
            if len(candles) == 0:
                return 0.0
            
            # Calculate buying vs selling pressure based on close relative to OHLC
            buy_signals = 0
            sell_signals = 0
            
            for _, candle in candles.iterrows():
                close_position = (candle['close'] - candle['low']) / max(candle['high'] - candle['low'], 0.001)
                
                if close_position > 0.6:  # Close in upper 40% = buying pressure
                    buy_signals += 1
                elif close_position < 0.4:  # Close in lower 40% = selling pressure
                    sell_signals += 1
            
            total_signals = buy_signals + sell_signals
            if total_signals == 0:
                return 0.0
                
            return (buy_signals - sell_signals) / total_signals
            
        except Exception as e:
            return 0.0
    
    def _identify_order_clustering(self, price_levels: List[PriceLadderLevel], 
                                 current_price: float) -> List[Dict[str, Any]]:
        """Identify zones where orders are clustering"""
        clustering_zones = []
        
        try:
            # Sort levels by significance
            significant_levels = sorted(
                [level for level in price_levels if level.significance_score > 0.8],
                key=lambda x: x.significance_score,
                reverse=True
            )
            
            # Group nearby significant levels
            for i, level in enumerate(significant_levels[:10]):  # Top 10 levels
                # Check if this level is part of a cluster
                cluster_levels = [level]
                price_tolerance = current_price * 0.001  # 0.1% tolerance
                
                for other_level in significant_levels[i+1:]:
                    if abs(other_level.price - level.price) <= price_tolerance:
                        cluster_levels.append(other_level)
                
                if len(cluster_levels) >= 2:  # Cluster of 2+ levels
                    total_volume = sum(cl.volume for cl in cluster_levels)
                    avg_price = np.mean([cl.price for cl in cluster_levels])
                    max_significance = max(cl.significance_score for cl in cluster_levels)
                    
                    clustering_zones.append({
                        'center_price': avg_price,
                        'total_volume': total_volume,
                        'level_count': len(cluster_levels),
                        'max_significance': max_significance,
                        'distance_from_current': abs(avg_price - current_price) / current_price,
                        'zone_type': 'support' if avg_price < current_price else 'resistance'
                    })
            
            return clustering_zones[:5]  # Return top 5 clusters
            
        except Exception as e:
            return []
    
    def _assess_ladder_quality(self, price_levels: List[PriceLadderLevel], 
                             overall_imbalance: float) -> Dict[str, Any]:
        """Assess the quality and reliability of price ladder data"""
        try:
            if not price_levels:
                return {'quality_score': 0.0, 'reliability': 'poor', 'issues': ['no_data']}
            
            # Calculate quality metrics
            avg_significance = np.mean([level.significance_score for level in price_levels])
            significant_level_count = len([level for level in price_levels if level.significance_score > 1.0])
            imbalance_strength = abs(overall_imbalance)
            
            # Quality score calculation
            quality_score = (
                min(avg_significance / 2.0, 1.0) * 0.4 +  # Average significance
                min(significant_level_count / 5.0, 1.0) * 0.3 +  # Number of significant levels
                min(imbalance_strength * 2, 1.0) * 0.3  # Imbalance strength
            )
            
            # Determine reliability
            if quality_score > 0.7:
                reliability = 'excellent'
            elif quality_score > 0.5:
                reliability = 'good'
            elif quality_score > 0.3:
                reliability = 'fair'
            else:
                reliability = 'poor'
            
            # Identify issues
            issues = []
            if avg_significance < 0.5:
                issues.append('low_significance')
            if significant_level_count < 2:
                issues.append('few_significant_levels')
            if imbalance_strength < 0.1:
                issues.append('weak_imbalance')
            
            return {
                'quality_score': quality_score,
                'reliability': reliability,
                'issues': issues,
                'avg_significance': avg_significance,
                'significant_level_count': significant_level_count,
                'imbalance_strength': imbalance_strength
            }
            
        except Exception as e:
            return {'quality_score': 0.0, 'reliability': 'poor', 'issues': ['calculation_error']}
    
    async def analyze_order_flow(self, df: pd.DataFrame) -> OrderFlowSignal:
        """Analyze order flow patterns to identify market maker vs taker activity"""
        try:
            # Calculate volume-based metrics
            volume_analysis = self._analyze_volume_patterns(df)
            
            # Analyze tick-by-tick movement patterns
            tick_analysis = self._analyze_tick_patterns(df)
            
            # Identify institutional vs retail behavior
            flow_classification = self._classify_order_flow(df, volume_analysis, tick_analysis)
            
            # Calculate overall signal
            direction = self._determine_flow_direction(volume_analysis, tick_analysis)
            strength = self._calculate_flow_strength(volume_analysis, tick_analysis)
            confidence = self._calculate_flow_confidence(volume_analysis, tick_analysis, flow_classification)
            
            return OrderFlowSignal(
                flow_type=flow_classification,
                direction=direction,
                strength=strength,
                volume_profile=volume_analysis,
                time_intensity=tick_analysis['intensity'],
                confidence=confidence
            )
            
        except Exception as e:
            return self._empty_order_flow_signal()
    
    def _analyze_volume_patterns(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze volume patterns to identify order flow characteristics"""
        try:
            if 'volume' not in df.columns:
                # Estimate volume based on price action
                df = df.copy()
                df['volume'] = (df['high'] - df['low']) * 1000  # Rough estimation
            
            # Calculate volume metrics with safe handling
            avg_volume_series = df['volume'].rolling(20, min_periods=1).mean()
            avg_volume = avg_volume_series.iloc[-1] if len(avg_volume_series) > 0 else df['volume'].iloc[-1]
            current_volume = df['volume'].iloc[-1]
            volume_ratio = current_volume / max(avg_volume, 1)
            
            # Volume profile analysis
            up_volume = df[df['close'] > df['open']]['volume'].sum()
            down_volume = df[df['close'] <= df['open']]['volume'].sum()
            total_volume = up_volume + down_volume
            
            volume_imbalance = (up_volume - down_volume) / max(total_volume, 1)
            
            # Large order detection
            volume_threshold = avg_volume * self.config['institutional_volume_threshold']
            large_orders = len(df[df['volume'] > volume_threshold])
            large_order_ratio = large_orders / len(df)
            
            return {
                'volume_ratio': volume_ratio,
                'volume_imbalance': volume_imbalance,
                'large_order_ratio': large_order_ratio,
                'avg_volume': avg_volume,
                'current_volume': current_volume,
                'up_volume_pct': up_volume / max(total_volume, 1),
                'down_volume_pct': down_volume / max(total_volume, 1)
            }
            
        except Exception as e:
            return {
                'volume_ratio': 1.0,
                'volume_imbalance': 0.0,
                'large_order_ratio': 0.0,
                'avg_volume': 1000,
                'current_volume': 1000,
                'up_volume_pct': 0.5,
                'down_volume_pct': 0.5
            }
    
    def _analyze_tick_patterns(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze tick-by-tick patterns for market microstructure insights"""
        try:
            # Calculate price changes
            price_changes = df['close'].diff()
            
            # Tick direction analysis
            up_ticks = len(price_changes[price_changes > 0])
            down_ticks = len(price_changes[price_changes < 0])
            neutral_ticks = len(price_changes[price_changes == 0])
            total_ticks = len(price_changes.dropna())
            
            if total_ticks == 0:
                return {'intensity': 0.0, 'directional_bias': 0.0, 'acceleration': 0.0}
            
            # Calculate metrics
            directional_bias = (up_ticks - down_ticks) / total_ticks
            tick_intensity = (up_ticks + down_ticks) / total_ticks  # Non-neutral ticks
            
            # Price acceleration (change in momentum)
            momentum = price_changes.rolling(5).mean()
            acceleration = momentum.diff().abs().mean()
            
            return {
                'intensity': tick_intensity,
                'directional_bias': directional_bias,
                'acceleration': acceleration,
                'up_tick_ratio': up_ticks / total_ticks,
                'down_tick_ratio': down_ticks / total_ticks,
                'neutral_tick_ratio': neutral_ticks / total_ticks
            }
            
        except Exception as e:
            return {
                'intensity': 0.5,
                'directional_bias': 0.0,
                'acceleration': 0.0,
                'up_tick_ratio': 0.33,
                'down_tick_ratio': 0.33,
                'neutral_tick_ratio': 0.34
            }
    
    def _classify_order_flow(self, df: pd.DataFrame, volume_analysis: Dict[str, float], 
                           tick_analysis: Dict[str, float]) -> OrderFlowType:
        """Classify the type of order flow (institutional vs retail, maker vs taker)"""
        try:
            # Institutional indicators
            large_order_indicator = volume_analysis['large_order_ratio'] > 0.2
            volume_concentration = volume_analysis['volume_ratio'] > 2.0
            
            # Market maker indicators
            low_acceleration = tick_analysis['acceleration'] < 0.001
            balanced_ticks = abs(tick_analysis['directional_bias']) < 0.1
            
            # Classification logic
            if large_order_indicator and volume_concentration:
                return OrderFlowType.INSTITUTIONAL
            elif low_acceleration and balanced_ticks:
                return OrderFlowType.MARKET_MAKER
            elif tick_analysis['intensity'] > 0.8:
                return OrderFlowType.MARKET_TAKER
            else:
                return OrderFlowType.RETAIL
                
        except Exception as e:
            return OrderFlowType.RETAIL
    
    def _determine_flow_direction(self, volume_analysis: Dict[str, float], 
                                tick_analysis: Dict[str, float]) -> str:
        """Determine overall order flow direction"""
        try:
            volume_signal = volume_analysis['volume_imbalance']
            tick_signal = tick_analysis['directional_bias']
            
            # Combined signal
            combined_signal = (volume_signal * 0.6) + (tick_signal * 0.4)
            
            if combined_signal > 0.1:
                return "bullish"
            elif combined_signal < -0.1:
                return "bearish"
            else:
                return "neutral"
                
        except Exception as e:
            return "neutral"
    
    def _calculate_flow_strength(self, volume_analysis: Dict[str, float], 
                               tick_analysis: Dict[str, float]) -> float:
        """Calculate the strength of the order flow signal"""
        try:
            # Volume strength component
            volume_strength = min(volume_analysis['volume_ratio'] / 3.0, 1.0)
            
            # Tick intensity component
            tick_strength = tick_analysis['intensity']
            
            # Imbalance strength
            volume_imbalance_strength = abs(volume_analysis['volume_imbalance'])
            tick_imbalance_strength = abs(tick_analysis['directional_bias'])
            
            # Combined strength
            strength = (
                volume_strength * 0.3 +
                tick_strength * 0.2 +
                volume_imbalance_strength * 0.3 +
                tick_imbalance_strength * 0.2
            )
            
            return min(strength, 1.0)
            
        except Exception as e:
            return 0.5
    
    def _calculate_flow_confidence(self, volume_analysis: Dict[str, float], 
                                 tick_analysis: Dict[str, float], 
                                 flow_type: OrderFlowType) -> float:
        """Calculate confidence in the order flow analysis"""
        try:
            base_confidence = 0.5
            
            # Boost confidence for institutional flow
            if flow_type == OrderFlowType.INSTITUTIONAL:
                base_confidence += 0.2
            
            # Volume data quality boost
            if volume_analysis['volume_ratio'] > 0.5:
                base_confidence += 0.1
            
            # Tick data quality boost
            if tick_analysis['intensity'] > 0.3:
                base_confidence += 0.1
            
            # Consistency boost
            volume_direction = 1 if volume_analysis['volume_imbalance'] > 0 else -1
            tick_direction = 1 if tick_analysis['directional_bias'] > 0 else -1
            
            if volume_direction == tick_direction:
                base_confidence += 0.1
            
            return min(base_confidence, 1.0)
            
        except Exception as e:
            return 0.5
    
    async def analyze_gaps(self, df: pd.DataFrame) -> List[GapAnalysis]:
        """Analyze price gaps and their fill probabilities"""
        try:
            gaps = []
            
            # Identify gaps in the data
            for i in range(1, len(df)):
                prev_high = df['high'].iloc[i-1]
                prev_low = df['low'].iloc[i-1]
                curr_high = df['high'].iloc[i]
                curr_low = df['low'].iloc[i]
                
                # Check for gap up
                if curr_low > prev_high:
                    gap_size = curr_low - prev_high
                    gap_analysis = await self._analyze_individual_gap(
                        df, i, gap_size, "up", prev_high, curr_low
                    )
                    if gap_analysis:
                        gaps.append(gap_analysis)
                
                # Check for gap down
                elif curr_high < prev_low:
                    gap_size = prev_low - curr_high
                    gap_analysis = await self._analyze_individual_gap(
                        df, i, gap_size, "down", curr_high, prev_low
                    )
                    if gap_analysis:
                        gaps.append(gap_analysis)
            
            return gaps[-10:]  # Return last 10 gaps
            
        except Exception as e:
            return []
    
    async def _analyze_individual_gap(self, df: pd.DataFrame, gap_index: int, 
                                    gap_size: float, gap_direction: str,
                                    gap_low: float, gap_high: float) -> Optional[GapAnalysis]:
        """Analyze an individual gap for type and fill probability"""
        try:
            current_price = df['close'].iloc[-1]
            gap_percentage = gap_size / current_price
            
            # Classify gap type
            gap_type = self._classify_gap_type(df, gap_index, gap_direction)
            
            # Calculate fill probability
            fill_probability = self._calculate_gap_fill_probability(
                gap_type, gap_percentage, gap_direction, 
                current_price, gap_low, gap_high
            )
            
            # Estimate fill time
            expected_fill_time = self._estimate_gap_fill_time(
                gap_type, gap_percentage, fill_probability
            )
            
            # Identify key levels
            support_levels, resistance_levels = self._identify_gap_levels(
                gap_low, gap_high, gap_direction
            )
            
            return GapAnalysis(
                gap_type=gap_type,
                gap_size=gap_size,
                gap_percentage=gap_percentage,
                fill_probability=fill_probability,
                expected_fill_time_hours=expected_fill_time,
                resistance_levels=resistance_levels,
                support_levels=support_levels
            )
            
        except Exception as e:
            return None
    
    def _classify_gap_type(self, df: pd.DataFrame, gap_index: int, 
                          gap_direction: str) -> GapType:
        """Classify the type of gap based on context"""
        try:
            # Analyze volume and price action around the gap
            pre_gap_volume = df['volume'].iloc[max(0, gap_index-5):gap_index].mean() if 'volume' in df.columns else 1000
            post_gap_volume = df['volume'].iloc[gap_index:gap_index+5].mean() if 'volume' in df.columns else 1000
            
            volume_ratio = post_gap_volume / max(pre_gap_volume, 1)
            
            # Analyze trend context
            pre_gap_trend = self._analyze_trend_strength(df, max(0, gap_index-20), gap_index)
            
            # Classification logic
            if volume_ratio > 2.0 and abs(pre_gap_trend) > 0.6:
                return GapType.BREAKAWAY
            elif volume_ratio > 1.5 and abs(pre_gap_trend) > 0.3:
                return GapType.CONTINUATION
            elif volume_ratio < 0.8 and abs(pre_gap_trend) > 0.7:
                return GapType.EXHAUSTION
            else:
                return GapType.COMMON
                
        except Exception as e:
            return GapType.COMMON
    
    def _analyze_trend_strength(self, df: pd.DataFrame, start_idx: int, end_idx: int) -> float:
        """Analyze trend strength in a given period"""
        try:
            if start_idx >= end_idx or end_idx > len(df):
                return 0.0
            
            period_data = df.iloc[start_idx:end_idx]
            start_price = period_data['close'].iloc[0]
            end_price = period_data['close'].iloc[-1]
            
            return (end_price - start_price) / start_price
            
        except Exception as e:
            return 0.0
    
    def _calculate_gap_fill_probability(self, gap_type: GapType, gap_percentage: float,
                                      gap_direction: str, current_price: float,
                                      gap_low: float, gap_high: float) -> float:
        """Calculate the probability that a gap will be filled"""
        try:
            base_probabilities = {
                GapType.COMMON: 0.9,
                GapType.BREAKAWAY: 0.3,
                GapType.CONTINUATION: 0.5,
                GapType.EXHAUSTION: 0.8
            }
            
            base_prob = base_probabilities[gap_type]
            
            # Adjust for gap size
            size_adjustment = max(0, 1 - gap_percentage * 10)  # Large gaps less likely to fill
            
            # Adjust for distance from current price
            if gap_direction == "up":
                distance_ratio = abs(current_price - gap_low) / current_price
            else:
                distance_ratio = abs(current_price - gap_high) / current_price
            
            distance_adjustment = max(0, 1 - distance_ratio * 5)
            
            # Final probability
            fill_probability = base_prob * size_adjustment * distance_adjustment
            
            return max(0.1, min(fill_probability, 0.95))
            
        except Exception as e:
            return 0.5
    
    def _estimate_gap_fill_time(self, gap_type: GapType, gap_percentage: float, 
                              fill_probability: float) -> Optional[float]:
        """Estimate time to gap fill in hours"""
        try:
            if fill_probability < 0.2:
                return None
            
            base_times = {
                GapType.COMMON: 4.0,      # 4 hours
                GapType.CONTINUATION: 24.0, # 1 day
                GapType.BREAKAWAY: 168.0,   # 1 week
                GapType.EXHAUSTION: 12.0    # 12 hours
            }
            
            base_time = base_times[gap_type]
            
            # Adjust for gap size and probability
            size_multiplier = 1 + gap_percentage * 20
            probability_multiplier = 2 - fill_probability
            
            estimated_time = base_time * size_multiplier * probability_multiplier
            
            return min(estimated_time, 720.0)  # Max 30 days
            
        except Exception as e:
            return None
    
    def _identify_gap_levels(self, gap_low: float, gap_high: float, 
                           gap_direction: str) -> Tuple[List[float], List[float]]:
        """Identify key support and resistance levels around gaps"""
        try:
            support_levels = []
            resistance_levels = []
            
            if gap_direction == "up":
                # Gap up: gap_low to gap_high is the gap
                support_levels.append(gap_low)  # Bottom of gap as support
                resistance_levels.append(gap_high)  # Top of gap as resistance if filled
            else:
                # Gap down: gap_high to gap_low is the gap  
                support_levels.append(gap_low)  # Bottom of gap as support if filled
                resistance_levels.append(gap_high)  # Top of gap as resistance
            
            return support_levels, resistance_levels
            
        except Exception as e:
            return [], []
    
    def _empty_price_ladder_analysis(self) -> Dict[str, Any]:
        """Return empty price ladder analysis"""
        return {
            'current_price': 0.0,
            'price_levels': [],
            'significant_levels': [],
            'overall_imbalance': 0.0,
            'clustering_zones': [],
            'ladder_quality': {'quality_score': 0.0, 'reliability': 'poor', 'issues': ['no_data']}
        }
    
    def _empty_order_flow_signal(self) -> OrderFlowSignal:
        """Return empty order flow signal"""
        return OrderFlowSignal(
            flow_type=OrderFlowType.RETAIL,
            direction="neutral",
            strength=0.0,
            volume_profile={},
            time_intensity=0.0,
            confidence=0.0
        )

# Global instance
_microstructure_analyzer = None

async def get_microstructure_analyzer() -> MarketMicrostructureAnalyzer:
    """Get or create the global microstructure analyzer instance"""
    global _microstructure_analyzer
    if _microstructure_analyzer is None:
        _microstructure_analyzer = MarketMicrostructureAnalyzer()
    return _microstructure_analyzer

async def analyze_price_ladder(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze price ladder and order clustering"""
    analyzer = await get_microstructure_analyzer()
    return await analyzer.analyze_price_ladder(df)

async def analyze_order_flow(df: pd.DataFrame) -> OrderFlowSignal:
    """Analyze order flow patterns"""
    analyzer = await get_microstructure_analyzer()
    return await analyzer.analyze_order_flow(df)

async def analyze_gaps(df: pd.DataFrame) -> List[GapAnalysis]:
    """Analyze price gaps and fill probabilities"""
    analyzer = await get_microstructure_analyzer()
    return await analyzer.analyze_gaps(df)

async def get_comprehensive_microstructure_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Get comprehensive market microstructure analysis"""
    try:
        analyzer = await get_microstructure_analyzer()
        
        # Run all analyses
        price_ladder = await analyzer.analyze_price_ladder(df)
        order_flow = await analyzer.analyze_order_flow(df)
        gaps = await analyzer.analyze_gaps(df)
        
        return {
            'price_ladder': price_ladder,
            'order_flow': {
                'flow_type': order_flow.flow_type.value,
                'direction': order_flow.direction,
                'strength': order_flow.strength,
                'confidence': order_flow.confidence,
                'volume_profile': order_flow.volume_profile,
                'time_intensity': order_flow.time_intensity
            },
            'gaps': [
                {
                    'gap_type': gap.gap_type.value,
                    'gap_size': gap.gap_size,
                    'gap_percentage': gap.gap_percentage,
                    'fill_probability': gap.fill_probability,
                    'expected_fill_time_hours': gap.expected_fill_time_hours,
                    'support_levels': gap.support_levels,
                    'resistance_levels': gap.resistance_levels
                } for gap in gaps
            ],
            'microstructure_quality': {
                'data_reliability': price_ladder['ladder_quality']['reliability'],
                'analysis_confidence': order_flow.confidence,
                'gap_analysis_count': len(gaps)
            }
        }
        
    except Exception as e:
        return {
            'price_ladder': {},
            'order_flow': {},
            'gaps': [],
            'microstructure_quality': {'data_reliability': 'poor', 'analysis_confidence': 0.0, 'gap_analysis_count': 0},
            'error': str(e)
        }