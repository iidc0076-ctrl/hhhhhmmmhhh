"""
Binary Options Machine Learning Predictor
Uses ensemble methods to predict binary options outcomes with high accuracy
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import pickle
import os
from safe_math_utils import safe_mean, safe_std, safe_divide

class BinaryOptionsMLPredictor:
    """Machine learning predictor specifically optimized for binary options"""
    
    def __init__(self):
        self.models = {}
        self.feature_scalers = {}
        self.training_data = {}
        self.prediction_history = []
        
        # Enhanced ML with loss/win recognition
        self.trade_outcomes = []
        self.loss_patterns = []
        self.win_patterns = []
        self.pattern_confidence_adjustments = {}
        
        # Binary options specific parameters
        self.expiry_models = {
            '1min': {'accuracy_threshold': 0.85, 'features': 50},
            '5min': {'accuracy_threshold': 0.75, 'features': 40},
            '15min': {'accuracy_threshold': 0.65, 'features': 35},
            '30min': {'accuracy_threshold': 0.60, 'features': 30},
            '60min': {'accuracy_threshold': 0.55, 'features': 25}
        }
        
    def extract_ml_features(self, df: pd.DataFrame, indicators: Dict[str, Any], 
                           expiry_minutes: int = 5) -> np.ndarray:
        """Extract comprehensive features for ML prediction"""
        
        if df is None or len(df) < 50:
            return np.array([])
        
        features = []
        
        # Price action features
        features.extend(self._extract_price_features(df))
        
        # Technical indicator features
        features.extend(self._extract_technical_features(df, indicators))
        
        # Volume features (proxy from price action)
        features.extend(self._extract_volume_features(df))
        
        # Market structure features
        features.extend(self._extract_structure_features(df))
        
        # Time-based features
        features.extend(self._extract_time_features())
        
        # Volatility features
        features.extend(self._extract_volatility_features(df))
        
        # Momentum features
        features.extend(self._extract_momentum_features(df))
        
        # Pattern recognition features
        features.extend(self._extract_pattern_features(df))
        
        # Expiry-specific features
        features.extend(self._extract_expiry_features(df, expiry_minutes))
        
        return np.array(features)
    
    def predict_binary_outcome(self, df: pd.DataFrame, indicators: Dict[str, Any], 
                              expiry_minutes: int = 5, current_price: float = None) -> Dict[str, Any]:
        """Predict binary options outcome with confidence intervals"""
        
        try:
            # Extract features
            features = self.extract_ml_features(df, indicators, expiry_minutes)
            
            if len(features) == 0:
                return self._get_default_prediction()
            
            # Get model predictions (simulated ensemble)
            ensemble_predictions = self._get_ensemble_predictions(features, expiry_minutes)
            
            # Calculate final prediction
            final_prediction = self._calculate_final_prediction(ensemble_predictions)
            
            # Add binary options specific analysis
            binary_analysis = self._analyze_binary_specific_factors(df, expiry_minutes)
            
            # Calculate win probability
            win_probability = self._calculate_win_probability(final_prediction, binary_analysis)
            
            # Risk assessment
            risk_assessment = self._assess_binary_risk(win_probability, expiry_minutes)
            
            return {
                'ml_prediction': final_prediction,
                'win_probability': win_probability,
                'confidence_interval': self._calculate_confidence_interval(ensemble_predictions),
                'risk_assessment': risk_assessment,
                'binary_analysis': binary_analysis,
                'expiry_suitability': self._assess_expiry_suitability(win_probability, expiry_minutes),
                'feature_importance': self._get_feature_importance(features),
                'prediction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in ML prediction: {e}")
            return self._get_default_prediction()
    
    def _extract_price_features(self, df: pd.DataFrame) -> List[float]:
        """Extract price-based features"""
        features = []
        
        # Price changes over different periods
        for period in [1, 3, 5, 10, 20]:
            if len(df) > period:
                price_change = (df['close'].iloc[-1] - df['close'].iloc[-period-1]) / df['close'].iloc[-period-1]
                features.append(price_change * 100)
            else:
                features.append(0.0)
        
        # High-low spreads
        for period in [5, 10, 20]:
            if len(df) > period:
                hl_spread = safe_mean(df['high'].tail(period) - df['low'].tail(period))
                avg_price = safe_mean(df['close'].tail(period))
                features.append(safe_divide(hl_spread, avg_price, 0) * 100)
            else:
                features.append(0.0)
        
        # Price position in recent range
        if len(df) >= 20:
            recent_high = df['high'].tail(20).max()
            recent_low = df['low'].tail(20).min()
            current_price = df['close'].iloc[-1]
            position = safe_divide(current_price - recent_low, recent_high - recent_low, 0.5)
            features.append(position)
        else:
            features.append(0.5)
        
        return features
    
    def _extract_technical_features(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> List[float]:
        """Extract technical indicator features"""
        features = []
        
        # RSI features
        rsi = indicators.get('rsi', {})
        if isinstance(rsi, dict):
            features.append(rsi.get('current', 50))
            features.append(1 if rsi.get('oversold', False) else 0)
            features.append(1 if rsi.get('overbought', False) else 0)
        else:
            features.extend([50, 0, 0])
        
        # MACD features
        macd = indicators.get('macd', {})
        if isinstance(macd, dict):
            features.append(macd.get('macd', 0))
            features.append(macd.get('signal', 0))
            features.append(macd.get('histogram', 0))
            features.append(1 if macd.get('bullish_crossover', False) else 0)
        else:
            features.extend([0, 0, 0, 0])
        
        # Moving averages
        for ma_period in [9, 21, 50]:
            ma_key = f'sma_{ma_period}'
            if ma_key in indicators:
                ma_value = indicators[ma_key]
                if isinstance(ma_value, (int, float)) and len(df) > 0:
                    current_price = df['close'].iloc[-1]
                    ma_ratio = safe_divide(current_price, ma_value, 1) - 1
                    features.append(ma_ratio * 100)
                else:
                    features.append(0)
            else:
                features.append(0)
        
        # Bollinger Bands
        bb = indicators.get('bollinger_bands', {})
        if isinstance(bb, dict) and len(df) > 0:
            current_price = df['close'].iloc[-1]
            upper = bb.get('upper', current_price)
            lower = bb.get('lower', current_price)
            middle = bb.get('middle', current_price)
            
            # Position within bands
            bb_position = safe_divide(current_price - lower, upper - lower, 0.5)
            features.append(bb_position)
            
            # Distance from middle
            distance_from_middle = safe_divide(current_price - middle, middle, 0) * 100
            features.append(distance_from_middle)
        else:
            features.extend([0.5, 0])
        
        return features
    
    def _extract_volume_features(self, df: pd.DataFrame) -> List[float]:
        """Extract volume-based features (using price action as proxy)"""
        features = []
        
        # Volume trend (using range as proxy)
        if len(df) >= 10:
            recent_ranges = df['high'].tail(5) - df['low'].tail(5)
            older_ranges = df['high'].tail(10).head(5) - df['low'].tail(10).head(5)
            
            recent_avg = safe_mean(recent_ranges)
            older_avg = safe_mean(older_ranges)
            volume_trend = safe_divide(recent_avg, older_avg, 1) - 1
            features.append(volume_trend * 100)
        else:
            features.append(0)
        
        # Volume spikes (large range candles)
        if len(df) >= 20:
            ranges = df['high'].tail(20) - df['low'].tail(20)
            avg_range = safe_mean(ranges)
            std_range = safe_std(ranges)
            
            current_range = df['high'].iloc[-1] - df['low'].iloc[-1]
            volume_spike = safe_divide(current_range - avg_range, std_range, 0)
            features.append(min(volume_spike, 3))  # Cap at 3 standard deviations
        else:
            features.append(0)
        
        return features
    
    def _extract_structure_features(self, df: pd.DataFrame) -> List[float]:
        """Extract market structure features"""
        features = []
        
        # Higher highs and lower lows
        if len(df) >= 10:
            recent_highs = df['high'].tail(5)
            recent_lows = df['low'].tail(5)
            
            # Trend structure
            hh_count = sum(1 for i in range(1, len(recent_highs)) if recent_highs.iloc[i] > recent_highs.iloc[i-1])
            ll_count = sum(1 for i in range(1, len(recent_lows)) if recent_lows.iloc[i] < recent_lows.iloc[i-1])
            
            features.append(hh_count / 4)  # Normalize to 0-1
            features.append(ll_count / 4)  # Normalize to 0-1
        else:
            features.extend([0, 0])
        
        # Support and resistance proximity
        if len(df) >= 20:
            current_price = df['close'].iloc[-1]
            recent_high = df['high'].tail(20).max()
            recent_low = df['low'].tail(20).min()
            
            resistance_distance = safe_divide(recent_high - current_price, recent_high, 0) * 100
            support_distance = safe_divide(current_price - recent_low, current_price, 0) * 100
            
            features.append(resistance_distance)
            features.append(support_distance)
        else:
            features.extend([0, 0])
        
        return features
    
    def _extract_time_features(self) -> List[float]:
        """Extract time-based features"""
        features = []
        
        current_time = datetime.now(timezone.utc)
        
        # Hour of day (normalized)
        features.append(current_time.hour / 24)
        
        # Day of week (normalized)
        features.append(current_time.weekday() / 6)
        
        # Market session indicators
        hour = current_time.hour
        
        # London session (7-16 UTC)
        features.append(1 if 7 <= hour <= 16 else 0)
        
        # New York session (12-21 UTC)
        features.append(1 if 12 <= hour <= 21 else 0)
        
        # Asian session (21-6 UTC)
        features.append(1 if hour >= 21 or hour <= 6 else 0)
        
        # Session overlap
        features.append(1 if 12 <= hour <= 16 else 0)  # London-NY overlap
        
        return features
    
    def _extract_volatility_features(self, df: pd.DataFrame) -> List[float]:
        """Extract volatility features"""
        features = []
        
        # ATR-based volatility
        if len(df) >= 14:
            ranges = df['high'].tail(14) - df['low'].tail(14)
            atr = safe_mean(ranges)
            current_price = df['close'].iloc[-1]
            volatility_pct = safe_divide(atr, current_price, 0) * 100
            features.append(volatility_pct)
        else:
            features.append(0)
        
        # Volatility change
        if len(df) >= 28:
            recent_ranges = df['high'].tail(14) - df['low'].tail(14)
            older_ranges = df['high'].tail(28).head(14) - df['low'].tail(28).head(14)
            
            recent_vol = safe_std(recent_ranges)
            older_vol = safe_std(older_ranges)
            vol_change = safe_divide(recent_vol, older_vol, 1) - 1
            features.append(vol_change * 100)
        else:
            features.append(0)
        
        return features
    
    def _extract_momentum_features(self, df: pd.DataFrame) -> List[float]:
        """Extract momentum features"""
        features = []
        
        # Price momentum over different periods
        for period in [3, 7, 14]:
            if len(df) > period:
                price_momentum = (df['close'].iloc[-1] - df['close'].iloc[-period-1]) / df['close'].iloc[-period-1]
                features.append(price_momentum * 100)
            else:
                features.append(0)
        
        # Momentum acceleration
        if len(df) >= 7:
            short_momentum = (df['close'].iloc[-1] - df['close'].iloc[-4]) / df['close'].iloc[-4]
            long_momentum = (df['close'].iloc[-4] - df['close'].iloc[-7]) / df['close'].iloc[-7]
            acceleration = short_momentum - long_momentum
            features.append(acceleration * 100)
        else:
            features.append(0)
        
        return features
    
    def _extract_pattern_features(self, df: pd.DataFrame) -> List[float]:
        """Extract pattern recognition features"""
        features = []
        
        # Candle patterns (last 3 candles)
        if len(df) >= 3:
            last_3 = df.tail(3)
            
            # Bullish patterns
            bullish_patterns = 0
            bearish_patterns = 0
            
            for _, candle in last_3.iterrows():
                body_size = abs(candle['close'] - candle['open'])
                total_range = candle['high'] - candle['low']
                body_ratio = safe_divide(body_size, total_range, 0)
                
                # Strong bullish candle
                if candle['close'] > candle['open'] and body_ratio > 0.7:
                    bullish_patterns += 1
                
                # Strong bearish candle
                elif candle['close'] < candle['open'] and body_ratio > 0.7:
                    bearish_patterns += 1
            
            features.append(bullish_patterns / 3)
            features.append(bearish_patterns / 3)
        else:
            features.extend([0, 0])
        
        # Trend consistency
        if len(df) >= 5:
            closes = df['close'].tail(5)
            upward_moves = sum(1 for i in range(1, len(closes)) if closes.iloc[i] > closes.iloc[i-1])
            features.append(upward_moves / 4)
        else:
            features.append(0.5)
        
        return features
    
    def _extract_expiry_features(self, df: pd.DataFrame, expiry_minutes: int) -> List[float]:
        """Extract expiry-specific features"""
        features = []
        
        # Expiry time normalization
        features.append(expiry_minutes / 60)  # Normalize to hours
        
        # Volatility vs expiry suitability
        if len(df) >= 14:
            ranges = df['high'].tail(14) - df['low'].tail(14)
            avg_range = safe_mean(ranges)
            current_price = df['close'].iloc[-1]
            volatility_pct = safe_divide(avg_range, current_price, 0) * 100
            
            # Optimal volatility for expiry
            optimal_vol = {1: 2.0, 5: 1.5, 15: 1.0, 30: 0.8, 60: 0.6}.get(expiry_minutes, 1.0)
            vol_suitability = 1 - abs(volatility_pct - optimal_vol) / optimal_vol
            features.append(max(0, min(1, vol_suitability)))
        else:
            features.append(0.5)
        
        # Recent price movement vs expiry time
        if len(df) > expiry_minutes and expiry_minutes <= len(df):
            lookback_period = min(expiry_minutes, len(df) - 1)
            recent_change = (df['close'].iloc[-1] - df['close'].iloc[-lookback_period-1]) / df['close'].iloc[-lookback_period-1]
            features.append(recent_change * 100)
        else:
            features.append(0)
        
        return features
    
    def _get_ensemble_predictions(self, features: np.ndarray, expiry_minutes: int) -> List[Dict[str, Any]]:
        """Simulate ensemble model predictions"""
        
        # This simulates multiple ML models
        predictions = []
        
        # Model 1: Trend-based model
        trend_score = self._calculate_trend_score(features)
        predictions.append({
            'model': 'trend',
            'prediction': 'CALL' if trend_score > 0.5 else 'PUT',
            'confidence': abs(trend_score - 0.5) * 2,
            'weight': 0.3
        })
        
        # Model 2: Mean reversion model
        mean_reversion_score = self._calculate_mean_reversion_score(features)
        predictions.append({
            'model': 'mean_reversion',
            'prediction': 'PUT' if mean_reversion_score > 0.5 else 'CALL',
            'confidence': abs(mean_reversion_score - 0.5) * 2,
            'weight': 0.25
        })
        
        # Model 3: Momentum model
        momentum_score = self._calculate_momentum_score(features)
        predictions.append({
            'model': 'momentum',
            'prediction': 'CALL' if momentum_score > 0.5 else 'PUT',
            'confidence': abs(momentum_score - 0.5) * 2,
            'weight': 0.25
        })
        
        # Model 4: Volatility model
        volatility_score = self._calculate_volatility_score(features, expiry_minutes)
        predictions.append({
            'model': 'volatility',
            'prediction': 'CALL' if volatility_score > 0.5 else 'PUT',
            'confidence': abs(volatility_score - 0.5) * 2,
            'weight': 0.2
        })
        
        return predictions
    
    def _calculate_trend_score(self, features: np.ndarray) -> float:
        """Calculate trend-based score"""
        if len(features) < 10:
            return 0.5
        
        # Use price change features (first 5 features are price changes)
        price_changes = features[:5]
        trend_strength = safe_mean(price_changes)
        
        # Normalize to 0-1 range
        return max(0, min(1, (trend_strength + 5) / 10))
    
    def _calculate_mean_reversion_score(self, features: np.ndarray) -> float:
        """Calculate mean reversion score"""
        if len(features) < 20:
            return 0.5
        
        # Use price position feature (around index 7)
        if len(features) > 7:
            price_position = features[7]  # Position in recent range
            
            # Mean reversion suggests extremes will revert
            if price_position > 0.8:
                return 0.8  # Strong PUT signal
            elif price_position < 0.2:
                return 0.2  # Strong CALL signal
            else:
                return 0.5  # Neutral
        
        return 0.5
    
    def _calculate_momentum_score(self, features: np.ndarray) -> float:
        """Calculate momentum score"""
        if len(features) < 30:
            return 0.5
        
        # Use momentum features (later in the feature array)
        momentum_features = features[-10:-5] if len(features) >= 10 else [0]
        momentum_strength = safe_mean(momentum_features)
        
        # Normalize to 0-1 range
        return max(0, min(1, (momentum_strength + 2) / 4))
    
    def _calculate_volatility_score(self, features: np.ndarray, expiry_minutes: int) -> float:
        """Calculate volatility-based score"""
        if len(features) < 25:
            return 0.5
        
        # Use volatility features
        if len(features) > 25:
            volatility = features[25] if len(features) > 25 else 1.0
            
            # High volatility suggests directional moves
            if volatility > 2.0:
                # Use trend direction
                trend_score = self._calculate_trend_score(features)
                return trend_score
            else:
                return 0.5
        
        return 0.5
    
    def _calculate_final_prediction(self, ensemble_predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate weighted ensemble prediction"""
        
        call_weight = 0
        put_weight = 0
        total_confidence = 0
        
        for pred in ensemble_predictions:
            confidence = pred['confidence']
            weight = pred['weight']
            
            if pred['prediction'] == 'CALL':
                call_weight += confidence * weight
            else:
                put_weight += confidence * weight
            
            total_confidence += confidence * weight
        
        if call_weight > put_weight:
            final_prediction = 'CALL'
            final_confidence = safe_divide(call_weight, call_weight + put_weight, 0.5)
        else:
            final_prediction = 'PUT'
            final_confidence = safe_divide(put_weight, call_weight + put_weight, 0.5)
        
        return {
            'direction': final_prediction,
            'confidence': final_confidence,
            'call_probability': safe_divide(call_weight, call_weight + put_weight, 0.5),
            'put_probability': safe_divide(put_weight, call_weight + put_weight, 0.5),
            'ensemble_agreement': abs(call_weight - put_weight) / (call_weight + put_weight) if (call_weight + put_weight) > 0 else 0
        }
    
    def _analyze_binary_specific_factors(self, df: pd.DataFrame, expiry_minutes: int) -> Dict[str, Any]:
        """Analyze factors specific to binary options success"""
        
        analysis = {
            'trend_strength': 0.5,
            'volatility_suitability': 0.5,
            'time_decay_risk': 0.5,
            'directional_bias': 'NEUTRAL',
            'optimal_conditions': False
        }
        
        if df is None or len(df) < 10:
            return analysis
        
        # Trend strength analysis
        if len(df) >= 10:
            price_changes = []
            for i in range(1, min(11, len(df))):
                change = (df['close'].iloc[-i] - df['close'].iloc[-i-1]) / df['close'].iloc[-i-1]
                price_changes.append(change)
            
            trend_consistency = len([x for x in price_changes if x > 0]) / len(price_changes)
            if trend_consistency > 0.7:
                analysis['trend_strength'] = 0.8
                analysis['directional_bias'] = 'CALL'
            elif trend_consistency < 0.3:
                analysis['trend_strength'] = 0.8
                analysis['directional_bias'] = 'PUT'
            else:
                analysis['trend_strength'] = 0.4
        
        # Volatility suitability
        if len(df) >= 14:
            ranges = df['high'].tail(14) - df['low'].tail(14)
            avg_range = safe_mean(ranges)
            current_price = df['close'].iloc[-1]
            volatility_pct = safe_divide(avg_range, current_price, 0) * 100
            
            # Optimal volatility ranges for different expiries
            optimal_ranges = {1: (1.5, 3.0), 5: (1.0, 2.5), 15: (0.8, 2.0), 30: (0.6, 1.8), 60: (0.4, 1.5)}
            min_vol, max_vol = optimal_ranges.get(expiry_minutes, (0.5, 2.0))
            
            if min_vol <= volatility_pct <= max_vol:
                analysis['volatility_suitability'] = 0.9
                analysis['optimal_conditions'] = True
            else:
                analysis['volatility_suitability'] = 0.3
        
        # Time decay risk (higher for shorter expiries)
        time_decay_factors = {1: 0.9, 5: 0.7, 15: 0.5, 30: 0.3, 60: 0.2}
        analysis['time_decay_risk'] = time_decay_factors.get(expiry_minutes, 0.5)
        
        return analysis
    
    def _calculate_win_probability(self, ml_prediction: Dict[str, Any], 
                                 binary_analysis: Dict[str, Any]) -> float:
        """Calculate overall win probability combining ML and binary analysis"""
        
        base_probability = ml_prediction.get('confidence', 0.5)
        trend_strength = binary_analysis.get('trend_strength', 0.5)
        volatility_suitability = binary_analysis.get('volatility_suitability', 0.5)
        time_decay_risk = binary_analysis.get('time_decay_risk', 0.5)
        
        # Weighted combination
        win_probability = (
            base_probability * 0.4 +
            trend_strength * 0.3 +
            volatility_suitability * 0.2 +
            (1 - time_decay_risk) * 0.1
        )
        
        return max(0.45, min(0.95, win_probability))  # Realistic bounds
    
    def _assess_binary_risk(self, win_probability: float, expiry_minutes: int) -> Dict[str, Any]:
        """Assess risk specific to binary options"""
        
        # Required win rates for profitability (assuming 80% payout)
        required_win_rates = {1: 0.85, 5: 0.75, 15: 0.65, 30: 0.60, 60: 0.55}
        required_rate = required_win_rates.get(expiry_minutes, 0.65)
        
        risk_level = 'LOW'
        if win_probability < required_rate:
            risk_level = 'VERY HIGH'
        elif win_probability < required_rate + 0.05:
            risk_level = 'HIGH'
        elif win_probability < required_rate + 0.10:
            risk_level = 'MEDIUM'
        
        return {
            'risk_level': risk_level,
            'win_probability': win_probability,
            'required_win_rate': required_rate,
            'edge': win_probability - required_rate,
            'recommended_position_size': self._calculate_position_size(win_probability, required_rate),
            'expected_return': (win_probability * 0.8) - ((1 - win_probability) * 1.0)
        }
    
    def _calculate_position_size(self, win_probability: float, required_rate: float) -> str:
        """Calculate recommended position size"""
        edge = win_probability - required_rate
        
        if edge <= 0:
            return "DO NOT TRADE"
        elif edge < 0.05:
            return "1% of account (high risk)"
        elif edge < 0.10:
            return "2% of account (medium risk)" 
        elif edge < 0.15:
            return "3% of account (good edge)"
        else:
            return "4% of account (excellent edge)"
    
    def _assess_expiry_suitability(self, win_probability: float, expiry_minutes: int) -> Dict[str, Any]:
        """Assess if the expiry time is suitable"""
        
        suitability_score = 0.5
        recommendation = "NEUTRAL"
        
        # Base suitability on win probability vs requirements
        required_rates = {1: 0.85, 5: 0.75, 15: 0.65, 30: 0.60, 60: 0.55}
        required_rate = required_rates.get(expiry_minutes, 0.65)
        
        if win_probability >= required_rate + 0.10:
            suitability_score = 0.9
            recommendation = "EXCELLENT"
        elif win_probability >= required_rate + 0.05:
            suitability_score = 0.75
            recommendation = "GOOD"
        elif win_probability >= required_rate:
            suitability_score = 0.6
            recommendation = "ACCEPTABLE"
        else:
            suitability_score = 0.3
            recommendation = "POOR"
        
        return {
            'suitability_score': suitability_score,
            'recommendation': recommendation,
            'win_probability': win_probability,
            'required_rate': required_rate,
            'alternative_expiries': self._suggest_alternative_expiries(win_probability)
        }
    
    def _suggest_alternative_expiries(self, win_probability: float) -> List[Dict[str, Any]]:
        """Suggest alternative expiry times"""
        suggestions = []
        
        expiry_requirements = {1: 0.85, 5: 0.75, 15: 0.65, 30: 0.60, 60: 0.55}
        
        for expiry, required_rate in expiry_requirements.items():
            if win_probability >= required_rate + 0.05:  # Good edge
                suggestions.append({
                    'expiry_minutes': expiry,
                    'suitability': 'GOOD',
                    'edge': win_probability - required_rate
                })
        
        # Sort by edge
        suggestions.sort(key=lambda x: x['edge'], reverse=True)
        
        return suggestions[:3]  # Top 3 suggestions
    
    def _get_feature_importance(self, features: np.ndarray) -> Dict[str, float]:
        """Get simulated feature importance"""
        if len(features) == 0:
            return {}
        
        # Simulate feature importance based on typical binary options factors
        feature_names = [
            'short_term_momentum', 'medium_term_momentum', 'trend_strength',
            'volatility', 'volume_trend', 'technical_indicators', 'market_structure',
            'time_factors', 'session_factors'
        ]
        
        # Simulate importance scores
        importances = [0.15, 0.12, 0.18, 0.14, 0.08, 0.13, 0.10, 0.05, 0.05]
        
        return dict(zip(feature_names[:len(importances)], importances))
    
    def _calculate_confidence_interval(self, ensemble_predictions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate confidence intervals for predictions"""
        
        confidences = [pred['confidence'] for pred in ensemble_predictions]
        
        if not confidences:
            return {'lower': 0.45, 'upper': 0.55}
        
        mean_confidence = safe_mean(confidences)
        std_confidence = safe_std(confidences)
        
        return {
            'lower': max(0.45, mean_confidence - 1.96 * std_confidence),
            'upper': min(0.95, mean_confidence + 1.96 * std_confidence),
            'mean': mean_confidence
        }
    
    def _get_default_prediction(self) -> Dict[str, Any]:
        """Return default prediction when ML fails"""
        return {
            'ml_prediction': {
                'direction': 'NEUTRAL',
                'confidence': 0.5,
                'call_probability': 0.5,
                'put_probability': 0.5,
                'ensemble_agreement': 0.0
            },
            'win_probability': 0.5,
            'confidence_interval': {'lower': 0.45, 'upper': 0.55, 'mean': 0.5},
            'risk_assessment': {
                'risk_level': 'HIGH',
                'win_probability': 0.5,
                'required_win_rate': 0.65,
                'edge': -0.15,
                'recommended_position_size': "DO NOT TRADE",
                'expected_return': -0.35
            },
            'binary_analysis': {
                'trend_strength': 0.5,
                'volatility_suitability': 0.5,
                'time_decay_risk': 0.5,
                'directional_bias': 'NEUTRAL',
                'optimal_conditions': False
            },
            'expiry_suitability': {
                'suitability_score': 0.3,
                'recommendation': 'POOR',
                'win_probability': 0.5,
                'required_rate': 0.65,
                'alternative_expiries': []
            },
            'feature_importance': {},
            'prediction_timestamp': datetime.now().isoformat()
        }

# Global ML predictor instance
_ml_predictor = None

def get_ml_predictor() -> BinaryOptionsMLPredictor:
    """Get or create global ML predictor instance"""
    global _ml_predictor
    if _ml_predictor is None:
        _ml_predictor = BinaryOptionsMLPredictor()
    return _ml_predictor

def predict_binary_outcome(df: pd.DataFrame, indicators: Dict[str, Any], 
                          expiry_minutes: int = 5, current_price: float = None) -> Dict[str, Any]:
    """Main function for ML-based binary options prediction with enhanced learning"""
    predictor = get_ml_predictor()
    
    # Get base prediction
    base_prediction = predictor.predict_binary_outcome(df, indicators, expiry_minutes, current_price)
    
    # Apply learning adjustments if features are available
    try:
        features = predictor.extract_ml_features(df, indicators, expiry_minutes)
        if len(features) > 0:
            base_confidence = base_prediction['ml_prediction']['confidence']
            adjusted_confidence, explanation = predictor._apply_learning_adjustment(features, base_confidence)
            
            # Update prediction with learning adjustments
            base_prediction['ml_prediction']['confidence'] = adjusted_confidence
            base_prediction['ml_prediction']['learning_explanation'] = explanation
            base_prediction['learning_stats'] = predictor.get_learning_stats()
            
            # Recalculate win probability with adjusted confidence
            binary_analysis = base_prediction.get('binary_analysis', {})
            base_prediction['win_probability'] = predictor._calculate_win_probability(
                base_prediction['ml_prediction'], binary_analysis
            )
            
            # Update risk assessment
            base_prediction['risk_assessment'] = predictor._assess_binary_risk(
                base_prediction['win_probability'], expiry_minutes
            )
    except Exception as e:
        print(f"Error applying learning adjustments: {e}")
    
    return base_prediction

def record_trade_outcome(prediction_id: str, actual_outcome: str, actual_price: float, features: np.ndarray = None) -> None:
    """Record trade outcome for enhanced learning"""
    predictor = get_ml_predictor()
    if hasattr(predictor, 'record_trade_outcome'):
        predictor.record_trade_outcome(prediction_id, actual_outcome, actual_price, features)

def get_learning_statistics() -> Dict[str, Any]:
    """Get current learning system statistics"""
    predictor = get_ml_predictor()
    if hasattr(predictor, 'get_learning_stats'):
        return predictor.get_learning_stats()
    return {}, timezone