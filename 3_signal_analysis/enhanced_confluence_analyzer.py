"""Fixing errors related to RSI calculation, list concatenation in comprehensive analysis, and trade manager session statistics."""
"""
Enhanced Confluence Analyzer for Trading Bot
Comprehensive confluence factor analysis with agreement/conflict detection
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from safe_math_utils import safe_mean, safe_std, safe_divide

class ConfluenceDirection(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

class ConfluenceStrength(Enum):
    VERY_STRONG = "very_strong"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"

@dataclass
class ConfluenceFactor:
    name: str
    direction: ConfluenceDirection
    strength: ConfluenceStrength
    confidence: float
    weight: float
    description: str
    details: Dict[str, Any]

class EnhancedConfluenceAnalyzer:
    """Advanced confluence analysis with comprehensive factor detection"""

    def __init__(self):
        self.factor_weights = {
            'ict_smc': 25,
            'liquidity_zones': 20,
            'institutional_flow': 20,
            'fractal_compression': 18,
            'order_flow_imbalance': 15,
            'volume_profile': 12,
            'market_structure': 15,
            'snr_levels': 10,
            'seasonal_patterns': 8,
            'breakout_validation': 12,
            'momentum_divergence': 10,
            'volatility_expansion': 8,
            'session_bias': 6,
            'economic_calendar': 5
        }

    def analyze_confluence_factors(self, df: pd.DataFrame, 
                                 analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze all confluence factors and determine agreement/conflicts"""
        try:
            confluence_factors = []

            # 1. ICT/SMC Analysis
            ict_factor = self._analyze_ict_smc_confluence(df, analysis_data)
            if ict_factor:
                confluence_factors.append(ict_factor)

            # 2. Liquidity Zones
            liquidity_factor = self._analyze_liquidity_confluence(df, analysis_data)
            if liquidity_factor:
                confluence_factors.append(liquidity_factor)

            # 3. Institutional Flow Detection
            institutional_factor = self._analyze_institutional_flow_confluence(df, analysis_data)
            if institutional_factor:
                confluence_factors.append(institutional_factor)

            # 4. Fractal Compression Zones
            fractal_factor = self._analyze_fractal_compression_confluence(df, analysis_data)
            if fractal_factor:
                confluence_factors.append(fractal_factor)

            # 5. Order Flow Imbalance
            order_flow_factor = self._analyze_order_flow_confluence(df, analysis_data)
            if order_flow_factor:
                confluence_factors.append(order_flow_factor)

            # 6. Volume Profile Analysis
            volume_factor = self._analyze_volume_profile_confluence(df, analysis_data)
            if volume_factor:
                confluence_factors.append(volume_factor)

            # 7. Market Structure
            structure_factor = self._analyze_market_structure_confluence(df, analysis_data)
            if structure_factor:
                confluence_factors.append(structure_factor)

            # 8. Support/Resistance Levels
            snr_factor = self._analyze_snr_confluence(df, analysis_data)
            if snr_factor:
                confluence_factors.append(snr_factor)

            # 9. Seasonal Patterns
            seasonal_factor = self._analyze_seasonal_confluence(df, analysis_data)
            if seasonal_factor:
                confluence_factors.append(seasonal_factor)

            # 10. Breakout Validation
            breakout_factor = self._analyze_breakout_confluence(df, analysis_data)
            if breakout_factor:
                confluence_factors.append(breakout_factor)

            # 11. Momentum Divergence
            momentum_factor = self._analyze_momentum_divergence_confluence(df, analysis_data)
            if momentum_factor:
                confluence_factors.append(momentum_factor)

            # 12. Volatility Expansion
            volatility_factor = self._analyze_volatility_expansion_confluence(df, analysis_data)
            if volatility_factor:
                confluence_factors.append(volatility_factor)

            # 13. Session Bias
            session_factor = self._analyze_session_bias_confluence(df, analysis_data)
            if session_factor:
                confluence_factors.append(session_factor)

            # 14. Economic Calendar Impact
            calendar_factor = self._analyze_calendar_confluence(df, analysis_data)
            if calendar_factor:
                confluence_factors.append(calendar_factor)

            # Calculate agreement and conflicts
            agreement_analysis = self._calculate_agreement_conflicts(confluence_factors)

            # Generate confluence summary
            confluence_summary = self._generate_confluence_summary(confluence_factors, agreement_analysis)

            return {
                'confluence_factors': confluence_factors,
                'agreement_analysis': agreement_analysis,
                'confluence_summary': confluence_summary,
                'total_factors': len(confluence_factors),
                'strong_factors': len([f for f in confluence_factors if f.strength in [ConfluenceStrength.STRONG, ConfluenceStrength.VERY_STRONG]]),
                'confluence_score': self._calculate_total_confluence_score(confluence_factors, agreement_analysis)
            }

        except Exception as e:
            print(f"Error in confluence analysis: {e}")
            return self._empty_confluence_analysis()

    def analyze_comprehensive_confluence(self, df: pd.DataFrame, 
                                       analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Backward compatibility method - calls analyze_confluence_factors"""
        return self.analyze_confluence_factors(df, analysis_data)

    def _analyze_ict_smc_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze ICT/SMC confluence factors"""
        try:
            ict_data = analysis_data.get('ict_analysis', {})
            if not ict_data:
                # Try to derive from other analysis data
                indicators = analysis_data.get('indicators', {})
                if indicators:
                    ict_data = self._derive_ict_data(df, indicators)
                else:
                    return None

            signal = ict_data.get('signal', 'NEUTRAL')
            confidence = ict_data.get('confidence', 0)

            direction = ConfluenceDirection.BULLISH if signal == 'BUY' else ConfluenceDirection.BEARISH if signal == 'SELL' else ConfluenceDirection.NEUTRAL
            strength = self._confidence_to_strength(confidence)

            details = {
                'order_blocks': ict_data.get('order_blocks', {}),
                'fair_value_gaps': ict_data.get('fair_value_gaps', {}),
                'liquidity_sweeps': ict_data.get('liquidity_sweeps', {}),
                'market_structure': ict_data.get('market_structure', {})
            }

            description = f"ICT/SMC {signal} ({confidence:.0f}%)"
            if details['order_blocks']:
                description += f" | OB: {details['order_blocks'].get('type', 'N/A')}"
            if details['fair_value_gaps']:
                description += f" | FVG: {details['fair_value_gaps'].get('type', 'N/A')}"

            return ConfluenceFactor(
                name="ICT/SMC Analysis",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['ict_smc'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing ICT/SMC confluence: {e}")
            return None

    def _analyze_liquidity_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze liquidity zone confluence"""
        try:
            liquidity_data = analysis_data.get('liquidity_analysis', {})
            if not liquidity_data:
                return None

            signal = liquidity_data.get('signal', 'NEUTRAL')
            confidence = liquidity_data.get('confidence', 0)

            direction = ConfluenceDirection.BULLISH if signal == 'BUY' else ConfluenceDirection.BEARISH if signal == 'SELL' else ConfluenceDirection.NEUTRAL
            strength = self._confidence_to_strength(confidence)

            zones = liquidity_data.get('zones', [])
            sweeps = liquidity_data.get('sweeps', [])

            details = {
                'zones_count': len(zones),
                'recent_sweeps': len(sweeps),
                'zones': zones[:3],  # Top 3 zones
                'sweep_direction': sweeps[-1].get('direction') if sweeps else None
            }

            description = f"Liquidity {signal} ({confidence:.0f}%)"
            if details['zones_count']:
                description += f" | {details['zones_count']} zones"
            if details['recent_sweeps']:
                description += f" | {details['recent_sweeps']} sweeps"

            return ConfluenceFactor(
                name="Liquidity Zones",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['liquidity_zones'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing liquidity confluence: {e}")
            return None

    def _analyze_institutional_flow_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze institutional flow confluence"""
        try:
            # Check multiple sources for institutional flow data
            institutional_data = (analysis_data.get('institutional_flow', {}) or 
                                analysis_data.get('smart_money_flow', {}) or
                                analysis_data.get('volume_analysis', {}).get('institutional_signature', {}))

            if not institutional_data:
                # Derive from volume and order flow analysis
                volume_data = analysis_data.get('volume_analysis', {})
                order_flow_data = analysis_data.get('order_flow', {})

                if volume_data or order_flow_data:
                    institutional_data = self._derive_institutional_flow(df, volume_data, order_flow_data)
                else:
                    return None

            signal = institutional_data.get('signal', 'NEUTRAL')
            confidence = institutional_data.get('confidence', 0)
            flow_strength = institutional_data.get('flow_strength', 0)

            direction = ConfluenceDirection.BULLISH if signal == 'BUY' else ConfluenceDirection.BEARISH if signal == 'SELL' else ConfluenceDirection.NEUTRAL
            strength = self._confidence_to_strength(confidence)

            details = {
                'flow_strength': flow_strength,
                'accumulation_score': institutional_data.get('accumulation_score', 0),
                'distribution_score': institutional_data.get('distribution_score', 0),
                'large_orders_detected': institutional_data.get('large_orders', False),
                'smart_money_index': institutional_data.get('smart_money_index', 0)
            }

            description = f"Institutional {signal} ({confidence:.0f}%)"
            if details['smart_money_index'] > 0.7:
                description += " | Strong SMI"
            elif details['large_orders_detected']:
                description += " | Large orders"

            return ConfluenceFactor(
                name="Institutional Flow",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['institutional_flow'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing institutional flow confluence: {e}")
            return None

    def _analyze_fractal_compression_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze fractal compression zones"""
        try:
            # Look for fractal compression in various analysis components
            fractal_data = analysis_data.get('fractal_zones', {})

            if not fractal_data:
                # Derive fractal compression from price action
                fractal_data = self._detect_fractal_compression(df)

            if not fractal_data:
                return None

            signal = fractal_data.get('signal', 'NEUTRAL')
            confidence = fractal_data.get('confidence', 0)
            compression_strength = fractal_data.get('compression_strength', 0)

            direction = ConfluenceDirection.BULLISH if signal == 'BUY' else ConfluenceDirection.BEARISH if signal == 'SELL' else ConfluenceDirection.NEUTRAL
            strength = self._confidence_to_strength(confidence)

            details = {
                'compression_strength': compression_strength,
                'compression_duration': fractal_data.get('compression_duration', 0),
                'breakout_potential': fractal_data.get('breakout_potential', 0),
                'compression_type': fractal_data.get('compression_type', 'symmetrical'),
                'expected_magnitude': fractal_data.get('expected_magnitude', 0)
            }

            description = f"Fractal {signal} ({confidence:.0f}%)"
            if details['compression_strength'] > 0.8:
                description += " | High compression"
            elif details['breakout_potential'] > 0.7:
                description += " | Breakout ready"

            return ConfluenceFactor(
                name="Fractal Compression",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['fractal_compression'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing fractal compression confluence: {e}")
            return None

    def _analyze_order_flow_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze order flow imbalance confluence"""
        try:
            order_flow_data = analysis_data.get('order_flow', {})
            if not order_flow_data:
                return None

            signal = order_flow_data.get('signal', 'NEUTRAL')
            confidence = order_flow_data.get('confidence', 0)
            imbalance_ratio = order_flow_data.get('imbalance_ratio', 0)

            direction = ConfluenceDirection.BULLISH if signal == 'BUY' else ConfluenceDirection.BEARISH if signal == 'SELL' else ConfluenceDirection.NEUTRAL
            strength = self._confidence_to_strength(confidence)

            details = {
                'imbalance_ratio': imbalance_ratio,
                'imbalance_type': order_flow_data.get('imbalance_type', 'balanced'),
                'absorption_detected': order_flow_data.get('absorption_detected', False),
                'market_impact_score': order_flow_data.get('market_impact_score', 0),
                'reliability_score': order_flow_data.get('reliability_score', 0)
            }

            description = f"Order Flow {signal} ({confidence:.0f}%)"
            if abs(details['imbalance_ratio']) > 0.7:
                description += " | Strong imbalance"
            elif details['absorption_detected']:
                description += " | Absorption"

            return ConfluenceFactor(
                name="Order Flow Imbalance",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['order_flow_imbalance'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing order flow confluence: {e}")
            return None

    def _analyze_volume_profile_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze volume profile confluence"""
        try:
            volume_data = analysis_data.get('volume_analysis', {})
            if not volume_data:
                return None

            signal = volume_data.get('signal', 'NEUTRAL')
            confidence = volume_data.get('confidence', 0)

            direction = ConfluenceDirection.BULLISH if signal == 'BUY' else ConfluenceDirection.BEARISH if signal == 'SELL' else ConfluenceDirection.NEUTRAL
            strength = self._confidence_to_strength(confidence)

            profile_data = volume_data.get('volume_profile', {})
            poc = profile_data.get('poc_price', 0)
            value_area = profile_data.get('value_area', {})

            details = {
                'poc_price': poc,
                'value_area_high': value_area.get('high', 0),
                'value_area_low': value_area.get('low', 0),
                'profile_type': profile_data.get('profile_type', 'normal'),
                'volume_trend': volume_data.get('volume_trend', 'neutral')
            }

            description = f"Volume Profile {signal} ({confidence:.0f}%)"
            if details['profile_type'] != 'normal':
                description += f" | {details['profile_type']}"

            return ConfluenceFactor(
                name="Volume Profile",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['volume_profile'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing volume profile confluence: {e}")
            return None

    def _analyze_market_structure_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze market structure confluence"""
        try:
            structure_data = analysis_data.get('market_structure', {})
            if not structure_data:
                return None

            trend = structure_data.get('trend', 'Neutral')
            strength_pct = structure_data.get('strength', 50)

            # Convert trend to signal
            if trend in ['Uptrend', 'Bullish']:
                signal = 'BUY'
                direction = ConfluenceDirection.BULLISH
            elif trend in ['Downtrend', 'Bearish']:
                signal = 'SELL'
                direction = ConfluenceDirection.BEARISH
            else:
                signal = 'NEUTRAL'
                direction = ConfluenceDirection.NEUTRAL

            strength = self._confidence_to_strength(strength_pct)

            details = {
                'trend': trend,
                'strength_percentage': strength_pct,
                'break_of_structure': structure_data.get('break_of_structure', None),
                'swing_highs': structure_data.get('swing_highs', []),
                'swing_lows': structure_data.get('swing_lows', [])
            }

            description = f"Structure {signal} ({strength_pct:.0f}%)"
            if details['break_of_structure']:
                description += " | BOS"

            return ConfluenceFactor(
                name="Market Structure",
                direction=direction,
                strength=strength,
                confidence=strength_pct,
                weight=self.factor_weights['market_structure'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing market structure confluence: {e}")
            return None

    def _analyze_snr_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze support/resistance confluence"""
        try:
            # Look for S/R data in various places
            snr_data = (analysis_data.get('snr_levels', {}) or 
                       analysis_data.get('support_resistance', {}) or
                       analysis_data.get('sr_levels', {}))

            if not snr_data:
                return None

            current_price = df['close'].iloc[-1]
            support_levels = snr_data.get('support', [])
            resistance_levels = snr_data.get('resistance', [])

            # Determine proximity to key levels
            nearest_support = max([level for level in support_levels if level < current_price], default=0)
            nearest_resistance = min([level for level in resistance_levels if level > current_price], default=float('inf'))

            support_distance = abs(current_price - nearest_support) / current_price if nearest_support else 1
            resistance_distance = abs(nearest_resistance - current_price) / current_price if nearest_resistance != float('inf') else 1

            # Determine signal based on proximity and price action
            if support_distance < 0.005:  # Within 0.5% of support
                signal = 'BUY'
                direction = ConfluenceDirection.BULLISH
                confidence = max(60, 100 - (support_distance * 10000))
            elif resistance_distance < 0.005:  # Within 0.5% of resistance
                signal = 'SELL'
                direction = ConfluenceDirection.BEARISH
                confidence = max(60, 100 - (resistance_distance * 10000))
            else:
                signal = 'NEUTRAL'
                direction = ConfluenceDirection.NEUTRAL
                confidence = 50

            strength = self._confidence_to_strength(confidence)

            details = {
                'nearest_support': nearest_support,
                'nearest_resistance': nearest_resistance,
                'support_distance': support_distance,
                'resistance_distance': resistance_distance,
                'total_support_levels': len(support_levels),
                'total_resistance_levels': len(resistance_levels)
            }

            description = f"S/R {signal} ({confidence:.0f}%)"
            if support_distance < 0.01:
                description += " | Near support"
            elif resistance_distance < 0.01:
                description += " | Near resistance"

            return ConfluenceFactor(
                name="Support/Resistance",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['snr_levels'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing S/R confluence: {e}")
            return None

    def _analyze_seasonal_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze seasonal pattern confluence"""
        try:
            seasonal_data = analysis_data.get('seasonal_analysis', {})
            if not seasonal_data:
                return None

            bias = seasonal_data.get('combined_bias', {})
            direction_str = bias.get('direction', 'neutral')
            confidence = bias.get('confidence', 0) * 100

            if direction_str == 'bullish':
                signal = 'BUY'
                direction = ConfluenceDirection.BULLISH
            elif direction_str == 'bearish':
                signal = 'SELL'
                direction = ConfluenceDirection.BEARISH
            else:
                signal = 'NEUTRAL'
                direction = ConfluenceDirection.NEUTRAL

            strength = self._confidence_to_strength(confidence)

            details = {
                'monthly_bias': seasonal_data.get('monthly_bias', {}),
                'weekly_bias': seasonal_data.get('weekly_bias', {}),
                'daily_bias': seasonal_data.get('daily_bias', {}),
                'session_bias': seasonal_data.get('session_bias', {}),
                'pattern_strength': bias.get('strength', 0)
            }

            description = f"Seasonal {signal} ({confidence:.0f}%)"
            if details['pattern_strength'] > 0.7:
                description += " | Strong pattern"

            return ConfluenceFactor(
                name="Seasonal Patterns",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['seasonal_patterns'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing seasonal confluence: {e}")
            return None

    def _analyze_breakout_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze breakout validation confluence"""
        try:
            breakout_data = analysis_data.get('breakout_analysis', {})
            if not breakout_data:
                return None

            validation_status = breakout_data.get('validation_status', 'pending')
            confidence = breakout_data.get('confidence', 0)
            breakout_direction = breakout_data.get('direction', 'neutral')

            if validation_status == 'confirmed' and breakout_direction == 'bullish':
                signal = 'BUY'
                direction = ConfluenceDirection.BULLISH
            elif validation_status == 'confirmed' and breakout_direction == 'bearish':
                signal = 'SELL'
                direction = ConfluenceDirection.BEARISH
            else:
                signal = 'NEUTRAL'
                direction = ConfluenceDirection.NEUTRAL
                confidence = max(confidence * 0.5, 30)  # Reduce confidence for unconfirmed breakouts

            strength = self._confidence_to_strength(confidence)

            details = {
                'validation_status': validation_status,
                'breakout_direction': breakout_direction,
                'volume_confirmation': breakout_data.get('volume_confirmation', False),
                'retest_status': breakout_data.get('retest_status', 'pending'),
                'strength_score': breakout_data.get('strength_score', 0)
            }

            description = f"Breakout {signal} ({confidence:.0f}%)"
            if details['validation_status'] == 'confirmed':
                description += " | Confirmed"
            elif details['volume_confirmation']:
                description += " | Volume conf."

            return ConfluenceFactor(
                name="Breakout Validation",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['breakout_validation'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing breakout confluence: {e}")
            return None

    def _analyze_momentum_divergence_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze momentum divergence confluence"""
        try:
            if len(df) < 50:
                return None

            # Calculate RSI and price for divergence analysis
            close_prices = df['close'].values
            rsi_values = self._calculate_rsi(close_prices)

            if len(rsi_values) < 20:
                return None

            # Look for divergences in recent data
            divergence_data = self._detect_momentum_divergence(close_prices, rsi_values)

            if not divergence_data['divergence_detected']:
                return None

            signal = divergence_data['signal']
            confidence = divergence_data['confidence']

            direction = ConfluenceDirection.BULLISH if signal == 'BUY' else ConfluenceDirection.BEARISH if signal == 'SELL' else ConfluenceDirection.NEUTRAL
            strength = self._confidence_to_strength(confidence)

            details = {
                'divergence_type': divergence_data['divergence_type'],
                'divergence_strength': divergence_data['strength'],
                'recent_rsi': rsi_values[-1] if len(rsi_values) > 0 else 50,
                'price_trend': divergence_data['price_trend'],
                'momentum_trend': divergence_data['momentum_trend']
            }

            description = f"Momentum {signal} ({confidence:.0f}%)"
            if details['divergence_type'] == 'hidden':
                description += " | Hidden div."
            elif details['divergence_type'] == 'regular':
                description += " | Regular div."

            return ConfluenceFactor(
                name="Momentum Divergence",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['momentum_divergence'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing momentum divergence confluence: {e}")
            return None

    def _analyze_volatility_expansion_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze volatility expansion confluence"""
        try:
            if len(df) < 20:
                return None

            # Calculate ATR and volatility metrics
            atr_values = self._calculate_atr(df)
            current_atr = atr_values[-1] if len(atr_values) > 0 else 0
            avg_atr = safe_mean(atr_values[-20:]) if len(atr_values) >= 20 else current_atr

            if avg_atr == 0:
                return None

            volatility_ratio = safe_divide(current_atr, avg_atr, 1.0)

            # Determine if volatility is expanding
            if volatility_ratio > 1.5:  # Significant expansion
                confidence = min(80, 50 + (volatility_ratio - 1) * 30)
                signal = 'BUY'  # Volatility expansion often precedes strong moves
                direction = ConfluenceDirection.BULLISH
            elif volatility_ratio < 0.7:  # Compression (potential for expansion)
                confidence = min(70, 40 + (1 - volatility_ratio) * 40)
                signal = 'NEUTRAL'  # Waiting for direction
                direction = ConfluenceDirection.NEUTRAL
            else:
                return None  # Normal volatility

            strength = self._confidence_to_strength(confidence)

            details = {
                'current_atr': current_atr,
                'average_atr': avg_atr,
                'volatility_ratio': volatility_ratio,
                'expansion_phase': volatility_ratio > 1.2,
                'compression_phase': volatility_ratio < 0.8
            }

            description = f"Volatility {signal} ({confidence:.0f}%)"
            if details['expansion_phase']:
                description += " | Expanding"
            elif details['compression_phase']:
                description += " | Compressed"

            return ConfluenceFactor(
                name="Volatility Expansion",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['volatility_expansion'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing volatility expansion confluence: {e}")
            return None

    def _analyze_session_bias_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze trading session bias confluence"""
        try:
            current_hour = datetime.now().hour

            # Define session characteristics
            session_bias = self._get_session_bias(current_hour)

            if not session_bias:
                return None

            signal = session_bias['bias']
            confidence = session_bias['confidence']

            direction = ConfluenceDirection.BULLISH if signal == 'BUY' else ConfluenceDirection.BEARISH if signal == 'SELL' else ConfluenceDirection.NEUTRAL
            strength = self._confidence_to_strength(confidence)

            details = {
                'current_session': session_bias['session'],
                'session_characteristics': session_bias['characteristics'],
                'volatility_expectation': session_bias['volatility'],
                'volume_expectation': session_bias['volume']
            }

            description = f"Session {signal} ({confidence:.0f}%)"
            description += f" | {details['current_session']}"

            return ConfluenceFactor(
                name="Session Bias",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['session_bias'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing session bias confluence: {e}")
            return None

    def _analyze_calendar_confluence(self, df: pd.DataFrame, analysis_data: Dict[str, Any]) -> Optional[ConfluenceFactor]:
        """Analyze economic calendar confluence"""
        try:
            calendar_data = analysis_data.get('calendar_impact', {})
            if not calendar_data:
                return None

            impact = calendar_data.get('impact', 'low')
            direction_bias = calendar_data.get('bias', 'neutral')
            confidence = calendar_data.get('confidence', 0)

            if direction_bias == 'bullish':
                signal = 'BUY'
                direction = ConfluenceDirection.BULLISH
            elif direction_bias == 'bearish':
                signal = 'SELL'
                direction = ConfluenceDirection.BEARISH
            else:
                signal = 'NEUTRAL'
                direction = ConfluenceDirection.NEUTRAL

            strength = self._confidence_to_strength(confidence)

            details = {
                'upcoming_events': calendar_data.get('upcoming_events', []),
                'impact_level': impact,
                'direction_bias': direction_bias,
                'event_details': calendar_data.get('event_details', [])
            }

            description = f"Calendar {signal} ({confidence:.0f}%)"
            description += f" | {impact} impact"

            return ConfluenceFactor(
                name="Economic Calendar",
                direction=direction,
                strength=strength,
                confidence=confidence,
                weight=self.factor_weights['economic_calendar'],
                description=description,
                details=details
            )

        except Exception as e:
            print(f"Error analyzing calendar confluence: {e}")
            return None

    def _calculate_agreement_conflicts(self, confluence_factors: List[ConfluenceFactor]) -> Dict[str, Any]:
        """Calculate agreement and conflicts among confluence factors"""
        try:
            bullish_factors = [f for f in confluence_factors if f.direction == ConfluenceDirection.BULLISH]
            bearish_factors = [f for f in confluence_factors if f.direction == ConfluenceDirection.BEARISH]
            neutral_factors = [f for f in confluence_factors if f.direction == ConfluenceDirection.NEUTRAL]

            total_factors = len(confluence_factors)
            bullish_count = len(bullish_factors)
            bearish_count = len(bearish_factors)
            neutral_count = len(neutral_factors)

            # Calculate agreement percentage
            agreement_percentage = (max(bullish_count, bearish_count) / total_factors) * 100 if total_factors > 0 else 0

            # Determine dominant direction
            if bullish_count > bearish_count:
                dominant_direction = "Bullish"
            elif bearish_count > bullish_count:
                dominant_direction = "Bearish"
            else:
                dominant_direction = "Neutral"

            # Identify strong conflicts (factors in opposite directions)
            strong_conflicts = min(bullish_count, bearish_count)

            # Calculate weighted agreement score
            weighted_agreement = sum(f.weight for f in bullish_factors) - sum(f.weight for f in bearish_factors)

            return {
                'total_factors': total_factors,
                'bullish_factors': bullish_count,
                'bearish_factors': bearish_count,
                'neutral_factors': neutral_count,
                'agreement_percentage': agreement_percentage,
                'dominant_direction': dominant_direction,
                'strong_conflicts': strong_conflicts,
                'weighted_agreement': weighted_agreement
            }

        except Exception as e:
            print(f"Error calculating agreement/conflicts: {e}")
            return {
                'total_factors': 0,
                'bullish_factors': 0,
                'bearish_factors': 0,
                'neutral_factors': 0,
                'agreement_percentage': 0,
                'dominant_direction': 'Neutral',
                'strong_conflicts': 0,
                'weighted_agreement': 0
            }

    def _generate_confluence_summary(self, confluence_factors: List[ConfluenceFactor], agreement_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of confluence analysis"""
        try:
            total_factors = len(confluence_factors)
            bullish_factors = agreement_analysis['bullish_factors']
            bearish_factors = agreement_analysis['bearish_factors']
            neutral_factors = agreement_analysis['neutral_factors']
            dominant_direction = agreement_analysis['dominant_direction']
            agreement_percentage = agreement_analysis['agreement_percentage']
            strong_conflicts = agreement_analysis['strong_conflicts']

            summary = {
                'total_factors': total_factors,
                'bullish_factors': bullish_factors,
                'bearish_factors': bearish_factors,
                'neutral_factors': neutral_factors,
                'dominant_direction': dominant_direction,
                'agreement_percentage': agreement_percentage,
                'strong_conflicts': strong_conflicts,
                'top_3_bullish': [f.name for f in sorted([f for f in confluence_factors if f.direction == ConfluenceDirection.BULLISH], key=lambda x: x.confidence, reverse=True)[:3]],
                'top_3_bearish': [f.name for f in sorted([f for f in confluence_factors if f.direction == ConfluenceDirection.BEARISH], key=lambda x: x.confidence, reverse=True)[:3]]
            }

            return summary

        except Exception as e:
            print(f"Error generating confluence summary: {e}")
            return {
                'total_factors': 0,
                'bullish_factors': 0,
                'bearish_factors': 0,
                'neutral_factors': 0,
                'dominant_direction': 'Neutral',
                'agreement_percentage': 0,
                'strong_conflicts': 0,
                'top_3_bullish': [],
                'top_3_bearish': []
            }

    def _calculate_total_confluence_score(self, confluence_factors: List[ConfluenceFactor], agreement_analysis: Dict[str, Any]) -> float:
        """Calculate total confluence score from factors"""
        try:
            if not confluence_factors:
                return 50.0
            
            # Calculate weighted confidence from all factors
            total_weight = sum(f.weight for f in confluence_factors)
            if total_weight == 0:
                return 50.0
            
            weighted_confidence = sum(f.confidence * f.weight for f in confluence_factors) / total_weight
            
            # Adjust based on agreement percentage
            agreement_percentage = agreement_analysis.get('agreement_percentage', 0)
            agreement_boost = (agreement_percentage / 100.0) * 10  # Up to 10% boost
            
            # Final score: 0-100, centered around 50
            confluence_score = min(100, max(0, weighted_confidence + agreement_boost))
            
            return confluence_score
            
        except Exception as e:
            print(f"Error calculating confluence score: {e}")
            return 50.0

    def _confidence_to_strength(self, confidence: float) -> ConfluenceStrength:
        """Convert confidence percentage to ConfluenceStrength enum"""
        if confidence >= 80:
            return ConfluenceStrength.VERY_STRONG
        elif confidence >= 60:
            return ConfluenceStrength.STRONG
        elif confidence >= 40:
            return ConfluenceStrength.MODERATE
        else:
            return ConfluenceStrength.WEAK

    def _derive_ict_data(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Derive ICT/SMC data from other indicators"""
        # Implement logic to derive ICT data
        return {}

    def _derive_institutional_flow(self, df: pd.DataFrame, volume_data: Dict[str, Any], order_flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Derive institutional flow data from volume and order flow analysis"""
        # Implement logic to derive institutional flow
        return {}

    def _detect_fractal_compression(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect fractal compression zones from price action"""
        # Implement logic to detect fractal compression
        return {}

    def _calculate_rsi(self, close_prices: List[float], period: int = 14) -> np.ndarray:
        """Calculate RSI (Relative Strength Index)"""
        delta = np.diff(close_prices)
        gain = delta * (delta > 0)
        loss = -delta * (delta < 0)

        avg_gain = np.zeros_like(close_prices)
        avg_loss = np.zeros_like(close_prices)

        avg_gain[period] = np.mean(gain[:period])
        avg_loss[period] = np.mean(loss[:period])

        for i in range(period + 1, len(close_prices)):
            avg_gain[i] = (avg_gain[i - 1] * (period - 1) + gain[i - 1]) / period
            avg_loss[i] = (avg_loss[i - 1] * (period - 1) + loss[i - 1]) / period

        rs = np.divide(avg_gain, avg_loss, out=np.zeros_like(avg_gain), where=avg_loss != 0)
        rsi = 100 - (100 / (1 + rs))

        return rsi[period:]

    def _detect_momentum_divergence(self, close_prices: List[float], rsi_values: np.ndarray) -> Dict[str, Any]:
        """Detect momentum divergence between price and RSI"""
        divergence_data = {
            'divergence_detected': False,
            'signal': 'NEUTRAL',
            'confidence': 0,
            'divergence_type': 'none',
            'strength': 0,
            'price_trend': 'neutral',
            'momentum_trend': 'neutral'
        }

        if len(close_prices) < 2 or len(rsi_values) < 2:
            return divergence_data

        # Simple divergence detection logic
        if close_prices[-1] > close_prices[-2] and rsi_values[-1] < rsi_values[-2]:
            divergence_data['divergence_detected'] = True
            divergence_data['signal'] = 'SELL'
            divergence_data['confidence'] = 65
            divergence_data['divergence_type'] = 'regular'
            divergence_data['strength'] = 0.6
            divergence_data['price_trend'] = 'up'
            divergence_data['momentum_trend'] = 'down'
        elif close_prices[-1] < close_prices[-2] and rsi_values[-1] > rsi_values[-2]:
            divergence_data['divergence_detected'] = True
            divergence_data['signal'] = 'BUY'
            divergence_data['confidence'] = 65
            divergence_data['divergence_type'] = 'regular'
            divergence_data['strength'] = 0.6
            divergence_data['price_trend'] = 'down'
            divergence_data['momentum_trend'] = 'up'

        return divergence_data

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> np.ndarray:
        """Calculate Average True Range (ATR)"""
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values

        tr = np.zeros_like(close)
        for i in range(1, len(close)):
            tr[i] = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))

        atr = np.zeros_like(close)
        atr[period] = np.mean(tr[1:period + 1])

        for i in range(period + 1, len(close)):
            atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period

        return atr[period:]

    def _get_session_bias(self, hour: int) -> Dict[str, Any]:
        """Determine trading session bias based on the hour of the day"""
        if 7 <= hour < 11:
            return {
                'session': 'Asian',
                'bias': 'NEUTRAL',
                'confidence': 50,
                'characteristics': 'Lower volatility, range-bound',
                'volatility': 'Low',
                'volume': 'Low'
            }
        elif 11 <= hour < 17:
            return {
                'session': 'London',
                'bias': 'BUY',
                'confidence': 60,
                'characteristics': 'Early breakout potential, trend initiation',
                'volatility': 'Moderate',
                'volume': 'Moderate'
            }
        elif 17 <= hour < 21:
            return {
                'session': 'New York',
                'bias': 'SELL',
                'confidence': 60,
                'characteristics': 'High volatility, news-driven moves',
                'volatility': 'High',
                'volume': 'High'
            }
        else:
            return None

    def _empty_confluence_analysis(self) -> Dict[str, Any]:
        """Return an empty confluence analysis result"""
        return {
            'confluence_factors': [],
            'agreement_analysis': {
                'total_factors': 0,
                'bullish_factors': 0,
                'bearish_factors': 0,
                'neutral_factors': 0,
                'agreement_percentage': 0,
                'dominant_direction': 'Neutral',
                'strong_conflicts': 0,
                'weighted_agreement': 0
            },
            'confluence_summary': {
                'total_factors': 0,
                'bullish_factors': 0,
                'bearish_factors': 0,
                'neutral_factors': 0,
                'dominant_direction': 'Neutral',
                'agreement_percentage': 0,
                'strong_conflicts': 0,
                'top_3_bullish': [],
                'top_3_bearish': []
            },
            'total_factors': 0,
            'strong_factors': 0,
            'confluence_score': 0
        }

    def calculate_enhanced_confluence(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate enhanced confluence score from all analysis components"""
        try:
            confluence_factors = []
            confluence_count = 0

            # Sentiment confluence
            sentiment_boost = analysis_result.get('sentiment_boost', 0)
            if sentiment_boost > 3:
                confluence_count += 2
                confluence_factors.append("Strong sentiment alignment")
            elif sentiment_boost > 0:
                confluence_count += 1
                confluence_factors.append("Sentiment support")

            # Volume confluence
            volume_boost = analysis_result.get('volume_boost', 0)
            if volume_boost > 5:
                confluence_count += 2
                confluence_factors.append("Strong volume confirmation")
            elif volume_boost > 2:
                confluence_count += 1
                confluence_factors.append("Volume support")

            # Calendar confluence (stability during low-impact periods)
            calendar_adjustment = analysis_result.get('calendar_adjustment', 0)
            if calendar_adjustment > -2:  # Low negative impact or positive
                confluence_count += 1
                confluence_factors.append("Favorable economic calendar")

            # Smart money confluence
            smart_money = analysis_result.get('volume_profile', {}).get('smart_money_flow', {})
            institutional_activity = smart_money.get('flow_direction', 'Neutral')
            if institutional_activity != 'Neutral':
                confluence_count += 1
                confluence_factors.append(f"Institutional {institutional_activity.lower()} flow")

            # Market context confluence
            market_bias = analysis_result.get('market_context', {}).get('overall_bias')
            if market_bias and market_bias != 'Mixed':
                confluence_count += 1
                confluence_factors.append(f"Market context: {market_bias}")

            return {
                'count': confluence_count,
                'factors': confluence_factors
            }

        except Exception as e:
            print(f"Error calculating enhanced confluence: {e}")
            return {
                'count': 0,
                'factors': []
            }