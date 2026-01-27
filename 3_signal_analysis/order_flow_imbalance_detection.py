"""
Order Flow Imbalance Detection System for Trading Bot
Detects bid/ask imbalances, absorption patterns, and institutional order flow
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from safe_math_utils import safe_mean, safe_divide, safe_std, safe_corrcoef, safe_rolling_mean, safe_polyfit

class ImbalanceType(Enum):
    BID_HEAVY = "bid_heavy"
    ASK_HEAVY = "ask_heavy"
    BALANCED = "balanced"
    EXTREME_BID = "extreme_bid"
    EXTREME_ASK = "extreme_ask"

class AbsorptionType(Enum):
    BUY_ABSORPTION = "buy_absorption"
    SELL_ABSORPTION = "sell_absorption"
    MUTUAL_ABSORPTION = "mutual_absorption"
    NO_ABSORPTION = "no_absorption"

@dataclass
class ImbalanceLevel:
    price: float
    bid_volume: float
    ask_volume: float
    imbalance_ratio: float
    absorption_strength: float
    institutional_signature: float

@dataclass
class OrderFlowImbalance:
    timestamp: datetime
    imbalance_type: ImbalanceType
    overall_ratio: float
    strength: float
    price_levels: List[ImbalanceLevel]
    absorption_analysis: Dict[str, Any]
    institutional_flow: Dict[str, Any]
    market_impact_score: float
    reliability_score: float

class OrderFlowImbalanceDetector:
    """Advanced order flow imbalance detection with institutional analysis"""
    
    def __init__(self):
        self.config = {
            'imbalance_threshold': 0.6,  # 60% imbalance considered significant
            'extreme_imbalance_threshold': 0.8,  # 80% for extreme imbalance
            'absorption_threshold': 1.5,  # 1.5x normal volume for absorption
            'institutional_volume_multiple': 3.0,  # 3x average for institutional
            'price_impact_sensitivity': 0.001,  # 0.1% price impact threshold
            'spread_analysis_levels': 10,  # Number of price levels to analyze
            'time_window_minutes': 15  # Analysis window
        }
        self.historical_imbalances = []
        
    async def detect_order_flow_imbalance(self, df: pd.DataFrame) -> OrderFlowImbalance:
        """Detect and analyze order flow imbalances"""
        try:
            current_time = datetime.now()
            current_price = df['close'].iloc[-1]
            
            # Analyze bid/ask spread and volume distribution
            spread_analysis = await self._analyze_spread_levels(df, current_price)
            
            # Detect absorption patterns
            absorption_analysis = await self._detect_absorption_patterns(df)
            
            # Analyze institutional flow signatures
            institutional_analysis = await self._analyze_institutional_signatures(df)
            
            # Calculate overall imbalance metrics
            overall_imbalance = self._calculate_overall_imbalance(spread_analysis)
            imbalance_type = self._classify_imbalance_type(overall_imbalance)
            
            # Calculate strength and reliability
            strength = self._calculate_imbalance_strength(spread_analysis, absorption_analysis)
            reliability = self._calculate_reliability_score(df, spread_analysis)
            
            # Calculate market impact potential
            market_impact = self._calculate_market_impact_score(
                overall_imbalance, absorption_analysis, institutional_analysis
            )
            
            imbalance_data = OrderFlowImbalance(
                timestamp=current_time,
                imbalance_type=imbalance_type,
                overall_ratio=overall_imbalance,
                strength=strength,
                price_levels=spread_analysis['levels'],
                absorption_analysis=absorption_analysis,
                institutional_flow=institutional_analysis,
                market_impact_score=market_impact,
                reliability_score=reliability
            )
            
            # Store for historical analysis
            self.historical_imbalances.append(imbalance_data)
            if len(self.historical_imbalances) > 100:
                self.historical_imbalances = self.historical_imbalances[-100:]
            
            return imbalance_data
            
        except Exception as e:
            return self._empty_imbalance_data()
    
    async def _analyze_spread_levels(self, df: pd.DataFrame, current_price: float) -> Dict[str, Any]:
        """Analyze bid/ask spread across multiple price levels"""
        try:
            levels = []
            
            # Calculate price range for analysis
            atr = self._calculate_atr(df, 14)
            price_step = atr / self.config['spread_analysis_levels']
            
            # Analyze levels above and below current price
            for i in range(-self.config['spread_analysis_levels']//2, 
                          self.config['spread_analysis_levels']//2 + 1):
                level_price = current_price + (i * price_step)
                
                # Estimate bid/ask volumes at this level
                bid_volume, ask_volume = self._estimate_level_volumes(df, level_price, price_step)
                
                # Calculate imbalance ratio
                total_volume = bid_volume + ask_volume
                if total_volume > 0:
                    imbalance_ratio = (bid_volume - ask_volume) / total_volume
                else:
                    imbalance_ratio = 0.0
                
                # Calculate absorption strength
                absorption_strength = self._calculate_level_absorption(df, level_price)
                
                # Detect institutional signature
                institutional_signature = self._detect_institutional_signature_at_level(
                    df, level_price, bid_volume, ask_volume
                )
                
                level_data = ImbalanceLevel(
                    price=level_price,
                    bid_volume=bid_volume,
                    ask_volume=ask_volume,
                    imbalance_ratio=imbalance_ratio,
                    absorption_strength=absorption_strength,
                    institutional_signature=institutional_signature
                )
                
                levels.append(level_data)
            
            # Calculate spread metrics
            total_bid_volume = sum(level.bid_volume for level in levels)
            total_ask_volume = sum(level.ask_volume for level in levels)
            weighted_spread = self._calculate_weighted_spread(levels, current_price)
            
            return {
                'levels': levels,
                'total_bid_volume': total_bid_volume,
                'total_ask_volume': total_ask_volume,
                'weighted_spread': weighted_spread,
                'significant_levels': [level for level in levels 
                                     if abs(level.imbalance_ratio) > self.config['imbalance_threshold']]
            }
            
        except Exception as e:
            return {'levels': [], 'total_bid_volume': 0, 'total_ask_volume': 0, 
                   'weighted_spread': 0, 'significant_levels': []}
    
    def _estimate_level_volumes(self, df: pd.DataFrame, target_price: float, 
                              tolerance: float) -> Tuple[float, float]:
        """Estimate bid/ask volumes at a specific price level"""
        try:
            # Find candles that interacted with this price level
            interacting_candles = df[
                (df['low'] <= target_price + tolerance) & 
                (df['high'] >= target_price - tolerance)
            ]
            
            if len(interacting_candles) == 0:
                return 0.0, 0.0
            
            total_volume = 0
            bid_volume = 0
            ask_volume = 0
            
            for _, candle in interacting_candles.iterrows():
                candle_volume = candle.get('volume', 1000)  # Default if no volume
                total_volume += candle_volume
                
                # Estimate bid/ask split based on price action within candle
                price_range = candle['high'] - candle['low']
                close_position = safe_divide(candle['close'] - candle['low'], price_range, 0.5)
                
                if target_price <= candle['close']:
                    # Price level at or below close - more likely ask volume
                    ask_volume += candle_volume * (1 - close_position)
                    bid_volume += candle_volume * close_position
                else:
                    # Price level above close - more likely bid volume
                    bid_volume += candle_volume * (1 - close_position)
                    ask_volume += candle_volume * close_position
            
            return bid_volume, ask_volume
            
        except Exception as e:
            return 0.0, 0.0
    
    def _calculate_level_absorption(self, df: pd.DataFrame, price_level: float) -> float:
        """Calculate absorption strength at a price level"""
        try:
            recent_data = df.tail(20)  # Last 20 candles
            
            # Find interactions with this price level
            level_interactions = 0
            absorption_events = 0
            
            for i in range(1, len(recent_data)):
                prev_candle = recent_data.iloc[i-1]
                curr_candle = recent_data.iloc[i]
                
                # Check if price approached this level
                if (prev_candle['low'] <= price_level <= prev_candle['high'] or
                    curr_candle['low'] <= price_level <= curr_candle['high']):
                    
                    level_interactions += 1
                    
                    # Check for absorption (high volume with limited price movement)
                    volume_ratio = curr_candle.get('volume', 1000) / max(
                        recent_data['volume'].mean() if 'volume' in df.columns else 1000, 1)
                    price_movement = abs(curr_candle['close'] - curr_candle['open']) / curr_candle['open']
                    
                    if volume_ratio > self.config['absorption_threshold'] and price_movement < 0.002:
                        absorption_events += 1
            
            if level_interactions == 0:
                return 0.0
                
            return absorption_events / level_interactions
            
        except Exception as e:
            return 0.0
    
    def _detect_institutional_signature_at_level(self, df: pd.DataFrame, price_level: float,
                                               bid_volume: float, ask_volume: float) -> float:
        """Detect institutional trading signatures at a price level"""
        try:
            signature_score = 0.0
            
            # Large volume concentration
            avg_volume = df['volume'].mean() if 'volume' in df.columns else 1000
            total_level_volume = bid_volume + ask_volume
            
            if total_level_volume > avg_volume * self.config['institutional_volume_multiple']:
                signature_score += 0.3
            
            # Volume imbalance patterns (institutions create imbalances)
            if total_level_volume > 0:
                imbalance_strength = abs(bid_volume - ask_volume) / total_level_volume
                if imbalance_strength > 0.7:
                    signature_score += 0.2
            
            # Persistence analysis (institutions maintain positions)
            persistence_score = self._analyze_level_persistence(df, price_level)
            signature_score += persistence_score * 0.3
            
            # Time-based analysis (institutions trade during specific times)
            time_signature = self._analyze_time_signature(df, price_level)
            signature_score += time_signature * 0.2
            
            return min(signature_score, 1.0)
            
        except Exception as e:
            return 0.0
    
    def _analyze_level_persistence(self, df: pd.DataFrame, price_level: float) -> float:
        """Analyze how persistently a price level shows activity"""
        try:
            recent_data = df.tail(50)  # Last 50 candles
            interactions = 0
            consecutive_interactions = 0
            max_consecutive = 0
            
            for _, candle in recent_data.iterrows():
                if candle['low'] <= price_level <= candle['high']:
                    interactions += 1
                    consecutive_interactions += 1
                    max_consecutive = max(max_consecutive, consecutive_interactions)
                else:
                    consecutive_interactions = 0
            
            persistence_ratio = interactions / len(recent_data)
            consistency_bonus = min(max_consecutive / 10, 0.5)  # Bonus for consistency
            
            return min(persistence_ratio + consistency_bonus, 1.0)
            
        except Exception as e:
            return 0.0
    
    def _analyze_time_signature(self, df: pd.DataFrame, price_level: float) -> float:
        """Analyze time-based patterns in level activity"""
        try:
            # This is a simplified version - in production, you'd analyze actual timestamps
            # For now, we'll analyze based on candle position patterns
            
            recent_data = df.tail(30)
            level_activity = []
            
            for i, (_, candle) in enumerate(recent_data.iterrows()):
                if candle['low'] <= price_level <= candle['high']:
                    level_activity.append(i)
            
            if len(level_activity) < 2:
                return 0.0
            
            # Calculate pattern regularity
            intervals = np.diff(level_activity)
            if len(intervals) == 0:
                return 0.0
                
            interval_consistency = 1.0 - safe_divide(safe_std(intervals), safe_mean(intervals, 1), 0)
            
            return max(0.0, min(interval_consistency, 1.0))
            
        except Exception as e:
            return 0.0
    
    async def _detect_absorption_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect order absorption patterns"""
        try:
            recent_data = df.tail(20)
            absorption_events = []
            
            for i in range(1, len(recent_data)):
                prev_candle = recent_data.iloc[i-1]
                curr_candle = recent_data.iloc[i]
                
                # Calculate volume and price movement metrics
                avg_volume = safe_mean(recent_data['volume']) if 'volume' in df.columns else 1000
                volume_ratio = safe_divide(curr_candle.get('volume', 1000), avg_volume, 1.0)
                price_movement = safe_divide(abs(curr_candle['close'] - curr_candle['open']), curr_candle['open'], 0.0)
                price_direction = 1 if curr_candle['close'] > curr_candle['open'] else -1
                
                # Detect absorption (high volume, low price movement)
                if volume_ratio > self.config['absorption_threshold'] and price_movement < 0.003:
                    absorption_type = self._classify_absorption_type(curr_candle, prev_candle)
                    
                    absorption_events.append({
                        'index': i,
                        'type': absorption_type,
                        'volume_ratio': volume_ratio,
                        'price_movement': price_movement,
                        'direction': price_direction,
                        'strength': volume_ratio * (1 - price_movement * 100)
                    })
            
            # Analyze overall absorption pattern
            if absorption_events:
                avg_strength = safe_mean([event['strength'] for event in absorption_events])
                buy_absorption = len([e for e in absorption_events if e['direction'] > 0])
                sell_absorption = len([e for e in absorption_events if e['direction'] < 0])
                
                dominant_type = AbsorptionType.BUY_ABSORPTION if buy_absorption > sell_absorption else AbsorptionType.SELL_ABSORPTION
                if abs(buy_absorption - sell_absorption) <= 1:
                    dominant_type = AbsorptionType.MUTUAL_ABSORPTION
            else:
                avg_strength = 0.0
                dominant_type = AbsorptionType.NO_ABSORPTION
                buy_absorption = 0
                sell_absorption = 0
            
            return {
                'absorption_events': absorption_events,
                'dominant_type': dominant_type,
                'average_strength': avg_strength,
                'buy_absorption_count': buy_absorption,
                'sell_absorption_count': sell_absorption,
                'total_absorption_score': len(absorption_events) / max(len(recent_data), 1)
            }
            
        except Exception as e:
            return {
                'absorption_events': [],
                'dominant_type': AbsorptionType.NO_ABSORPTION,
                'average_strength': 0.0,
                'buy_absorption_count': 0,
                'sell_absorption_count': 0,
                'total_absorption_score': 0.0
            }
    
    def _classify_absorption_type(self, current_candle: pd.Series, previous_candle: pd.Series) -> str:
        """Classify the type of absorption based on price action"""
        try:
            curr_close = current_candle['close']
            curr_open = current_candle['open']
            prev_close = previous_candle['close']
            
            # Determine if buying or selling was absorbed
            if curr_close > prev_close and curr_close < curr_open:
                return "sell_absorption"  # Selling pressure was absorbed
            elif curr_close < prev_close and curr_close > curr_open:
                return "buy_absorption"   # Buying pressure was absorbed
            else:
                return "neutral_absorption"
                
        except Exception as e:
            return "neutral_absorption"
    
    async def _analyze_institutional_signatures(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze institutional order flow signatures"""
        try:
            recent_data = df.tail(30)
            
            # Large block detection
            avg_volume = recent_data['volume'].mean() if 'volume' in df.columns else 1000
            large_blocks = recent_data[recent_data.get('volume', 1000) > avg_volume * 2.5]
            
            # Iceberg order detection (consistent large volumes at similar prices)
            iceberg_score = self._detect_iceberg_orders(recent_data)
            
            # Stealth trading detection (volume without price impact)
            stealth_score = self._detect_stealth_trading(recent_data)
            
            # Cross-trading detection (balanced buy/sell activity)
            cross_trading_score = self._detect_cross_trading(recent_data)
            
            # Calculate institutional probability
            institutional_indicators = [
                len(large_blocks) / len(recent_data),  # Large block frequency
                iceberg_score,
                stealth_score,
                cross_trading_score
            ]
            
            institutional_probability = safe_mean(institutional_indicators)
            
            return {
                'institutional_probability': institutional_probability,
                'large_block_ratio': len(large_blocks) / len(recent_data),
                'iceberg_score': iceberg_score,
                'stealth_score': stealth_score,
                'cross_trading_score': cross_trading_score,
                'dominant_pattern': self._identify_dominant_institutional_pattern(institutional_indicators)
            }
            
        except Exception as e:
            return {
                'institutional_probability': 0.0,
                'large_block_ratio': 0.0,
                'iceberg_score': 0.0,
                'stealth_score': 0.0,
                'cross_trading_score': 0.0,
                'dominant_pattern': 'retail'
            }
    
    def _detect_iceberg_orders(self, df: pd.DataFrame) -> float:
        """Detect iceberg order patterns"""
        try:
            # Look for repeated large volumes at similar price levels
            iceberg_indicators = 0
            price_tolerance = df['close'].iloc[-1] * 0.001  # 0.1% tolerance
            
            for i in range(len(df) - 5):
                window = df.iloc[i:i+5]
                
                # Check for consistent large volumes
                avg_volume = window['volume'].mean() if 'volume' in df.columns else 1000
                large_volume_count = len(window[window.get('volume', 1000) > avg_volume * 1.5])
                
                # Check price clustering
                price_range = window['high'].max() - window['low'].min()
                
                if large_volume_count >= 3 and price_range < price_tolerance * 3:
                    iceberg_indicators += 1
            
            return min(iceberg_indicators / max(len(df) - 5, 1), 1.0)
            
        except Exception as e:
            return 0.0
    
    def _detect_stealth_trading(self, df: pd.DataFrame) -> float:
        """Detect stealth trading patterns"""
        try:
            stealth_events = 0
            
            for _, candle in df.iterrows():
                volume = candle.get('volume', 1000)
                price_impact = abs(candle['close'] - candle['open']) / candle['open']
                
                # High volume with low price impact = stealth trading
                avg_volume = df['volume'].mean() if 'volume' in df.columns else 1000
                if volume > avg_volume * 1.5 and price_impact < 0.002:
                    stealth_events += 1
            
            return stealth_events / max(len(df), 1)
            
        except Exception as e:
            return 0.0
    
    def _detect_cross_trading(self, df: pd.DataFrame) -> float:
        """Detect cross-trading patterns"""
        try:
            # Look for balanced buying and selling activity
            up_candles = len(df[df['close'] > df['open']])
            down_candles = len(df[df['close'] <= df['open']])
            
            # Cross-trading shows balanced activity
            balance_ratio = min(up_candles, down_candles) / max(max(up_candles, down_candles), 1)
            
            # Also check for consistent volumes
            volume_consistency = 1.0 - (df['volume'].std() / max(df['volume'].mean(), 1)) if 'volume' in df.columns else 0.5
            
            return (balance_ratio + volume_consistency) / 2
            
        except Exception as e:
            return 0.0
    
    def _identify_dominant_institutional_pattern(self, indicators: List[float]) -> str:
        """Identify the dominant institutional trading pattern"""
        try:
            pattern_names = ['large_blocks', 'iceberg', 'stealth', 'cross_trading']
            max_index = np.argmax(indicators)
            max_value = indicators[max_index]
            
            if max_value > 0.6:
                return pattern_names[max_index]
            elif max_value > 0.3:
                return f"moderate_{pattern_names[max_index]}"
            else:
                return "retail"
                
        except Exception as e:
            return "retail"
    
    def _calculate_overall_imbalance(self, spread_analysis: Dict[str, Any]) -> float:
        """Calculate overall order flow imbalance"""
        try:
            total_bid = spread_analysis['total_bid_volume']
            total_ask = spread_analysis['total_ask_volume']
            
            if total_bid + total_ask == 0:
                return 0.0
                
            return (total_bid - total_ask) / (total_bid + total_ask)
            
        except Exception as e:
            return 0.0
    
    def _classify_imbalance_type(self, overall_imbalance: float) -> ImbalanceType:
        """Classify the type of order flow imbalance"""
        if overall_imbalance > self.config['extreme_imbalance_threshold']:
            return ImbalanceType.EXTREME_BID
        elif overall_imbalance > self.config['imbalance_threshold']:
            return ImbalanceType.BID_HEAVY
        elif overall_imbalance < -self.config['extreme_imbalance_threshold']:
            return ImbalanceType.EXTREME_ASK
        elif overall_imbalance < -self.config['imbalance_threshold']:
            return ImbalanceType.ASK_HEAVY
        else:
            return ImbalanceType.BALANCED
    
    def _calculate_imbalance_strength(self, spread_analysis: Dict[str, Any], 
                                   absorption_analysis: Dict[str, Any]) -> float:
        """Calculate the strength of the imbalance"""
        try:
            # Base strength from imbalance magnitude
            imbalance_strength = len(spread_analysis['significant_levels']) / max(len(spread_analysis['levels']), 1)
            
            # Boost from absorption activity
            absorption_boost = absorption_analysis['total_absorption_score'] * 0.3
            
            # Boost from concentration
            if spread_analysis['levels']:
                max_level_volume = max(level.bid_volume + level.ask_volume for level in spread_analysis['levels'])
                total_volume = spread_analysis['total_bid_volume'] + spread_analysis['total_ask_volume']
                concentration_boost = (max_level_volume / max(total_volume, 1)) * 0.2
            else:
                concentration_boost = 0.0
            
            total_strength = imbalance_strength + absorption_boost + concentration_boost
            return min(total_strength, 1.0)
            
        except Exception as e:
            return 0.0
    
    def _calculate_reliability_score(self, df: pd.DataFrame, spread_analysis: Dict[str, Any]) -> float:
        """Calculate reliability of the imbalance analysis"""
        try:
            # Data quality factors
            data_completeness = 1.0 if 'volume' in df.columns else 0.7
            data_recency = min(len(df) / 50, 1.0)  # More data = more reliable
            
            # Analysis quality factors
            level_coverage = len(spread_analysis['levels']) / self.config['spread_analysis_levels']
            significant_level_ratio = len(spread_analysis['significant_levels']) / max(len(spread_analysis['levels']), 1)
            
            # Consistency factors
            spread_consistency = 1.0 - (spread_analysis.get('weighted_spread', 0) / 0.01)  # Lower spread = more reliable
            spread_consistency = max(0.0, min(spread_consistency, 1.0))
            
            reliability = (
                data_completeness * 0.3 +
                data_recency * 0.2 +
                level_coverage * 0.2 +
                significant_level_ratio * 0.15 +
                spread_consistency * 0.15
            )
            
            return min(reliability, 1.0)
            
        except Exception as e:
            return 0.3  # Default low but non-zero reliability
    
    def _calculate_market_impact_score(self, overall_imbalance: float, 
                                     absorption_analysis: Dict[str, Any],
                                     institutional_analysis: Dict[str, Any]) -> float:
        """Calculate potential market impact of the imbalance"""
        try:
            # Base impact from imbalance magnitude
            base_impact = abs(overall_imbalance)
            
            # Amplification from absorption patterns
            absorption_amplifier = 1 + (absorption_analysis['average_strength'] * 0.5)
            
            # Amplification from institutional activity
            institutional_amplifier = 1 + (institutional_analysis['institutional_probability'] * 0.7)
            
            # Calculate combined impact
            market_impact = base_impact * absorption_amplifier * institutional_amplifier
            
            return min(market_impact, 1.0)
            
        except Exception as e:
            return 0.0
    
    def _calculate_weighted_spread(self, levels: List[ImbalanceLevel], current_price: float) -> float:
        """Calculate volume-weighted spread"""
        try:
            if not levels:
                return 0.0
            
            total_weighted_spread = 0.0
            total_weight = 0.0
            
            for level in levels:
                volume_weight = level.bid_volume + level.ask_volume
                price_distance = abs(level.price - current_price) / current_price
                
                if volume_weight > 0:
                    total_weighted_spread += price_distance * volume_weight
                    total_weight += volume_weight
            
            return total_weighted_spread / max(total_weight, 1)
            
        except Exception as e:
            return 0.0
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(period).mean()
            return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0.01
        except:
            return 0.01
    
    def _empty_imbalance_data(self) -> OrderFlowImbalance:
        """Return empty imbalance data"""
        return OrderFlowImbalance(
            timestamp=datetime.now(),
            imbalance_type=ImbalanceType.BALANCED,
            overall_ratio=0.0,
            strength=0.0,
            price_levels=[],
            absorption_analysis={},
            institutional_flow={},
            market_impact_score=0.0,
            reliability_score=0.0
        )
    
    def get_historical_imbalance_patterns(self) -> Dict[str, Any]:
        """Analyze historical imbalance patterns"""
        try:
            if not self.historical_imbalances:
                return {'pattern_analysis': 'insufficient_data'}
            
            # Analyze pattern frequency
            imbalance_types = [imb.imbalance_type.value for imb in self.historical_imbalances]
            type_counts = {itype: imbalance_types.count(itype) for itype in set(imbalance_types)}
            
            # Analyze strength trends
            strengths = [imb.strength for imb in self.historical_imbalances]
            avg_strength = safe_mean(strengths)
            strength_trend = safe_polyfit(np.array(range(len(strengths))), np.array(strengths), 1)[0]
            
            # Analyze reliability trends
            reliabilities = [imb.reliability_score for imb in self.historical_imbalances]
            avg_reliability = safe_mean(reliabilities)
            
            return {
                'pattern_analysis': 'complete',
                'imbalance_type_distribution': type_counts,
                'average_strength': avg_strength,
                'strength_trend': strength_trend,
                'average_reliability': avg_reliability,
                'total_samples': len(self.historical_imbalances),
                'dominant_pattern': max(type_counts, key=type_counts.get) if type_counts else 'balanced'
            }
            
        except Exception as e:
            return {'pattern_analysis': 'error', 'error': str(e)}

# Global instance
_imbalance_detector = None

async def get_imbalance_detector() -> OrderFlowImbalanceDetector:
    """Get or create the global imbalance detector instance"""
    global _imbalance_detector
    if _imbalance_detector is None:
        _imbalance_detector = OrderFlowImbalanceDetector()
    return _imbalance_detector

async def detect_order_flow_imbalance(df: pd.DataFrame) -> OrderFlowImbalance:
    """Detect order flow imbalances in market data"""
    detector = await get_imbalance_detector()
    return await detector.detect_order_flow_imbalance(df)

async def get_imbalance_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Get comprehensive order flow imbalance summary"""
    try:
        imbalance_data = await detect_order_flow_imbalance(df)
        detector = await get_imbalance_detector()
        historical_patterns = detector.get_historical_imbalance_patterns()
        
        return {
            'current_imbalance': {
                'type': imbalance_data.imbalance_type.value,
                'ratio': imbalance_data.overall_ratio,
                'strength': imbalance_data.strength,
                'market_impact': imbalance_data.market_impact_score,
                'reliability': imbalance_data.reliability_score
            },
            'absorption_analysis': imbalance_data.absorption_analysis,
            'institutional_flow': imbalance_data.institutional_flow,
            'historical_patterns': historical_patterns,
            'trading_implications': {
                'direction_bias': 'bullish' if imbalance_data.overall_ratio > 0.3 else 'bearish' if imbalance_data.overall_ratio < -0.3 else 'neutral',
                'strength_assessment': 'strong' if imbalance_data.strength > 0.7 else 'moderate' if imbalance_data.strength > 0.4 else 'weak',
                'institutional_presence': 'high' if imbalance_data.institutional_flow.get('institutional_probability', 0) > 0.6 else 'moderate' if imbalance_data.institutional_flow.get('institutional_probability', 0) > 0.3 else 'low'
            }
        }
        
    except Exception as e:
        return {
            'current_imbalance': {'type': 'balanced', 'ratio': 0.0, 'strength': 0.0, 'market_impact': 0.0, 'reliability': 0.0},
            'absorption_analysis': {},
            'institutional_flow': {},
            'historical_patterns': {'pattern_analysis': 'error'},
            'trading_implications': {'direction_bias': 'neutral', 'strength_assessment': 'weak', 'institutional_presence': 'low'},
            'error': str(e)
        }