"""
Analysis Integration Pipeline
Integrates enhanced confluence analyzer with main trading analysis system
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from datetime import datetime

# Import analysis modules
try:
    from enhanced_confluence_analyzer import get_enhanced_confluence_analysis
    from unified_confidence_system import get_recommendation_confidence
    from advanced_signal_integration import get_advanced_processor
    from false_breakout_strategy import AdvancedFalseBreakoutStrategy
    from ml_ensemble_engine import get_ml_ensemble
    from advanced_liquidity_analysis import get_comprehensive_liquidity_analysis
    from advanced_volume_analysis import get_volume_profile_analysis
    from order_flow_imbalance_detection import get_imbalance_summary
    from seasonal_cyclical_pattern_recognition import get_comprehensive_seasonal_analysis
    from breakout_validation_system import validate_breakouts
    from market_microstructure_analysis import get_comprehensive_microstructure_analysis
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Some analysis modules not available: {e}")
    MODULES_AVAILABLE = False

class IntegratedAnalysisEngine:
    """Main analysis engine that integrates all analysis components with enhanced confluence"""

    def __init__(self):
        self.false_breakout_analyzer = AdvancedFalseBreakoutStrategy() if MODULES_AVAILABLE else None
        self.ml_ensemble = get_ml_ensemble() if MODULES_AVAILABLE else None
        self.confluence_enabled = True

    async def process_comprehensive_analysis(self, df: pd.DataFrame, pair: str, 
                                           timeframe: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process comprehensive analysis with enhanced confluence factors"""
        try:
            # Step 1: Run primary analysis engine
            primary_analysis = await self._run_primary_analysis(df, pair, timeframe)

            # Step 2: Run advanced analysis modules
            advanced_analysis = await self._run_advanced_analysis(df, pair, timeframe)

            # Step 3: Combine all analysis data
            combined_analysis = self._combine_analysis_results(primary_analysis, advanced_analysis)

            # Step 4: Run enhanced confluence analysis
            if self.confluence_enabled and MODULES_AVAILABLE:
                confluence_analysis = await get_enhanced_confluence_analysis(df, combined_analysis)
                combined_analysis['enhanced_confluence_analysis'] = confluence_analysis

                # Update main confidence based on confluence
                self._update_confidence_with_confluence(combined_analysis, confluence_analysis)

            # Step 5: Add final recommendations
            combined_analysis['final_recommendations'] = self._generate_final_recommendations(combined_analysis)
            combined_analysis['analysis_timestamp'] = datetime.now().isoformat()
            combined_analysis['analysis_version'] = '2.0_enhanced'

            return combined_analysis

        except Exception as e:
            print(f"Error in comprehensive analysis: {e}")
            # Return basic analysis fallback
            return await self._run_primary_analysis(df, pair, timeframe)

    async def _run_primary_analysis(self, df: pd.DataFrame, pair: str, timeframe: str) -> Dict[str, Any]:
        """Run primary analysis engine using False Breakout Strategy and ML Ensemble"""
        try:
            # Calculate indicators for primary engine
            indicators = self._calculate_basic_indicators(df)

            # Run False Breakout Strategy as primary analysis
            false_breakout_results = {}
            if self.false_breakout_analyzer:
                false_breakout_results = self.false_breakout_analyzer.analyze_false_breakouts(df)

            # Run ML Ensemble as secondary primary analysis
            ml_results = {}
            if self.ml_ensemble:
                features = self.ml_ensemble.prepare_features(df)
                ensemble_prediction = self.ml_ensemble.predict_ensemble(features)
                ml_results = {
                    'prediction': ensemble_prediction.final_prediction.value,
                    'confidence': ensemble_prediction.ensemble_confidence,
                    'recommended_action': ensemble_prediction.recommended_action,
                    'consensus_level': ensemble_prediction.consensus_level
                }

            # Combine False Breakout and ML analysis for final signal
            combined_signal, combined_confidence = self._combine_primary_signals(
                false_breakout_results, ml_results
            )

            confidence_data = {
                'signal': combined_signal,
                'confidence': combined_confidence,
                'false_breakout_data': false_breakout_results,
                'ml_ensemble_data': ml_results,
                'analysis_method': 'false_breakout_ml_ensemble'
            }

            return {
                'primary_analysis': confidence_data,
                'indicators': indicators,
                'signal': combined_signal,
                'confidence': combined_confidence,
                'pair': pair,
                'timeframe': timeframe
            }

        except Exception as e:
            print(f"Error in primary analysis: {e}")
            return {
                'primary_analysis': {},
                'indicators': {},
                'signal': 'NEUTRAL',
                'confidence': 55.0,
                'pair': pair,
                'timeframe': timeframe
            }

    async def _run_advanced_analysis(self, df: pd.DataFrame, pair: str, timeframe: str) -> Dict[str, Any]:
        """Run all advanced analysis modules"""
        advanced_results = {}

        try:
            # Run analyses in parallel for efficiency
            tasks = []

            if MODULES_AVAILABLE:
                # False Breakout Strategy Analysis
                if self.false_breakout_analyzer:
                    tasks.append(self._run_false_breakout_analysis(df))
                
                # Machine Learning Ensemble Analysis
                if self.ml_ensemble:
                    tasks.append(self._run_ml_ensemble_analysis(df))

                # Liquidity Analysis (preserved as requested)
                tasks.append(self._run_liquidity_analysis(df))

                # Volume Analysis
                tasks.append(self._run_volume_analysis(df))

                # Order Flow Analysis
                tasks.append(self._run_order_flow_analysis(df))

                # Seasonal Analysis
                tasks.append(self._run_seasonal_analysis(pair, df))

                # Breakout Analysis
                tasks.append(self._run_breakout_analysis(df))

                # Microstructure Analysis
                tasks.append(self._run_microstructure_analysis(df))

                # Execute all tasks
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Process results
                    analysis_types = ['false_breakout_analysis', 'ml_ensemble_analysis', 'liquidity_analysis', 'volume_analysis', 
                                    'order_flow', 'seasonal_analysis', 'breakout_analysis', 
                                    'microstructure_analysis']

                    for i, result in enumerate(results):
                        if i < len(analysis_types) and not isinstance(result, Exception):
                            advanced_results[analysis_types[i]] = result

            return advanced_results

        except Exception as e:
            print(f"Error in advanced analysis: {e}")
            return {}

    async def _run_false_breakout_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run False Breakout Strategy analysis"""
        try:
            if self.false_breakout_analyzer:
                return self.false_breakout_analyzer.analyze_false_breakouts(df)
            return {}
        except Exception as e:
            print(f"Error in false breakout analysis: {e}")
            return {}
    
    async def _run_ml_ensemble_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run Machine Learning Ensemble analysis"""
        try:
            if self.ml_ensemble:
                # Prepare features for ML analysis
                features = self.ml_ensemble.prepare_features(df)
                
                # Get ensemble prediction
                ensemble_prediction = self.ml_ensemble.predict_ensemble(features)
                
                return {
                    'prediction': ensemble_prediction.final_prediction.value,
                    'confidence': ensemble_prediction.ensemble_confidence,
                    'recommended_action': ensemble_prediction.recommended_action,
                    'consensus_level': ensemble_prediction.consensus_level,
                    'probability_distribution': ensemble_prediction.probability_distribution,
                    'individual_models': [
                        {
                            'model': pred.model_type.value,
                            'prediction': pred.prediction.value,
                            'confidence': pred.confidence
                        } for pred in ensemble_prediction.individual_predictions
                    ],
                    'features_used': features
                }
            return {}
        except Exception as e:
            print(f"Error in ML ensemble analysis: {e}")
            return {}

    async def _run_liquidity_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run liquidity analysis"""
        try:
            return await get_comprehensive_liquidity_analysis(df)
        except Exception as e:
            print(f"Error in liquidity analysis: {e}")
            return {}

    async def _run_volume_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run volume profile analysis"""
        try:
            return await get_volume_profile_analysis(df)
        except Exception as e:
            print(f"Error in volume analysis: {e}")
            return {}

    async def _run_order_flow_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run order flow analysis"""
        try:
            return await get_imbalance_summary(df)
        except Exception as e:
            print(f"Error in order flow analysis: {e}")
            return {}

    async def _run_seasonal_analysis(self, pair: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Run seasonal pattern analysis"""
        try:
            return await get_comprehensive_seasonal_analysis(pair, df)
        except Exception as e:
            print(f"Error in seasonal analysis: {e}")
            return {}

    async def _run_breakout_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run breakout validation analysis"""
        try:
            return await validate_breakouts(df)
        except Exception as e:
            print(f"Error in breakout analysis: {e}")
            return {}

    async def _run_microstructure_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run market microstructure analysis"""
        try:
            return await get_comprehensive_microstructure_analysis(df)
        except Exception as e:
            print(f"Error in microstructure analysis: {e}")
            return {}

    def _combine_analysis_results(self, primary: Dict[str, Any], advanced: Dict[str, Any]) -> Dict[str, Any]:
        """Combine primary and advanced analysis results"""
        combined = primary.copy()

        # Add advanced analyses
        for key, value in advanced.items():
            combined[key] = value

        # Extract key signals for confluence analysis
        self._extract_confluence_signals(combined)

        return combined

    def _extract_confluence_signals(self, analysis: Dict[str, Any]):
        """Extract signals from various analysis components for confluence"""
        try:
            # Extract False Breakout Strategy signals
            fb_data = analysis.get('false_breakout_analysis', {})
            if fb_data:
                market_bias = fb_data.get('market_bias', {})
                primary_signal = fb_data.get('primary_signal', {})
                
                if primary_signal:
                    analysis['breakout_signal'] = primary_signal.get('direction', 'NEUTRAL')
                    analysis['breakout_confidence'] = primary_signal.get('confidence', 0)
                else:
                    analysis['breakout_signal'] = market_bias.get('direction', 'NEUTRAL')
                    analysis['breakout_confidence'] = market_bias.get('confidence', 50)
            
            # Extract ML Ensemble signals
            ml_data = analysis.get('ml_ensemble_analysis', {})
            if ml_data:
                prediction = ml_data.get('prediction', 'neutral')
                recommended_action = ml_data.get('recommended_action', 'WAIT')
                
                if recommended_action in ['CALL', 'CALL_WEAK']:
                    analysis['ml_signal'] = 'BUY'
                elif recommended_action in ['PUT', 'PUT_WEAK']:
                    analysis['ml_signal'] = 'SELL'
                else:
                    analysis['ml_signal'] = 'NEUTRAL'
                    
                analysis['ml_confidence'] = ml_data.get('confidence', 50)
                analysis['ml_consensus'] = ml_data.get('consensus_level', 0) * 100

            # Extract liquidity signals
            liquidity_data = analysis.get('liquidity_analysis', {})
            if liquidity_data:
                analysis['liquidity_signal'] = liquidity_data.get('signal', 'NEUTRAL')
                analysis['liquidity_confidence'] = liquidity_data.get('confidence', 0)

            # Extract volume signals
            volume_data = analysis.get('volume_analysis', {})
            if volume_data:
                volume_signal = volume_data.get('volume_trend', 'neutral')
                analysis['volume_signal'] = 'BUY' if volume_signal == 'increasing' else 'SELL' if volume_signal == 'decreasing' else 'NEUTRAL'
                analysis['volume_confidence'] = volume_data.get('confidence', 0)

            # Extract order flow signals
            order_flow_data = analysis.get('order_flow', {})
            if order_flow_data:
                flow_type = order_flow_data.get('current_imbalance', {}).get('type', 'balanced')
                if flow_type == 'bid_heavy':
                    analysis['order_flow_signal'] = 'BUY'
                elif flow_type == 'ask_heavy':
                    analysis['order_flow_signal'] = 'SELL'
                else:
                    analysis['order_flow_signal'] = 'NEUTRAL'
                analysis['order_flow_confidence'] = order_flow_data.get('strength', 0) * 100

            # Extract seasonal signals
            seasonal_data = analysis.get('seasonal_analysis', {})
            if seasonal_data:
                combined_bias = seasonal_data.get('combined_bias', {})
                direction = combined_bias.get('direction', 'neutral')
                if direction == 'bullish':
                    analysis['seasonal_signal'] = 'BUY'
                elif direction == 'bearish':
                    analysis['seasonal_signal'] = 'SELL'
                else:
                    analysis['seasonal_signal'] = 'NEUTRAL'
                analysis['seasonal_confidence'] = combined_bias.get('confidence', 0) * 100

        except Exception as e:
            print(f"Error extracting confluence signals: {e}")

    def _update_confidence_with_confluence(self, analysis: Dict[str, Any], confluence: Dict[str, Any]):
        """Update main confidence based on confluence analysis"""
        try:
            confluence_summary = confluence.get('confluence_summary', {})
            confluence_score = confluence.get('confluence_score', 0)

            # Get original confidence
            original_confidence = analysis.get('confidence', 55.0)

            # Calculate confidence adjustment based on confluence
            quality = confluence_summary.get('quality', 'poor')
            quality_multipliers = {'excellent': 1.15, 'good': 1.10, 'fair': 1.05, 'poor': 0.95}
            quality_multiplier = quality_multipliers.get(quality, 1.0)

            # Score-based adjustment
            score_adjustment = (confluence_score - 50) * 0.2  # Max ±10 points

            # Calculate final confidence
            enhanced_confidence = original_confidence * quality_multiplier + score_adjustment
            enhanced_confidence = max(30, min(95, enhanced_confidence))

            # Update analysis
            analysis['original_confidence'] = original_confidence
            analysis['confidence'] = enhanced_confidence
            analysis['confluence_adjustment'] = enhanced_confidence - original_confidence

        except Exception as e:
            print(f"Error updating confidence with confluence: {e}")

    def _generate_final_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final trading recommendations"""
        try:
            signal = analysis.get('signal', 'NEUTRAL')
            confidence = analysis.get('confidence', 55.0)
            confluence_data = analysis.get('enhanced_confluence_analysis', {})

            recommendations = {
                'primary_action': signal,
                'confidence_level': confidence,
                'quality_assessment': 'high' if confidence >= 75 else 'medium' if confidence >= 60 else 'low',
                'risk_level': 'low' if confidence >= 80 else 'medium' if confidence >= 65 else 'high',
                'entry_timing': 'immediate' if confidence >= 80 else 'wait_for_confirmation' if confidence >= 60 else 'avoid',
                'position_sizing': 'standard' if confidence >= 70 else 'reduced' if confidence >= 55 else 'minimal'
            }

            # Add confluence-specific recommendations
            if confluence_data:
                agreement = confluence_data.get('agreement_analysis', {})
                if agreement.get('conflicts', False):
                    recommendations['risk_level'] = 'high'
                    recommendations['position_sizing'] = 'reduced'
                    recommendations['additional_notes'] = f"Conflicting signals detected ({agreement.get('conflict_score', 0)} conflicts)"

                quality = confluence_data.get('confluence_summary', {}).get('quality', 'poor')
                if quality == 'excellent':
                    recommendations['entry_timing'] = 'immediate'
                elif quality == 'poor':
                    recommendations['entry_timing'] = 'wait_for_confirmation'

            return recommendations

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return {
                'primary_action': 'NEUTRAL',
                'confidence_level': 55.0,
                'quality_assessment': 'low',
                'risk_level': 'high',
                'entry_timing': 'avoid',
                'position_sizing': 'minimal'
            }

    def _calculate_basic_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic technical indicators"""
        try:
            if len(df) < 20:
                return {}

            indicators = {}

            # Moving averages
            sma_20_series = df['close'].rolling(20, min_periods=1).mean()
            sma_50_series = df['close'].rolling(50, min_periods=1).mean()
            indicators['sma_20'] = sma_20_series.iloc[-1] if len(sma_20_series) > 0 and not pd.isna(sma_20_series.iloc[-1]) else df['close'].iloc[-1]
            indicators['sma_50'] = sma_50_series.iloc[-1] if len(sma_50_series) > 0 and not pd.isna(sma_50_series.iloc[-1]) else df['close'].iloc[-1]
            
            ema_12_series = df['close'].ewm(span=12, min_periods=1).mean()
            ema_26_series = df['close'].ewm(span=26, min_periods=1).mean()
            indicators['ema_12'] = ema_12_series.iloc[-1] if len(ema_12_series) > 0 and not pd.isna(ema_12_series.iloc[-1]) else df['close'].iloc[-1]
            indicators['ema_26'] = ema_26_series.iloc[-1] if len(ema_26_series) > 0 and not pd.isna(ema_26_series.iloc[-1]) else df['close'].iloc[-1]

            # RSI with safe division
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
            
            # Use safe_divide to prevent division by zero
            from safe_math_utils import safe_divide
            rs = safe_divide(gain.iloc[-1], loss.iloc[-1], 1.0) if len(gain) > 0 and len(loss) > 0 else 1.0
            rsi_value = 100 - (100 / (1 + rs)) if rs is not None and not np.isnan(rs) else 50.0
            indicators['rsi'] = rsi_value

            # MACD
            indicators['macd'] = indicators['ema_12'] - indicators['ema_26']
            indicators['macd_signal'] = df['close'].ewm(span=9).mean().iloc[-1]

            # Current price
            indicators['current_price'] = df['close'].iloc[-1]

            return indicators

        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return {}

    def _fallback_confidence_calculation(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback confidence calculation when primary engine not available"""
        try:
            current_price = indicators.get('current_price', df['close'].iloc[-1])
            sma_20 = indicators.get('sma_20', current_price)
            rsi = indicators.get('rsi', 50)

            # Simple signal determination
            if current_price > sma_20 and rsi < 70:
                signal = 'BUY'
                confidence = 60 + min(10, (current_price - sma_20) / sma_20 * 1000)
            elif current_price < sma_20 and rsi > 30:
                signal = 'SELL'
                confidence = 60 + min(10, (sma_20 - current_price) / sma_20 * 1000)
            else:
                signal = 'NEUTRAL'
                confidence = 55

            return {
                'signal': signal,
                'confidence': confidence,
                'primary_components': [
                    {'name': 'Price vs SMA20', 'signal': signal, 'strength': confidence - 50},
                    {'name': 'RSI', 'signal': signal, 'strength': min(50, abs(rsi - 50))}
                ]
            }

        except Exception as e:
            print(f"Error in fallback calculation: {e}")
            return {'signal': 'NEUTRAL', 'confidence': 55.0}

    def _combine_primary_signals(self, false_breakout_results: Dict[str, Any], 
                                ml_results: Dict[str, Any]) -> Tuple[str, float]:
        """Combine False Breakout Strategy and ML Ensemble signals for primary analysis"""
        try:
            # Extract False Breakout signal
            fb_signal = 'NEUTRAL'
            fb_confidence = 50.0
            
            if false_breakout_results:
                market_bias = false_breakout_results.get('market_bias', {})
                primary_signal = false_breakout_results.get('primary_signal', {})
                
                if primary_signal and primary_signal.get('confidence', 0) > 70:
                    # Use primary signal if high confidence
                    fb_signal = primary_signal.get('direction', 'NEUTRAL')
                    fb_confidence = primary_signal.get('confidence', 50)
                elif market_bias:
                    # Use market bias as backup
                    fb_signal = market_bias.get('direction', 'NEUTRAL')
                    fb_confidence = market_bias.get('confidence', 50)
            
            # Extract ML Ensemble signal
            ml_signal = 'NEUTRAL'
            ml_confidence = 50.0
            
            if ml_results:
                recommended_action = ml_results.get('recommended_action', 'WAIT')
                ml_confidence = ml_results.get('confidence', 50)
                consensus = ml_results.get('consensus_level', 0)
                
                # Convert ML recommendation to trading signal
                if recommended_action in ['CALL', 'CALL_WEAK']:
                    ml_signal = 'BUY'
                elif recommended_action in ['PUT', 'PUT_WEAK']:
                    ml_signal = 'SELL'
                else:
                    ml_signal = 'NEUTRAL'
                
                # Adjust confidence based on consensus
                ml_confidence = ml_confidence * (0.7 + 0.3 * consensus)
            
            # Combine signals with weighted approach
            # False Breakout Strategy gets 60% weight (higher accuracy)
            # ML Ensemble gets 40% weight
            fb_weight = 0.6
            ml_weight = 0.4
            
            # Calculate signal agreement
            signals_agree = (fb_signal == ml_signal)
            
            if signals_agree and fb_signal != 'NEUTRAL':
                # Strong agreement - use the signal with boosted confidence
                combined_signal = fb_signal
                combined_confidence = min(95, fb_confidence * fb_weight + ml_confidence * ml_weight + 10)
                
            elif fb_confidence > ml_confidence + 15:
                # False Breakout much more confident
                combined_signal = fb_signal
                combined_confidence = min(90, fb_confidence * 0.9)
                
            elif ml_confidence > fb_confidence + 15:
                # ML Ensemble much more confident
                combined_signal = ml_signal
                combined_confidence = min(90, ml_confidence * 0.9)
                
            elif fb_signal != 'NEUTRAL' and ml_signal == 'NEUTRAL':
                # Only False Breakout has signal
                combined_signal = fb_signal
                combined_confidence = fb_confidence * 0.85
                
            elif ml_signal != 'NEUTRAL' and fb_signal == 'NEUTRAL':
                # Only ML has signal
                combined_signal = ml_signal
                combined_confidence = ml_confidence * 0.85
                
            else:
                # Conflicting signals or both neutral
                if fb_confidence > ml_confidence:
                    combined_signal = fb_signal
                    combined_confidence = max(45, fb_confidence * 0.7)  # Reduce confidence due to conflict
                else:
                    combined_signal = ml_signal
                    combined_confidence = max(45, ml_confidence * 0.7)
            
            # Ensure minimum confidence for non-neutral signals
            if combined_signal != 'NEUTRAL' and combined_confidence < 55:
                combined_confidence = 55
            
            # Ensure reasonable bounds
            combined_confidence = max(35, min(95, combined_confidence))
            
            return combined_signal, combined_confidence
            
        except Exception as e:
            print(f"Error combining primary signals: {e}")
            return 'NEUTRAL', 50.0

# Global instance
integrated_engine = IntegratedAnalysisEngine()

# Export functions for easy integration
async def get_integrated_analysis(df: pd.DataFrame, pair: str, timeframe: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get comprehensive integrated analysis with enhanced confluence"""
    return await integrated_engine.process_comprehensive_analysis(df, pair, timeframe, user_id)

def set_confluence_enabled(enabled: bool):
    """Enable or disable confluence analysis"""
    integrated_engine.confluence_enabled = enabled

def get_analysis_capabilities() -> Dict[str, bool]:
    """Get current analysis capabilities"""
    return {
        'modules_available': MODULES_AVAILABLE,
        'confluence_enabled': integrated_engine.confluence_enabled,
        'false_breakout_analyzer': integrated_engine.false_breakout_analyzer is not None,
        'ml_ensemble': integrated_engine.ml_ensemble is not None,
        'liquidity_analysis': True  # Preserved as requested
    }