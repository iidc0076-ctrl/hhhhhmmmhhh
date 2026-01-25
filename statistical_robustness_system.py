#!/usr/bin/env python3
"""
Statistical Robustness System for QuantVision Trading Bot
Advanced validation system to improve win rates through cross-regime testing and curve-fitting prevention
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass
from enum import Enum
import statistics
from safe_math_utils import safe_mean, safe_std, safe_divide

class MarketRegime(Enum):
    STRONG_UPTREND = "strong_uptrend"
    WEAK_UPTREND = "weak_uptrend"
    STRONG_DOWNTREND = "strong_downtrend"
    WEAK_DOWNTREND = "weak_downtrend"
    CONSOLIDATION = "consolidation"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"

@dataclass
class RobustnessMetrics:
    signal_strength: float
    regime_consistency: float
    stability_score: float
    overfitting_risk: float
    cross_validation_score: float
    regime_performance: Dict[str, float]
    recommendation: str
    confidence_adjustment: float

class StatisticalRobustnessEngine:
    """Advanced statistical validation system for trading signals"""
    
    def __init__(self):
        self.min_samples_per_regime = 50  # Minimum samples needed for robust validation
        self.min_regimes_required = 5     # Minimum regimes signal must work in
        self.stability_threshold = 0.65   # Minimum stability score for acceptance
        self.overfitting_threshold = 0.3  # Maximum overfitting risk allowed
        
        # Performance thresholds for each regime
        self.regime_thresholds = {
            MarketRegime.STRONG_UPTREND: 0.68,
            MarketRegime.WEAK_UPTREND: 0.62,
            MarketRegime.STRONG_DOWNTREND: 0.68,
            MarketRegime.WEAK_DOWNTREND: 0.62,
            MarketRegime.CONSOLIDATION: 0.58,
            MarketRegime.HIGH_VOLATILITY: 0.60,
            MarketRegime.LOW_VOLATILITY: 0.65,
            MarketRegime.BREAKOUT: 0.72,
            MarketRegime.REVERSAL: 0.58
        }
    
    async def validate_signal_robustness(self, signal_data: Dict[str, Any], 
                                       df: pd.DataFrame, 
                                       extended_history: Optional[pd.DataFrame] = None) -> RobustnessMetrics:
        """
        Comprehensive statistical robustness validation for trading signals
        """
        try:
            # Use extended history if available, otherwise generate synthetic regimes
            if extended_history is not None and len(extended_history) > 500:
                validation_data = extended_history
            else:
                validation_data = await self._generate_extended_validation_data(df)
            
            # Identify market regimes in the data
            regime_classifications = self._classify_market_regimes(validation_data)
            
            # Test signal performance across all regimes
            regime_performance = await self._test_cross_regime_performance(
                signal_data, validation_data, regime_classifications
            )
            
            # Calculate robustness metrics
            stability_score = self._calculate_stability_score(regime_performance)
            overfitting_risk = self._calculate_overfitting_risk(regime_performance)
            cross_validation_score = await self._perform_cross_validation(
                signal_data, validation_data, regime_classifications
            )
            
            # Calculate regime consistency
            regime_consistency = self._calculate_regime_consistency(regime_performance)
            
            # Overall signal strength assessment
            signal_strength = self._calculate_overall_signal_strength(
                regime_performance, stability_score, cross_validation_score
            )
            
            # Generate recommendation and confidence adjustment
            recommendation, confidence_adjustment = self._generate_robustness_recommendation(
                stability_score, overfitting_risk, regime_consistency, signal_strength
            )
            
            return RobustnessMetrics(
                signal_strength=signal_strength,
                regime_consistency=regime_consistency,
                stability_score=stability_score,
                overfitting_risk=overfitting_risk,
                cross_validation_score=cross_validation_score,
                regime_performance=regime_performance,
                recommendation=recommendation,
                confidence_adjustment=confidence_adjustment
            )
            
        except Exception as e:
            print(f"Error in robustness validation: {e}")
            return self._default_robustness_metrics()
    
    def _classify_market_regimes(self, df: pd.DataFrame) -> Dict[int, MarketRegime]:
        """
        Classify each period in the data into market regimes
        """
        regimes = {}
        
        try:
            # Calculate technical indicators for regime classification
            close = df['close']
            high = df['high']
            low = df['low']
            volume = df.get('volume', pd.Series([1000] * len(df)))
            
            # Trend indicators
            sma_short = close.rolling(window=20).mean()
            sma_long = close.rolling(window=50).mean()
            
            # Volatility indicators
            returns = close.pct_change()
            volatility = returns.rolling(window=20).std() * np.sqrt(252)
            
            # ADX for trend strength
            adx = self._calculate_adx(df)
            
            for i in range(50, len(df)):  # Start after sufficient data for indicators
                current_close = close.iloc[i]
                current_sma_short = sma_short.iloc[i]
                current_sma_long = sma_long.iloc[i]
                current_vol = volatility.iloc[i]
                current_adx = adx.iloc[i] if i < len(adx) else 20
                
                # Trend direction and strength
                if current_sma_short > current_sma_long:
                    if current_adx > 30:
                        regimes[i] = MarketRegime.STRONG_UPTREND
                    else:
                        regimes[i] = MarketRegime.WEAK_UPTREND
                else:
                    if current_adx > 30:
                        regimes[i] = MarketRegime.STRONG_DOWNTREND
                    else:
                        regimes[i] = MarketRegime.WEAK_DOWNTREND
                
                # Override with volatility-based regimes
                if current_vol > volatility.quantile(0.8):
                    regimes[i] = MarketRegime.HIGH_VOLATILITY
                elif current_vol < volatility.quantile(0.2):
                    regimes[i] = MarketRegime.LOW_VOLATILITY
                
                # Check for consolidation
                if current_adx < 20 and current_vol < volatility.median():
                    regimes[i] = MarketRegime.CONSOLIDATION
                
                # Check for breakouts (high volume + high volatility + strong trend)
                if (current_adx > 35 and current_vol > volatility.quantile(0.7) and
                    volume.iloc[i] > volume.rolling(window=20).mean().iloc[i] * 1.5):
                    regimes[i] = MarketRegime.BREAKOUT
                
                # Check for reversals (changing trend direction with high volatility)
                if i > 60:
                    prev_trend = 1 if sma_short.iloc[i-20] > sma_long.iloc[i-20] else -1
                    curr_trend = 1 if current_sma_short > current_sma_long else -1
                    if prev_trend != curr_trend and current_vol > volatility.quantile(0.6):
                        regimes[i] = MarketRegime.REVERSAL
            
            return regimes
            
        except Exception as e:
            print(f"Error classifying market regimes: {e}")
            return {}
    
    async def _test_cross_regime_performance(self, signal_data: Dict[str, Any], 
                                           df: pd.DataFrame, 
                                           regimes: Dict[int, MarketRegime]) -> Dict[str, float]:
        """
        Test signal performance across different market regimes
        """
        regime_performance = {}
        
        try:
            # Group data by regime
            regime_groups = {}
            for idx, regime in regimes.items():
                if regime.value not in regime_groups:
                    regime_groups[regime.value] = []
                regime_groups[regime.value].append(idx)
            
            # Test performance in each regime
            for regime_name, indices in regime_groups.items():
                if len(indices) < self.min_samples_per_regime:
                    continue  # Skip regimes with insufficient data
                
                # Extract regime-specific data
                regime_df = df.iloc[indices].copy()
                
                # Simulate signal performance in this regime
                regime_win_rate = await self._simulate_regime_performance(
                    signal_data, regime_df, regime_name
                )
                
                regime_performance[regime_name] = regime_win_rate
            
            return regime_performance
            
        except Exception as e:
            print(f"Error testing cross-regime performance: {e}")
            return {}
    
    async def _simulate_regime_performance(self, signal_data: Dict[str, Any], 
                                         regime_df: pd.DataFrame, 
                                         regime_name: str) -> float:
        """
        Simulate signal performance in a specific market regime
        """
        try:
            # Apply signal logic to regime data
            signal_direction = signal_data.get('signal', 'NEUTRAL')
            base_confidence = signal_data.get('confidence', 50)
            
            if signal_direction == 'NEUTRAL' or len(regime_df) < 10:
                return 0.5  # Neutral performance
            
            # Analyze regime characteristics for signal effectiveness
            returns = regime_df['close'].pct_change().dropna()
            
            if signal_direction == 'BUY':
                # For BUY signals, check how often price went up
                positive_moves = (returns > 0).sum()
                win_rate = positive_moves / len(returns)
            else:  # SELL signals
                # For SELL signals, check how often price went down
                negative_moves = (returns < 0).sum()
                win_rate = negative_moves / len(returns)
            
            # Adjust based on signal confidence and regime characteristics
            confidence_factor = base_confidence / 100.0
            regime_adjusted_rate = win_rate * confidence_factor + 0.5 * (1 - confidence_factor)
            
            return min(max(regime_adjusted_rate, 0.3), 0.9)  # Reasonable bounds
            
        except Exception as e:
            print(f"Error simulating regime performance: {e}")
            return 0.5
    
    def _calculate_stability_score(self, regime_performance: Dict[str, float]) -> float:
        """
        Calculate stability score based on performance consistency across regimes
        """
        try:
            if not regime_performance:
                return 0.0
            
            performances = list(regime_performance.values())
            
            # Calculate coefficient of variation (lower is more stable)
            mean_performance = safe_mean(performances)
            std_performance = safe_std(performances)
            
            if mean_performance == 0:
                return 0.0
            
            cv = std_performance / mean_performance
            
            # Convert to stability score (higher is better)
            stability_score = max(0, 1 - cv)
            
            # Bonus for high average performance
            performance_bonus = max(0, mean_performance - 0.6) * 0.5
            
            return min(stability_score + performance_bonus, 1.0)
            
        except Exception:
            return 0.0
    
    def _calculate_overfitting_risk(self, regime_performance: Dict[str, float]) -> float:
        """
        Calculate overfitting risk based on extreme performance variations
        """
        try:
            if len(regime_performance) < 3:
                return 1.0  # High risk if not enough regimes tested
            
            performances = list(regime_performance.values())
            
            # Check for extreme outliers
            q75 = np.percentile(performances, 75)
            q25 = np.percentile(performances, 25)
            iqr = q75 - q25
            
            outliers = [p for p in performances if p > q75 + 1.5 * iqr or p < q25 - 1.5 * iqr]
            outlier_ratio = len(outliers) / len(performances)
            
            # Check for very high performance in any single regime
            max_performance = max(performances)
            min_performance = min(performances)
            performance_range = max_performance - min_performance
            
            # Risk factors
            outlier_risk = outlier_ratio * 0.4
            range_risk = min(performance_range, 0.5) * 0.6
            
            total_risk = outlier_risk + range_risk
            
            return min(total_risk, 1.0)
            
        except Exception:
            return 0.5
    
    async def _perform_cross_validation(self, signal_data: Dict[str, Any], 
                                      df: pd.DataFrame, 
                                      regimes: Dict[int, MarketRegime]) -> float:
        """
        Perform k-fold cross-validation across time periods
        """
        try:
            # Split data into 5 folds temporally
            n_folds = 5
            fold_size = len(df) // n_folds
            validation_scores = []
            
            for fold in range(n_folds):
                start_idx = fold * fold_size
                end_idx = (fold + 1) * fold_size if fold < n_folds - 1 else len(df)
                
                # Use this fold as validation set
                validation_df = df.iloc[start_idx:end_idx]
                
                # Test signal on validation fold
                fold_score = await self._simulate_regime_performance(
                    signal_data, validation_df, "cross_validation"
                )
                
                validation_scores.append(fold_score)
            
            # Return average cross-validation score
            return safe_mean(validation_scores)
            
        except Exception:
            return 0.5
    
    def _calculate_regime_consistency(self, regime_performance: Dict[str, float]) -> float:
        """
        Calculate how consistently the signal performs across regimes
        """
        try:
            if not regime_performance:
                return 0.0
            
            # Count regimes where performance exceeds threshold
            passing_regimes = 0
            total_regimes = len(regime_performance)
            
            for regime_name, performance in regime_performance.items():
                try:
                    regime_enum = MarketRegime(regime_name)
                    threshold = self.regime_thresholds.get(regime_enum, 0.6)
                    if performance >= threshold:
                        passing_regimes += 1
                except ValueError:
                    # Unknown regime, use default threshold
                    if performance >= 0.6:
                        passing_regimes += 1
            
            consistency_ratio = passing_regimes / total_regimes
            
            # Require performance in minimum number of regimes
            if total_regimes < self.min_regimes_required:
                consistency_ratio *= 0.7  # Penalty for insufficient regime coverage
            
            return consistency_ratio
            
        except Exception:
            return 0.0
    
    def _calculate_overall_signal_strength(self, regime_performance: Dict[str, float], 
                                         stability_score: float, 
                                         cross_validation_score: float) -> float:
        """
        Calculate overall signal strength combining all metrics
        """
        try:
            if not regime_performance:
                return 0.0
            
            # Average regime performance (40% weight)
            avg_performance = safe_mean(list(regime_performance.values())) * 0.4
            
            # Stability score (30% weight)
            stability_component = stability_score * 0.3
            
            # Cross-validation score (30% weight)
            cv_component = cross_validation_score * 0.3
            
            overall_strength = avg_performance + stability_component + cv_component
            
            return min(overall_strength, 1.0)
            
        except Exception:
            return 0.0
    
    def _generate_robustness_recommendation(self, stability_score: float, 
                                          overfitting_risk: float, 
                                          regime_consistency: float, 
                                          signal_strength: float) -> Tuple[str, float]:
        """
        Generate recommendation and confidence adjustment based on robustness analysis
        """
        try:
            # Confidence adjustment calculation
            base_adjustment = 0.0
            
            # Reward high stability
            if stability_score >= 0.8:
                base_adjustment += 8.0
            elif stability_score >= 0.65:
                base_adjustment += 4.0
            
            # Reward regime consistency
            if regime_consistency >= 0.8:
                base_adjustment += 6.0
            elif regime_consistency >= 0.6:
                base_adjustment += 3.0
            
            # Penalize overfitting risk
            if overfitting_risk <= 0.2:
                base_adjustment += 3.0
            elif overfitting_risk >= 0.5:
                base_adjustment -= 5.0
            
            # Reward high signal strength
            if signal_strength >= 0.75:
                base_adjustment += 5.0
            elif signal_strength >= 0.65:
                base_adjustment += 2.0
            elif signal_strength < 0.5:
                base_adjustment -= 8.0
            
            # Generate recommendation
            if (stability_score >= self.stability_threshold and 
                overfitting_risk <= self.overfitting_threshold and 
                regime_consistency >= 0.6):
                recommendation = "ROBUST_SIGNAL"
            elif stability_score >= 0.5 and overfitting_risk <= 0.4:
                recommendation = "MODERATE_SIGNAL"
            elif overfitting_risk > 0.6:
                recommendation = "OVERFITTED_SIGNAL"
            else:
                recommendation = "WEAK_SIGNAL"
            
            # Cap adjustment
            confidence_adjustment = max(min(base_adjustment, 15.0), -15.0)
            
            return recommendation, confidence_adjustment
            
        except Exception:
            return "UNKNOWN_SIGNAL", 0.0
    
    async def _generate_extended_validation_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate extended validation data with multiple market scenarios
        """
        try:
            # Create synthetic market scenarios based on historical patterns
            base_data = df.copy()
            extended_data = []
            
            # Original data
            extended_data.append(base_data)
            
            # Generate trending scenarios
            trend_data = self._create_trending_scenario(base_data)
            extended_data.append(trend_data)
            
            # Generate ranging scenarios
            range_data = self._create_ranging_scenario(base_data)
            extended_data.append(range_data)
            
            # Generate high volatility scenarios
            volatile_data = self._create_volatile_scenario(base_data)
            extended_data.append(volatile_data)
            
            # Combine all scenarios
            combined_data = pd.concat(extended_data, ignore_index=True)
            
            return combined_data
            
        except Exception as e:
            print(f"Error generating extended validation data: {e}")
            return df
    
    def _create_trending_scenario(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create a trending market scenario"""
        try:
            trend_df = df.copy()
            trend_factor = np.linspace(1.0, 1.05, len(df))  # 5% uptrend
            
            trend_df['close'] = trend_df['close'] * trend_factor
            trend_df['high'] = trend_df['high'] * trend_factor
            trend_df['low'] = trend_df['low'] * trend_factor
            trend_df['open'] = trend_df['open'] * trend_factor
            
            return trend_df
        except Exception:
            return df
    
    def _create_ranging_scenario(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create a ranging market scenario"""
        try:
            range_df = df.copy()
            # Add oscillating pattern
            oscillation = np.sin(np.linspace(0, 4*np.pi, len(df))) * 0.002
            
            range_df['close'] = range_df['close'] * (1 + oscillation)
            range_df['high'] = range_df['high'] * (1 + oscillation + 0.001)
            range_df['low'] = range_df['low'] * (1 + oscillation - 0.001)
            
            return range_df
        except Exception:
            return df
    
    def _create_volatile_scenario(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create a high volatility scenario"""
        try:
            volatile_df = df.copy()
            # Increase volatility by 50%
            returns = volatile_df['close'].pct_change()
            enhanced_returns = returns * 1.5
            
            # Reconstruct prices
            new_close = [volatile_df['close'].iloc[0]]
            for ret in enhanced_returns.iloc[1:]:
                if pd.notna(ret):
                    new_price = new_close[-1] * (1 + ret)
                    new_close.append(new_price)
                else:
                    new_close.append(new_close[-1])
            
            volatile_df['close'] = new_close
            
            return volatile_df
        except Exception:
            return df
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ADX indicator"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # Calculate directional movement
            dm_plus = high.diff()
            dm_minus = low.diff() * -1
            
            # True range
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Smooth the values
            tr_smooth = tr.rolling(window=period).mean()
            dm_plus_smooth = dm_plus.rolling(window=period).mean()
            dm_minus_smooth = dm_minus.rolling(window=period).mean()
            
            # Calculate DI+ and DI-
            di_plus = 100 * dm_plus_smooth / tr_smooth
            di_minus = 100 * dm_minus_smooth / tr_smooth
            
            # Calculate ADX
            dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
            adx = dx.rolling(window=period).mean()
            
            return adx.where(adx.notna(), 20)  # Default neutral ADX
            
        except Exception:
            return pd.Series([20] * len(df))  # Default values
    
    def _default_robustness_metrics(self) -> RobustnessMetrics:
        """Return default robustness metrics for error cases"""
        return RobustnessMetrics(
            signal_strength=0.5,
            regime_consistency=0.5,
            stability_score=0.5,
            overfitting_risk=0.5,
            cross_validation_score=0.5,
            regime_performance={},
            recommendation="UNKNOWN_SIGNAL",
            confidence_adjustment=0.0
        )

# Global instance
_robustness_engine = None

async def get_robustness_engine() -> StatisticalRobustnessEngine:
    """Get or create the global robustness engine"""
    global _robustness_engine
    if _robustness_engine is None:
        _robustness_engine = StatisticalRobustnessEngine()
    return _robustness_engine

async def validate_signal_robustness(signal_data: Dict[str, Any], 
                                   df: pd.DataFrame,
                                   extended_history: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Main function to validate signal robustness and improve win rate
    """
    try:
        engine = await get_robustness_engine()
        metrics = await engine.validate_signal_robustness(signal_data, df, extended_history)
        
        return {
            'robustness_validated': True,
            'signal_strength': metrics.signal_strength,
            'regime_consistency': metrics.regime_consistency,
            'stability_score': metrics.stability_score,
            'overfitting_risk': metrics.overfitting_risk,
            'cross_validation_score': metrics.cross_validation_score,
            'regime_performance': metrics.regime_performance,
            'recommendation': metrics.recommendation,
            'confidence_adjustment': metrics.confidence_adjustment,
            'pass_robustness_filter': metrics.recommendation in ['ROBUST_SIGNAL', 'MODERATE_SIGNAL']
        }
        
    except Exception as e:
        print(f"Error in robustness validation: {e}")
        return {
            'robustness_validated': False,
            'confidence_adjustment': 0.0,
            'recommendation': 'VALIDATION_ERROR',
            'pass_robustness_filter': False
        }

def format_robustness_analysis(robustness_data: Dict[str, Any]) -> str:
    """Format robustness analysis for Discord display"""
    try:
        if not robustness_data.get('robustness_validated', False):
            return "⚠️ Robustness validation unavailable"
        
        recommendation = robustness_data.get('recommendation', 'UNKNOWN')
        confidence_adj = robustness_data.get('confidence_adjustment', 0)
        
        # Status emoji
        status_emojis = {
            'ROBUST_SIGNAL': '🟢',
            'MODERATE_SIGNAL': '🟡',
            'WEAK_SIGNAL': '🟠',
            'OVERFITTED_SIGNAL': '🔴',
            'UNKNOWN_SIGNAL': '⚪'
        }
        
        status_emoji = status_emojis.get(recommendation, '⚪')
        
        # Format output
        lines = [
            f"{status_emoji} **Robustness: {recommendation.replace('_', ' ').title()}**",
            f"📊 Signal Strength: {robustness_data.get('signal_strength', 0):.1%}",
            f"⚖️ Stability Score: {robustness_data.get('stability_score', 0):.1%}",
            f"🎯 Regime Consistency: {robustness_data.get('regime_consistency', 0):.1%}",
            f"📈 Confidence Adjust: {confidence_adj:+.1f}%"
        ]
        
        return "\n".join(lines)
        
    except Exception:
        return "⚠️ Error formatting robustness analysis"

if __name__ == "__main__":
    print("🔬 Statistical Robustness System")
    print("Advanced validation for improved win rates")
    print("Testing across market regimes to prevent overfitting")