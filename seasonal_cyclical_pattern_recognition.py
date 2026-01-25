"""
Seasonal and Cyclical Pattern Recognition System for Trading Bot
Analyzes monthly seasonality, intraday cycles, and cyclical market behaviors
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import calendar

class SeasonalStrength(Enum):
    VERY_STRONG = "very_strong"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    NONE = "none"

class TradingSession(Enum):
    ASIAN = "asian"
    LONDON = "london"
    NEW_YORK = "newyork"
    OVERLAP_ASIAN_LONDON = "overlap_asian_london"
    OVERLAP_LONDON_NY = "overlap_london_ny"
    QUIET = "quiet"

@dataclass
class SeasonalPattern:
    period_type: str  # 'monthly', 'weekly', 'daily', 'hourly'
    period_identifier: str  # 'january', 'monday', 'hour_9', etc.
    bullish_probability: float
    bearish_probability: float
    volatility_factor: float
    volume_factor: float
    pattern_strength: SeasonalStrength
    confidence_score: float
    historical_data_points: int

@dataclass
class CyclicalPattern:
    cycle_name: str
    cycle_length_days: int
    current_cycle_position: float  # 0.0 to 1.0
    cycle_phase: str  # 'accumulation', 'markup', 'distribution', 'markdown'
    expected_direction: str
    cycle_strength: float
    time_to_next_phase: int  # days
    reliability_score: float

@dataclass
class IntradayPattern:
    session: TradingSession
    session_start_hour: int
    session_end_hour: int
    typical_volatility: float
    typical_volume_multiplier: float
    common_reversals: List[int]  # hours when reversals commonly occur
    breakout_probability: float
    fade_probability: float

class SeasonalCyclicalAnalyzer:
    """Advanced seasonal and cyclical pattern recognition system"""
    
    def __init__(self):
        self.seasonal_database = self._initialize_seasonal_database()
        self.cyclical_patterns = self._initialize_cyclical_patterns()
        self.intraday_sessions = self._initialize_intraday_sessions()
        
    def _initialize_seasonal_database(self) -> Dict[str, Dict[str, SeasonalPattern]]:
        """Initialize seasonal pattern database with historical tendencies"""
        # This would be populated from historical analysis
        # For now, we'll use common market seasonality patterns
        
        monthly_patterns = {
            'EURUSD': {
                'january': SeasonalPattern('monthly', 'january', 0.55, 0.45, 1.2, 1.1, SeasonalStrength.MODERATE, 0.65, 120),
                'february': SeasonalPattern('monthly', 'february', 0.52, 0.48, 1.0, 0.9, SeasonalStrength.WEAK, 0.55, 120),
                'march': SeasonalPattern('monthly', 'march', 0.48, 0.52, 1.3, 1.2, SeasonalStrength.MODERATE, 0.62, 120),
                'april': SeasonalPattern('monthly', 'april', 0.58, 0.42, 1.1, 1.0, SeasonalStrength.STRONG, 0.72, 120),
                'may': SeasonalPattern('monthly', 'may', 0.45, 0.55, 0.8, 0.8, SeasonalStrength.MODERATE, 0.68, 120),
                'june': SeasonalPattern('monthly', 'june', 0.42, 0.58, 0.7, 0.7, SeasonalStrength.STRONG, 0.75, 120),
                'july': SeasonalPattern('monthly', 'july', 0.40, 0.60, 0.6, 0.6, SeasonalStrength.VERY_STRONG, 0.82, 120),
                'august': SeasonalPattern('monthly', 'august', 0.38, 0.62, 0.5, 0.5, SeasonalStrength.VERY_STRONG, 0.85, 120),
                'september': SeasonalPattern('monthly', 'september', 0.62, 0.38, 1.4, 1.3, SeasonalStrength.STRONG, 0.78, 120),
                'october': SeasonalPattern('monthly', 'october', 0.65, 0.35, 1.5, 1.4, SeasonalStrength.VERY_STRONG, 0.88, 120),
                'november': SeasonalPattern('monthly', 'november', 0.60, 0.40, 1.2, 1.1, SeasonalStrength.STRONG, 0.70, 120),
                'december': SeasonalPattern('monthly', 'december', 0.48, 0.52, 0.8, 0.7, SeasonalStrength.MODERATE, 0.60, 120)
            }
        }
        
        weekly_patterns = {
            'EURUSD': {
                'monday': SeasonalPattern('weekly', 'monday', 0.52, 0.48, 1.2, 1.1, SeasonalStrength.MODERATE, 0.65, 520),
                'tuesday': SeasonalPattern('weekly', 'tuesday', 0.58, 0.42, 1.4, 1.3, SeasonalStrength.STRONG, 0.75, 520),
                'wednesday': SeasonalPattern('weekly', 'wednesday', 0.55, 0.45, 1.3, 1.2, SeasonalStrength.STRONG, 0.72, 520),
                'thursday': SeasonalPattern('weekly', 'thursday', 0.53, 0.47, 1.2, 1.1, SeasonalStrength.MODERATE, 0.68, 520),
                'friday': SeasonalPattern('weekly', 'friday', 0.45, 0.55, 0.9, 0.8, SeasonalStrength.MODERATE, 0.70, 520)
            }
        }
        
        return {
            'monthly': monthly_patterns,
            'weekly': weekly_patterns
        }
    
    def _initialize_cyclical_patterns(self) -> Dict[str, List[CyclicalPattern]]:
        """Initialize cyclical pattern database"""
        return {
            'EURUSD': [
                CyclicalPattern('short_cycle', 7, 0.0, 'accumulation', 'neutral', 0.6, 3, 0.65),
                CyclicalPattern('medium_cycle', 21, 0.0, 'markup', 'bullish', 0.7, 10, 0.72),
                CyclicalPattern('long_cycle', 90, 0.0, 'distribution', 'bearish', 0.8, 45, 0.78)
            ]
        }
    
    def _initialize_intraday_sessions(self) -> Dict[TradingSession, IntradayPattern]:
        """Initialize intraday session patterns"""
        return {
            TradingSession.ASIAN: IntradayPattern(
                TradingSession.ASIAN, 0, 8, 0.7, 0.6, [4, 7], 0.3, 0.7
            ),
            TradingSession.LONDON: IntradayPattern(
                TradingSession.LONDON, 8, 16, 1.3, 1.4, [10, 14], 0.7, 0.3
            ),
            TradingSession.NEW_YORK: IntradayPattern(
                TradingSession.NEW_YORK, 13, 21, 1.2, 1.3, [15, 18], 0.6, 0.4
            ),
            TradingSession.OVERLAP_LONDON_NY: IntradayPattern(
                TradingSession.OVERLAP_LONDON_NY, 13, 16, 1.8, 2.0, [14], 0.8, 0.2
            ),
            TradingSession.QUIET: IntradayPattern(
                TradingSession.QUIET, 21, 24, 0.4, 0.3, [22, 23], 0.2, 0.8
            )
        }
    
    async def analyze_seasonal_patterns(self, symbol: str, current_date: datetime = None) -> Dict[str, Any]:
        """Analyze current seasonal patterns for the symbol"""
        try:
            if current_date is None:
                current_date = datetime.now()
            
            # Get current time periods
            current_month = current_date.strftime('%B').lower()
            current_weekday = current_date.strftime('%A').lower()
            current_hour = current_date.hour
            
            # Analyze monthly seasonality
            monthly_analysis = self._analyze_monthly_seasonality(symbol, current_month)
            
            # Analyze weekly seasonality
            weekly_analysis = self._analyze_weekly_seasonality(symbol, current_weekday)
            
            # Analyze intraday patterns
            intraday_analysis = self._analyze_intraday_patterns(current_hour)
            
            # Calculate end-of-period effects
            eop_effects = self._analyze_end_of_period_effects(current_date)
            
            # Calculate overall seasonal bias
            overall_bias = self._calculate_overall_seasonal_bias(
                monthly_analysis, weekly_analysis, intraday_analysis, eop_effects
            )
            
            return {
                'analysis_date': current_date.isoformat(),
                'symbol': symbol,
                'monthly_seasonality': monthly_analysis,
                'weekly_seasonality': weekly_analysis,
                'intraday_patterns': intraday_analysis,
                'end_of_period_effects': eop_effects,
                'overall_seasonal_bias': overall_bias,
                'seasonal_strength': self._classify_seasonal_strength(overall_bias),
                'trading_recommendations': self._generate_seasonal_recommendations(overall_bias)
            }
            
        except Exception as e:
            return self._empty_seasonal_analysis(symbol, current_date)
    
    def _analyze_monthly_seasonality(self, symbol: str, current_month: str) -> Dict[str, Any]:
        """Analyze monthly seasonal patterns"""
        try:
            if symbol not in self.seasonal_database.get('monthly', {}):
                # Use EURUSD as default pattern
                symbol = 'EURUSD'
            
            monthly_patterns = self.seasonal_database['monthly'].get(symbol, {})
            current_pattern = monthly_patterns.get(current_month)
            
            if not current_pattern:
                return {'pattern_found': False, 'bias': 'neutral'}
            
            # Calculate seasonal bias
            bias_score = current_pattern.bullish_probability - current_pattern.bearish_probability
            bias_direction = 'bullish' if bias_score > 0.1 else 'bearish' if bias_score < -0.1 else 'neutral'
            
            return {
                'pattern_found': True,
                'month': current_month,
                'bias': bias_direction,
                'bias_strength': abs(bias_score),
                'bullish_probability': current_pattern.bullish_probability,
                'bearish_probability': current_pattern.bearish_probability,
                'volatility_factor': current_pattern.volatility_factor,
                'volume_factor': current_pattern.volume_factor,
                'pattern_strength': current_pattern.pattern_strength.value,
                'confidence': current_pattern.confidence_score
            }
            
        except Exception as e:
            return {'pattern_found': False, 'bias': 'neutral', 'error': str(e)}
    
    def _analyze_weekly_seasonality(self, symbol: str, current_weekday: str) -> Dict[str, Any]:
        """Analyze weekly seasonal patterns"""
        try:
            if symbol not in self.seasonal_database.get('weekly', {}):
                symbol = 'EURUSD'
            
            weekly_patterns = self.seasonal_database['weekly'].get(symbol, {})
            current_pattern = weekly_patterns.get(current_weekday)
            
            if not current_pattern:
                return {'pattern_found': False, 'bias': 'neutral'}
            
            bias_score = current_pattern.bullish_probability - current_pattern.bearish_probability
            bias_direction = 'bullish' if bias_score > 0.05 else 'bearish' if bias_score < -0.05 else 'neutral'
            
            return {
                'pattern_found': True,
                'weekday': current_weekday,
                'bias': bias_direction,
                'bias_strength': abs(bias_score),
                'bullish_probability': current_pattern.bullish_probability,
                'bearish_probability': current_pattern.bearish_probability,
                'volatility_factor': current_pattern.volatility_factor,
                'volume_factor': current_pattern.volume_factor,
                'pattern_strength': current_pattern.pattern_strength.value,
                'confidence': current_pattern.confidence_score
            }
            
        except Exception as e:
            return {'pattern_found': False, 'bias': 'neutral', 'error': str(e)}
    
    def _analyze_intraday_patterns(self, current_hour: int) -> Dict[str, Any]:
        """Analyze intraday session patterns"""
        try:
            # Determine current session
            current_session = self._determine_trading_session(current_hour)
            session_pattern = self.intraday_sessions.get(current_session)
            
            if not session_pattern:
                return {'session': 'unknown', 'volatility_expected': 'normal'}
            
            # Calculate session characteristics
            session_analysis = {
                'current_session': current_session.value,
                'session_start': session_pattern.session_start_hour,
                'session_end': session_pattern.session_end_hour,
                'expected_volatility': session_pattern.typical_volatility,
                'expected_volume_multiplier': session_pattern.typical_volume_multiplier,
                'breakout_probability': session_pattern.breakout_probability,
                'fade_probability': session_pattern.fade_probability,
                'reversal_hours': session_pattern.common_reversals,
                'time_to_next_reversal': self._calculate_time_to_next_reversal(
                    current_hour, session_pattern.common_reversals
                )
            }
            
            return session_analysis
            
        except Exception as e:
            return {'session': 'unknown', 'volatility_expected': 'normal', 'error': str(e)}
    
    def _determine_trading_session(self, hour: int) -> TradingSession:
        """Determine which trading session is currently active"""
        # Convert to GMT/UTC for standardization
        if 0 <= hour < 8:
            return TradingSession.ASIAN
        elif 8 <= hour < 13:
            return TradingSession.LONDON
        elif 13 <= hour < 16:
            return TradingSession.OVERLAP_LONDON_NY
        elif 16 <= hour < 21:
            return TradingSession.NEW_YORK
        else:
            return TradingSession.QUIET
    
    def _calculate_time_to_next_reversal(self, current_hour: int, reversal_hours: List[int]) -> Optional[int]:
        """Calculate hours until next expected reversal"""
        try:
            future_reversals = [h for h in reversal_hours if h > current_hour]
            if future_reversals:
                return min(future_reversals) - current_hour
            elif reversal_hours:
                # Next reversal is tomorrow
                return (24 - current_hour) + min(reversal_hours)
            else:
                return None
        except:
            return None
    
    def _analyze_end_of_period_effects(self, current_date: datetime) -> Dict[str, Any]:
        """Analyze end-of-period effects (month-end, quarter-end, year-end)"""
        try:
            effects = {
                'month_end_proximity': self._calculate_month_end_proximity(current_date),
                'quarter_end_proximity': self._calculate_quarter_end_proximity(current_date),
                'year_end_proximity': self._calculate_year_end_proximity(current_date),
                'expected_rebalancing': False,
                'volatility_adjustment': 1.0
            }
            
            # Check for significant end-of-period effects
            if effects['month_end_proximity'] <= 3:
                effects['expected_rebalancing'] = True
                effects['volatility_adjustment'] *= 1.2
                
            if effects['quarter_end_proximity'] <= 2:
                effects['expected_rebalancing'] = True
                effects['volatility_adjustment'] *= 1.4
                
            if effects['year_end_proximity'] <= 5:
                effects['expected_rebalancing'] = True
                effects['volatility_adjustment'] *= 1.6
            
            return effects
            
        except Exception as e:
            return {
                'month_end_proximity': 15,
                'quarter_end_proximity': 45,
                'year_end_proximity': 180,
                'expected_rebalancing': False,
                'volatility_adjustment': 1.0,
                'error': str(e)
            }
    
    def _calculate_month_end_proximity(self, date: datetime) -> int:
        """Calculate days until month end"""
        last_day = calendar.monthrange(date.year, date.month)[1]
        return last_day - date.day
    
    def _calculate_quarter_end_proximity(self, date: datetime) -> int:
        """Calculate days until quarter end"""
        quarter_end_months = [3, 6, 9, 12]
        current_quarter_end = None
        
        for month in quarter_end_months:
            if month >= date.month:
                current_quarter_end = month
                break
        
        if current_quarter_end is None:
            current_quarter_end = 12  # Next year's Q1
            
        if current_quarter_end == date.month:
            return self._calculate_month_end_proximity(date)
        else:
            # Calculate days to quarter end
            quarter_end_date = datetime(date.year, current_quarter_end, 1)
            last_day = calendar.monthrange(quarter_end_date.year, quarter_end_date.month)[1]
            quarter_end_date = quarter_end_date.replace(day=last_day)
            return (quarter_end_date - date).days
    
    def _calculate_year_end_proximity(self, date: datetime) -> int:
        """Calculate days until year end"""
        year_end = datetime(date.year, 12, 31)
        return (year_end - date).days
    
    def _calculate_overall_seasonal_bias(self, monthly: Dict[str, Any], weekly: Dict[str, Any],
                                       intraday: Dict[str, Any], eop: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall seasonal bias from all components"""
        try:
            bias_scores = []
            confidence_scores = []
            
            # Monthly bias
            if monthly.get('pattern_found'):
                monthly_bias = monthly['bias_strength'] if monthly['bias'] == 'bullish' else -monthly['bias_strength']
                bias_scores.append(monthly_bias * 0.4)  # 40% weight
                confidence_scores.append(monthly['confidence'] * 0.4)
            
            # Weekly bias
            if weekly.get('pattern_found'):
                weekly_bias = weekly['bias_strength'] if weekly['bias'] == 'bullish' else -weekly['bias_strength']
                bias_scores.append(weekly_bias * 0.3)  # 30% weight
                confidence_scores.append(weekly['confidence'] * 0.3)
            
            # Intraday bias (from volatility and breakout probability)
            intraday_bias = (intraday.get('breakout_probability', 0.5) - 0.5) * 2  # Convert to -1 to 1 scale
            bias_scores.append(intraday_bias * 0.2)  # 20% weight
            confidence_scores.append(0.6 * 0.2)  # Moderate confidence for intraday
            
            # End-of-period adjustment
            eop_adjustment = 1.0
            if eop.get('expected_rebalancing'):
                eop_adjustment = eop.get('volatility_adjustment', 1.0)
                bias_scores.append(0.1 * 0.1)  # Slight bullish bias for rebalancing
                confidence_scores.append(0.5 * 0.1)
            
            # Calculate overall bias
            overall_bias_score = sum(bias_scores) if bias_scores else 0.0
            overall_confidence = sum(confidence_scores) if confidence_scores else 0.3
            
            # Determine bias direction
            if overall_bias_score > 0.1:
                bias_direction = 'bullish'
            elif overall_bias_score < -0.1:
                bias_direction = 'bearish'
            else:
                bias_direction = 'neutral'
            
            return {
                'bias_direction': bias_direction,
                'bias_strength': abs(overall_bias_score),
                'confidence': overall_confidence,
                'volatility_adjustment': eop_adjustment,
                'component_contributions': {
                    'monthly': monthly.get('bias', 'neutral'),
                    'weekly': weekly.get('bias', 'neutral'),
                    'intraday': 'positive' if intraday_bias > 0 else 'negative' if intraday_bias < 0 else 'neutral',
                    'end_of_period': 'active' if eop.get('expected_rebalancing') else 'inactive'
                }
            }
            
        except Exception as e:
            return {
                'bias_direction': 'neutral',
                'bias_strength': 0.0,
                'confidence': 0.3,
                'volatility_adjustment': 1.0,
                'component_contributions': {},
                'error': str(e)
            }
    
    def _classify_seasonal_strength(self, overall_bias: Dict[str, Any]) -> str:
        """Classify the strength of seasonal patterns"""
        bias_strength = overall_bias.get('bias_strength', 0.0)
        confidence = overall_bias.get('confidence', 0.0)
        
        combined_strength = bias_strength * confidence
        
        if combined_strength > 0.4:
            return 'very_strong'
        elif combined_strength > 0.25:
            return 'strong'
        elif combined_strength > 0.15:
            return 'moderate'
        elif combined_strength > 0.05:
            return 'weak'
        else:
            return 'none'
    
    def _generate_seasonal_recommendations(self, overall_bias: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading recommendations based on seasonal analysis"""
        try:
            bias_direction = overall_bias.get('bias_direction', 'neutral')
            bias_strength = overall_bias.get('bias_strength', 0.0)
            confidence = overall_bias.get('confidence', 0.0)
            volatility_adj = overall_bias.get('volatility_adjustment', 1.0)
            
            recommendations = {
                'primary_bias': bias_direction,
                'conviction_level': 'high' if confidence > 0.7 else 'medium' if confidence > 0.4 else 'low',
                'position_sizing': 'normal',
                'volatility_expectation': 'normal',
                'time_horizon': 'medium_term'
            }
            
            # Adjust position sizing based on confidence
            if confidence > 0.8:
                recommendations['position_sizing'] = 'increased'
            elif confidence < 0.4:
                recommendations['position_sizing'] = 'reduced'
            
            # Adjust volatility expectation
            if volatility_adj > 1.3:
                recommendations['volatility_expectation'] = 'high'
            elif volatility_adj > 1.1:
                recommendations['volatility_expectation'] = 'elevated'
            elif volatility_adj < 0.8:
                recommendations['volatility_expectation'] = 'low'
            
            # Generate specific advice
            if bias_direction == 'bullish' and confidence > 0.6:
                recommendations['advice'] = 'Consider bullish positions with seasonal tailwinds'
            elif bias_direction == 'bearish' and confidence > 0.6:
                recommendations['advice'] = 'Consider bearish positions aligned with seasonal patterns'
            else:
                recommendations['advice'] = 'Neutral seasonal bias - focus on technical analysis'
            
            return recommendations
            
        except Exception as e:
            return {
                'primary_bias': 'neutral',
                'conviction_level': 'low',
                'position_sizing': 'reduced',
                'volatility_expectation': 'normal',
                'time_horizon': 'short_term',
                'advice': 'Seasonal analysis unavailable - use technical analysis',
                'error': str(e)
            }
    
    async def analyze_cyclical_patterns(self, symbol: str, price_history: pd.DataFrame = None) -> Dict[str, Any]:
        """Analyze cyclical patterns for the symbol"""
        try:
            if symbol not in self.cyclical_patterns:
                symbol = 'EURUSD'  # Default
            
            cycles = self.cyclical_patterns[symbol]
            cyclical_analysis = []
            
            for cycle in cycles:
                # Update cycle position based on current date/price
                updated_cycle = self._update_cycle_position(cycle, price_history)
                
                cycle_analysis = {
                    'cycle_name': updated_cycle.cycle_name,
                    'cycle_length': updated_cycle.cycle_length_days,
                    'current_position': updated_cycle.current_cycle_position,
                    'current_phase': updated_cycle.cycle_phase,
                    'expected_direction': updated_cycle.expected_direction,
                    'cycle_strength': updated_cycle.cycle_strength,
                    'days_to_next_phase': updated_cycle.time_to_next_phase,
                    'reliability': updated_cycle.reliability_score
                }
                
                cyclical_analysis.append(cycle_analysis)
            
            # Calculate overall cyclical bias
            overall_cyclical_bias = self._calculate_cyclical_bias(cyclical_analysis)
            
            return {
                'symbol': symbol,
                'cyclical_patterns': cyclical_analysis,
                'overall_bias': overall_cyclical_bias,
                'dominant_cycle': self._identify_dominant_cycle(cyclical_analysis),
                'cycle_confluence': self._calculate_cycle_confluence(cyclical_analysis)
            }
            
        except Exception as e:
            return {
                'symbol': symbol,
                'cyclical_patterns': [],
                'overall_bias': {'direction': 'neutral', 'strength': 0.0},
                'dominant_cycle': None,
                'cycle_confluence': 0.0,
                'error': str(e)
            }
    
    def _update_cycle_position(self, cycle: CyclicalPattern, price_history: pd.DataFrame = None) -> CyclicalPattern:
        """Update cycle position based on current market data"""
        # This is a simplified version - in production, you'd analyze actual price data
        # For now, we'll simulate cycle progression
        
        # Advance cycle position slightly
        new_position = (cycle.current_cycle_position + 0.02) % 1.0
        
        # Determine phase based on position
        if 0.0 <= new_position < 0.25:
            phase = 'accumulation'
            expected_direction = 'neutral'
        elif 0.25 <= new_position < 0.5:
            phase = 'markup'
            expected_direction = 'bullish'
        elif 0.5 <= new_position < 0.75:
            phase = 'distribution'
            expected_direction = 'neutral'
        else:
            phase = 'markdown'
            expected_direction = 'bearish'
        
        # Calculate time to next phase
        if new_position < 0.25:
            time_to_next = int((0.25 - new_position) * cycle.cycle_length_days)
        elif new_position < 0.5:
            time_to_next = int((0.5 - new_position) * cycle.cycle_length_days)
        elif new_position < 0.75:
            time_to_next = int((0.75 - new_position) * cycle.cycle_length_days)
        else:
            time_to_next = int((1.0 - new_position) * cycle.cycle_length_days)
        
        return CyclicalPattern(
            cycle.cycle_name,
            cycle.cycle_length_days,
            new_position,
            phase,
            expected_direction,
            cycle.cycle_strength,
            time_to_next,
            cycle.reliability_score
        )
    
    def _calculate_cyclical_bias(self, cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall bias from all cyclical patterns"""
        try:
            bullish_weight = 0.0
            bearish_weight = 0.0
            total_weight = 0.0
            
            for cycle in cycles:
                weight = cycle['cycle_strength'] * cycle['reliability']
                total_weight += weight
                
                if cycle['expected_direction'] == 'bullish':
                    bullish_weight += weight
                elif cycle['expected_direction'] == 'bearish':
                    bearish_weight += weight
            
            if total_weight == 0:
                return {'direction': 'neutral', 'strength': 0.0, 'confidence': 0.0}
            
            net_bias = (bullish_weight - bearish_weight) / total_weight
            
            if net_bias > 0.2:
                direction = 'bullish'
            elif net_bias < -0.2:
                direction = 'bearish'
            else:
                direction = 'neutral'
            
            return {
                'direction': direction,
                'strength': abs(net_bias),
                'confidence': total_weight / len(cycles) if cycles else 0.0
            }
            
        except Exception as e:
            return {'direction': 'neutral', 'strength': 0.0, 'confidence': 0.0, 'error': str(e)}
    
    def _identify_dominant_cycle(self, cycles: List[Dict[str, Any]]) -> Optional[str]:
        """Identify the dominant cycle affecting the market"""
        try:
            if not cycles:
                return None
            
            # Weight by strength and reliability
            max_influence = 0.0
            dominant_cycle = None
            
            for cycle in cycles:
                influence = cycle['cycle_strength'] * cycle['reliability']
                if influence > max_influence:
                    max_influence = influence
                    dominant_cycle = cycle['cycle_name']
            
            return dominant_cycle
            
        except Exception as e:
            return None
    
    def _calculate_cycle_confluence(self, cycles: List[Dict[str, Any]]) -> float:
        """Calculate confluence between different cycles"""
        try:
            if len(cycles) < 2:
                return 0.0
            
            aligned_cycles = 0
            total_pairs = 0
            
            for i in range(len(cycles)):
                for j in range(i + 1, len(cycles)):
                    total_pairs += 1
                    if cycles[i]['expected_direction'] == cycles[j]['expected_direction']:
                        aligned_cycles += 1
            
            return aligned_cycles / total_pairs if total_pairs > 0 else 0.0
            
        except Exception as e:
            return 0.0
    
    def _empty_seasonal_analysis(self, symbol: str, date: datetime) -> Dict[str, Any]:
        """Return empty seasonal analysis"""
        return {
            'analysis_date': date.isoformat() if date else datetime.now().isoformat(),
            'symbol': symbol,
            'monthly_seasonality': {'pattern_found': False, 'bias': 'neutral'},
            'weekly_seasonality': {'pattern_found': False, 'bias': 'neutral'},
            'intraday_patterns': {'session': 'unknown', 'volatility_expected': 'normal'},
            'end_of_period_effects': {'expected_rebalancing': False, 'volatility_adjustment': 1.0},
            'overall_seasonal_bias': {'bias_direction': 'neutral', 'bias_strength': 0.0, 'confidence': 0.0},
            'seasonal_strength': 'none',
            'trading_recommendations': {'primary_bias': 'neutral', 'conviction_level': 'low'}
        }

# Global instance
_seasonal_analyzer = None

async def get_seasonal_analyzer() -> SeasonalCyclicalAnalyzer:
    """Get or create the global seasonal analyzer instance"""
    global _seasonal_analyzer
    if _seasonal_analyzer is None:
        _seasonal_analyzer = SeasonalCyclicalAnalyzer()
    return _seasonal_analyzer

async def analyze_seasonal_patterns(symbol: str, current_date: datetime = None) -> Dict[str, Any]:
    """Analyze seasonal patterns for a symbol"""
    analyzer = await get_seasonal_analyzer()
    return await analyzer.analyze_seasonal_patterns(symbol, current_date)

async def analyze_cyclical_patterns(symbol: str, price_history: pd.DataFrame = None) -> Dict[str, Any]:
    """Analyze cyclical patterns for a symbol"""
    analyzer = await get_seasonal_analyzer()
    return await analyzer.analyze_cyclical_patterns(symbol, price_history)

async def get_comprehensive_seasonal_analysis(symbol: str, price_history: pd.DataFrame = None) -> Dict[str, Any]:
    """Get comprehensive seasonal and cyclical analysis"""
    try:
        analyzer = await get_seasonal_analyzer()
        
        # Run both analyses
        seasonal_analysis = await analyzer.analyze_seasonal_patterns(symbol)
        cyclical_analysis = await analyzer.analyze_cyclical_patterns(symbol, price_history)
        
        # Combine analyses
        combined_bias = _combine_seasonal_cyclical_bias(
            seasonal_analysis['overall_seasonal_bias'],
            cyclical_analysis['overall_bias']
        )
        
        return {
            'symbol': symbol,
            'seasonal_analysis': seasonal_analysis,
            'cyclical_analysis': cyclical_analysis,
            'combined_bias': combined_bias,
            'comprehensive_recommendations': _generate_comprehensive_recommendations(
                seasonal_analysis, cyclical_analysis, combined_bias
            ),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'symbol': symbol,
            'seasonal_analysis': {},
            'cyclical_analysis': {},
            'combined_bias': {'direction': 'neutral', 'strength': 0.0},
            'comprehensive_recommendations': {'advice': 'Analysis unavailable'},
            'analysis_timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

def _combine_seasonal_cyclical_bias(seasonal_bias: Dict[str, Any], cyclical_bias: Dict[str, Any]) -> Dict[str, Any]:
    """Combine seasonal and cyclical bias into overall assessment"""
    try:
        seasonal_strength = seasonal_bias.get('bias_strength', 0.0)
        seasonal_direction = seasonal_bias.get('bias_direction', 'neutral')
        seasonal_confidence = seasonal_bias.get('confidence', 0.0)
        
        cyclical_strength = cyclical_bias.get('strength', 0.0)
        cyclical_direction = cyclical_bias.get('direction', 'neutral')
        cyclical_confidence = cyclical_bias.get('confidence', 0.0)
        
        # Weight seasonal and cyclical components
        seasonal_weight = 0.6
        cyclical_weight = 0.4
        
        # Calculate combined direction
        seasonal_score = seasonal_strength if seasonal_direction == 'bullish' else -seasonal_strength if seasonal_direction == 'bearish' else 0.0
        cyclical_score = cyclical_strength if cyclical_direction == 'bullish' else -cyclical_strength if cyclical_direction == 'bearish' else 0.0
        
        combined_score = (seasonal_score * seasonal_weight) + (cyclical_score * cyclical_weight)
        combined_strength = abs(combined_score)
        
        if combined_score > 0.1:
            combined_direction = 'bullish'
        elif combined_score < -0.1:
            combined_direction = 'bearish'
        else:
            combined_direction = 'neutral'
        
        combined_confidence = (seasonal_confidence * seasonal_weight) + (cyclical_confidence * cyclical_weight)
        
        return {
            'direction': combined_direction,
            'strength': combined_strength,
            'confidence': combined_confidence,
            'seasonal_contribution': seasonal_score * seasonal_weight,
            'cyclical_contribution': cyclical_score * cyclical_weight,
            'alignment': 'aligned' if seasonal_direction == cyclical_direction else 'conflicted' if seasonal_direction != 'neutral' and cyclical_direction != 'neutral' else 'partial'
        }
        
    except Exception as e:
        return {
            'direction': 'neutral',
            'strength': 0.0,
            'confidence': 0.0,
            'seasonal_contribution': 0.0,
            'cyclical_contribution': 0.0,
            'alignment': 'unknown',
            'error': str(e)
        }

def _generate_comprehensive_recommendations(seasonal_analysis: Dict[str, Any], 
                                         cyclical_analysis: Dict[str, Any],
                                         combined_bias: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive trading recommendations"""
    try:
        direction = combined_bias.get('direction', 'neutral')
        strength = combined_bias.get('strength', 0.0)
        confidence = combined_bias.get('confidence', 0.0)
        alignment = combined_bias.get('alignment', 'unknown')
        
        recommendations = {
            'primary_recommendation': direction,
            'conviction_level': 'high' if confidence > 0.7 else 'medium' if confidence > 0.4 else 'low',
            'time_horizon': 'medium_term',
            'position_sizing': 'normal'
        }
        
        # Adjust based on alignment
        if alignment == 'aligned' and confidence > 0.6:
            recommendations['conviction_level'] = 'high'
            recommendations['position_sizing'] = 'increased'
        elif alignment == 'conflicted':
            recommendations['conviction_level'] = 'low'
            recommendations['position_sizing'] = 'reduced'
        
        # Generate specific advice
        seasonal_strength = seasonal_analysis.get('seasonal_strength', 'none')
        cyclical_confluence = cyclical_analysis.get('cycle_confluence', 0.0)
        
        if direction != 'neutral' and confidence > 0.6:
            if seasonal_strength in ['strong', 'very_strong'] and cyclical_confluence > 0.7:
                recommendations['advice'] = f'Strong {direction} bias with seasonal and cyclical confluence'
            elif seasonal_strength in ['strong', 'very_strong']:
                recommendations['advice'] = f'Seasonal patterns favor {direction} direction'
            elif cyclical_confluence > 0.7:
                recommendations['advice'] = f'Cyclical patterns align for {direction} movement'
            else:
                recommendations['advice'] = f'Moderate {direction} bias from combined analysis'
        else:
            recommendations['advice'] = 'Neutral seasonal/cyclical bias - rely on technical analysis'
        
        return recommendations
        
    except Exception as e:
        return {
            'primary_recommendation': 'neutral',
            'conviction_level': 'low',
            'time_horizon': 'short_term',
            'position_sizing': 'reduced',
            'advice': 'Seasonal/cyclical analysis unavailable',
            'error': str(e)
        }