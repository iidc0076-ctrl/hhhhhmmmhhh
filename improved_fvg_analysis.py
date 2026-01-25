#!/usr/bin/env python3
"""
Improved Fair Value Gap (FVG) Analysis System
Enhanced ICT/SMC analysis focused exclusively on FVG accuracy and precision
Removes: Order blocks, liquidity sweeps, displacement, seasonal patterns, ML predictor
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from safe_math_utils import safe_mean, safe_std, safe_divide

@dataclass
class EnhancedFVG:
    """Enhanced Fair Value Gap with improved validation"""
    gap_start: float
    gap_end: float
    gap_index: int
    gap_type: str  # "bullish", "bearish"
    gap_size: float
    gap_strength: float  # 0-100 strength rating
    volume_confirmation: bool
    filled: bool = False
    fill_percentage: float = 0.0
    reaction_quality: float = 0.0  # How well price reacted to the gap
    confluence_score: float = 0.0  # Additional confluence factors

class ImprovedFVGAnalyzer:
    """Improved Fair Value Gap analyzer with enhanced precision"""
    
    def __init__(self):
        # Enhanced FVG detection parameters
        self.min_gap_percentage = 0.0008  # 0.08% minimum gap size (more precise)
        self.max_gap_percentage = 0.015   # 1.5% maximum gap size (filters noise)
        self.volume_confirmation_threshold = 1.5  # Volume must be 1.5x average
        self.strength_calculation_periods = 20   # Periods for strength calculation
        self.confluence_lookback = 10     # Periods to check for confluence
        
    def analyze_enhanced_fvg(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Enhanced FVG analysis with improved accuracy and precision
        """
        try:
            if df is None or len(df) < 20:
                return self._empty_fvg_result()
            
            # Detect all potential FVGs with enhanced validation
            fvgs = self._detect_enhanced_fvgs(df)
            
            # Filter and validate FVGs
            validated_fvgs = self._validate_fvg_quality(df, fvgs)
            
            # Analyze current price relationship to FVGs
            current_analysis = self._analyze_current_fvg_context(df, validated_fvgs)
            
            # Calculate overall FVG signal
            fvg_signal = self._calculate_fvg_signal(df, validated_fvgs, current_analysis)
            
            return {
                'signal': fvg_signal['signal'],
                'confidence': fvg_signal['confidence'],
                'strength': fvg_signal['strength'],
                'factors': fvg_signal['factors'],
                'fvgs_detected': len(validated_fvgs),
                'active_fvgs': len([fvg for fvg in validated_fvgs if not fvg.filled]),
                'bullish_fvgs': len([fvg for fvg in validated_fvgs if fvg.gap_type == 'bullish' and not fvg.filled]),
                'bearish_fvgs': len([fvg for fvg in validated_fvgs if fvg.gap_type == 'bearish' and not fvg.filled]),
                'current_context': current_analysis,
                'fvg_details': [self._fvg_to_dict(fvg) for fvg in validated_fvgs[-5:]]  # Last 5 FVGs
            }
            
        except Exception as e:
            print(f"Error in enhanced FVG analysis: {e}")
            return self._empty_fvg_result()
    
    def _detect_enhanced_fvgs(self, df: pd.DataFrame) -> List[EnhancedFVG]:
        """Detect Fair Value Gaps with enhanced precision"""
        fvgs = []
        
        for i in range(2, len(df) - 1):  # Need 3 candles for FVG
            # Get three consecutive candles
            candle1 = df.iloc[i-2]  # First candle
            candle2 = df.iloc[i-1]  # Middle candle (gap creator)
            candle3 = df.iloc[i]    # Third candle (gap confirmer)
            
            # Enhanced bullish FVG detection
            bullish_gap = self._detect_bullish_fvg(candle1, candle2, candle3, i)
            if bullish_gap:
                # Validate gap quality
                gap_strength = self._calculate_gap_strength(df, bullish_gap, i)
                volume_conf = self._check_volume_confirmation(df, i-1)  # Middle candle volume
                confluence = self._calculate_confluence_score(df, bullish_gap, i)
                
                enhanced_fvg = EnhancedFVG(
                    gap_start=bullish_gap['start'],
                    gap_end=bullish_gap['end'],
                    gap_index=i,
                    gap_type='bullish',
                    gap_size=bullish_gap['size'],
                    gap_strength=gap_strength,
                    volume_confirmation=volume_conf,
                    confluence_score=confluence
                )
                fvgs.append(enhanced_fvg)
            
            # Enhanced bearish FVG detection
            bearish_gap = self._detect_bearish_fvg(candle1, candle2, candle3, i)
            if bearish_gap:
                # Validate gap quality
                gap_strength = self._calculate_gap_strength(df, bearish_gap, i)
                volume_conf = self._check_volume_confirmation(df, i-1)  # Middle candle volume
                confluence = self._calculate_confluence_score(df, bearish_gap, i)
                
                enhanced_fvg = EnhancedFVG(
                    gap_start=bearish_gap['start'],
                    gap_end=bearish_gap['end'],
                    gap_index=i,
                    gap_type='bearish',
                    gap_size=bearish_gap['size'],
                    gap_strength=gap_strength,
                    volume_confirmation=volume_conf,
                    confluence_score=confluence
                )
                fvgs.append(enhanced_fvg)
        
        return fvgs
    
    def _detect_bullish_fvg(self, candle1: pd.Series, candle2: pd.Series, candle3: pd.Series, index: int) -> Optional[Dict]:
        """Enhanced bullish FVG detection with strict validation"""
        # Bullish FVG: candle1_high < candle3_low (gap between them)
        # Middle candle (candle2) should show strong bullish momentum
        
        if candle1['high'] >= candle3['low']:
            return None  # No gap exists
        
        gap_start = candle1['high']
        gap_end = candle3['low']
        gap_size = gap_end - gap_start
        
        # Calculate gap size as percentage of price
        avg_price = (candle1['close'] + candle2['close'] + candle3['close']) / 3
        gap_percentage = gap_size / avg_price
        
        # Enhanced validation criteria
        if not (self.min_gap_percentage <= gap_percentage <= self.max_gap_percentage):
            return None
        
        # Additional bullish momentum validation
        candle2_body = abs(candle2['close'] - candle2['open'])
        candle2_range = candle2['high'] - candle2['low']
        
        # Middle candle should be bullish and strong
        if candle2['close'] <= candle2['open']:  # Not bullish
            return None
            
        # Body should be at least 60% of the candle range
        if candle2_range > 0 and (candle2_body / candle2_range) < 0.6:
            return None
        
        return {
            'start': gap_start,
            'end': gap_end,
            'size': gap_size,
            'percentage': gap_percentage,
            'middle_candle_strength': candle2_body / candle2_range if candle2_range > 0 else 0
        }
    
    def _detect_bearish_fvg(self, candle1: pd.Series, candle2: pd.Series, candle3: pd.Series, index: int) -> Optional[Dict]:
        """Enhanced bearish FVG detection with strict validation"""
        # Bearish FVG: candle1_low > candle3_high (gap between them)
        # Middle candle (candle2) should show strong bearish momentum
        
        if candle1['low'] <= candle3['high']:
            return None  # No gap exists
        
        gap_start = candle3['high']
        gap_end = candle1['low']
        gap_size = gap_end - gap_start
        
        # Calculate gap size as percentage of price
        avg_price = (candle1['close'] + candle2['close'] + candle3['close']) / 3
        gap_percentage = gap_size / avg_price
        
        # Enhanced validation criteria
        if not (self.min_gap_percentage <= gap_percentage <= self.max_gap_percentage):
            return None
        
        # Additional bearish momentum validation
        candle2_body = abs(candle2['close'] - candle2['open'])
        candle2_range = candle2['high'] - candle2['low']
        
        # Middle candle should be bearish and strong
        if candle2['close'] >= candle2['open']:  # Not bearish
            return None
            
        # Body should be at least 60% of the candle range
        if candle2_range > 0 and (candle2_body / candle2_range) < 0.6:
            return None
        
        return {
            'start': gap_start,
            'end': gap_end,
            'size': gap_size,
            'percentage': gap_percentage,
            'middle_candle_strength': candle2_body / candle2_range if candle2_range > 0 else 0
        }
    
    def _calculate_gap_strength(self, df: pd.DataFrame, gap: Dict, index: int) -> float:
        """Calculate gap strength based on multiple factors"""
        try:
            strength = 0.0
            
            # 1. Gap size relative to recent volatility (40 points)
            if index >= 20:
                recent_ranges = []
                for i in range(max(0, index-20), index):
                    candle_range = df.iloc[i]['high'] - df.iloc[i]['low']
                    recent_ranges.append(candle_range)
                
                avg_range = safe_mean(recent_ranges) if recent_ranges else 0
                if avg_range > 0:
                    gap_to_range_ratio = gap['size'] / avg_range
                    strength += min(40, gap_to_range_ratio * 20)
            
            # 2. Middle candle strength (30 points)
            middle_strength = gap.get('middle_candle_strength', 0)
            strength += middle_strength * 30
            
            # 3. Gap percentage relative to price (30 points)
            gap_percentage = gap.get('percentage', 0)
            if 0.001 <= gap_percentage <= 0.005:  # Optimal range
                strength += 30
            elif 0.0005 <= gap_percentage < 0.001:
                strength += 20
            elif 0.005 < gap_percentage <= 0.01:
                strength += 20
            else:
                strength += 10
            
            return min(100.0, strength)
            
        except Exception as e:
            print(f"Error calculating gap strength: {e}")
            return 50.0
    
    def _check_volume_confirmation(self, df: pd.DataFrame, index: int) -> bool:
        """Check if volume confirms the FVG formation"""
        try:
            if index < 10 or 'volume' not in df.columns:
                return False
            
            # Get average volume of last 10 candles (excluding current)
            recent_volume = []
            for i in range(max(0, index-10), index):
                if not pd.isna(df.iloc[i]['volume']):
                    recent_volume.append(df.iloc[i]['volume'])
            
            if not recent_volume:
                return False
            
            avg_volume = safe_mean(recent_volume)
            current_volume = df.iloc[index]['volume']
            
            # Volume should be at least 1.5x average
            return current_volume >= (avg_volume * self.volume_confirmation_threshold)
            
        except Exception as e:
            return False
    
    def _calculate_confluence_score(self, df: pd.DataFrame, gap: Dict, index: int) -> float:
        """Calculate confluence score for additional validation"""
        try:
            confluence = 0.0
            
            # Check if gap aligns with recent trend (50 points)
            if index >= 10:
                recent_closes = [df.iloc[i]['close'] for i in range(max(0, index-10), index)]
                if len(recent_closes) >= 5:
                    trend_direction = 1 if recent_closes[-1] > recent_closes[0] else -1
                    
                    # Check if FVG aligns with trend
                    gap_center = (gap['start'] + gap['end']) / 2
                    price_at_gap = df.iloc[index-1]['close']
                    
                    if trend_direction == 1 and gap_center > price_at_gap:  # Bullish trend, bullish gap
                        confluence += 25
                    elif trend_direction == -1 and gap_center < price_at_gap:  # Bearish trend, bearish gap
                        confluence += 25
            
            # Check if gap occurs at significant price levels (50 points)
            gap_center = (gap['start'] + gap['end']) / 2
            
            # Simple support/resistance check using recent highs/lows
            if index >= 20:
                recent_highs = [df.iloc[i]['high'] for i in range(max(0, index-20), index)]
                recent_lows = [df.iloc[i]['low'] for i in range(max(0, index-20), index)]
                
                # Check if gap is near recent significant levels
                for level in recent_highs + recent_lows:
                    price_diff = abs(gap_center - level) / gap_center
                    if price_diff <= 0.002:  # Within 0.2%
                        confluence += 25
                        break
            
            return min(100.0, confluence)
            
        except Exception as e:
            return 0.0
    
    def _validate_fvg_quality(self, df: pd.DataFrame, fvgs: List[EnhancedFVG]) -> List[EnhancedFVG]:
        """Filter FVGs based on quality criteria"""
        validated_fvgs = []
        
        for fvg in fvgs:
            # Quality criteria
            quality_score = 0
            
            # Minimum strength requirement (30 points minimum)
            if fvg.gap_strength >= 30:
                quality_score += 30
            
            # Volume confirmation bonus (20 points)
            if fvg.volume_confirmation:
                quality_score += 20
            
            # Confluence bonus (20 points)
            if fvg.confluence_score >= 25:
                quality_score += 20
            
            # Gap size validation (30 points)
            if 0.001 <= (fvg.gap_size / 1.0) <= 0.01:  # Reasonable gap size
                quality_score += 30
            
            # Only keep FVGs with quality score >= 50
            if quality_score >= 50:
                validated_fvgs.append(fvg)
        
        return validated_fvgs
    
    def _analyze_current_fvg_context(self, df: pd.DataFrame, fvgs: List[EnhancedFVG]) -> Dict[str, Any]:
        """Analyze current price relationship to FVGs"""
        if not fvgs or len(df) == 0:
            return {'near_fvg': False, 'fvg_direction': 'none', 'distance_to_nearest': 999}
        
        current_price = df.iloc[-1]['close']
        nearest_fvg = None
        min_distance = float('inf')
        
        # Find nearest unfilled FVG
        for fvg in fvgs:
            if not fvg.filled:
                # Calculate distance to FVG center
                fvg_center = (fvg.gap_start + fvg.gap_end) / 2
                distance = abs(current_price - fvg_center) / current_price
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_fvg = fvg
        
        if nearest_fvg and min_distance <= 0.003:  # Within 0.3%
            return {
                'near_fvg': True,
                'fvg_direction': nearest_fvg.gap_type,
                'distance_to_nearest': min_distance,
                'fvg_strength': nearest_fvg.gap_strength,
                'volume_confirmed': nearest_fvg.volume_confirmation
            }
        
        return {'near_fvg': False, 'fvg_direction': 'none', 'distance_to_nearest': min_distance}
    
    def _calculate_fvg_signal(self, df: pd.DataFrame, fvgs: List[EnhancedFVG], context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall FVG-based signal"""
        try:
            if not fvgs:
                return {
                    'signal': 'NEUTRAL',
                    'confidence': 45.0,
                    'strength': 'weak',
                    'factors': ['No valid FVGs detected']
                }
            
            # Count active FVGs by type
            active_bullish = [fvg for fvg in fvgs if fvg.gap_type == 'bullish' and not fvg.filled]
            active_bearish = [fvg for fvg in fvgs if fvg.gap_type == 'bearish' and not fvg.filled]
            
            # Calculate signal based on FVG context
            confidence = 45.0  # Base confidence
            factors = []
            signal = 'NEUTRAL'
            
            # Primary signal from nearest FVG
            if context['near_fvg']:
                if context['fvg_direction'] == 'bullish':
                    signal = 'BUY'
                    confidence += 25
                    factors.append(f"Near bullish FVG (strength: {context['fvg_strength']:.1f})")
                elif context['fvg_direction'] == 'bearish':
                    signal = 'SELL'
                    confidence += 25
                    factors.append(f"Near bearish FVG (strength: {context['fvg_strength']:.1f})")
                
                # Volume confirmation bonus
                if context['volume_confirmed']:
                    confidence += 10
                    factors.append("Volume-confirmed FVG")
            
            # Additional confidence from FVG balance
            if len(active_bullish) > len(active_bearish) and len(active_bullish) >= 2:
                if signal == 'NEUTRAL':
                    signal = 'BUY'
                confidence += min(15, len(active_bullish) * 5)
                factors.append(f"Multiple bullish FVGs ({len(active_bullish)})")
            elif len(active_bearish) > len(active_bullish) and len(active_bearish) >= 2:
                if signal == 'NEUTRAL':
                    signal = 'SELL'
                confidence += min(15, len(active_bearish) * 5)
                factors.append(f"Multiple bearish FVGs ({len(active_bearish)})")
            
            # Quality bonus from high-strength FVGs
            high_quality_fvgs = [fvg for fvg in fvgs if fvg.gap_strength >= 70 and not fvg.filled]
            if high_quality_fvgs:
                confidence += min(10, len(high_quality_fvgs) * 5)
                factors.append(f"High-quality FVGs detected ({len(high_quality_fvgs)})")
            
            # Determine strength
            if confidence >= 75:
                strength = 'strong'
            elif confidence >= 65:
                strength = 'moderate'
            else:
                strength = 'weak'
            
            return {
                'signal': signal,
                'confidence': min(92.0, confidence),  # Cap at 92%
                'strength': strength,
                'factors': factors if factors else ['Basic FVG analysis completed']
            }
            
        except Exception as e:
            print(f"Error calculating FVG signal: {e}")
            return {
                'signal': 'NEUTRAL',
                'confidence': 45.0,
                'strength': 'weak',
                'factors': ['Error in FVG signal calculation']
            }
    
    def _fvg_to_dict(self, fvg: EnhancedFVG) -> Dict[str, Any]:
        """Convert FVG to dictionary"""
        return {
            'start': fvg.gap_start,
            'end': fvg.gap_end,
            'type': fvg.gap_type,
            'size': fvg.gap_size,
            'strength': fvg.gap_strength,
            'volume_confirmed': fvg.volume_confirmation,
            'confluence_score': fvg.confluence_score,
            'filled': fvg.filled,
            'reaction_quality': fvg.reaction_quality
        }
    
    def _empty_fvg_result(self) -> Dict[str, Any]:
        """Return empty FVG result"""
        return {
            'signal': 'NEUTRAL',
            'confidence': 45.0,
            'strength': 'weak',
            'factors': ['Insufficient data for FVG analysis'],
            'fvgs_detected': 0,
            'active_fvgs': 0,
            'bullish_fvgs': 0,
            'bearish_fvgs': 0,
            'current_context': {'near_fvg': False, 'fvg_direction': 'none'},
            'fvg_details': []
        }

# Global function for integration
def get_improved_fvg_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Get improved FVG analysis for a DataFrame"""
    analyzer = ImprovedFVGAnalyzer()
    return analyzer.analyze_enhanced_fvg(df)