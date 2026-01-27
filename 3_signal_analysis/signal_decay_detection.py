"""
Signal Decay Detection System for Trading Bot
Monitors signal strength degradation and invalidation conditions over time
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import json

class SignalDecayReason(Enum):
    TIME_DECAY = "time_decay"
    MOMENTUM_SHIFT = "momentum_shift"
    MARKET_CONDITION_CHANGE = "market_condition_change"
    VOLUME_DETERIORATION = "volume_deterioration"
    TREND_REVERSAL = "trend_reversal"
    SUPPORT_RESISTANCE_BREAK = "support_resistance_break"
    VOLATILITY_SPIKE = "volatility_spike"

@dataclass
class SignalDecayMetrics:
    initial_strength: float
    current_strength: float
    decay_rate: float
    time_elapsed_minutes: int
    momentum_change: float
    volume_change: float
    volatility_change: float
    trend_alignment: float
    decay_reasons: List[SignalDecayReason]
    invalidation_score: float
    recommended_action: str  # "hold", "reduce", "close", "invalidate"

@dataclass
class ActiveSignal:
    signal_id: str
    symbol: str
    signal_type: str  # "BUY", "SELL"
    initial_timestamp: datetime
    initial_price: float
    initial_confidence: float
    initial_technical_state: Dict[str, Any]
    current_confidence: float
    decay_metrics: Optional[SignalDecayMetrics] = None
    is_active: bool = True

class SignalDecayDetector:
    """Advanced signal decay detection and invalidation system"""
    
    def __init__(self):
        self.active_signals: Dict[str, ActiveSignal] = {}
        self.decay_config = {
            'max_signal_age_hours': 24,
            'critical_decay_threshold': 0.3,  # 70% strength loss
            'momentum_shift_threshold': 0.4,
            'volume_deterioration_threshold': 0.5,
            'volatility_spike_threshold': 2.0,
            'trend_reversal_threshold': 0.6,
            'time_decay_rate': 0.02  # 2% per hour base decay
        }
        
    def register_signal(self, signal_data: Dict[str, Any]) -> str:
        """Register a new signal for decay monitoring"""
        signal_id = f"{signal_data['symbol']}_{signal_data['type']}_{int(datetime.now().timestamp())}"
        
        signal = ActiveSignal(
            signal_id=signal_id,
            symbol=signal_data['symbol'],
            signal_type=signal_data['type'],
            initial_timestamp=datetime.now(),
            initial_price=signal_data['price'],
            initial_confidence=signal_data['confidence'],
            initial_technical_state=signal_data.get('technical_state', {}),
            current_confidence=signal_data['confidence']
        )
        
        self.active_signals[signal_id] = signal
        return signal_id
    
    async def update_signal_decay(self, signal_id: str, current_data: pd.DataFrame) -> SignalDecayMetrics:
        """Update decay metrics for a specific signal"""
        if signal_id not in self.active_signals:
            raise ValueError(f"Signal {signal_id} not found in active signals")
            
        signal = self.active_signals[signal_id]
        current_price = current_data['close'].iloc[-1]
        current_time = datetime.now()
        
        # Calculate time-based decay
        time_elapsed = current_time - signal.initial_timestamp
        time_elapsed_minutes = time_elapsed.total_seconds() / 60
        time_decay_factor = 1 - (self.decay_config['time_decay_rate'] * (time_elapsed_minutes / 60))
        
        # Calculate momentum shift
        momentum_change = self._calculate_momentum_change(signal, current_data)
        
        # Calculate volume deterioration
        volume_change = self._calculate_volume_change(signal, current_data)
        
        # Calculate volatility change
        volatility_change = self._calculate_volatility_change(signal, current_data)
        
        # Calculate trend alignment
        trend_alignment = self._calculate_trend_alignment(signal, current_data)
        
        # Identify decay reasons
        decay_reasons = self._identify_decay_reasons(
            time_elapsed_minutes, momentum_change, volume_change, 
            volatility_change, trend_alignment
        )
        
        # Calculate current signal strength
        current_strength = self._calculate_current_strength(
            signal.initial_confidence, time_decay_factor, momentum_change,
            volume_change, volatility_change, trend_alignment
        )
        
        # Calculate decay rate
        decay_rate = (signal.initial_confidence - current_strength) / signal.initial_confidence
        
        # Calculate invalidation score
        invalidation_score = self._calculate_invalidation_score(
            decay_rate, decay_reasons, time_elapsed_minutes
        )
        
        # Determine recommended action
        recommended_action = self._determine_recommended_action(invalidation_score, decay_rate)
        
        # Create decay metrics
        decay_metrics = SignalDecayMetrics(
            initial_strength=signal.initial_confidence,
            current_strength=current_strength,
            decay_rate=decay_rate,
            time_elapsed_minutes=int(time_elapsed_minutes),
            momentum_change=momentum_change,
            volume_change=volume_change,
            volatility_change=volatility_change,
            trend_alignment=trend_alignment,
            decay_reasons=decay_reasons,
            invalidation_score=invalidation_score,
            recommended_action=recommended_action
        )
        
        # Update signal
        signal.current_confidence = current_strength
        signal.decay_metrics = decay_metrics
        
        # Check if signal should be deactivated
        if recommended_action == "invalidate":
            signal.is_active = False
            
        return decay_metrics
    
    def _calculate_momentum_change(self, signal: ActiveSignal, current_data: pd.DataFrame) -> float:
        """Calculate momentum change since signal generation"""
        try:
            # Calculate current momentum indicators
            current_rsi = self._calculate_rsi(current_data['close'], 14)
            current_macd = self._calculate_macd(current_data['close'])
            
            # Get initial momentum state
            initial_rsi = signal.initial_technical_state.get('rsi', 50)
            initial_macd = signal.initial_technical_state.get('macd', 0)
            
            # Calculate momentum shift
            rsi_change = abs(current_rsi - initial_rsi) / 100
            macd_change = abs(current_macd - initial_macd) / max(abs(initial_macd), 0.001)
            
            momentum_change = (rsi_change + macd_change) / 2
            
            # Check if momentum is moving against the signal
            if signal.signal_type == "BUY":
                if current_rsi < initial_rsi and current_macd < initial_macd:
                    momentum_change *= 1.5  # Penalty for opposing momentum
            else:  # SELL signal
                if current_rsi > initial_rsi and current_macd > initial_macd:
                    momentum_change *= 1.5
                    
            return min(momentum_change, 1.0)
            
        except Exception as e:
            return 0.2  # Default moderate momentum change if calculation fails
    
    def _calculate_volume_change(self, signal: ActiveSignal, current_data: pd.DataFrame) -> float:
        """Calculate volume deterioration since signal generation"""
        try:
            if 'volume' not in current_data.columns:
                return 0.1  # Minimal penalty if no volume data
                
            # Calculate average volume over different periods
            recent_volume = current_data['volume'].tail(5).mean()
            initial_volume = signal.initial_technical_state.get('volume', recent_volume)
            
            if initial_volume == 0:
                return 0.1
                
            volume_change = 1 - (recent_volume / initial_volume)
            return max(0, min(volume_change, 1.0))
            
        except Exception as e:
            return 0.1
    
    def _calculate_volatility_change(self, signal: ActiveSignal, current_data: pd.DataFrame) -> float:
        """Calculate volatility change since signal generation"""
        try:
            # Calculate current ATR
            current_atr = self._calculate_atr(current_data, 14)
            initial_atr = signal.initial_technical_state.get('atr', current_atr)
            
            if initial_atr == 0:
                return 1.0
                
            volatility_ratio = current_atr / initial_atr
            
            # High volatility can invalidate signals
            if volatility_ratio > self.decay_config['volatility_spike_threshold']:
                return min(volatility_ratio - 1, 1.0)
            else:
                return 0.0
                
        except Exception as e:
            return 0.0
    
    def _calculate_trend_alignment(self, signal: ActiveSignal, current_data: pd.DataFrame) -> float:
        """Calculate how well the current trend aligns with the signal"""
        try:
            # Calculate moving averages
            ma_20 = current_data['close'].rolling(20).mean().iloc[-1]
            ma_50 = current_data['close'].rolling(50).mean().iloc[-1]
            current_price = current_data['close'].iloc[-1]
            
            # Determine current trend
            if current_price > ma_20 > ma_50:
                current_trend = "bullish"
            elif current_price < ma_20 < ma_50:
                current_trend = "bearish"
            else:
                current_trend = "neutral"
            
            # Check alignment with signal
            if signal.signal_type == "BUY" and current_trend == "bullish":
                return 1.0
            elif signal.signal_type == "SELL" and current_trend == "bearish":
                return 1.0
            elif current_trend == "neutral":
                return 0.5
            else:
                return 0.0  # Trend is against the signal
                
        except Exception as e:
            return 0.5
    
    def _identify_decay_reasons(self, time_elapsed: int, momentum_change: float, 
                             volume_change: float, volatility_change: float, 
                             trend_alignment: float) -> List[SignalDecayReason]:
        """Identify specific reasons for signal decay"""
        reasons = []
        
        # Time decay
        if time_elapsed > 120:  # 2 hours
            reasons.append(SignalDecayReason.TIME_DECAY)
            
        # Momentum shift
        if momentum_change > self.decay_config['momentum_shift_threshold']:
            reasons.append(SignalDecayReason.MOMENTUM_SHIFT)
            
        # Volume deterioration
        if volume_change > self.decay_config['volume_deterioration_threshold']:
            reasons.append(SignalDecayReason.VOLUME_DETERIORATION)
            
        # Volatility spike
        if volatility_change > 0.5:
            reasons.append(SignalDecayReason.VOLATILITY_SPIKE)
            
        # Trend reversal
        if trend_alignment < self.decay_config['trend_reversal_threshold']:
            reasons.append(SignalDecayReason.TREND_REVERSAL)
            
        return reasons
    
    def _calculate_current_strength(self, initial_confidence: float, time_decay_factor: float,
                                  momentum_change: float, volume_change: float,
                                  volatility_change: float, trend_alignment: float) -> float:
        """Calculate current signal strength considering all factors"""
        
        # Base strength with time decay
        current_strength = initial_confidence * time_decay_factor
        
        # Apply momentum penalty
        current_strength *= (1 - momentum_change * 0.3)
        
        # Apply volume penalty
        current_strength *= (1 - volume_change * 0.2)
        
        # Apply volatility penalty
        current_strength *= (1 - volatility_change * 0.4)
        
        # Apply trend alignment bonus/penalty
        current_strength *= (0.7 + trend_alignment * 0.3)
        
        return max(0.0, min(current_strength, 1.0))
    
    def _calculate_invalidation_score(self, decay_rate: float, decay_reasons: List[SignalDecayReason],
                                    time_elapsed: int) -> float:
        """Calculate overall invalidation score"""
        base_score = decay_rate
        
        # Add penalties for specific decay reasons
        reason_penalties = {
            SignalDecayReason.MOMENTUM_SHIFT: 0.3,
            SignalDecayReason.TREND_REVERSAL: 0.4,
            SignalDecayReason.VOLATILITY_SPIKE: 0.2,
            SignalDecayReason.VOLUME_DETERIORATION: 0.1,
            SignalDecayReason.TIME_DECAY: 0.1
        }
        
        for reason in decay_reasons:
            base_score += reason_penalties.get(reason, 0.0)
            
        # Time-based invalidation boost
        if time_elapsed > 360:  # 6 hours
            base_score += 0.2
            
        return min(base_score, 1.0)
    
    def _determine_recommended_action(self, invalidation_score: float, decay_rate: float) -> str:
        """Determine recommended action based on invalidation metrics"""
        if invalidation_score > 0.8 or decay_rate > 0.7:
            return "invalidate"
        elif invalidation_score > 0.6 or decay_rate > 0.5:
            return "close"
        elif invalidation_score > 0.4 or decay_rate > 0.3:
            return "reduce"
        else:
            return "hold"
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return 50.0
    
    def _calculate_macd(self, prices: pd.Series) -> float:
        """Calculate MACD indicator"""
        try:
            ema_12 = prices.ewm(span=12).mean()
            ema_26 = prices.ewm(span=26).mean()
            macd = ema_12 - ema_26
            return macd.iloc[-1]
        except:
            return 0.0
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift())
            low_close = np.abs(data['low'] - data['close'].shift())
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(period).mean()
            return atr.iloc[-1]
        except:
            return 0.01
    
    def get_active_signals_summary(self) -> Dict[str, Any]:
        """Get summary of all active signals and their decay status"""
        summary = {
            'total_active_signals': len([s for s in self.active_signals.values() if s.is_active]),
            'total_invalidated_signals': len([s for s in self.active_signals.values() if not s.is_active]),
            'signals_requiring_attention': [],
            'average_decay_rate': 0.0,
            'signals_by_action': {'hold': 0, 'reduce': 0, 'close': 0, 'invalidate': 0}
        }
        
        decay_rates = []
        for signal in self.active_signals.values():
            if signal.decay_metrics:
                decay_rates.append(signal.decay_metrics.decay_rate)
                summary['signals_by_action'][signal.decay_metrics.recommended_action] += 1
                
                if signal.decay_metrics.recommended_action in ['close', 'invalidate']:
                    summary['signals_requiring_attention'].append({
                        'signal_id': signal.signal_id,
                        'symbol': signal.symbol,
                        'type': signal.signal_type,
                        'decay_rate': signal.decay_metrics.decay_rate,
                        'recommended_action': signal.decay_metrics.recommended_action,
                        'decay_reasons': [r.value for r in signal.decay_metrics.decay_reasons]
                    })
        
        if decay_rates:
            summary['average_decay_rate'] = np.mean(decay_rates)
            
        return summary
    
    def cleanup_old_signals(self, max_age_hours: int = 48):
        """Remove signals older than specified age"""
        current_time = datetime.now()
        signals_to_remove = []
        
        for signal_id, signal in self.active_signals.items():
            age = current_time - signal.initial_timestamp
            if age.total_seconds() / 3600 > max_age_hours:
                signals_to_remove.append(signal_id)
        
        for signal_id in signals_to_remove:
            del self.active_signals[signal_id]
        
        return len(signals_to_remove)

# Global instance
_signal_decay_detector = None

async def get_signal_decay_detector() -> SignalDecayDetector:
    """Get or create the global signal decay detector instance"""
    global _signal_decay_detector
    if _signal_decay_detector is None:
        _signal_decay_detector = SignalDecayDetector()
    return _signal_decay_detector

async def register_new_signal(signal_data: Dict[str, Any]) -> str:
    """Register a new signal for decay monitoring"""
    detector = await get_signal_decay_detector()
    return detector.register_signal(signal_data)

async def update_signal_decay(signal_id: str, current_data: pd.DataFrame) -> SignalDecayMetrics:
    """Update decay metrics for a specific signal"""
    detector = await get_signal_decay_detector()
    return await detector.update_signal_decay(signal_id, current_data)

async def get_signals_summary() -> Dict[str, Any]:
    """Get summary of all active signals"""
    detector = await get_signal_decay_detector()
    return detector.get_active_signals_summary()

async def cleanup_old_signals(max_age_hours: int = 48) -> int:
    """Clean up old signals"""
    detector = await get_signal_decay_detector()
    return detector.cleanup_old_signals(max_age_hours)