"""
Cross-Timeframe Signal Validation System for Trading Bot
Validates signals across multiple timeframes for higher accuracy
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

class TimeframeAlignment(Enum):
    FULLY_ALIGNED = "fully_aligned"
    MOSTLY_ALIGNED = "mostly_aligned"
    PARTIALLY_ALIGNED = "partially_aligned"
    CONFLICTED = "conflicted"
    INSUFFICIENT_DATA = "insufficient_data"

class TrendDirection(Enum):
    STRONG_BULLISH = "strong_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    STRONG_BEARISH = "strong_bearish"

@dataclass
class TimeframeAnalysis:
    timeframe: str
    trend_direction: TrendDirection
    trend_strength: float
    momentum_score: float
    support_resistance_levels: List[float]
    volume_confirmation: float
    signal_quality: float
    last_updated: datetime

@dataclass
class CrossTimeframeValidation:
    primary_timeframe: str
    signal_direction: str
    overall_alignment: TimeframeAlignment
    alignment_score: float
    timeframe_analyses: Dict[str, TimeframeAnalysis]
    conflicting_timeframes: List[str]
    supporting_timeframes: List[str]
    entry_optimization: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    confidence_multiplier: float

class CrossTimeframeValidator:
    """Advanced cross-timeframe signal validation system"""
    
    def __init__(self):
        self.timeframes = ['1min', '5min', '15min', '1hour', '1day']
        self.timeframe_weights = {
            '1min': 0.1,    # Short-term entry timing
            '5min': 0.15,   # Entry confirmation
            '15min': 0.2,   # Medium-term trend
            '1hour': 0.3,   # Primary trend
            '1day': 0.25    # Long-term bias
        }
        self.config = {
            'min_alignment_score': 0.6,  # Minimum score for valid signal
            'strong_alignment_threshold': 0.8,
            'trend_strength_threshold': 0.5,
            'momentum_threshold': 0.4,
            'volume_confirmation_threshold': 0.3
        }
        
    async def validate_signal_across_timeframes(self, symbol: str, signal_direction: str, 
                                              primary_timeframe: str = '15min') -> CrossTimeframeValidation:
        """Validate a signal across multiple timeframes"""
        try:
            timeframe_analyses = {}
            
            # Analyze each timeframe
            for tf in self.timeframes:
                analysis = await self._analyze_single_timeframe(symbol, tf, signal_direction)
                if analysis:
                    timeframe_analyses[tf] = analysis
            
            # Calculate overall alignment
            alignment_score = self._calculate_alignment_score(timeframe_analyses, signal_direction)
            overall_alignment = self._classify_alignment(alignment_score)
            
            # Identify supporting and conflicting timeframes
            supporting_tfs, conflicting_tfs = self._categorize_timeframes(
                timeframe_analyses, signal_direction
            )
            
            # Optimize entry timing
            entry_optimization = self._optimize_entry_timing(
                timeframe_analyses, primary_timeframe, signal_direction
            )
            
            # Assess risk based on timeframe conflicts
            risk_assessment = self._assess_cross_timeframe_risk(
                timeframe_analyses, alignment_score
            )
            
            # Calculate confidence multiplier
            confidence_multiplier = self._calculate_confidence_multiplier(
                alignment_score, len(supporting_tfs), len(conflicting_tfs)
            )
            
            return CrossTimeframeValidation(
                primary_timeframe=primary_timeframe,
                signal_direction=signal_direction,
                overall_alignment=overall_alignment,
                alignment_score=alignment_score,
                timeframe_analyses=timeframe_analyses,
                conflicting_timeframes=conflicting_tfs,
                supporting_timeframes=supporting_tfs,
                entry_optimization=entry_optimization,
                risk_assessment=risk_assessment,
                confidence_multiplier=confidence_multiplier
            )
            
        except Exception as e:
            return self._empty_validation_result(primary_timeframe, signal_direction)
    
    async def _analyze_single_timeframe(self, symbol: str, timeframe: str, 
                                      signal_direction: str) -> Optional[TimeframeAnalysis]:
        """Analyze a single timeframe for trend and momentum"""
        try:
            # In production, this would fetch actual data for the timeframe
            # For now, we'll simulate realistic analysis
            df = await self._get_timeframe_data(symbol, timeframe)
            
            if df is None or len(df) < 20:
                return None
            
            # Analyze trend direction and strength
            trend_analysis = self._analyze_trend(df)
            
            # Calculate momentum indicators
            momentum_score = self._calculate_momentum_score(df)
            
            # Identify key levels
            support_resistance = self._identify_key_levels(df)
            
            # Volume confirmation
            volume_confirmation = self._analyze_volume_confirmation(df, signal_direction)
            
            # Calculate signal quality for this timeframe
            signal_quality = self._calculate_timeframe_signal_quality(
                trend_analysis, momentum_score, volume_confirmation
            )
            
            return TimeframeAnalysis(
                timeframe=timeframe,
                trend_direction=trend_analysis['direction'],
                trend_strength=trend_analysis['strength'],
                momentum_score=momentum_score,
                support_resistance_levels=support_resistance,
                volume_confirmation=volume_confirmation,
                signal_quality=signal_quality,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            return None
    
    async def _get_timeframe_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Get data for specific timeframe - placeholder for actual data fetching"""
        try:
            # This would integrate with your existing data fetching system
            # For now, return None to indicate we need actual implementation
            return None
            
        except Exception as e:
            return None
    
    def _analyze_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trend direction and strength"""
        try:
            # Calculate moving averages with safe handling
            ma_short = df['close'].rolling(10, min_periods=1).mean()
            ma_medium = df['close'].rolling(20, min_periods=1).mean()
            ma_long = df['close'].rolling(50, min_periods=1).mean()
            
            current_price = df['close'].iloc[-1]
            ma_short_val = ma_short.iloc[-1]
            ma_medium_val = ma_medium.iloc[-1]
            ma_long_val = ma_long.iloc[-1]
            
            # Determine trend direction
            if current_price > ma_short_val > ma_medium_val > ma_long_val:
                direction = TrendDirection.STRONG_BULLISH
                strength = 0.9
            elif current_price > ma_short_val > ma_medium_val:
                direction = TrendDirection.BULLISH
                strength = 0.7
            elif current_price < ma_short_val < ma_medium_val < ma_long_val:
                direction = TrendDirection.STRONG_BEARISH
                strength = 0.9
            elif current_price < ma_short_val < ma_medium_val:
                direction = TrendDirection.BEARISH
                strength = 0.7
            else:
                direction = TrendDirection.NEUTRAL
                strength = 0.3
            
            # Calculate trend consistency
            price_changes = df['close'].diff().dropna()
            trend_consistency = abs(price_changes.sum()) / price_changes.abs().sum()
            
            # Adjust strength based on consistency
            final_strength = strength * trend_consistency
            
            return {
                'direction': direction,
                'strength': min(final_strength, 1.0),
                'consistency': trend_consistency,
                'ma_alignment': self._check_ma_alignment(ma_short_val, ma_medium_val, ma_long_val)
            }
            
        except Exception as e:
            return {
                'direction': TrendDirection.NEUTRAL,
                'strength': 0.0,
                'consistency': 0.0,
                'ma_alignment': False
            }
    
    def _check_ma_alignment(self, ma_short: float, ma_medium: float, ma_long: float) -> bool:
        """Check if moving averages are properly aligned"""
        try:
            bullish_alignment = ma_short > ma_medium > ma_long
            bearish_alignment = ma_short < ma_medium < ma_long
            return bullish_alignment or bearish_alignment
        except:
            return False
    
    def _calculate_momentum_score(self, df: pd.DataFrame) -> float:
        """Calculate momentum score for the timeframe"""
        try:
            # RSI calculation
            rsi = self._calculate_rsi(df['close'])
            
            # MACD calculation
            macd_line, signal_line = self._calculate_macd(df['close'])
            
            # Price momentum
            price_momentum = (df['close'].iloc[-1] - df['close'].iloc[-10]) / df['close'].iloc[-10]
            
            # Volume momentum (if available)
            if 'volume' in df.columns:
                volume_momentum = (df['volume'].iloc[-5:].mean() - df['volume'].iloc[-15:-5].mean()) / df['volume'].iloc[-15:-5].mean()
            else:
                volume_momentum = 0.1
            
            # Combine momentum indicators
            rsi_score = self._normalize_rsi_score(rsi)
            macd_score = 1.0 if macd_line > signal_line else 0.0
            price_score = min(abs(price_momentum) * 10, 1.0)
            volume_score = min(abs(volume_momentum), 0.5)
            
            momentum_score = (rsi_score * 0.3 + macd_score * 0.3 + price_score * 0.3 + volume_score * 0.1)
            
            return min(momentum_score, 1.0)
            
        except Exception as e:
            return 0.3
    
    def _normalize_rsi_score(self, rsi: float) -> float:
        """Normalize RSI to momentum score"""
        try:
            if rsi > 70 or rsi < 30:
                return 1.0  # Strong momentum
            elif rsi > 60 or rsi < 40:
                return 0.7  # Moderate momentum
            else:
                return 0.3  # Weak momentum
        except:
            return 0.3
    
    def _identify_key_levels(self, df: pd.DataFrame) -> List[float]:
        """Identify key support and resistance levels"""
        try:
            levels = []
            
            # Find swing highs and lows
            highs = df['high'].rolling(5, center=True).max()
            lows = df['low'].rolling(5, center=True).min()
            
            # Identify swing points
            swing_highs = df[df['high'] == highs]['high'].dropna()
            swing_lows = df[df['low'] == lows]['low'].dropna()
            
            # Add recent significant levels
            levels.extend(swing_highs.tail(3).tolist())
            levels.extend(swing_lows.tail(3).tolist())
            
            # Add round numbers and psychological levels
            current_price = df['close'].iloc[-1]
            price_magnitude = 10 ** (len(str(int(current_price))) - 1)
            round_levels = [
                round(current_price / price_magnitude) * price_magnitude,
                round(current_price / (price_magnitude/2)) * (price_magnitude/2),
                round(current_price / (price_magnitude/5)) * (price_magnitude/5)
            ]
            levels.extend(round_levels)
            
            # Remove duplicates and sort
            levels = sorted(list(set([round(level, 5) for level in levels if level > 0])))
            
            return levels[-10:]  # Return top 10 levels
            
        except Exception as e:
            return []
    
    def _analyze_volume_confirmation(self, df: pd.DataFrame, signal_direction: str) -> float:
        """Analyze volume confirmation for the signal"""
        try:
            if 'volume' not in df.columns:
                return 0.5  # Neutral if no volume data
            
            recent_volume = df['volume'].tail(5).mean()
            avg_volume = df['volume'].rolling(20).mean().iloc[-1]
            
            volume_ratio = recent_volume / max(avg_volume, 1)
            
            # Check volume trend alignment with price
            price_direction = 1 if df['close'].iloc[-1] > df['close'].iloc[-5] else -1
            signal_numeric = 1 if signal_direction.upper() == 'BUY' else -1
            
            # Volume confirmation score
            base_score = min(volume_ratio / 2, 1.0)  # Higher volume = better confirmation
            
            # Bonus for volume-price alignment
            if price_direction == signal_numeric:
                alignment_bonus = 0.2
            else:
                alignment_bonus = -0.2
            
            confirmation_score = base_score + alignment_bonus
            
            return max(0.0, min(confirmation_score, 1.0))
            
        except Exception as e:
            return 0.3
    
    def _calculate_timeframe_signal_quality(self, trend_analysis: Dict[str, Any], 
                                          momentum_score: float, volume_confirmation: float) -> float:
        """Calculate overall signal quality for a timeframe"""
        try:
            trend_score = trend_analysis['strength']
            consistency_score = trend_analysis['consistency']
            ma_alignment_score = 1.0 if trend_analysis['ma_alignment'] else 0.5
            
            quality_score = (
                trend_score * 0.4 +
                momentum_score * 0.3 +
                volume_confirmation * 0.2 +
                consistency_score * 0.05 +
                ma_alignment_score * 0.05
            )
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            return 0.3
    
    def _calculate_alignment_score(self, timeframe_analyses: Dict[str, TimeframeAnalysis], 
                                 signal_direction: str) -> float:
        """Calculate overall alignment score across timeframes"""
        try:
            if not timeframe_analyses:
                return 0.0
            
            weighted_score = 0.0
            total_weight = 0.0
            
            for tf, analysis in timeframe_analyses.items():
                weight = self.timeframe_weights.get(tf, 0.1)
                
                # Check if timeframe supports the signal
                trend_support = self._check_trend_support(analysis.trend_direction, signal_direction)
                momentum_support = analysis.momentum_score
                volume_support = analysis.volume_confirmation
                
                # Calculate timeframe contribution
                tf_score = (trend_support * 0.5 + momentum_support * 0.3 + volume_support * 0.2)
                
                weighted_score += tf_score * weight
                total_weight += weight
            
            return weighted_score / max(total_weight, 1)
            
        except Exception as e:
            return 0.0
    
    def _check_trend_support(self, trend_direction: TrendDirection, signal_direction: str) -> float:
        """Check how well the trend supports the signal direction"""
        signal_bullish = signal_direction.upper() == 'BUY'
        
        if signal_bullish:
            if trend_direction == TrendDirection.STRONG_BULLISH:
                return 1.0
            elif trend_direction == TrendDirection.BULLISH:
                return 0.8
            elif trend_direction == TrendDirection.NEUTRAL:
                return 0.5
            elif trend_direction == TrendDirection.BEARISH:
                return 0.2
            else:  # STRONG_BEARISH
                return 0.0
        else:  # SELL signal
            if trend_direction == TrendDirection.STRONG_BEARISH:
                return 1.0
            elif trend_direction == TrendDirection.BEARISH:
                return 0.8
            elif trend_direction == TrendDirection.NEUTRAL:
                return 0.5
            elif trend_direction == TrendDirection.BULLISH:
                return 0.2
            else:  # STRONG_BULLISH
                return 0.0
    
    def _classify_alignment(self, alignment_score: float) -> TimeframeAlignment:
        """Classify the overall timeframe alignment"""
        if alignment_score >= 0.85:
            return TimeframeAlignment.FULLY_ALIGNED
        elif alignment_score >= 0.7:
            return TimeframeAlignment.MOSTLY_ALIGNED
        elif alignment_score >= 0.5:
            return TimeframeAlignment.PARTIALLY_ALIGNED
        elif alignment_score > 0.0:
            return TimeframeAlignment.CONFLICTED
        else:
            return TimeframeAlignment.INSUFFICIENT_DATA
    
    def _categorize_timeframes(self, timeframe_analyses: Dict[str, TimeframeAnalysis], 
                             signal_direction: str) -> Tuple[List[str], List[str]]:
        """Categorize timeframes as supporting or conflicting"""
        supporting = []
        conflicting = []
        
        for tf, analysis in timeframe_analyses.items():
            trend_support = self._check_trend_support(analysis.trend_direction, signal_direction)
            
            if trend_support >= 0.6:
                supporting.append(tf)
            elif trend_support <= 0.4:
                conflicting.append(tf)
            # 0.4 < trend_support < 0.6 are considered neutral and not categorized
        
        return supporting, conflicting
    
    def _optimize_entry_timing(self, timeframe_analyses: Dict[str, TimeframeAnalysis],
                             primary_timeframe: str, signal_direction: str) -> Dict[str, Any]:
        """Optimize entry timing based on lower timeframes"""
        try:
            # Get lower timeframe data for entry optimization
            lower_timeframes = ['1min', '5min'] if primary_timeframe not in ['1min', '5min'] else ['1min']
            
            entry_signals = {}
            for tf in lower_timeframes:
                if tf in timeframe_analyses:
                    analysis = timeframe_analyses[tf]
                    
                    # Calculate entry readiness
                    momentum_ready = analysis.momentum_score > self.config['momentum_threshold']
                    volume_ready = analysis.volume_confirmation > self.config['volume_confirmation_threshold']
                    trend_aligned = self._check_trend_support(analysis.trend_direction, signal_direction) > 0.5
                    
                    entry_signals[tf] = {
                        'momentum_ready': momentum_ready,
                        'volume_ready': volume_ready,
                        'trend_aligned': trend_aligned,
                        'overall_ready': all([momentum_ready, volume_ready, trend_aligned])
                    }
            
            # Determine optimal entry strategy
            if any(signals['overall_ready'] for signals in entry_signals.values()):
                entry_timing = 'immediate'
                entry_confidence = 0.9
            elif any(signals['trend_aligned'] for signals in entry_signals.values()):
                entry_timing = 'wait_for_momentum'
                entry_confidence = 0.6
            else:
                entry_timing = 'wait_for_alignment'
                entry_confidence = 0.3
            
            return {
                'entry_timing': entry_timing,
                'entry_confidence': entry_confidence,
                'timeframe_signals': entry_signals,
                'recommended_timeframe': min(lower_timeframes) if lower_timeframes else primary_timeframe
            }
            
        except Exception as e:
            return {
                'entry_timing': 'cautious',
                'entry_confidence': 0.3,
                'timeframe_signals': {},
                'recommended_timeframe': primary_timeframe
            }
    
    def _assess_cross_timeframe_risk(self, timeframe_analyses: Dict[str, TimeframeAnalysis],
                                   alignment_score: float) -> Dict[str, Any]:
        """Assess risk based on timeframe conflicts"""
        try:
            # Calculate conflict ratio
            total_timeframes = len(timeframe_analyses)
            strong_trends = sum(1 for analysis in timeframe_analyses.values() 
                              if analysis.trend_strength > 0.7)
            
            # Higher timeframe bias (daily and hourly carry more weight)
            higher_tf_strength = 0.0
            if '1day' in timeframe_analyses:
                higher_tf_strength += timeframe_analyses['1day'].trend_strength * 0.6
            if '1hour' in timeframe_analyses:
                higher_tf_strength += timeframe_analyses['1hour'].trend_strength * 0.4
            
            # Risk factors
            alignment_risk = 1.0 - alignment_score  # Lower alignment = higher risk
            trend_strength_risk = 1.0 - (strong_trends / max(total_timeframes, 1))
            higher_tf_risk = 1.0 - higher_tf_strength
            
            # Overall risk score
            overall_risk = (alignment_risk * 0.4 + trend_strength_risk * 0.3 + higher_tf_risk * 0.3)
            
            # Risk classification
            if overall_risk <= 0.3:
                risk_level = 'low'
            elif overall_risk <= 0.6:
                risk_level = 'moderate'
            else:
                risk_level = 'high'
            
            return {
                'overall_risk_score': overall_risk,
                'risk_level': risk_level,
                'alignment_risk': alignment_risk,
                'trend_strength_risk': trend_strength_risk,
                'higher_timeframe_risk': higher_tf_risk,
                'recommended_position_size': self._calculate_position_size_adjustment(overall_risk)
            }
            
        except Exception as e:
            return {
                'overall_risk_score': 0.8,
                'risk_level': 'high',
                'alignment_risk': 0.8,
                'trend_strength_risk': 0.8,
                'higher_timeframe_risk': 0.8,
                'recommended_position_size': 0.5
            }
    
    def _calculate_position_size_adjustment(self, risk_score: float) -> float:
        """Calculate position size adjustment based on risk"""
        if risk_score <= 0.3:
            return 1.0  # Full position
        elif risk_score <= 0.5:
            return 0.8  # Reduce by 20%
        elif risk_score <= 0.7:
            return 0.6  # Reduce by 40%
        else:
            return 0.4  # Reduce by 60%
    
    def _calculate_confidence_multiplier(self, alignment_score: float, 
                                       supporting_count: int, conflicting_count: int) -> float:
        """Calculate confidence multiplier for the signal"""
        try:
            base_multiplier = alignment_score
            
            # Support bonus
            support_bonus = min(supporting_count * 0.1, 0.3)
            
            # Conflict penalty
            conflict_penalty = conflicting_count * 0.15
            
            # Final multiplier
            multiplier = base_multiplier + support_bonus - conflict_penalty
            
            return max(0.1, min(multiplier, 1.5))  # Cap between 0.1 and 1.5
            
        except Exception as e:
            return 0.5
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
        except:
            return 50.0
    
    def _calculate_macd(self, prices: pd.Series) -> Tuple[float, float]:
        """Calculate MACD indicator"""
        try:
            ema_12 = prices.ewm(span=12).mean()
            ema_26 = prices.ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()
            return macd_line.iloc[-1], signal_line.iloc[-1]
        except:
            return 0.0, 0.0
    
    def _empty_validation_result(self, primary_timeframe: str, signal_direction: str) -> CrossTimeframeValidation:
        """Return empty validation result"""
        return CrossTimeframeValidation(
            primary_timeframe=primary_timeframe,
            signal_direction=signal_direction,
            overall_alignment=TimeframeAlignment.INSUFFICIENT_DATA,
            alignment_score=0.0,
            timeframe_analyses={},
            conflicting_timeframes=[],
            supporting_timeframes=[],
            entry_optimization={'entry_timing': 'wait', 'entry_confidence': 0.0},
            risk_assessment={'overall_risk_score': 1.0, 'risk_level': 'high'},
            confidence_multiplier=0.1
        )
    
    async def get_timeframe_summary(self, symbol: str) -> Dict[str, Any]:
        """Get summary of all timeframe analyses"""
        try:
            summary = {}
            
            for tf in self.timeframes:
                analysis = await self._analyze_single_timeframe(symbol, tf, 'BUY')  # Neutral analysis
                if analysis:
                    summary[tf] = {
                        'trend': analysis.trend_direction.value,
                        'strength': analysis.trend_strength,
                        'momentum': analysis.momentum_score,
                        'volume_confirmation': analysis.volume_confirmation,
                        'signal_quality': analysis.signal_quality,
                        'key_levels': analysis.support_resistance_levels
                    }
            
            return {
                'timeframe_summary': summary,
                'overall_market_bias': self._determine_market_bias(summary),
                'strongest_timeframe': max(summary.keys(), key=lambda x: summary[x]['signal_quality']) if summary else None,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'timeframe_summary': {},
                'overall_market_bias': 'unknown',
                'strongest_timeframe': None,
                'analysis_timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _determine_market_bias(self, timeframe_summary: Dict[str, Any]) -> str:
        """Determine overall market bias from timeframe analysis"""
        try:
            if not timeframe_summary:
                return 'unknown'
            
            bullish_count = 0
            bearish_count = 0
            
            for tf_data in timeframe_summary.values():
                trend = tf_data['trend']
                if 'bullish' in trend:
                    bullish_count += 1
                elif 'bearish' in trend:
                    bearish_count += 1
            
            if bullish_count > bearish_count:
                return 'bullish'
            elif bearish_count > bullish_count:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            return 'unknown'

# Global instance
_cross_timeframe_validator = None

async def get_cross_timeframe_validator() -> CrossTimeframeValidator:
    """Get or create the global cross-timeframe validator instance"""
    global _cross_timeframe_validator
    if _cross_timeframe_validator is None:
        _cross_timeframe_validator = CrossTimeframeValidator()
    return _cross_timeframe_validator

async def validate_signal_cross_timeframe(symbol: str, signal_direction: str, 
                                        primary_timeframe: str = '15min') -> CrossTimeframeValidation:
    """Validate a signal across multiple timeframes"""
    validator = await get_cross_timeframe_validator()
    return await validator.validate_signal_across_timeframes(symbol, signal_direction, primary_timeframe)

async def get_timeframe_market_summary(symbol: str) -> Dict[str, Any]:
    """Get comprehensive timeframe market summary"""
    validator = await get_cross_timeframe_validator()
    return await validator.get_timeframe_summary(symbol)

def format_cross_timeframe_analysis(validation: CrossTimeframeValidation) -> str:
    """Format cross-timeframe analysis for display"""
    try:
        alignment_emoji = {
            TimeframeAlignment.FULLY_ALIGNED: "🟢",
            TimeframeAlignment.MOSTLY_ALIGNED: "🟡",
            TimeframeAlignment.PARTIALLY_ALIGNED: "🟠",
            TimeframeAlignment.CONFLICTED: "🔴",
            TimeframeAlignment.INSUFFICIENT_DATA: "⚫"
        }
        
        result = f"**Cross-Timeframe Analysis ({validation.signal_direction.upper()})**\n"
        result += f"{alignment_emoji.get(validation.overall_alignment, '⚫')} Alignment: {validation.overall_alignment.value.replace('_', ' ').title()}\n"
        result += f"📊 Alignment Score: {validation.alignment_score:.2f}\n"
        result += f"🎯 Confidence Multiplier: {validation.confidence_multiplier:.1f}\n\n"
        
        if validation.supporting_timeframes:
            result += f"✅ Supporting: {', '.join(validation.supporting_timeframes)}\n"
        if validation.conflicting_timeframes:
            result += f"❌ Conflicting: {', '.join(validation.conflicting_timeframes)}\n"
        
        result += f"\n📈 Entry: {validation.entry_optimization.get('entry_timing', 'unknown').replace('_', ' ').title()}\n"
        result += f"⚠️ Risk Level: {validation.risk_assessment.get('risk_level', 'unknown').title()}\n"
        
        return result
        
    except Exception as e:
        return f"Cross-timeframe analysis error: {str(e)}"