"""
Ranging and Trending Market Detection Systems
Specialized systems to handle both ranging (sideways) and trending markets effectively
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from safe_math_utils import safe_mean, safe_std, safe_divide

class MarketRegimeDetector:
    """Advanced market regime detection for ranging vs trending markets"""
    
    def __init__(self):
        self.trending_threshold = 0.7
        self.ranging_threshold = 0.3
        self.volatility_window = 20
        self.trend_window = 50
        
    def detect_market_regime(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect if market is trending or ranging with confidence"""
        try:
            if len(df) < 50:
                return self._default_regime()
            
            # Multiple regime detection methods
            trend_strength = self._calculate_trend_strength(df)
            range_characteristics = self._analyze_range_characteristics(df)
            volatility_analysis = self._analyze_volatility_regime(df)
            price_action_regime = self._analyze_price_action_regime(df)
            
            # Combine all methods for final determination
            regime_decision = self._determine_final_regime(
                trend_strength, range_characteristics, 
                volatility_analysis, price_action_regime
            )
            
            return {
                'regime': regime_decision['regime'],
                'confidence': regime_decision['confidence'],
                'trend_strength': trend_strength,
                'range_characteristics': range_characteristics,
                'volatility_analysis': volatility_analysis,
                'price_action_regime': price_action_regime,
                'regime_factors': regime_decision['factors'],
                'trading_approach': self._get_trading_approach(regime_decision['regime'])
            }
            
        except Exception as e:
            print(f"Error in market regime detection: {e}")
            return self._default_regime()
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trend strength using multiple methods"""
        try:
            # Linear regression slope
            prices = df['close'].tail(self.trend_window)
            x = np.arange(len(prices))
            slope, _ = np.polyfit(x, prices, 1)
            slope_strength = abs(slope) / prices.mean() * 100
            
            # ADX calculation
            adx = self._calculate_adx(df)
            
            # Moving average alignment
            ma_alignment = self._calculate_ma_alignment(df)
            
            # R-squared for trend linearity
            correlation = np.corrcoef(x, prices)[0, 1] ** 2
            
            # Combine trend metrics
            overall_trend_strength = (
                min(slope_strength * 20, 100) * 0.3 +
                adx * 0.3 +
                ma_alignment * 0.25 +
                correlation * 100 * 0.15
            ) / 100
            
            return {
                'overall_strength': overall_trend_strength,
                'slope_strength': slope_strength,
                'adx': adx,
                'ma_alignment': ma_alignment,
                'r_squared': correlation,
                'trend_direction': 'bullish' if slope > 0 else 'bearish' if slope < 0 else 'neutral'
            }
            
        except Exception as e:
            print(f"Error calculating trend strength: {e}")
            return {'overall_strength': 0.5, 'trend_direction': 'neutral'}
    
    def _analyze_range_characteristics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze ranging market characteristics"""
        try:
            recent_data = df.tail(self.trend_window)
            
            # Support/Resistance levels
            highs = recent_data['high']
            lows = recent_data['low']
            
            # Find significant levels
            resistance_levels = self._find_resistance_levels(highs)
            support_levels = self._find_support_levels(lows)
            
            # Range tightness
            price_range = highs.max() - lows.min()
            avg_price = recent_data['close'].mean()
            range_percentage = (price_range / avg_price) * 100
            
            # Level respect count
            level_respects = self._count_level_respects(recent_data, resistance_levels + support_levels)
            
            # Sideways movement score
            price_volatility = recent_data['close'].std() / avg_price * 100
            
            # Range quality score
            range_quality = 0
            if range_percentage < 3:  # Tight range
                range_quality += 30
            if level_respects > 4:  # Good level respect
                range_quality += 25
            if price_volatility < 1.5:  # Low volatility
                range_quality += 25
            if len(resistance_levels) >= 2 and len(support_levels) >= 2:  # Clear levels
                range_quality += 20
            
            return {
                'range_quality': range_quality / 100,
                'price_range_percentage': range_percentage,
                'level_respects': level_respects,
                'volatility': price_volatility,
                'resistance_levels': resistance_levels,
                'support_levels': support_levels,
                'is_tight_range': range_percentage < 2,
                'is_clear_levels': len(resistance_levels) >= 1 and len(support_levels) >= 1
            }
            
        except Exception as e:
            print(f"Error analyzing range characteristics: {e}")
            return {'range_quality': 0.5}
    
    def _analyze_volatility_regime(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volatility to determine regime"""
        try:
            # ATR analysis
            atr = self._calculate_atr(df)
            # Calculate ATR moving average more safely
            if len(df) > 40:
                atr_values = []
                for i in range(20, len(df)):
                    subset_df = df.iloc[i-20:i]
                    atr_val = self._calculate_atr(subset_df)
                    atr_values.append(atr_val)
                atr_ma = np.mean(atr_values) if atr_values else atr
            else:
                atr_ma = atr
            
            # Volatility expansion/contraction
            vol_ratio = atr / atr_ma if atr_ma > 0 else 1
            
            # Bollinger Band squeeze
            bb_squeeze = self._detect_bb_squeeze(df)
            
            # Volume volatility
            if 'volume' in df.columns:
                vol_volatility = df['volume'].tail(20).std() / df['volume'].tail(20).mean()
            else:
                vol_volatility = 0.5
            
            return {
                'atr_ratio': vol_ratio,
                'bb_squeeze': bb_squeeze,
                'volume_volatility': vol_volatility,
                'volatility_regime': 'expanding' if vol_ratio > 1.2 else 'contracting' if vol_ratio < 0.8 else 'stable'
            }
            
        except Exception as e:
            print(f"Error analyzing volatility regime: {e}")
            return {'volatility_regime': 'stable'}
    
    def _analyze_price_action_regime(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze price action patterns for regime"""
        try:
            recent_data = df.tail(30)
            
            # Breakout attempts
            breakout_attempts = self._count_breakout_attempts(recent_data)
            
            # Failed breakouts (ranging characteristic)
            failed_breakouts = self._count_failed_breakouts(recent_data)
            
            # Trend continuation patterns
            trend_continuations = self._count_trend_continuations(recent_data)
            
            # Reversal patterns
            reversal_patterns = self._count_reversal_patterns(recent_data)
            
            # Price action score
            ranging_score = (failed_breakouts * 2 + reversal_patterns) / max(1, breakout_attempts + trend_continuations + failed_breakouts + reversal_patterns)
            trending_score = (trend_continuations * 2 + breakout_attempts) / max(1, breakout_attempts + trend_continuations + failed_breakouts + reversal_patterns)
            
            return {
                'ranging_score': ranging_score,
                'trending_score': trending_score,
                'breakout_attempts': breakout_attempts,
                'failed_breakouts': failed_breakouts,
                'trend_continuations': trend_continuations,
                'reversal_patterns': reversal_patterns
            }
            
        except Exception as e:
            print(f"Error analyzing price action regime: {e}")
            return {'ranging_score': 0.5, 'trending_score': 0.5}
    
    def _determine_final_regime(self, trend_strength: Dict, range_chars: Dict, 
                               vol_analysis: Dict, price_action: Dict) -> Dict[str, Any]:
        """Determine final market regime"""
        
        # Scoring system
        trending_score = 0
        ranging_score = 0
        factors = []
        
        # Trend strength contribution
        if trend_strength.get('overall_strength', 0) > 0.7:
            trending_score += 40
            factors.append("Strong trend detected")
        elif trend_strength.get('overall_strength', 0) < 0.3:
            ranging_score += 30
            factors.append("Weak trend indicates ranging")
        
        # Range characteristics contribution
        range_quality = range_chars.get('range_quality', 0)
        if range_quality > 0.7:
            ranging_score += 35
            factors.append("High range quality")
        elif range_quality < 0.3:
            trending_score += 25
            factors.append("Poor range quality indicates trending")
        
        # Price action contribution
        if price_action.get('trending_score', 0) > price_action.get('ranging_score', 0):
            trending_score += 25
            factors.append("Price action favors trending")
        else:
            ranging_score += 25
            factors.append("Price action favors ranging")
        
        # Volatility contribution
        vol_regime = vol_analysis.get('volatility_regime', 'stable')
        if vol_regime == 'expanding':
            trending_score += 15
            factors.append("Expanding volatility")
        elif vol_regime == 'contracting':
            ranging_score += 15
            factors.append("Contracting volatility")
        
        # Determine final regime
        total_score = trending_score + ranging_score
        if total_score == 0:
            return {'regime': 'uncertain', 'confidence': 50, 'factors': ['Insufficient data']}
        
        if trending_score > ranging_score:
            confidence = (trending_score / total_score) * 100
            regime = 'trending'
        else:
            confidence = (ranging_score / total_score) * 100
            regime = 'ranging'
        
        return {
            'regime': regime,
            'confidence': confidence,
            'factors': factors,
            'trending_score': trending_score,
            'ranging_score': ranging_score
        }
    
    def _get_trading_approach(self, regime: str) -> Dict[str, Any]:
        """Get recommended trading approach for regime"""
        if regime == 'trending':
            return {
                'strategy': 'trend_following',
                'entry_method': 'pullback_entries',
                'stop_placement': 'trailing_stops',
                'profit_targets': 'ride_trend',
                'indicators': ['moving_averages', 'momentum', 'breakouts'],
                'avoid': ['range_trading', 'mean_reversion']
            }
        elif regime == 'ranging':
            return {
                'strategy': 'range_trading',
                'entry_method': 'support_resistance_bounces',
                'stop_placement': 'outside_range',
                'profit_targets': 'opposite_range_boundary',
                'indicators': ['oscillators', 'support_resistance', 'volume'],
                'avoid': ['trend_following', 'breakout_trading']
            }
        else:
            return {
                'strategy': 'wait_for_clarity',
                'entry_method': 'confirmed_breakouts_only',
                'stop_placement': 'tight_stops',
                'profit_targets': 'quick_scalps',
                'indicators': ['volume', 'volatility'],
                'avoid': ['large_positions']
            }
    
    def _default_regime(self) -> Dict[str, Any]:
        """Default regime when detection fails"""
        return {
            'regime': 'uncertain',
            'confidence': 50,
            'trading_approach': self._get_trading_approach('uncertain')
        }
    
    # Helper methods (simplified implementations)
    def _calculate_adx(self, df: pd.DataFrame) -> float:
        """Calculate Average Directional Index"""
        try:
            if len(df) < 14:
                return 25
            
            high = df['high'].tail(14)
            low = df['low'].tail(14)
            close = df['close'].tail(14)
            
            # Simplified ADX calculation
            plus_dm = high.diff()
            minus_dm = low.diff().abs()
            plus_dm = plus_dm.where(plus_dm > minus_dm, 0)
            minus_dm = minus_dm.where(minus_dm > plus_dm, 0)
            
            tr_series = pd.concat([
                high - low,
                (high - close.shift()).abs(),
                (low - close.shift()).abs()
            ], axis=1).max(axis=1)
            
            tr_ma_series = tr_series.rolling(14, min_periods=1).mean()
            tr_ma = tr_ma_series.iloc[-1] if len(tr_ma_series) > 0 else 1.0
            
            plus_dm_ma_series = plus_dm.rolling(14, min_periods=1).mean()
            minus_dm_ma_series = minus_dm.rolling(14, min_periods=1).mean()
            
            plus_di = (plus_dm_ma_series.iloc[-1] / tr_ma) * 100 if tr_ma > 0 and len(plus_dm_ma_series) > 0 else 0
            minus_di = (minus_dm_ma_series.iloc[-1] / tr_ma) * 100 if tr_ma > 0 and len(minus_dm_ma_series) > 0 else 0
            
            dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
            return min(100, max(0, dx))
        except:
            return 25
    
    def _calculate_ma_alignment(self, df: pd.DataFrame) -> float:
        """Calculate moving average alignment score"""
        try:
            if len(df) < 50:
                return 0.5
            
            sma_20_series = df['close'].rolling(20, min_periods=1).mean()
            sma_50_series = df['close'].rolling(50, min_periods=1).mean()
            sma_20 = sma_20_series.iloc[-1] if len(sma_20_series) > 0 else df['close'].iloc[-1]
            sma_50 = sma_50_series.iloc[-1] if len(sma_50_series) > 0 else df['close'].iloc[-1]
            
            # Check alignment
            if sma_20 > sma_50:
                return 0.8  # Bullish alignment
            elif sma_20 < sma_50:
                return 0.2  # Bearish alignment
            else:
                return 0.5  # Neutral
        except:
            return 0.5
    
    def _calculate_atr(self, df: pd.DataFrame) -> float:
        """Calculate Average True Range"""
        try:
            if len(df) < 14:
                return (df['high'] - df['low']).mean()
            
            tr_series = pd.concat([
                df['high'] - df['low'],
                (df['high'] - df['close'].shift()).abs(),
                (df['low'] - df['close'].shift()).abs()
            ], axis=1).max(axis=1)
            
            return tr_series.tail(14).mean()
        except:
            return 0.001
    
    def _find_resistance_levels(self, highs: pd.Series) -> List[float]:
        """Find resistance levels"""
        levels = []
        try:
            for i in range(2, len(highs) - 2):
                if (highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i-2] and
                    highs.iloc[i] > highs.iloc[i+1] and highs.iloc[i] > highs.iloc[i+2]):
                    levels.append(highs.iloc[i])
        except:
            pass
        return levels
    
    def _find_support_levels(self, lows: pd.Series) -> List[float]:
        """Find support levels"""
        levels = []
        try:
            for i in range(2, len(lows) - 2):
                if (lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i-2] and
                    lows.iloc[i] < lows.iloc[i+1] and lows.iloc[i] < lows.iloc[i+2]):
                    levels.append(lows.iloc[i])
        except:
            pass
        return levels
    
    def _count_level_respects(self, df: pd.DataFrame, levels: List[float]) -> int:
        """Count how many times levels were respected"""
        count = 0
        for level in levels:
            tolerance = level * 0.002  # 0.2% tolerance
            for _, row in df.iterrows():
                if abs(row['high'] - level) <= tolerance or abs(row['low'] - level) <= tolerance:
                    count += 1
        return count
    
    def _detect_bb_squeeze(self, df: pd.DataFrame) -> bool:
        """Detect Bollinger Band squeeze"""
        try:
            if len(df) < 20:
                return False
            
            close = df['close'].tail(20)
            bb_upper = close.rolling(20).mean() + (close.rolling(20).std() * 2)
            bb_lower = close.rolling(20).mean() - (close.rolling(20).std() * 2)
            
            current_width = (bb_upper.iloc[-1] - bb_lower.iloc[-1]) / close.iloc[-1]
            avg_width = ((bb_upper - bb_lower) / close).mean()
            
            return current_width < avg_width * 0.8
        except:
            return False
    
    def _count_breakout_attempts(self, df: pd.DataFrame) -> int:
        """Count breakout attempts"""
        return len(df) // 10  # Simplified
    
    def _count_failed_breakouts(self, df: pd.DataFrame) -> int:
        """Count failed breakouts"""
        return len(df) // 15  # Simplified
    
    def _count_trend_continuations(self, df: pd.DataFrame) -> int:
        """Count trend continuation patterns"""
        return len(df) // 12  # Simplified
    
    def _count_reversal_patterns(self, df: pd.DataFrame) -> int:
        """Count reversal patterns"""
        return len(df) // 20  # Simplified

class RangingMarketStrategy:
    """Specialized strategy for ranging markets"""
    
    def analyze_ranging_opportunity(self, df: pd.DataFrame, regime_data: Dict) -> Dict[str, Any]:
        """Analyze trading opportunities in ranging markets"""
        try:
            if regime_data.get('regime') != 'ranging':
                return {'suitable': False, 'reason': 'Not a ranging market'}
            
            range_chars = regime_data.get('range_characteristics', {})
            resistance_levels = range_chars.get('resistance_levels', [])
            support_levels = range_chars.get('support_levels', [])
            
            current_price = df['close'].iloc[-1]
            
            # Find current position in range
            position_analysis = self._analyze_range_position(current_price, resistance_levels, support_levels)
            
            # Generate ranging signals
            signals = self._generate_ranging_signals(df, position_analysis, range_chars)
            
            return {
                'suitable': True,
                'range_position': position_analysis,
                'signals': signals,
                'risk_management': self._get_ranging_risk_management(resistance_levels, support_levels, current_price)
            }
            
        except Exception as e:
            print(f"Error in ranging market analysis: {e}")
            return {'suitable': False, 'reason': str(e)}
    
    def _analyze_range_position(self, current_price: float, resistance: List[float], support: List[float]) -> Dict[str, Any]:
        """Analyze current position within the range"""
        if not resistance or not support:
            return {'position': 'unknown'}
        
        nearest_resistance = min(resistance, key=lambda x: abs(x - current_price) if x > current_price else float('inf'))
        nearest_support = min(support, key=lambda x: abs(x - current_price) if x < current_price else float('inf'))
        
        # Calculate position percentage
        range_size = nearest_resistance - nearest_support
        position_pct = (current_price - nearest_support) / range_size * 100 if range_size > 0 else 50
        
        return {
            'position': 'upper' if position_pct > 70 else 'lower' if position_pct < 30 else 'middle',
            'position_percentage': position_pct,
            'nearest_resistance': nearest_resistance,
            'nearest_support': nearest_support,
            'range_size': range_size
        }
    
    def _generate_ranging_signals(self, df: pd.DataFrame, position: Dict, range_chars: Dict) -> Dict[str, Any]:
        """Generate signals for ranging markets"""
        signals = {'signal': 'NEUTRAL', 'strength': 0, 'factors': []}
        
        position_pct = position.get('position_percentage', 50)
        current_price = df['close'].iloc[-1]
        
        # Near support - look for bounce
        if position_pct < 20:
            signals['signal'] = 'BUY'
            signals['strength'] = 70
            signals['factors'].append('Near range support - bounce expected')
        
        # Near resistance - look for rejection
        elif position_pct > 80:
            signals['signal'] = 'SELL'
            signals['strength'] = 70
            signals['factors'].append('Near range resistance - rejection expected')
        
        # Middle of range - wait for direction
        else:
            signals['signal'] = 'NEUTRAL'
            signals['strength'] = 30
            signals['factors'].append('Middle of range - wait for clear direction')
        
        return signals
    
    def _get_ranging_risk_management(self, resistance: List[float], support: List[float], current_price: float) -> Dict[str, Any]:
        """Get risk management for ranging trades"""
        if not resistance or not support:
            return {}
        
        nearest_resistance = min(resistance, key=lambda x: abs(x - current_price) if x > current_price else float('inf'))
        nearest_support = min(support, key=lambda x: abs(x - current_price) if x < current_price else float('inf'))
        
        return {
            'buy_stop_loss': nearest_support * 0.999,  # Just below support
            'sell_stop_loss': nearest_resistance * 1.001,  # Just above resistance
            'buy_take_profit': nearest_resistance * 0.998,  # Just below resistance
            'sell_take_profit': nearest_support * 1.002,  # Just above support
            'position_size': 'moderate',  # Ranging markets allow larger positions
            'holding_period': 'short_to_medium'
        }

class TrendingMarketStrategy:
    """Specialized strategy for trending markets"""
    
    def analyze_trending_opportunity(self, df: pd.DataFrame, regime_data: Dict) -> Dict[str, Any]:
        """Analyze trading opportunities in trending markets"""
        try:
            if regime_data.get('regime') != 'trending':
                return {'suitable': False, 'reason': 'Not a trending market'}
            
            trend_strength = regime_data.get('trend_strength', {})
            trend_direction = trend_strength.get('trend_direction', 'neutral')
            
            if trend_direction == 'neutral':
                return {'suitable': False, 'reason': 'No clear trend direction'}
            
            # Analyze trend characteristics
            trend_analysis = self._analyze_trend_characteristics(df, trend_strength)
            
            # Find entry opportunities
            entry_opportunities = self._find_trend_entries(df, trend_direction, trend_analysis)
            
            return {
                'suitable': True,
                'trend_direction': trend_direction,
                'trend_analysis': trend_analysis,
                'entry_opportunities': entry_opportunities,
                'risk_management': self._get_trending_risk_management(df, trend_direction)
            }
            
        except Exception as e:
            print(f"Error in trending market analysis: {e}")
            return {'suitable': False, 'reason': str(e)}
    
    def _analyze_trend_characteristics(self, df: pd.DataFrame, trend_strength: Dict) -> Dict[str, Any]:
        """Analyze characteristics of the current trend"""
        try:
            # Trend age
            trend_start = self._find_trend_start(df)
            trend_age = len(df) - trend_start if trend_start else len(df)
            
            # Trend momentum
            momentum = self._calculate_trend_momentum(df)
            
            # Pullback analysis
            pullbacks = self._analyze_pullbacks(df)
            
            return {
                'trend_age': trend_age,
                'trend_momentum': momentum,
                'pullback_analysis': pullbacks,
                'trend_strength_score': trend_strength.get('overall_strength', 0),
                'trend_health': 'strong' if momentum > 0.7 else 'moderate' if momentum > 0.4 else 'weak'
            }
            
        except Exception as e:
            print(f"Error analyzing trend characteristics: {e}")
            return {'trend_health': 'unknown'}
    
    def _find_trend_entries(self, df: pd.DataFrame, direction: str, analysis: Dict) -> Dict[str, Any]:
        """Find optimal entry points in trending markets"""
        signals = {'signal': 'NEUTRAL', 'strength': 0, 'factors': []}
        
        current_price = df['close'].iloc[-1]
        ma_20 = df['close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else current_price
        
        # Pullback entries
        if direction == 'bullish':
            # Look for pullbacks to moving average
            if current_price > ma_20 * 1.005:  # Above MA
                signals['signal'] = 'BUY'
                signals['strength'] = 65
                signals['factors'].append('Bullish trend - price above MA20')
            elif abs(current_price - ma_20) / ma_20 < 0.01:  # Near MA
                signals['signal'] = 'BUY'
                signals['strength'] = 75
                signals['factors'].append('Bullish trend - pullback to MA20')
        
        elif direction == 'bearish':
            # Look for pullbacks to moving average
            if current_price < ma_20 * 0.995:  # Below MA
                signals['signal'] = 'SELL'
                signals['strength'] = 65
                signals['factors'].append('Bearish trend - price below MA20')
            elif abs(current_price - ma_20) / ma_20 < 0.01:  # Near MA
                signals['signal'] = 'SELL'
                signals['strength'] = 75
                signals['factors'].append('Bearish trend - pullback to MA20')
        
        return signals
    
    def _get_trending_risk_management(self, df: pd.DataFrame, direction: str) -> Dict[str, Any]:
        """Get risk management for trending trades"""
        try:
            atr = self._calculate_atr(df)
            current_price = df['close'].iloc[-1]
            
            if direction == 'bullish':
                stop_loss = current_price - (atr * 2)
                take_profit = current_price + (atr * 4)  # 2:1 RR
            else:
                stop_loss = current_price + (atr * 2)
                take_profit = current_price - (atr * 4)  # 2:1 RR
            
            return {
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size': 'small_to_moderate',  # Trending markets can be volatile
                'trailing_stop': True,
                'holding_period': 'medium_to_long',
                'atr_multiple_stop': 2,
                'atr_multiple_target': 4
            }
            
        except Exception as e:
            print(f"Error calculating trending risk management: {e}")
            return {}
    
    def _calculate_atr(self, df: pd.DataFrame) -> float:
        """Calculate ATR for risk management"""
        try:
            if len(df) < 14:
                return (df['high'] - df['low']).mean()
            
            tr_series = pd.concat([
                df['high'] - df['low'],
                (df['high'] - df['close'].shift()).abs(),
                (df['low'] - df['close'].shift()).abs()
            ], axis=1).max(axis=1)
            
            return tr_series.tail(14).mean()
        except:
            return 0.001
    
    def _find_trend_start(self, df: pd.DataFrame) -> Optional[int]:
        """Find approximate trend start"""
        # Simplified implementation
        return max(0, len(df) - 50)
    
    def _calculate_trend_momentum(self, df: pd.DataFrame) -> float:
        """Calculate trend momentum"""
        try:
            if len(df) < 10:
                return 0.5
            
            recent_closes = df['close'].tail(10)
            momentum = (recent_closes.iloc[-1] - recent_closes.iloc[0]) / recent_closes.iloc[0]
            return min(1.0, abs(momentum) * 10)
        except:
            return 0.5
    
    def _analyze_pullbacks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze pullback patterns"""
        return {
            'pullback_count': 3,  # Simplified
            'avg_pullback_depth': 0.05,  # 5%
            'pullback_quality': 'healthy'
        }

# Global functions for integration
def detect_market_regime(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect market regime for a DataFrame"""
    detector = MarketRegimeDetector()
    return detector.detect_market_regime(df)

def get_ranging_analysis(df: pd.DataFrame, regime_data: Dict) -> Dict[str, Any]:
    """Get ranging market analysis"""
    strategy = RangingMarketStrategy()
    return strategy.analyze_ranging_opportunity(df, regime_data)

def get_trending_analysis(df: pd.DataFrame, regime_data: Dict) -> Dict[str, Any]:
    """Get trending market analysis"""
    strategy = TrendingMarketStrategy()
    return strategy.analyze_trending_opportunity(df, regime_data)