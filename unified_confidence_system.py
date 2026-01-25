#!/usr/bin/env python3
"""
Unified Confidence System - Combines streamlined speed with comprehensive analysis
Replaces both unified_confidence_system.py and hierarchical calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from safe_math_utils import safe_mean, safe_std, safe_divide

# ML predictor completely removed as requested
ML_PREDICTOR_AVAILABLE = False

# Import statistical robustness system
try:
    from statistical_robustness_system import validate_signal_robustness
    ROBUSTNESS_VALIDATION_AVAILABLE = True
except ImportError:
    ROBUSTNESS_VALIDATION_AVAILABLE = False

class UnifiedConfidenceEngine:
    """Unified confidence calculation combining speed and comprehensive analysis"""
    
    def __init__(self):
        # Primary signal weights (drive the main decision) - 70% total
        self.primary_weights = {
            'ict_smc': 25,           # 25% - Enhanced FVG-focused ICT/SMC
            'moving_averages': 12,   # 12% - Reduced, trend-focused only
            'order_flow': 18,        # 18% - Increased importance
            'volume_analysis': 15    # 15% - Increased importance
        }
        
        # Advanced analysis weights (enhance confidence when aligned) - 30% total
        # Removed: liquidity_zones, seasonal_patterns (as requested)
        self.enhancement_weights = {
            'snr_analysis': 12,      # 12% - Increased to compensate
            'donchian_channels': 8,  # 8% - Increased
            'market_structure': 8,   # 8% - Increased
            'confluence_factors': 2  # 2% - Reduced
        }
        
        # Cross-timeframe validation - Total system = 100%
        self.cross_timeframe_weight = 0.08  # 8% adjustment
        
    async def calculate_unified_confidence(self, df: pd.DataFrame, indicators: dict, 
                                         pair: str, expiry: str, mode: str = "unified") -> dict:
        """
        Unified confidence calculation - comprehensive analysis for both signals and recommendations
        """
        try:
            if df is None or len(df) < 20 or indicators is None:
                return self._empty_confidence_result()
            
            # Step 1: Calculate Primary Signals (always computed)
            primary_results = self._calculate_primary_signals(df, indicators, pair, expiry)
            
            # Step 2: Calculate Enhancement Signals (always computed for comprehensive analysis)
            enhancement_results = await self._calculate_enhancement_signals(df, indicators, pair, expiry)
            
            # Step 3: Calculate Final Unified Confidence (ML removed)
            final_confidence = self._calculate_final_confidence(
                primary_results, enhancement_results, {}, mode
            )
            
            # Step 5: Statistical Robustness Validation (for improved win rate)
            robustness_results = {}
            if ROBUSTNESS_VALIDATION_AVAILABLE:
                signal_data = {
                    'signal': final_confidence['signal'],
                    'confidence': final_confidence['confidence'],
                    'pair': pair,
                    'expiry': expiry
                }
                robustness_results = await validate_signal_robustness(signal_data, df)
                
                # Apply robustness confidence adjustment
                if robustness_results.get('robustness_validated', False):
                    confidence_adjustment = robustness_results.get('confidence_adjustment', 0)
                    final_confidence['confidence'] = min(
                        final_confidence['confidence'] + confidence_adjustment, 95
                    )
                    final_confidence['robustness_applied'] = True
                    final_confidence['robustness_adjustment'] = confidence_adjustment
            
            # Step 6: Generate Detailed Confluence Analysis
            confluence_analysis = self._generate_confluence_analysis(
                primary_results, enhancement_results, {}
            )
            
            return {
                'signal': final_confidence['signal'],
                'confidence': final_confidence['confidence'],
                'primary_analysis': primary_results,
                'enhancement_analysis': enhancement_results,
                'ml_analysis': {},
                'robustness_analysis': robustness_results,
                'confluence_analysis': confluence_analysis,
                'calculation_mode': 'unified',
                'factors_summary': confluence_analysis['factors_summary'],
                'agreement_stats': confluence_analysis['agreement_stats'],
                'breakdown': final_confidence['breakdown'],
                'robustness_applied': final_confidence.get('robustness_applied', False),
                'robustness_adjustment': final_confidence.get('robustness_adjustment', 0.0)
            }
            
        except Exception as e:
            print(f"Error in unified confidence calculation: {e}")
            return self._empty_confidence_result()
    
    def _calculate_primary_signals(self, df: pd.DataFrame, indicators: dict, 
                                 pair: str, expiry: str) -> dict:
        """Calculate core primary signals for speed"""
        primary_signals = {}
        
        # ICT/SMC Analysis (30%)
        primary_signals['ict_smc'] = self._analyze_ict_quick(df, indicators)
        
        # Moving Average Trend (25%)
        primary_signals['moving_averages'] = self._analyze_ma_trend_quick(df, indicators)
        
        # Order Flow (25%)
        primary_signals['order_flow'] = self._analyze_order_flow_quick(df)
        
        # Volume Analysis (20%)
        primary_signals['volume_analysis'] = self._analyze_volume_quick(df)
        
        # Calculate primary consensus
        consensus = self._calculate_primary_consensus(primary_signals)
        
        return {
            'signals': primary_signals,
            'consensus': consensus,
            'primary_signal': consensus['signal'],
            'primary_strength': consensus['strength'],
            'primary_confidence': consensus['confidence']
        }
    
    async def _calculate_enhancement_signals(self, df: pd.DataFrame, indicators: dict, 
                                           pair: str, expiry: str) -> dict:
        """Calculate enhancement signals for comprehensive analysis"""
        enhancement_signals = {}
        
        try:
            # SNR Analysis
            enhancement_signals['snr_analysis'] = self._analyze_snr_levels(df, indicators)
            
            # Donchian Channels
            enhancement_signals['donchian_channels'] = self._analyze_donchian_channels(df, indicators)
            
            # Market Structure
            enhancement_signals['market_structure'] = self._analyze_market_structure(df, indicators)
            
            # Removed: Liquidity Zones and Seasonal Patterns (as requested by user)
            
            # Enhanced Confluence Factors
            try:
                # Legacy confluence - now using unified system
                # Import and use confluence analysis safely
                try:
                    from enhanced_confluence_analyzer import analyze_confluence_factors
                    confluence_data = analyze_confluence_factors(df, indicators, pair)
                except Exception:
                    confluence_data = {'signal': 'NEUTRAL', 'strength': 50, 'factors': []}
                enhancement_signals['confluence_factors'] = self._analyze_confluence_impact(confluence_data)
            except ImportError:
                enhancement_signals['confluence_factors'] = {'signal': 'NEUTRAL', 'strength': 50}
            
        except Exception as e:
            print(f"Error in enhancement signals: {e}")
        
        return enhancement_signals
    
    # ML predictor completely removed as requested
    
    def _calculate_final_confidence(self, primary_results: dict, enhancement_results: dict, 
                                  ml_results: dict, mode: str) -> dict:
        """Calculate final unified confidence score"""
        try:
            # Base confidence from primary signals
            base_signal = primary_results['primary_signal']
            base_confidence = primary_results['primary_confidence']
            
            # Start with primary signal strength
            final_confidence = base_confidence
            confidence_adjustments = {}
            
            # Apply enhancements if available
            if enhancement_results:
                enhancement_adjustment = self._calculate_enhancement_bonus(
                    enhancement_results, base_signal
                )
                final_confidence += enhancement_adjustment
                confidence_adjustments['enhancement_bonus'] = enhancement_adjustment
            
            # ML adjustment removed as requested
            
            # Apply unified confidence cap (92% as per latest specifications)
            final_confidence = min(final_confidence, 92)
            
            # Ensure minimum confidence
            final_confidence = max(final_confidence, 45)
            
            return {
                'signal': base_signal,
                'confidence': final_confidence,
                'breakdown': {
                    'base_confidence': base_confidence,
                    'adjustments': confidence_adjustments,
                    'mode': 'unified',
                    'final_confidence': final_confidence
                }
            }
            
        except Exception as e:
            print(f"Error calculating final confidence: {e}")
            return {'signal': 'NEUTRAL', 'confidence': 50, 'breakdown': {}}
    
    def _generate_confluence_analysis(self, primary_results: dict, enhancement_results: dict, 
                                    ml_results: dict) -> dict:
        """Generate detailed confluence analysis for display"""
        try:
            factors = []
            agreement_count = 0
            disagreement_count = 0
            neutral_count = 0
            
            primary_signal = primary_results.get('primary_signal', 'NEUTRAL')
            
            # Analyze primary factors
            for factor_name, factor_data in primary_results.get('signals', {}).items():
                factor_signal = factor_data.get('signal', 'NEUTRAL')
                factor_strength = factor_data.get('strength', 50)
                
                # Determine agreement
                if factor_signal == primary_signal and factor_signal != 'NEUTRAL':
                    agreement = 'agree'
                    agreement_count += 1
                elif factor_signal != 'NEUTRAL' and factor_signal != primary_signal:
                    agreement = 'disagree'
                    disagreement_count += 1
                else:
                    agreement = 'neutral'
                    neutral_count += 1
                
                factors.append({
                    'name': factor_name.replace('_', ' ').title(),
                    'signal': factor_signal,
                    'strength': factor_strength,
                    'agreement': agreement,
                    'category': 'primary'
                })
            
            # Analyze enhancement factors
            for factor_name, factor_data in enhancement_results.items():
                if isinstance(factor_data, dict):
                    factor_signal = factor_data.get('signal', 'NEUTRAL')
                    factor_strength = factor_data.get('strength', 50)
                    
                    # Determine agreement
                    if factor_signal == primary_signal and factor_signal != 'NEUTRAL':
                        agreement = 'agree'
                        agreement_count += 1
                    elif factor_signal != 'NEUTRAL' and factor_signal != primary_signal:
                        agreement = 'disagree'
                        disagreement_count += 1
                    else:
                        agreement = 'neutral'
                        neutral_count += 1
                    
                    factors.append({
                        'name': factor_name.replace('_', ' ').title(),
                        'signal': factor_signal,
                        'strength': factor_strength,
                        'agreement': agreement,
                        'category': 'enhancement'
                    })
            
            # ML analysis removed - system now relies on technical analysis only
            ml_opinion = "N/A (Disabled)"
            
            # Calculate agreement statistics
            total_factors = agreement_count + disagreement_count + neutral_count
            
            factors_summary = f"{agreement_count}🟢 | {disagreement_count}🔴 | {neutral_count}⚪"
            
            agreement_stats = {
                'total_factors': total_factors,
                'agreement_count': agreement_count,
                'disagreement_count': disagreement_count,
                'neutral_count': neutral_count,
                'agreement_percentage': (agreement_count / total_factors * 100) if total_factors > 0 else 0,
                'ml_opinion': ml_opinion
            }
            
            return {
                'factors': factors,
                'factors_summary': factors_summary,
                'agreement_stats': agreement_stats,
                'quality': self._assess_confluence_quality(agreement_stats)
            }
            
        except Exception as e:
            print(f"Error generating confluence analysis: {e}")
            return {
                'factors': [],
                'factors_summary': "0🟢 | 0🔴 | 0⚪",
                'agreement_stats': {'ml_opinion': 'N/A'},
                'quality': 'unknown'
            }
    
    def _assess_confluence_quality(self, stats: dict) -> str:
        """Assess overall confluence quality"""
        agreement_pct = stats.get('agreement_percentage', 0)
        disagreement_count = stats.get('disagreement_count', 0)
        
        if agreement_pct >= 70 and disagreement_count <= 1:
            return 'strong'
        elif agreement_pct >= 50 and disagreement_count <= 2:
            return 'moderate'
        elif disagreement_count >= 3:
            return 'conflicted'
        else:
            return 'weak'
    
    # Quick analysis methods for speed
    def _analyze_ict_quick(self, df: pd.DataFrame, indicators: dict) -> dict:
        """Quick ICT/SMC analysis"""
        try:
            closes = df['close'].values
            highs = df['high'].values
            lows = df['low'].values
            
            if len(closes) < 10:
                return {'signal': 'NEUTRAL', 'strength': 50}
            
            # Simple order block detection
            recent_high = safe_mean(highs[-5:])
            recent_low = safe_mean(lows[-5:])
            current_price = closes[-1]
            
            # Fair value gap detection (simplified)
            fvg_signal = 0
            if len(closes) >= 3:
                for i in range(max(0, len(closes) - 20), len(closes) - 2):
                    if i + 2 < len(closes):
                        if lows[i] > highs[i+2]:  # Bullish FVG
                            fvg_signal += 1
                        elif highs[i] < lows[i+2]:  # Bearish FVG
                            fvg_signal -= 1
            
            # Determine signal
            if fvg_signal > 2:
                return {'signal': 'BUY', 'strength': min(80, 60 + fvg_signal * 5)}
            elif fvg_signal < -2:
                return {'signal': 'SELL', 'strength': min(80, 60 + abs(fvg_signal) * 5)}
            else:
                return {'signal': 'NEUTRAL', 'strength': 50}
                
        except Exception as e:
            return {'signal': 'NEUTRAL', 'strength': 50}
    
    def _analyze_ma_trend_quick(self, df: pd.DataFrame, indicators: dict) -> dict:
        """Quick moving average trend analysis"""
        try:
            if 'sma_50' not in indicators or 'ema_21' not in indicators:
                return {'signal': 'NEUTRAL', 'strength': 50}
            
            current_price = df['close'].iloc[-1]
            sma_50 = indicators['sma_50'].iloc[-1]
            ema_21 = indicators['ema_21'].iloc[-1]
            
            # Price above/below MAs
            above_sma = current_price > sma_50
            above_ema = current_price > ema_21
            ema_above_sma = ema_21 > sma_50
            
            # Calculate strength based on alignment
            if above_sma and above_ema and ema_above_sma:
                return {'signal': 'BUY', 'strength': 75}
            elif not above_sma and not above_ema and not ema_above_sma:
                return {'signal': 'SELL', 'strength': 75}
            elif above_ema and ema_above_sma:
                return {'signal': 'BUY', 'strength': 65}
            elif not above_ema and not ema_above_sma:
                return {'signal': 'SELL', 'strength': 65}
            else:
                return {'signal': 'NEUTRAL', 'strength': 50}
                
        except Exception as e:
            return {'signal': 'NEUTRAL', 'strength': 50}
    
    def _analyze_order_flow_quick(self, df: pd.DataFrame) -> dict:
        """Quick order flow analysis"""
        try:
            if len(df) < 10:
                return {'signal': 'NEUTRAL', 'strength': 50}
            
            # Simple order flow proxy using price action
            closes = df['close'].values
            highs = df['high'].values
            lows = df['low'].values
            
            # Calculate buying/selling pressure
            buying_pressure = 0
            selling_pressure = 0
            
            for i in range(max(0, len(closes) - 10), len(closes)):
                body = abs(closes[i] - df['open'].iloc[i]) if i < len(df) else 0
                upper_wick = highs[i] - max(closes[i], df['open'].iloc[i]) if i < len(df) else 0
                lower_wick = min(closes[i], df['open'].iloc[i]) - lows[i] if i < len(df) else 0
                
                if closes[i] > df['open'].iloc[i]:  # Bullish candle
                    buying_pressure += body + (lower_wick * 0.5)
                else:  # Bearish candle
                    selling_pressure += body + (upper_wick * 0.5)
            
            total_pressure = buying_pressure + selling_pressure
            if total_pressure == 0:
                return {'signal': 'NEUTRAL', 'strength': 50}
            
            buy_ratio = buying_pressure / total_pressure
            
            if buy_ratio > 0.65:
                return {'signal': 'BUY', 'strength': min(80, 50 + buy_ratio * 40)}
            elif buy_ratio < 0.35:
                return {'signal': 'SELL', 'strength': min(80, 50 + (1 - buy_ratio) * 40)}
            else:
                return {'signal': 'NEUTRAL', 'strength': 50}
                
        except Exception as e:
            return {'signal': 'NEUTRAL', 'strength': 50}
    
    def _analyze_volume_quick(self, df: pd.DataFrame) -> dict:
        """Quick volume analysis"""
        try:
            if len(df) < 10:
                return {'signal': 'NEUTRAL', 'strength': 50}
            
            # Volume proxy using price ranges
            ranges = df['high'] - df['low']
            bodies = abs(df['close'] - df['open'])
            
            # Recent volume proxy
            recent_volume = safe_mean(ranges.tail(5)) + safe_mean(bodies.tail(5))
            avg_volume = safe_mean(ranges.tail(20)) + safe_mean(bodies.tail(20))
            
            volume_ratio = safe_divide(recent_volume, avg_volume, 1.0)
            
            # Price direction with volume
            recent_close_change = df['close'].iloc[-1] - df['close'].iloc[-5]
            
            if volume_ratio > 1.5 and recent_close_change > 0:
                return {'signal': 'BUY', 'strength': min(75, 50 + volume_ratio * 15)}
            elif volume_ratio > 1.5 and recent_close_change < 0:
                return {'signal': 'SELL', 'strength': min(75, 50 + volume_ratio * 15)}
            else:
                return {'signal': 'NEUTRAL', 'strength': 50}
                
        except Exception as e:
            return {'signal': 'NEUTRAL', 'strength': 50}
    
    def _calculate_primary_consensus(self, primary_signals: dict) -> dict:
        """Calculate consensus from primary signals"""
        try:
            buy_weight = 0
            sell_weight = 0
            total_weight = 0
            
            for signal_name, signal_data in primary_signals.items():
                weight = self.primary_weights.get(signal_name, 0)
                strength = signal_data.get('strength', 50) / 100
                
                if signal_data.get('signal') == 'BUY':
                    buy_weight += weight * strength
                elif signal_data.get('signal') == 'SELL':
                    sell_weight += weight * strength
                
                total_weight += weight
            
            if total_weight == 0:
                return {'signal': 'NEUTRAL', 'strength': 50, 'confidence': 50}
            
            # Determine final signal and confidence (95% system potential)
            if buy_weight > sell_weight:
                signal = 'BUY'
                confidence = min(95, 55 + (buy_weight / total_weight * 95) * 0.42)
                strength = (buy_weight / total_weight) * 95
            elif sell_weight > buy_weight:
                signal = 'SELL'
                confidence = min(95, 55 + (sell_weight / total_weight * 95) * 0.42)
                strength = (sell_weight / total_weight) * 95
            else:
                signal = 'NEUTRAL'
                confidence = 50
                strength = 50
            
            return {
                'signal': signal,
                'strength': strength,
                'confidence': confidence,
                'buy_weight': buy_weight,
                'sell_weight': sell_weight
            }
            
        except Exception as e:
            return {'signal': 'NEUTRAL', 'strength': 50, 'confidence': 50}
    
    def _calculate_enhancement_bonus(self, enhancement_results: dict, base_signal: str) -> float:
        """Calculate bonus from enhancement signals when aligned"""
        try:
            bonus = 0
            
            for signal_name, signal_data in enhancement_results.items():
                if isinstance(signal_data, dict) and signal_data.get('signal') == base_signal:
                    weight = self.enhancement_weights.get(signal_name, 0)
                    strength = signal_data.get('strength', 50) / 100
                    bonus += weight * strength * 0.1  # Scale down enhancement impact
            
            return min(bonus, 15)  # Cap enhancement bonus at 15% (95% system)
            
        except Exception as e:
            return 0
    
    def _calculate_ml_adjustment(self, ml_results: dict, base_signal: str) -> float:
        """ML prediction adjustment disabled - returns 0"""
        return 0.0
    
    def _empty_confidence_result(self) -> dict:
        """Return empty confidence result"""
        return {
            'signal': 'NEUTRAL',
            'confidence': 50.0,
            'primary_analysis': {},
            'enhancement_analysis': {},
            'ml_analysis': {'available': False},
            'confluence_analysis': {
                'factors_summary': "0🟢 | 0🔴 | 0⚪",
                'agreement_stats': {'ml_opinion': 'N/A'}
            },
            'calculation_mode': 'error'
        }
    
    # Placeholder methods for enhancement signals (implement as needed)
    def _analyze_snr_levels(self, df: pd.DataFrame, indicators: dict) -> dict:
        """Analyze support/resistance levels"""
        return {'signal': 'NEUTRAL', 'strength': 50}
    
    def _analyze_donchian_channels(self, df: pd.DataFrame, indicators: dict) -> dict:
        """Analyze Donchian channel breakouts"""
        return {'signal': 'NEUTRAL', 'strength': 50}
    
    def _analyze_market_structure(self, df: pd.DataFrame, indicators: dict) -> dict:
        """Analyze market structure"""
        return {'signal': 'NEUTRAL', 'strength': 50}
    
    def _analyze_liquidity_impact(self, liquidity_zones: List, df: pd.DataFrame) -> dict:
        """Analyze liquidity zones impact"""
        return {'signal': 'NEUTRAL', 'strength': 50}
    
    def _analyze_seasonal_impact(self, seasonal_data: dict) -> dict:
        """Analyze seasonal patterns impact"""
        return {'signal': 'NEUTRAL', 'strength': 50}
    
    def _analyze_confluence_impact(self, confluence_data: dict) -> dict:
        """Analyze confluence factors impact"""
        return {'signal': 'NEUTRAL', 'strength': 50}
    
    def _prepare_ml_features(self, df: pd.DataFrame, indicators: dict) -> dict:
        """Prepare features for ML model"""
        return {}

# Global instance
unified_engine = UnifiedConfidenceEngine()

# Public API functions - Unified system for both signals and recommendations
async def calculate_unified_confidence(df: pd.DataFrame, indicators: dict, 
                                     pair: str, expiry: str, mode: str = "unified") -> dict:
    """Unified confidence calculation - same comprehensive analysis for both signals and recommendations"""
    return await unified_engine.calculate_unified_confidence(df, indicators, pair, expiry, mode)

async def get_signal_confidence(df: pd.DataFrame, indicators: dict, 
                              pair: str, expiry: str = "5m") -> dict:
    """Signal confidence calculation - uses unified comprehensive analysis"""
    return await calculate_unified_confidence(df, indicators, pair, expiry, "unified")

async def get_recommendation_confidence(df: pd.DataFrame, indicators: dict, 
                                      pair: str, expiry: str = "5m") -> dict:
    """Recommendation confidence calculation - uses unified comprehensive analysis"""
    return await calculate_unified_confidence(df, indicators, pair, expiry, "unified")