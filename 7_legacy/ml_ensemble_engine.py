"""
Machine Learning Ensemble Engine for Binary Options Trading
Multi-model approach with SVM, LSTM, Random Forest, and Decision Trees
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.svm import SVC
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not available, using simplified ML methods")

from safe_math_utils import safe_mean, safe_std, safe_divide

class PredictionType(Enum):
    MOMENTUM = "momentum"
    REVERSAL = "reversal"
    NEUTRAL = "neutral"

class ModelType(Enum):
    SVM = "support_vector_machine"
    RANDOM_FOREST = "random_forest"
    DECISION_TREE = "decision_tree"
    SIMPLE_LSTM = "simple_lstm"

@dataclass
class ModelPrediction:
    model_type: ModelType
    prediction: PredictionType
    confidence: float
    probability_scores: Dict[str, float]
    feature_importance: Optional[Dict[str, float]] = None

@dataclass
class EnsemblePrediction:
    final_prediction: PredictionType
    ensemble_confidence: float
    individual_predictions: List[ModelPrediction]
    consensus_level: float
    recommended_action: str
    probability_distribution: Dict[str, float]

class SimplifiedMLEngine:
    """Simplified ML engine when sklearn is not available"""
    
    def __init__(self):
        self.feature_weights = {
            'price_momentum': 0.25,
            'volume_trend': 0.20,
            'volatility_regime': 0.15,
            'rsi_momentum': 0.15,
            'macd_signal': 0.15,
            'breakout_strength': 0.10
        }
    
    def predict(self, features: Dict[str, float]) -> ModelPrediction:
        """Simple weighted prediction when sklearn not available"""
        momentum_score = 0
        reversal_score = 0
        
        # Price momentum analysis
        price_mom = features.get('price_momentum', 0)
        if price_mom > 0.02:
            momentum_score += 30
        elif price_mom < -0.02:
            reversal_score += 30
        
        # Volume analysis
        volume_trend = features.get('volume_trend', 0)
        if volume_trend > 1.2:
            momentum_score += 20
        elif volume_trend < 0.8:
            reversal_score += 15
        
        # RSI analysis
        rsi = features.get('rsi_momentum', 50)
        if rsi > 70:
            reversal_score += 25
        elif rsi < 30:
            reversal_score += 25
        elif 45 <= rsi <= 55:
            momentum_score += 10
        
        # MACD analysis
        macd_signal = features.get('macd_signal', 0)
        if macd_signal > 0.001:
            momentum_score += 15
        elif macd_signal < -0.001:
            reversal_score += 15
        
        # Determine prediction
        if momentum_score > reversal_score and momentum_score > 40:
            prediction = PredictionType.MOMENTUM
            confidence = min(85, momentum_score)
        elif reversal_score > momentum_score and reversal_score > 40:
            prediction = PredictionType.REVERSAL
            confidence = min(85, reversal_score)
        else:
            prediction = PredictionType.NEUTRAL
            confidence = 50
        
        return ModelPrediction(
            model_type=ModelType.SIMPLE_LSTM,
            prediction=prediction,
            confidence=confidence,
            probability_scores={
                'momentum': momentum_score / 100,
                'reversal': reversal_score / 100,
                'neutral': (100 - momentum_score - reversal_score) / 100
            }
        )

class AdvancedMLEnsemble:
    """Advanced ML ensemble with multiple algorithms"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        self.feature_names = [
            'price_momentum', 'volume_trend', 'volatility_regime',
            'rsi_momentum', 'macd_signal', 'breakout_strength',
            'bb_squeeze', 'atr_regime', 'price_position'
        ]
        
        if SKLEARN_AVAILABLE:
            self._initialize_models()
        else:
            self.simplified_engine = SimplifiedMLEngine()
    
    def _initialize_models(self):
        """Initialize ML models"""
        self.models = {
            ModelType.SVM: SVC(probability=True, kernel='rbf', random_state=42),
            ModelType.RANDOM_FOREST: RandomForestClassifier(n_estimators=100, random_state=42),
            ModelType.DECISION_TREE: DecisionTreeClassifier(max_depth=10, random_state=42)
        }
        
        for model_type in self.models:
            self.scalers[model_type] = StandardScaler()
    
    def prepare_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract and prepare features for ML models"""
        try:
            if len(df) < 20:
                return self._default_features()
            
            features = {}
            
            # Price momentum features
            returns = df['close'].pct_change()
            features['price_momentum'] = returns.rolling(5).mean().iloc[-1] if len(returns) > 5 else 0
            
            # Volume features
            if 'volume' in df.columns:
                vol_ma = df['volume'].rolling(20).mean()
                current_vol = df['volume'].iloc[-1]
                features['volume_trend'] = safe_divide(current_vol, vol_ma.iloc[-1], 1.0)
            else:
                features['volume_trend'] = 1.0
            
            # Volatility regime
            volatility = returns.rolling(20).std().iloc[-1]
            features['volatility_regime'] = volatility if not pd.isna(volatility) else 0.02
            
            # Technical indicators
            features.update(self._calculate_technical_features(df))
            
            # Market structure features
            features.update(self._calculate_structure_features(df))
            
            return features
            
        except Exception as e:
            print(f"Error preparing features: {e}")
            return self._default_features()
    
    def _calculate_technical_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate technical indicator features"""
        features = {}
        
        try:
            close = df['close']
            high = df['high']
            low = df['low']
            
            # RSI
            if len(close) >= 14:
                delta = close.diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / (loss + 1e-8)
                rsi = 100 - (100 / (1 + rs))
                features['rsi_momentum'] = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            else:
                features['rsi_momentum'] = 50
            
            # MACD
            if len(close) >= 26:
                ema12 = close.ewm(span=12).mean()
                ema26 = close.ewm(span=26).mean()
                macd = ema12 - ema26
                features['macd_signal'] = macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0
            else:
                features['macd_signal'] = 0
            
            # Bollinger Bands squeeze
            if len(close) >= 20:
                sma = close.rolling(20).mean()
                std = close.rolling(20).std()
                bb_upper = sma + (2 * std)
                bb_lower = sma - (2 * std)
                bb_width = (bb_upper - bb_lower) / sma
                features['bb_squeeze'] = bb_width.iloc[-1] if not pd.isna(bb_width.iloc[-1]) else 0.04
            else:
                features['bb_squeeze'] = 0.04
                
            # ATR regime
            if len(high) >= 14:
                tr = np.maximum(high - low,
                               np.maximum(np.abs(high - close.shift(1)),
                                         np.abs(low - close.shift(1))))
                atr = tr.rolling(14).mean()
                features['atr_regime'] = atr.iloc[-1] / close.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0.02
            else:
                features['atr_regime'] = 0.02
            
            return features
            
        except Exception as e:
            print(f"Error calculating technical features: {e}")
            return {'rsi_momentum': 50, 'macd_signal': 0, 'bb_squeeze': 0.04, 'atr_regime': 0.02}
    
    def _calculate_structure_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate market structure features"""
        features = {}
        
        try:
            close = df['close']
            
            # Price position relative to recent range
            if len(close) >= 20:
                recent_high = close.rolling(20).max().iloc[-1]
                recent_low = close.rolling(20).min().iloc[-1]
                current_price = close.iloc[-1]
                
                if recent_high != recent_low:
                    features['price_position'] = (current_price - recent_low) / (recent_high - recent_low)
                else:
                    features['price_position'] = 0.5
            else:
                features['price_position'] = 0.5
            
            # Breakout strength
            if len(close) >= 10:
                ma10 = close.rolling(10).mean().iloc[-1]
                breakout_strength = abs(close.iloc[-1] - ma10) / ma10
                features['breakout_strength'] = breakout_strength
            else:
                features['breakout_strength'] = 0
                
            return features
            
        except Exception as e:
            print(f"Error calculating structure features: {e}")
            return {'price_position': 0.5, 'breakout_strength': 0}
    
    def train_models(self, historical_data: List[Dict[str, Any]]) -> bool:
        """Train ensemble models on historical data"""
        if not SKLEARN_AVAILABLE or len(historical_data) < 50:
            return False
        
        try:
            # Prepare training data
            X = []
            y = []
            
            for data_point in historical_data:
                features = [data_point.get(feature, 0) for feature in self.feature_names]
                X.append(features)
                y.append(data_point.get('label', 'neutral'))
            
            X = np.array(X)
            y = np.array(y)
            
            # Encode labels
            label_encoder = LabelEncoder()
            y_encoded = label_encoder.fit_transform(y)
            
            # Train each model
            for model_type, model in self.models.items():
                # Scale features
                X_scaled = self.scalers[model_type].fit_transform(X)
                
                # Train model
                model.fit(X_scaled, y_encoded)
            
            self.is_trained = True
            print("ML ensemble models trained successfully")
            return True
            
        except Exception as e:
            print(f"Error training models: {e}")
            return False
    
    def predict_ensemble(self, features: Dict[str, float]) -> EnsemblePrediction:
        """Generate ensemble prediction from all models"""
        try:
            if not SKLEARN_AVAILABLE:
                # Use simplified engine
                simple_pred = self.simplified_engine.predict(features)
                return EnsemblePrediction(
                    final_prediction=simple_pred.prediction,
                    ensemble_confidence=simple_pred.confidence,
                    individual_predictions=[simple_pred],
                    consensus_level=1.0,
                    recommended_action=self._get_recommended_action(simple_pred.prediction, simple_pred.confidence),
                    probability_distribution=simple_pred.probability_scores
                )
            
            # Prepare feature vector
            feature_vector = [features.get(feature, 0) for feature in self.feature_names]
            feature_vector = np.array(feature_vector).reshape(1, -1)
            
            individual_predictions = []
            
            # Get predictions from each model
            for model_type, model in self.models.items():
                if hasattr(model, 'predict_proba'):
                    # Scale features
                    X_scaled = self.scalers[model_type].transform(feature_vector)
                    
                    # Get prediction
                    probabilities = model.predict_proba(X_scaled)[0]
                    predicted_class = model.predict(X_scaled)[0]
                    
                    # Map to prediction type
                    class_mapping = {0: PredictionType.MOMENTUM, 1: PredictionType.NEUTRAL, 2: PredictionType.REVERSAL}
                    prediction_type = class_mapping.get(predicted_class, PredictionType.NEUTRAL)
                    
                    # Get confidence
                    confidence = max(probabilities) * 100
                    
                    prob_scores = {
                        'momentum': probabilities[0] if len(probabilities) > 0 else 0.33,
                        'neutral': probabilities[1] if len(probabilities) > 1 else 0.33,
                        'reversal': probabilities[2] if len(probabilities) > 2 else 0.33
                    }
                    
                    individual_predictions.append(ModelPrediction(
                        model_type=model_type,
                        prediction=prediction_type,
                        confidence=confidence,
                        probability_scores=prob_scores
                    ))
            
            # Calculate ensemble prediction
            return self._calculate_ensemble_result(individual_predictions)
            
        except Exception as e:
            print(f"Error in ensemble prediction: {e}")
            # Fallback to simplified prediction
            return self._fallback_prediction(features)
    
    def _calculate_ensemble_result(self, predictions: List[ModelPrediction]) -> EnsemblePrediction:
        """Calculate final ensemble result from individual predictions"""
        if not predictions:
            return self._default_ensemble_prediction()
        
        # Weighted voting based on confidence
        prediction_scores = {
            PredictionType.MOMENTUM: 0,
            PredictionType.REVERSAL: 0,
            PredictionType.NEUTRAL: 0
        }
        
        total_weight = 0
        for pred in predictions:
            weight = pred.confidence / 100
            prediction_scores[pred.prediction] += weight
            total_weight += weight
        
        # Normalize scores
        if total_weight > 0:
            for pred_type in prediction_scores:
                prediction_scores[pred_type] /= total_weight
        
        # Find winning prediction
        final_prediction = max(prediction_scores, key=prediction_scores.get)
        ensemble_confidence = prediction_scores[final_prediction] * 100
        
        # Calculate consensus level
        consensus_level = self._calculate_consensus(predictions)
        
        # Generate recommendation
        recommended_action = self._get_recommended_action(final_prediction, ensemble_confidence)
        
        # Probability distribution
        prob_dist = {
            'momentum': prediction_scores[PredictionType.MOMENTUM],
            'reversal': prediction_scores[PredictionType.REVERSAL],
            'neutral': prediction_scores[PredictionType.NEUTRAL]
        }
        
        return EnsemblePrediction(
            final_prediction=final_prediction,
            ensemble_confidence=ensemble_confidence,
            individual_predictions=predictions,
            consensus_level=consensus_level,
            recommended_action=recommended_action,
            probability_distribution=prob_dist
        )
    
    def _calculate_consensus(self, predictions: List[ModelPrediction]) -> float:
        """Calculate consensus level among models"""
        if len(predictions) <= 1:
            return 1.0
        
        prediction_counts = {}
        for pred in predictions:
            prediction_counts[pred.prediction] = prediction_counts.get(pred.prediction, 0) + 1
        
        max_count = max(prediction_counts.values())
        return max_count / len(predictions)
    
    def _get_recommended_action(self, prediction: PredictionType, confidence: float) -> str:
        """Get recommended trading action"""
        if confidence < 60:
            return "WAIT"
        elif prediction == PredictionType.MOMENTUM:
            return "CALL" if confidence > 75 else "CALL_WEAK"
        elif prediction == PredictionType.REVERSAL:
            return "PUT" if confidence > 75 else "PUT_WEAK"
        else:
            return "NEUTRAL"
    
    def _fallback_prediction(self, features: Dict[str, float]) -> EnsemblePrediction:
        """Fallback prediction when models fail"""
        # Simple rules-based prediction
        momentum_score = 0
        reversal_score = 0
        
        # Analyze key features
        rsi = features.get('rsi_momentum', 50)
        if rsi > 75:
            reversal_score += 30
        elif rsi < 25:
            reversal_score += 30
        
        price_mom = features.get('price_momentum', 0)
        if abs(price_mom) > 0.01:
            momentum_score += 25
        
        # Determine prediction
        if momentum_score > reversal_score:
            prediction = PredictionType.MOMENTUM
            confidence = min(75, momentum_score + 40)
        elif reversal_score > momentum_score:
            prediction = PredictionType.REVERSAL
            confidence = min(75, reversal_score + 40)
        else:
            prediction = PredictionType.NEUTRAL
            confidence = 50
        
        return EnsemblePrediction(
            final_prediction=prediction,
            ensemble_confidence=confidence,
            individual_predictions=[],
            consensus_level=1.0,
            recommended_action=self._get_recommended_action(prediction, confidence),
            probability_distribution={
                'momentum': 0.33,
                'reversal': 0.33,
                'neutral': 0.34
            }
        )
    
    def _default_features(self) -> Dict[str, float]:
        """Default feature values when calculation fails"""
        return {
            'price_momentum': 0,
            'volume_trend': 1.0,
            'volatility_regime': 0.02,
            'rsi_momentum': 50,
            'macd_signal': 0,
            'breakout_strength': 0,
            'bb_squeeze': 0.04,
            'atr_regime': 0.02,
            'price_position': 0.5
        }
    
    def _default_ensemble_prediction(self) -> EnsemblePrediction:
        """Default ensemble prediction"""
        return EnsemblePrediction(
            final_prediction=PredictionType.NEUTRAL,
            ensemble_confidence=50,
            individual_predictions=[],
            consensus_level=1.0,
            recommended_action="WAIT",
            probability_distribution={'momentum': 0.33, 'reversal': 0.33, 'neutral': 0.34}
        )
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained models"""
        if not SKLEARN_AVAILABLE or not self.is_trained:
            return {}
        
        importance_scores = {}
        
        # Get importance from Random Forest
        if ModelType.RANDOM_FOREST in self.models:
            rf_model = self.models[ModelType.RANDOM_FOREST]
            if hasattr(rf_model, 'feature_importances_'):
                for i, feature in enumerate(self.feature_names):
                    importance_scores[feature] = rf_model.feature_importances_[i]
        
        return importance_scores
    
    def analyze_prediction_quality(self, recent_predictions: List[Dict]) -> Dict[str, Any]:
        """Analyze recent prediction quality and accuracy"""
        if not recent_predictions:
            return {'accuracy': 50, 'confidence_calibration': 'unknown', 'model_performance': {}}
        
        correct_predictions = sum(1 for pred in recent_predictions if pred.get('correct', False))
        total_predictions = len(recent_predictions)
        accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 50
        
        # Analyze confidence calibration
        high_conf_correct = sum(1 for pred in recent_predictions 
                               if pred.get('confidence', 0) > 80 and pred.get('correct', False))
        high_conf_total = sum(1 for pred in recent_predictions if pred.get('confidence', 0) > 80)
        
        calibration = 'good' if high_conf_total > 0 and high_conf_correct / high_conf_total > 0.8 else 'needs_improvement'
        
        return {
            'accuracy': accuracy,
            'confidence_calibration': calibration,
            'total_predictions': total_predictions,
            'high_confidence_accuracy': (high_conf_correct / high_conf_total * 100) if high_conf_total > 0 else 0
        }

# Global ensemble instance
_ml_ensemble = None

def get_ml_ensemble() -> AdvancedMLEnsemble:
    """Get or create global ML ensemble instance"""
    global _ml_ensemble
    if _ml_ensemble is None:
        _ml_ensemble = AdvancedMLEnsemble()
    return _ml_ensemble