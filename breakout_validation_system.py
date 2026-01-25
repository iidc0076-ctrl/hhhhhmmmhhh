"""
Breakout Validation System for Trading Bot
Validates breakouts using volume, retest patterns, and time-based filters
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from safe_math_utils import safe_mean, safe_std, safe_divide, safe_correlation, safe_polyfit

class BreakoutType(Enum):
    RESISTANCE_BREAK = "resistance_break"
    SUPPORT_BREAK = "support_break"
    CHANNEL_BREAK = "channel_break"
    TRIANGLE_BREAK = "triangle_break"
    RANGE_BREAK = "range_break"

class BreakoutValidation(Enum):
    CONFIRMED = "confirmed"
    PENDING = "pending"
    FALSE_BREAKOUT = "false_breakout"
    RETEST_REQUIRED = "retest_required"
    INSUFFICIENT_DATA = "insufficient_data"

class SessionFilter(Enum):
    LONDON_OPEN = "london_open"
    NY_OPEN = "ny_open"
    LONDON_NY_OVERLAP = "london_ny_overlap"
    QUIET_HOURS = "quiet_hours"
    VALID_HOURS = "valid_hours"

@dataclass
class BreakoutLevel:
    price: float
    level_type: str  # 'resistance', 'support', 'channel_top', 'channel_bottom'
    strength: float  # Number of touches/tests
    age_hours: float  # How long the level has been relevant
    last_test_time: datetime
    volume_at_level: float

@dataclass
class BreakoutEvent:
    breakout_time: datetime
    breakout_price: float
    level_broken: BreakoutLevel
    breakout_type: BreakoutType
    volume_ratio: float  # Volume vs average
    speed_factor: float  # How fast the breakout occurred
    distance_factor: float  # How far price moved from level
    session_quality: SessionFilter

@dataclass
class RetestAnalysis:
    retest_occurred: bool
    retest_time: Optional[datetime]
    retest_price: Optional[float]
    retest_hold: bool  # Did the level hold on retest
    time_to_retest_hours: Optional[float]
    retest_volume_ratio: Optional[float]

@dataclass
class BreakoutValidationResult:
    breakout_event: BreakoutEvent
    validation_status: BreakoutValidation
    retest_analysis: RetestAnalysis
    strength_score: float
    reliability_score: float
    false_breakout_probability: float
    continuation_probability: float
    recommended_action: str
    target_levels: List[float]
    stop_loss_level: float

class BreakoutValidator:
    """Advanced breakout validation with comprehensive filtering"""
    
    def __init__(self):
        self.config = {
            'min_volume_ratio': 1.5,  # Minimum volume for valid breakout
            'strong_volume_ratio': 2.5,  # Strong volume confirmation
            'min_distance_factor': 0.002,  # 0.2% minimum distance from level
            'retest_window_hours': 24,  # Hours to wait for retest
            'false_breakout_threshold': 0.001,  # 0.1% false breakout tolerance
            'session_filter_enabled': True,
            'min_level_strength': 2,  # Minimum number of level tests
            'speed_threshold': 0.5  # Minimum breakout speed
        }
        self.session_times = {
            SessionFilter.LONDON_OPEN: (8, 10),     # 8-10 GMT
            SessionFilter.NY_OPEN: (13, 15),        # 13-15 GMT  
            SessionFilter.LONDON_NY_OVERLAP: (13, 16), # 13-16 GMT
            SessionFilter.QUIET_HOURS: (21, 8),     # 21-08 GMT
            SessionFilter.VALID_HOURS: (8, 21)      # 8-21 GMT
        }
        
    async def validate_breakout(self, df: pd.DataFrame, 
                              suspected_level: float = None) -> List[BreakoutValidationResult]:
        """Validate breakouts in market data"""
        try:
            # Identify key levels if not provided
            key_levels = await self._identify_key_levels(df) if suspected_level is None else [suspected_level]
            
            breakout_results = []
            
            for level in key_levels:
                # Detect breakout events at this level
                breakout_events = await self._detect_breakout_events(df, level)
                
                for event in breakout_events:
                    # Validate each breakout
                    validation_result = await self._validate_single_breakout(df, event)
                    if validation_result:
                        breakout_results.append(validation_result)
            
            return breakout_results
            
        except Exception as e:
            return []
    
    async def _identify_key_levels(self, df: pd.DataFrame) -> List[float]:
        """Identify key support and resistance levels"""
        try:
            levels = []
            
            # Find swing highs and lows
            window = 5
            swing_highs = []
            swing_lows = []
            
            for i in range(window, len(df) - window):
                # Check for swing high
                if all(df['high'].iloc[i] >= df['high'].iloc[i-j] for j in range(1, window+1)) and \
                   all(df['high'].iloc[i] >= df['high'].iloc[i+j] for j in range(1, window+1)):
                    swing_highs.append(df['high'].iloc[i])
                
                # Check for swing low
                if all(df['low'].iloc[i] <= df['low'].iloc[i-j] for j in range(1, window+1)) and \
                   all(df['low'].iloc[i] <= df['low'].iloc[i+j] for j in range(1, window+1)):
                    swing_lows.append(df['low'].iloc[i])
            
            # Cluster similar levels
            all_levels = swing_highs + swing_lows
            clustered_levels = self._cluster_price_levels(all_levels, df['close'].iloc[-1] * 0.002)
            
            return clustered_levels[:10]  # Return top 10 levels
            
        except Exception as e:
            return []
    
    def _cluster_price_levels(self, levels: List[float], tolerance: float) -> List[float]:
        """Cluster nearby price levels together"""
        try:
            if not levels:
                return []
            
            levels_sorted = sorted(levels)
            clustered = []
            current_cluster = [levels_sorted[0]]
            
            for level in levels_sorted[1:]:
                if level - current_cluster[-1] <= tolerance:
                    current_cluster.append(level)
                else:
                    # Finish current cluster, start new one
                    clustered.append(safe_mean(current_cluster))
                    current_cluster = [level]
            
            # Add final cluster
            clustered.append(safe_mean(current_cluster))
            
            return clustered
            
        except Exception as e:
            return levels
    
    async def _detect_breakout_events(self, df: pd.DataFrame, level: float) -> List[BreakoutEvent]:
        """Detect breakout events at a specific level"""
        try:
            events = []
            tolerance = level * 0.001  # 0.1% tolerance
            
            # Create level object
            level_obj = self._create_level_object(df, level)
            
            # Scan for breakouts
            for i in range(1, len(df)):
                prev_candle = df.iloc[i-1]
                curr_candle = df.iloc[i]
                
                # Check for resistance breakout
                if (prev_candle['high'] <= level + tolerance and 
                    curr_candle['high'] > level + tolerance):
                    
                    breakout_event = self._create_breakout_event(
                        df, i, level_obj, BreakoutType.RESISTANCE_BREAK
                    )
                    if breakout_event:
                        events.append(breakout_event)
                
                # Check for support breakout
                elif (prev_candle['low'] >= level - tolerance and 
                      curr_candle['low'] < level - tolerance):
                    
                    breakout_event = self._create_breakout_event(
                        df, i, level_obj, BreakoutType.SUPPORT_BREAK
                    )
                    if breakout_event:
                        events.append(breakout_event)
            
            return events
            
        except Exception as e:
            return []
    
    def _create_level_object(self, df: pd.DataFrame, level: float) -> BreakoutLevel:
        """Create a BreakoutLevel object from price data"""
        try:
            tolerance = level * 0.001
            
            # Count touches/tests of the level
            touches = 0
            last_test_time = datetime.now() - timedelta(days=30)  # Default old time
            total_volume = 0
            
            for i, (_, candle) in enumerate(df.iterrows()):
                if (candle['low'] <= level + tolerance and 
                    candle['high'] >= level - tolerance):
                    touches += 1
                    last_test_time = datetime.now() - timedelta(minutes=(len(df) - i) * 5)  # Rough estimate
                    total_volume += candle.get('volume', 1000)
            
            avg_volume = total_volume / max(touches, 1)
            age_hours = (datetime.now() - last_test_time).total_seconds() / 3600
            
            # Determine level type based on position relative to current price
            current_price = df['close'].iloc[-1]
            level_type = 'resistance' if level > current_price else 'support'
            
            return BreakoutLevel(
                price=level,
                level_type=level_type,
                strength=touches,
                age_hours=age_hours,
                last_test_time=last_test_time,
                volume_at_level=avg_volume
            )
            
        except Exception as e:
            return BreakoutLevel(level, 'unknown', 1, 24.0, datetime.now(), 1000)
    
    def _create_breakout_event(self, df: pd.DataFrame, breakout_index: int, 
                             level: BreakoutLevel, breakout_type: BreakoutType) -> Optional[BreakoutEvent]:
        """Create a breakout event from the data"""
        try:
            candle = df.iloc[breakout_index]
            
            # Calculate breakout metrics
            volume_ratio = self._calculate_volume_ratio(df, breakout_index)
            speed_factor = self._calculate_speed_factor(df, breakout_index, level.price)
            distance_factor = self._calculate_distance_factor(candle, level.price, breakout_type)
            
            # Determine session quality
            breakout_time = datetime.now() - timedelta(minutes=(len(df) - breakout_index) * 5)
            session_quality = self._assess_session_quality(breakout_time)
            
            # Basic validation - skip obviously weak breakouts
            if (volume_ratio < self.config['min_volume_ratio'] or 
                distance_factor < self.config['min_distance_factor'] or
                speed_factor < self.config['speed_threshold']):
                return None
            
            return BreakoutEvent(
                breakout_time=breakout_time,
                breakout_price=candle['close'],
                level_broken=level,
                breakout_type=breakout_type,
                volume_ratio=volume_ratio,
                speed_factor=speed_factor,
                distance_factor=distance_factor,
                session_quality=session_quality
            )
            
        except Exception as e:
            return None
    
    def _calculate_volume_ratio(self, df: pd.DataFrame, index: int) -> float:
        """Calculate volume ratio for breakout candle"""
        try:
            if 'volume' not in df.columns:
                return 1.5  # Default moderate volume
            
            current_volume = df['volume'].iloc[index]
            avg_volume_series = df['volume'].rolling(20, min_periods=1).mean()
            avg_volume = avg_volume_series.iloc[index] if index < len(avg_volume_series) else 0
            
            return current_volume / max(avg_volume, 1)
            
        except Exception as e:
            return 1.0
    
    def _calculate_speed_factor(self, df: pd.DataFrame, index: int, level: float) -> float:
        """Calculate how quickly the breakout occurred"""
        try:
            if index < 3:
                return 0.5
            
            # Look at price movement in the 3 candles leading to breakout
            pre_breakout_range = df['close'].iloc[index-3:index].max() - df['close'].iloc[index-3:index].min()
            breakout_movement = abs(df['close'].iloc[index] - level)
            
            if pre_breakout_range == 0:
                return 1.0
            
            speed_factor = breakout_movement / pre_breakout_range
            return min(speed_factor, 2.0)
            
        except Exception as e:
            return 0.5
    
    def _calculate_distance_factor(self, candle: pd.Series, level: float, 
                                 breakout_type: BreakoutType) -> float:
        """Calculate how far price moved from the level"""
        try:
            if breakout_type == BreakoutType.RESISTANCE_BREAK:
                distance = (candle['close'] - level) / level
            else:  # Support break
                distance = (level - candle['close']) / level
            
            return max(distance, 0.0)
            
        except Exception as e:
            return 0.0
    
    def _assess_session_quality(self, breakout_time: datetime) -> SessionFilter:
        """Assess the quality of the session when breakout occurred"""
        try:
            hour = breakout_time.hour
            
            # Check against session times
            for session, (start, end) in self.session_times.items():
                if session == SessionFilter.QUIET_HOURS:
                    if hour >= start or hour < end:  # Overnight session
                        return session
                else:
                    if start <= hour < end:
                        return session
            
            return SessionFilter.VALID_HOURS  # Default
            
        except Exception as e:
            return SessionFilter.VALID_HOURS
    
    async def _validate_single_breakout(self, df: pd.DataFrame, 
                                      event: BreakoutEvent) -> Optional[BreakoutValidationResult]:
        """Validate a single breakout event"""
        try:
            # Find the breakout index in the dataframe
            breakout_index = self._find_breakout_index(df, event)
            if breakout_index is None:
                return None
            
            # Analyze retest behavior
            retest_analysis = await self._analyze_retest_behavior(df, event, breakout_index)
            
            # Calculate validation scores
            strength_score = self._calculate_strength_score(event, retest_analysis)
            reliability_score = self._calculate_reliability_score(event, retest_analysis)
            false_breakout_prob = self._calculate_false_breakout_probability(event, retest_analysis)
            continuation_prob = 1.0 - false_breakout_prob
            
            # Determine validation status
            validation_status = self._determine_validation_status(
                event, retest_analysis, strength_score, false_breakout_prob
            )
            
            # Generate recommendations
            recommended_action = self._generate_recommendation(validation_status, strength_score)
            target_levels = self._calculate_target_levels(df, event, breakout_index)
            stop_loss = self._calculate_stop_loss_level(event, retest_analysis)
            
            return BreakoutValidationResult(
                breakout_event=event,
                validation_status=validation_status,
                retest_analysis=retest_analysis,
                strength_score=strength_score,
                reliability_score=reliability_score,
                false_breakout_probability=false_breakout_prob,
                continuation_probability=continuation_prob,
                recommended_action=recommended_action,
                target_levels=target_levels,
                stop_loss_level=stop_loss
            )
            
        except Exception as e:
            return None
    
    def _find_breakout_index(self, df: pd.DataFrame, event: BreakoutEvent) -> Optional[int]:
        """Find the index of the breakout candle in the dataframe"""
        try:
            # Simple approximation - find candle closest to breakout price and time
            tolerance = event.level_broken.price * 0.002
            
            for i, (_, candle) in enumerate(df.iterrows()):
                if abs(candle['close'] - event.breakout_price) < tolerance:
                    return i
            
            return None
            
        except Exception as e:
            return None
    
    async def _analyze_retest_behavior(self, df: pd.DataFrame, event: BreakoutEvent, 
                                     breakout_index: int) -> RetestAnalysis:
        """Analyze retest behavior after breakout"""
        try:
            level_price = event.level_broken.price
            tolerance = level_price * 0.005  # 0.5% tolerance for retest
            
            # Look for retest in subsequent candles
            retest_window = min(48, len(df) - breakout_index - 1)  # Max 48 candles after breakout
            
            retest_occurred = False
            retest_time = None
            retest_price = None
            retest_hold = False
            time_to_retest = None
            retest_volume_ratio = None
            
            for i in range(1, retest_window + 1):
                if breakout_index + i >= len(df):
                    break
                    
                candle = df.iloc[breakout_index + i]
                
                # Check if price retested the level
                if event.breakout_type == BreakoutType.RESISTANCE_BREAK:
                    # Look for pullback to resistance (now support)
                    if candle['low'] <= level_price + tolerance and candle['low'] >= level_price - tolerance:
                        retest_occurred = True
                        retest_price = candle['low']
                        retest_hold = candle['close'] > level_price - tolerance
                        break
                else:  # Support break
                    # Look for bounce to support (now resistance)
                    if candle['high'] >= level_price - tolerance and candle['high'] <= level_price + tolerance:
                        retest_occurred = True
                        retest_price = candle['high']
                        retest_hold = candle['close'] < level_price + tolerance
                        break
            
            if retest_occurred:
                time_to_retest = i * 5  # Assuming 5-minute candles
                retest_time = event.breakout_time + timedelta(minutes=time_to_retest)
                
                # Calculate retest volume
                if 'volume' in df.columns:
                    retest_volume = df['volume'].iloc[breakout_index + i]
                    avg_volume_series = df['volume'].rolling(20, min_periods=1).mean()
                    avg_volume = avg_volume_series.iloc[breakout_index + i] if (breakout_index + i) < len(avg_volume_series) else 0
                    retest_volume_ratio = retest_volume / max(avg_volume, 1)
                else:
                    retest_volume_ratio = 1.0
            
            return RetestAnalysis(
                retest_occurred=retest_occurred,
                retest_time=retest_time,
                retest_price=retest_price,
                retest_hold=retest_hold,
                time_to_retest_hours=time_to_retest / 60 if time_to_retest else None,
                retest_volume_ratio=retest_volume_ratio
            )
            
        except Exception as e:
            return RetestAnalysis(False, None, None, False, None, None)
    
    def _calculate_strength_score(self, event: BreakoutEvent, retest: RetestAnalysis) -> float:
        """Calculate overall strength score for the breakout"""
        try:
            score = 0.0
            
            # Volume component (30%)
            volume_score = min(event.volume_ratio / 3.0, 1.0)
            score += volume_score * 0.3
            
            # Speed component (20%)
            speed_score = min(event.speed_factor, 1.0)
            score += speed_score * 0.2
            
            # Distance component (20%)
            distance_score = min(event.distance_factor * 50, 1.0)  # Scale up distance
            score += distance_score * 0.2
            
            # Level strength component (15%)
            level_score = min(event.level_broken.strength / 5.0, 1.0)
            score += level_score * 0.15
            
            # Retest component (15%)
            retest_score = 0.0
            if retest.retest_occurred:
                if retest.retest_hold:
                    retest_score = 1.0  # Perfect retest and hold
                else:
                    retest_score = 0.3  # Retest but failed
            else:
                retest_score = 0.6  # No retest yet (neutral)
            score += retest_score * 0.15
            
            return min(score, 1.0)
            
        except Exception as e:
            return 0.5
    
    def _calculate_reliability_score(self, event: BreakoutEvent, retest: RetestAnalysis) -> float:
        """Calculate reliability score based on multiple factors"""
        try:
            score = 0.5  # Base score
            
            # Session quality boost
            if event.session_quality in [SessionFilter.LONDON_OPEN, SessionFilter.NY_OPEN, SessionFilter.LONDON_NY_OVERLAP]:
                score += 0.2
            elif event.session_quality == SessionFilter.QUIET_HOURS:
                score -= 0.2
            
            # Volume reliability
            if event.volume_ratio > self.config['strong_volume_ratio']:
                score += 0.15
            elif event.volume_ratio < self.config['min_volume_ratio']:
                score -= 0.15
            
            # Level strength reliability
            if event.level_broken.strength >= 4:
                score += 0.1
            elif event.level_broken.strength < 2:
                score -= 0.1
            
            # Retest reliability
            if retest.retest_occurred and retest.retest_hold:
                score += 0.15
            elif retest.retest_occurred and not retest.retest_hold:
                score -= 0.3
            
            return max(0.1, min(score, 1.0))
            
        except Exception as e:
            return 0.5
    
    def _calculate_false_breakout_probability(self, event: BreakoutEvent, retest: RetestAnalysis) -> float:
        """Calculate probability that this is a false breakout"""
        try:
            false_prob = 0.3  # Base probability
            
            # Volume factor
            if event.volume_ratio < self.config['min_volume_ratio']:
                false_prob += 0.2
            elif event.volume_ratio > self.config['strong_volume_ratio']:
                false_prob -= 0.15
            
            # Distance factor
            if event.distance_factor < self.config['min_distance_factor']:
                false_prob += 0.2
            elif event.distance_factor > 0.01:  # 1% move
                false_prob -= 0.1
            
            # Session timing
            if event.session_quality == SessionFilter.QUIET_HOURS:
                false_prob += 0.15
            elif event.session_quality in [SessionFilter.LONDON_NY_OVERLAP]:
                false_prob -= 0.1
            
            # Retest factor
            if retest.retest_occurred:
                if retest.retest_hold:
                    false_prob -= 0.2  # Successful retest
                else:
                    false_prob += 0.3  # Failed retest
            
            # Level strength
            if event.level_broken.strength < 2:
                false_prob += 0.1
            elif event.level_broken.strength > 4:
                false_prob -= 0.1
            
            return max(0.05, min(false_prob, 0.9))
            
        except Exception as e:
            return 0.5
    
    def _determine_validation_status(self, event: BreakoutEvent, retest: RetestAnalysis,
                                   strength_score: float, false_prob: float) -> BreakoutValidation:
        """Determine the validation status of the breakout"""
        try:
            # Clear false breakout
            if false_prob > 0.7:
                return BreakoutValidation.FALSE_BREAKOUT
            
            # Strong confirmation
            if strength_score > 0.7 and false_prob < 0.3:
                if retest.retest_occurred and retest.retest_hold:
                    return BreakoutValidation.CONFIRMED
                elif not retest.retest_occurred:
                    return BreakoutValidation.PENDING
            
            # Needs retest for confirmation
            if not retest.retest_occurred and strength_score > 0.5:
                return BreakoutValidation.RETEST_REQUIRED
            
            # Confirmed after successful retest
            if retest.retest_occurred and retest.retest_hold and false_prob < 0.4:
                return BreakoutValidation.CONFIRMED
            
            # Failed retest
            if retest.retest_occurred and not retest.retest_hold:
                return BreakoutValidation.FALSE_BREAKOUT
            
            # Default pending status
            return BreakoutValidation.PENDING
            
        except Exception as e:
            return BreakoutValidation.INSUFFICIENT_DATA
    
    def _generate_recommendation(self, validation_status: BreakoutValidation, 
                               strength_score: float) -> str:
        """Generate trading recommendation based on validation"""
        if validation_status == BreakoutValidation.CONFIRMED:
            if strength_score > 0.8:
                return "strong_buy" if strength_score > 0.9 else "buy"
            else:
                return "cautious_buy"
        elif validation_status == BreakoutValidation.PENDING:
            return "wait_for_confirmation"
        elif validation_status == BreakoutValidation.RETEST_REQUIRED:
            return "wait_for_retest"
        elif validation_status == BreakoutValidation.FALSE_BREAKOUT:
            return "avoid_or_fade"
        else:
            return "insufficient_data"
    
    def _calculate_target_levels(self, df: pd.DataFrame, event: BreakoutEvent, 
                               breakout_index: int) -> List[float]:
        """Calculate potential target levels for the breakout"""
        try:
            targets = []
            level_price = event.level_broken.price
            
            # Calculate average true range for scaling
            atr = self._calculate_atr(df, 14)
            
            if event.breakout_type == BreakoutType.RESISTANCE_BREAK:
                # Bullish breakout targets
                targets.append(level_price + atr)        # Conservative target
                targets.append(level_price + atr * 2)    # Medium target
                targets.append(level_price + atr * 3)    # Aggressive target
            else:
                # Bearish breakout targets
                targets.append(level_price - atr)        # Conservative target
                targets.append(level_price - atr * 2)    # Medium target
                targets.append(level_price - atr * 3)    # Aggressive target
            
            return targets
            
        except Exception as e:
            return []
    
    def _calculate_stop_loss_level(self, event: BreakoutEvent, retest: RetestAnalysis) -> float:
        """Calculate appropriate stop loss level"""
        try:
            level_price = event.level_broken.price
            
            # Base stop loss at the broken level
            if event.breakout_type == BreakoutType.RESISTANCE_BREAK:
                # For bullish breakout, stop below the broken resistance
                stop_loss = level_price - (level_price * 0.005)  # 0.5% buffer
            else:
                # For bearish breakout, stop above the broken support
                stop_loss = level_price + (level_price * 0.005)  # 0.5% buffer
            
            # Adjust based on retest if available
            if retest.retest_occurred and retest.retest_price:
                if event.breakout_type == BreakoutType.RESISTANCE_BREAK:
                    # Use retest low as stop (with small buffer)
                    stop_loss = retest.retest_price - (retest.retest_price * 0.002)
                else:
                    # Use retest high as stop (with small buffer)
                    stop_loss = retest.retest_price + (retest.retest_price * 0.002)
            
            return stop_loss
            
        except Exception as e:
            return event.level_broken.price
    
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

# Global instance
_breakout_validator = None

async def get_breakout_validator() -> BreakoutValidator:
    """Get or create the global breakout validator instance"""
    global _breakout_validator
    if _breakout_validator is None:
        _breakout_validator = BreakoutValidator()
    return _breakout_validator

async def validate_breakouts(df: pd.DataFrame, suspected_level: float = None) -> List[BreakoutValidationResult]:
    """Validate breakouts in market data"""
    validator = await get_breakout_validator()
    return await validator.validate_breakout(df, suspected_level)

async def analyze_level_strength(df: pd.DataFrame, level: float) -> Dict[str, Any]:
    """Analyze the strength of a specific price level"""
    try:
        validator = await get_breakout_validator()
        level_obj = validator._create_level_object(df, level)
        
        return {
            'level_price': level_obj.price,
            'level_type': level_obj.level_type,
            'strength_touches': level_obj.strength,
            'age_hours': level_obj.age_hours,
            'average_volume': level_obj.volume_at_level,
            'last_test': level_obj.last_test_time.isoformat(),
            'breakout_likelihood': min(level_obj.strength / 5.0, 1.0),
            'significance': 'high' if level_obj.strength >= 4 else 'medium' if level_obj.strength >= 2 else 'low'
        }
        
    except Exception as e:
        return {
            'level_price': level,
            'level_type': 'unknown',
            'strength_touches': 0,
            'age_hours': 0,
            'average_volume': 0,
            'breakout_likelihood': 0.0,
            'significance': 'low',
            'error': str(e)
        }

def format_breakout_analysis(results: List[BreakoutValidationResult]) -> str:
    """Format breakout analysis results for display"""
    try:
        if not results:
            return "No significant breakouts detected in the analyzed period."
        
        formatted = "**Breakout Analysis Results**\n\n"
        
        for i, result in enumerate(results, 1):
            event = result.breakout_event
            validation_emoji = {
                BreakoutValidation.CONFIRMED: "✅",
                BreakoutValidation.PENDING: "⏳",
                BreakoutValidation.FALSE_BREAKOUT: "❌",
                BreakoutValidation.RETEST_REQUIRED: "🔄",
                BreakoutValidation.INSUFFICIENT_DATA: "❓"
            }
            
            formatted += f"**Breakout #{i}**\n"
            formatted += f"{validation_emoji.get(result.validation_status, '❓')} Status: {result.validation_status.value.replace('_', ' ').title()}\n"
            formatted += f"📍 Level: {event.level_broken.price:.5f} ({event.breakout_type.value.replace('_', ' ').title()})\n"
            formatted += f"📊 Strength: {result.strength_score:.2f} | Reliability: {result.reliability_score:.2f}\n"
            formatted += f"⚠️ False Breakout Risk: {result.false_breakout_probability:.1%}\n"
            formatted += f"🎯 Action: {result.recommended_action.replace('_', ' ').title()}\n"
            
            if result.target_levels:
                formatted += f"🎯 Targets: {', '.join([f'{t:.5f}' for t in result.target_levels[:2]])}\n"
            formatted += f"🛑 Stop Loss: {result.stop_loss_level:.5f}\n"
            
            if result.retest_analysis.retest_occurred:
                retest_status = "Held ✅" if result.retest_analysis.retest_hold else "Failed ❌"
                formatted += f"🔄 Retest: {retest_status}\n"
            
            formatted += "\n"
        
        return formatted
        
    except Exception as e:
        return f"Error formatting breakout analysis: {str(e)}"