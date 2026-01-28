"""
ML Ensemble Confidence Adjuster
Integrates ML Ensemble predictions to boost/reduce confidence based on model agreement
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '7_legacy'))

from typing import Dict, Tuple, Optional
import pandas as pd

try:
    from ml_ensemble_engine import MLEnsembleEngine, PredictionType
    ML_ENSEMBLE_AVAILABLE = True
except ImportError:
    ML_ENSEMBLE_AVAILABLE = False


def get_ml_confidence_adjustment(
    df: pd.DataFrame,
    indicators: Dict,
    signal: str,
    confidence: float,
    pair: str = 'EUR/USD'
) -> Tuple[float, Optional[Dict]]:
    """
    Adjust confidence based on ML Ensemble prediction agreement
    
    Returns:
        Tuple of (adjusted_confidence, ml_details)
        - adjusted_confidence: Original confidence +/- ML adjustment
        - ml_details: Dict with ML analysis details for display
    """
    
    if not ML_ENSEMBLE_AVAILABLE or df is None or df.empty:
        return confidence, None
    
    try:
        # Initialize ML Ensemble engine
        ml_engine = MLEnsembleEngine(minimal_mode=True)
        
        # Prepare features for ML engine
        features = _extract_ml_features(df, indicators)
        if not features:
            return confidence, None
        
        # Get ML ensemble prediction
        ensemble_prediction = ml_engine.predict(features)
        if not ensemble_prediction:
            return confidence, None
        
        # Map signal to ML prediction type
        signal_to_ml = {
            'BUY': 'momentum',
            'SELL': 'reversal',
            'NEUTRAL': 'neutral'
        }
        
        signal_map = signal_to_ml.get(signal, 'neutral')
        ml_signal_map = {
            'momentum': 'BUY',
            'reversal': 'SELL',
            'neutral': 'NEUTRAL'
        }
        
        # Extract ML consensus
        ml_prediction = ensemble_prediction.final_prediction
        ml_confidence = ensemble_prediction.ensemble_confidence
        consensus_level = ensemble_prediction.consensus_level
        
        # Calculate confidence adjustment based on agreement
        adjustment = 0
        agreement_level = "None"
        
        # Convert ML prediction to BUY/SELL/NEUTRAL
        ml_signal = ml_signal_map.get(ml_prediction.value, 'NEUTRAL')
        
        # Strong agreement - both models agree
        if signal == ml_signal and ml_confidence >= 70:
            # Strong consensus: +10 confidence
            adjustment = min(10, (100 - confidence) * 0.5)  # Scale to available room
            agreement_level = "Strong"
        
        # Moderate agreement
        elif signal == ml_signal and ml_confidence >= 55:
            # Moderate consensus: +5 confidence
            adjustment = min(5, (100 - confidence) * 0.3)
            agreement_level = "Moderate"
        
        # Disagreement
        elif signal != ml_signal and ml_confidence >= 70:
            # Strong disagreement: -8 confidence
            adjustment = max(-8, confidence * -0.15)
            agreement_level = "Disagreement"
        
        # Weak disagreement
        elif signal != ml_signal and ml_confidence >= 55:
            # Weak disagreement: -4 confidence
            adjustment = max(-4, confidence * -0.08)
            agreement_level = "Weak Disagreement"
        
        else:
            agreement_level = "Low Confidence"
        
        # Calculate final adjusted confidence
        adjusted_confidence = max(0, min(100, confidence + adjustment))
        
        # Prepare details for display
        ml_details = {
            'ml_signal': ml_signal,
            'ml_confidence': ml_confidence,
            'consensus_level': consensus_level * 100,  # Convert to percentage
            'agreement_level': agreement_level,
            'confidence_adjustment': adjustment,
            'adjusted_confidence': adjusted_confidence,
            'individual_models': len(ensemble_prediction.individual_predictions),
            'model_agreement_count': _count_agreeing_models(
                ensemble_prediction.individual_predictions,
                signal
            )
        }
        
        return adjusted_confidence, ml_details
        
    except Exception as e:
        print(f"[ML Confidence] Error in ML adjustment for {pair}: {e}")
        return confidence, None


def _extract_ml_features(df: pd.DataFrame, indicators: Dict) -> Optional[Dict]:
    """Extract features needed for ML Ensemble prediction"""
    
    try:
        if df.empty or len(df) < 20:
            return None
        
        # Basic price features
        close_prices = df['close'].values
        recent_returns = (close_prices[-1] - close_prices[-20]) / close_prices[-20]
        
        features = {
            'price_momentum': recent_returns,
            'volume_trend': indicators.get('volume_trend', 1.0),
            'volatility_regime': indicators.get('atr_percent', 0.5) / 100,
            'rsi_momentum': indicators.get('rsi', 50),
            'macd_signal': indicators.get('macd_diff', 0),
            'breakout_strength': indicators.get('breakout_strength', 0.5),
            'trend_strength': indicators.get('adx', 20) / 50,  # Normalize to 0-1
        }
        
        return features
        
    except Exception as e:
        print(f"[ML Features] Error extracting features: {e}")
        return None


def _count_agreeing_models(individual_predictions, signal: str) -> int:
    """Count how many individual models agree with the signal"""
    
    try:
        signal_to_ml = {
            'BUY': 'momentum',
            'SELL': 'reversal',
            'NEUTRAL': 'neutral'
        }
        
        target_prediction = signal_to_ml.get(signal, 'neutral')
        agreeing = sum(
            1 for pred in individual_predictions 
            if pred.prediction.value == target_prediction
        )
        return agreeing
        
    except Exception:
        return 0
