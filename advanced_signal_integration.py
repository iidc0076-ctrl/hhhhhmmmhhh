"""
Advanced Signal Integration Module for Trading Bot
Integrates all advanced features into the main trading system
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import asyncio

# Import all advanced modules
try:
    from signal_decay_detection import get_signal_decay_detector, register_new_signal, update_signal_decay
    from market_microstructure_analysis import get_comprehensive_microstructure_analysis
    from order_flow_imbalance_detection import get_imbalance_summary
    from cross_timeframe_signal_validation import validate_signal_cross_timeframe, format_cross_timeframe_analysis
    from seasonal_cyclical_pattern_recognition import get_comprehensive_seasonal_analysis
    from breakout_validation_system import validate_breakouts, format_breakout_analysis
except ImportError as e:
    print(f"Warning: Could not import advanced modules: {e}")

class AdvancedSignalProcessor:
    """Main processor that integrates all advanced signal analysis features"""
    
    def __init__(self):
        self.enabled_features = {
            'signal_decay': True,
            'microstructure': True,
            'order_flow_imbalance': True,
            'cross_timeframe': True,
            'seasonal_cyclical': True,
            'breakout_validation': True
        }
        self.active_signals = {}
        
    async def process_enhanced_signal(self, symbol: str, signal_data: Dict[str, Any], 
                                    df: pd.DataFrame) -> Dict[str, Any]:
        """Process a signal through all advanced validation systems"""
        try:
            enhanced_analysis = {
                'symbol': symbol,
                'original_signal': signal_data,
                'timestamp': datetime.now().isoformat(),
                'enhanced_confidence': signal_data.get('confidence', 0.5),
                'validation_results': {},
                'final_recommendation': 'hold',
                'confidence_multipliers': {},
                'risk_adjustments': {}
            }
            
            # 1. Cross-Timeframe Validation (highest priority)
            if self.enabled_features['cross_timeframe']:
                tf_validation = await validate_signal_cross_timeframe(
                    symbol, signal_data.get('signal', 'BUY'), '15min'
                )
                enhanced_analysis['validation_results']['cross_timeframe'] = {
                    'alignment': tf_validation.overall_alignment.value,
                    'alignment_score': tf_validation.alignment_score,
                    'confidence_multiplier': tf_validation.confidence_multiplier,
                    'supporting_timeframes': tf_validation.supporting_timeframes,
                    'conflicting_timeframes': tf_validation.conflicting_timeframes,
                    'entry_timing': tf_validation.entry_optimization.get('entry_timing', 'wait'),
                    'risk_level': tf_validation.risk_assessment.get('risk_level', 'medium')
                }
                enhanced_analysis['confidence_multipliers']['timeframe'] = tf_validation.confidence_multiplier
            
            # 2. Seasonal and Cyclical Analysis
            if self.enabled_features['seasonal_cyclical']:
                seasonal_analysis = await get_comprehensive_seasonal_analysis(symbol, df)
                seasonal_bias = seasonal_analysis.get('combined_bias', {})
                enhanced_analysis['validation_results']['seasonal'] = {
                    'bias_direction': seasonal_bias.get('direction', 'neutral'),
                    'bias_strength': seasonal_bias.get('strength', 0.0),
                    'confidence': seasonal_bias.get('confidence', 0.0),
                    'alignment': seasonal_bias.get('alignment', 'unknown'),
                    'recommendations': seasonal_analysis.get('comprehensive_recommendations', {})
                }
                
                # Calculate seasonal confidence multiplier
                seasonal_multiplier = self._calculate_seasonal_multiplier(
                    signal_data.get('signal', 'BUY'), seasonal_bias
                )
                enhanced_analysis['confidence_multipliers']['seasonal'] = seasonal_multiplier
            
            # 3. Order Flow Imbalance Analysis
            if self.enabled_features['order_flow_imbalance']:
                imbalance_analysis = await get_imbalance_summary(df)
                current_imbalance = imbalance_analysis.get('current_imbalance', {})
                enhanced_analysis['validation_results']['order_flow'] = {
                    'imbalance_type': current_imbalance.get('type', 'balanced'),
                    'imbalance_ratio': current_imbalance.get('ratio', 0.0),
                    'strength': current_imbalance.get('strength', 0.0),
                    'market_impact': current_imbalance.get('market_impact', 0.0),
                    'institutional_presence': imbalance_analysis.get('trading_implications', {}).get('institutional_presence', 'low')
                }
                
                # Calculate order flow confidence adjustment
                flow_multiplier = self._calculate_order_flow_multiplier(
                    signal_data.get('signal', 'BUY'), current_imbalance
                )
                enhanced_analysis['confidence_multipliers']['order_flow'] = flow_multiplier
            
            # 4. Market Microstructure Analysis
            if self.enabled_features['microstructure']:
                microstructure = await get_comprehensive_microstructure_analysis(df)
                price_ladder = microstructure.get('price_ladder', {})
                enhanced_analysis['validation_results']['microstructure'] = {
                    'ladder_quality': price_ladder.get('ladder_quality', {}).get('reliability', 'poor'),
                    'overall_imbalance': price_ladder.get('overall_imbalance', 0.0),
                    'significant_levels_count': len(price_ladder.get('significant_levels', [])),
                    'clustering_zones': len(price_ladder.get('clustering_zones', [])),
                    'order_flow_direction': microstructure.get('order_flow', {}).get('direction', 'neutral')
                }
            
            # 5. Breakout Validation
            if self.enabled_features['breakout_validation']:
                breakout_results = await validate_breakouts(df)
                enhanced_analysis['validation_results']['breakouts'] = {
                    'breakout_count': len(breakout_results),
                    'confirmed_breakouts': len([b for b in breakout_results if b.validation_status.value == 'confirmed']),
                    'false_breakouts': len([b for b in breakout_results if b.validation_status.value == 'false_breakout']),
                    'breakout_quality': 'high' if any(b.strength_score > 0.7 for b in breakout_results) else 'medium' if breakout_results else 'none'
                }
                
                # Calculate breakout confidence adjustment
                breakout_multiplier = self._calculate_breakout_multiplier(breakout_results, signal_data.get('signal', 'BUY'))
                enhanced_analysis['confidence_multipliers']['breakout'] = breakout_multiplier
            
            # 6. Register for Signal Decay Monitoring
            if self.enabled_features['signal_decay']:
                signal_id = await register_new_signal({
                    'symbol': symbol,
                    'type': signal_data.get('signal', 'BUY'),
                    'price': df['close'].iloc[-1],
                    'confidence': signal_data.get('confidence', 0.5),
                    'technical_state': self._extract_technical_state(df)
                })
                enhanced_analysis['signal_decay_id'] = signal_id
                self.active_signals[signal_id] = enhanced_analysis
            
            # Calculate Final Enhanced Confidence
            enhanced_analysis['enhanced_confidence'] = self._calculate_final_confidence(
                signal_data.get('confidence', 0.5),
                enhanced_analysis['confidence_multipliers']
            )
            
            # Generate Final Recommendation
            enhanced_analysis['final_recommendation'] = self._generate_final_recommendation(
                enhanced_analysis['enhanced_confidence'],
                enhanced_analysis['validation_results']
            )
            
            # Calculate Risk Adjustments
            enhanced_analysis['risk_adjustments'] = self._calculate_risk_adjustments(
                enhanced_analysis['validation_results']
            )
            
            return enhanced_analysis
            
        except Exception as e:
            # Return safe default analysis
            return {
                'symbol': symbol,
                'original_signal': signal_data,
                'timestamp': datetime.now().isoformat(),
                'enhanced_confidence': signal_data.get('confidence', 0.5) * 0.8,  # Slight reduction due to error
                'validation_results': {'error': str(e)},
                'final_recommendation': 'cautious',
                'confidence_multipliers': {},
                'risk_adjustments': {'position_size_multiplier': 0.7},
                'error': str(e)
            }
    
    def _calculate_seasonal_multiplier(self, signal_direction: str, seasonal_bias: Dict[str, Any]) -> float:
        """Calculate confidence multiplier from seasonal analysis"""
        try:
            bias_direction = seasonal_bias.get('direction', 'neutral')
            bias_strength = seasonal_bias.get('strength', 0.0)
            confidence = seasonal_bias.get('confidence', 0.0)
            
            # Check alignment
            signal_bullish = signal_direction.upper() == 'BUY'
            bias_bullish = bias_direction == 'bullish'
            bias_bearish = bias_direction == 'bearish'
            
            if (signal_bullish and bias_bullish) or (not signal_bullish and bias_bearish):
                # Aligned with seasonal bias
                multiplier = 1.0 + (bias_strength * confidence * 0.3)  # Max 30% boost
            elif bias_direction == 'neutral':
                # Neutral seasonal bias
                multiplier = 1.0
            else:
                # Against seasonal bias
                multiplier = 1.0 - (bias_strength * confidence * 0.2)  # Max 20% penalty
            
            return max(0.5, min(multiplier, 1.4))  # Cap between 0.5 and 1.4
            
        except Exception as e:
            return 1.0
    
    def _calculate_order_flow_multiplier(self, signal_direction: str, imbalance_data: Dict[str, Any]) -> float:
        """Calculate confidence multiplier from order flow analysis"""
        try:
            imbalance_ratio = imbalance_data.get('ratio', 0.0)
            strength = imbalance_data.get('strength', 0.0)
            market_impact = imbalance_data.get('market_impact', 0.0)
            
            signal_bullish = signal_direction.upper() == 'BUY'
            flow_bullish = imbalance_ratio > 0.1
            flow_bearish = imbalance_ratio < -0.1
            
            if (signal_bullish and flow_bullish) or (not signal_bullish and flow_bearish):
                # Order flow supports signal
                boost = strength * market_impact * 0.25  # Max 25% boost
                multiplier = 1.0 + boost
            elif abs(imbalance_ratio) < 0.1:
                # Neutral order flow
                multiplier = 1.0
            else:
                # Order flow against signal
                penalty = strength * market_impact * 0.15  # Max 15% penalty
                multiplier = 1.0 - penalty
            
            return max(0.6, min(multiplier, 1.3))
            
        except Exception as e:
            return 1.0
    
    def _calculate_breakout_multiplier(self, breakout_results: List[Any], signal_direction: str) -> float:
        """Calculate confidence multiplier from breakout analysis"""
        try:
            if not breakout_results:
                return 1.0
            
            signal_bullish = signal_direction.upper() == 'BUY'
            
            # Find relevant breakouts
            relevant_breakouts = []
            for breakout in breakout_results:
                breakout_bullish = 'resistance' in breakout.breakout_event.breakout_type.value
                if (signal_bullish and breakout_bullish) or (not signal_bullish and not breakout_bullish):
                    relevant_breakouts.append(breakout)
            
            if not relevant_breakouts:
                return 1.0
            
            # Calculate multiplier based on breakout quality
            total_strength = sum(b.strength_score for b in relevant_breakouts)
            avg_strength = total_strength / len(relevant_breakouts)
            
            confirmed_count = len([b for b in relevant_breakouts if b.validation_status.value == 'confirmed'])
            confirmation_ratio = confirmed_count / len(relevant_breakouts)
            
            multiplier = 1.0 + (avg_strength * confirmation_ratio * 0.2)  # Max 20% boost
            
            return max(0.8, min(multiplier, 1.25))
            
        except Exception as e:
            return 1.0
    
    def _calculate_final_confidence(self, original_confidence: float, 
                                  multipliers: Dict[str, float]) -> float:
        """Calculate final enhanced confidence from all multipliers"""
        try:
            enhanced_confidence = original_confidence
            
            # Apply each multiplier
            for multiplier_type, multiplier_value in multipliers.items():
                enhanced_confidence *= multiplier_value
            
            # Apply diminishing returns for very high confidence
            if enhanced_confidence > 0.85:
                excess = enhanced_confidence - 0.85
                enhanced_confidence = 0.85 + (excess * 0.5)  # Diminishing returns
            
            return max(0.1, min(enhanced_confidence, 0.95))  # Cap between 10% and 95%
            
        except Exception as e:
            return original_confidence * 0.9  # Slight reduction on error
    
    def _generate_final_recommendation(self, confidence: float, 
                                     validation_results: Dict[str, Any]) -> str:
        """Generate final trading recommendation"""
        try:
            # Get cross-timeframe recommendation (highest priority)
            tf_results = validation_results.get('cross_timeframe', {})
            entry_timing = tf_results.get('entry_timing', 'wait')
            risk_level = tf_results.get('risk_level', 'medium')
            
            # Base recommendation on confidence and timing
            if confidence > 0.8 and entry_timing == 'immediate':
                if risk_level == 'low':
                    return 'strong_buy'
                else:
                    return 'buy'
            elif confidence > 0.65:
                if entry_timing in ['immediate', 'wait_for_momentum']:
                    return 'buy'
                else:
                    return 'wait_for_confirmation'
            elif confidence > 0.45:
                return 'cautious_buy'
            elif confidence > 0.3:
                return 'wait_for_confirmation'
            else:
                return 'avoid'
                
        except Exception as e:
            return 'hold'
    
    def _calculate_risk_adjustments(self, validation_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate risk management adjustments"""
        try:
            adjustments = {
                'position_size_multiplier': 1.0,
                'stop_loss_adjustment': 1.0,
                'take_profit_adjustment': 1.0
            }
            
            # Cross-timeframe risk adjustment
            tf_results = validation_results.get('cross_timeframe', {})
            risk_level = tf_results.get('risk_level', 'medium')
            
            if risk_level == 'low':
                adjustments['position_size_multiplier'] *= 1.2
            elif risk_level == 'high':
                adjustments['position_size_multiplier'] *= 0.7
                adjustments['stop_loss_adjustment'] *= 0.8  # Tighter stops
            
            # Seasonal risk adjustment
            seasonal_results = validation_results.get('seasonal', {})
            if seasonal_results.get('alignment') == 'conflicted':
                adjustments['position_size_multiplier'] *= 0.8
            
            # Order flow risk adjustment
            flow_results = validation_results.get('order_flow', {})
            institutional_presence = flow_results.get('institutional_presence', 'low')
            if institutional_presence == 'high':
                adjustments['take_profit_adjustment'] *= 1.3  # Wider targets
            
            return adjustments
            
        except Exception as e:
            return {'position_size_multiplier': 0.8, 'stop_loss_adjustment': 1.0, 'take_profit_adjustment': 1.0}
    
    def _extract_technical_state(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract technical state for signal decay monitoring"""
        try:
            current_price = df['close'].iloc[-1]
            
            # Calculate basic indicators
            rsi = self._calculate_rsi(df['close'])
            macd = self._calculate_macd(df['close'])
            atr = self._calculate_atr(df)
            volume = df['volume'].iloc[-1] if 'volume' in df.columns else 1000
            
            return {
                'rsi': rsi,
                'macd': macd,
                'atr': atr,
                'volume': volume,
                'price': current_price
            }
            
        except Exception as e:
            return {}
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI"""
        try:
            from safe_math_utils import safe_divide
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
            rs = gain / loss.replace(0, np.nan)  # Avoid division by zero
            rs = rs.where(rs.notna(), 0)
            rsi = 100 - (100 / (1 + rs))
            rsi = rsi.where(rsi.notna(), 50.0)
            return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
        except:
            return 50.0
    
    def _calculate_macd(self, prices: pd.Series) -> float:
        """Calculate MACD"""
        try:
            ema_12 = prices.ewm(span=12).mean()
            ema_26 = prices.ewm(span=26).mean()
            macd = ema_12 - ema_26
            return macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0.0
        except:
            return 0.0
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate ATR"""
        try:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(period, min_periods=1).mean()
            return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0.01
        except:
            return 0.01
    
    async def update_active_signals(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Update all active signals for decay monitoring"""
        try:
            updates = {}
            
            for signal_id in list(self.active_signals.keys()):
                try:
                    decay_metrics = await update_signal_decay(signal_id, df)
                    updates[signal_id] = {
                        'decay_rate': decay_metrics.decay_rate,
                        'current_strength': decay_metrics.current_strength,
                        'recommended_action': decay_metrics.recommended_action,
                        'decay_reasons': [r.value for r in decay_metrics.decay_reasons]
                    }
                    
                    # Remove invalidated signals
                    if decay_metrics.recommended_action == 'invalidate':
                        del self.active_signals[signal_id]
                        
                except Exception as e:
                    # Remove problematic signal
                    if signal_id in self.active_signals:
                        del self.active_signals[signal_id]
            
            return updates
            
        except Exception as e:
            return {}

# Global instance
_advanced_processor = None

async def get_advanced_processor() -> AdvancedSignalProcessor:
    """Get or create the global advanced signal processor"""
    global _advanced_processor
    if _advanced_processor is None:
        _advanced_processor = AdvancedSignalProcessor()
    return _advanced_processor

async def process_signal_with_advanced_analysis(symbol: str, signal_data: Dict[str, Any], 
                                              df: pd.DataFrame) -> Dict[str, Any]:
    """Main function to process signals through all advanced systems"""
    processor = await get_advanced_processor()
    return await processor.process_enhanced_signal(symbol, signal_data, df)

async def update_signal_monitoring(df: pd.DataFrame) -> Dict[str, Any]:
    """Update monitoring for all active signals"""
    processor = await get_advanced_processor()
    return await processor.update_active_signals(df)

def format_enhanced_analysis_for_discord(analysis: Dict[str, Any]) -> str:
    """Format enhanced analysis results for Discord display"""
    try:
        result = f"**Enhanced Signal Analysis - {analysis['symbol']}**\n\n"
        
        # Original vs Enhanced Confidence
        original_conf = analysis['original_signal'].get('confidence', 0.5)
        enhanced_conf = analysis['enhanced_confidence']
        conf_change = ((enhanced_conf - original_conf) / original_conf) * 100
        
        result += f"**Confidence:** {original_conf:.1%} → {enhanced_conf:.1%} "
        if conf_change > 5:
            result += f"(+{conf_change:.0f}% ⬆️)\n"
        elif conf_change < -5:
            result += f"({conf_change:.0f}% ⬇️)\n"
        else:
            result += f"(unchanged)\n"
        
        result += f"**Recommendation:** {analysis['final_recommendation'].replace('_', ' ').title()}\n\n"
        
        # Validation Results Summary
        validations = analysis.get('validation_results', {})
        
        # Cross-Timeframe
        if 'cross_timeframe' in validations:
            tf = validations['cross_timeframe']
            result += f"🕐 **Timeframes:** {tf.get('alignment', 'unknown').replace('_', ' ').title()}\n"
            result += f"   Supporting: {', '.join(tf.get('supporting_timeframes', ['none']))}\n"
            if tf.get('conflicting_timeframes'):
                result += f"   Conflicting: {', '.join(tf.get('conflicting_timeframes', []))}\n"
        
        # Seasonal Analysis
        if 'seasonal' in validations:
            seasonal = validations['seasonal']
            result += f"📅 **Seasonal:** {seasonal.get('bias_direction', 'neutral').title()} "
            result += f"({seasonal.get('bias_strength', 0):.1%} strength)\n"
        
        # Order Flow
        if 'order_flow' in validations:
            flow = validations['order_flow']
            result += f"💹 **Order Flow:** {flow.get('imbalance_type', 'balanced').replace('_', ' ').title()}\n"
            result += f"   Institutional: {flow.get('institutional_presence', 'low').title()}\n"
        
        # Risk Adjustments
        risk_adj = analysis.get('risk_adjustments', {})
        pos_size = risk_adj.get('position_size_multiplier', 1.0)
        if pos_size != 1.0:
            change = "Increase" if pos_size > 1.0 else "Reduce"
            result += f"⚖️ **Position Size:** {change} by {abs((pos_size - 1.0) * 100):.0f}%\n"
        
        return result
        
    except Exception as e:
        return f"Enhanced analysis formatting error: {str(e)}"