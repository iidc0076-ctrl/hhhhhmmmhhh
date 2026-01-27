#!/usr/bin/env python3
"""
ML Ensemble Integration: Combines Phase 3 signals with statistical confidence scoring
Uses ensemble methods (voting + weighting) to improve signal reliability
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict
from phase3_enhanced_signals import Phase3SignalEngine


class MLEnsembleSignalGenerator:
    """Ensemble that combines Phase 3 + technical + statistical signals"""
    
    def __init__(self, params: dict, ensemble_method: str = 'weighted_vote'):
        """
        Initialize ensemble
        
        ensemble_method: 'weighted_vote', 'consensus', or 'confidence_threshold'
        """
        self.params = params
        self.phase3_engine = Phase3SignalEngine(params)
        self.ensemble_method = ensemble_method
        self.signal_history = []  # Track signal confidence over time
        
    def generate_signal(self, data: pd.DataFrame, current_idx: int, pair: str = 'USD/CAD') -> Tuple[Optional[str], float]:
        """
        Generate signal with confidence score
        
        Returns:
            (signal, confidence) where confidence is 0.0-1.0
        """
        if current_idx < 100:
            return None, 0.0
        
        # Collect signals from multiple sources
        signals = {}
        
        # Signal 1: Phase 3 (regime-aware)
        phase3_signal = self.phase3_engine.generate_signal(data, current_idx, pair)
        if phase3_signal:
            signals['phase3'] = phase3_signal
        
        # Signal 2: RSI extreme
        rsi_signal = self._rsi_extreme_signal(data, current_idx)
        if rsi_signal:
            signals['rsi'] = rsi_signal
        
        # Signal 3: MACD momentum
        macd_signal = self._macd_momentum_signal(data, current_idx)
        if macd_signal:
            signals['macd'] = macd_signal
        
        # Signal 4: Moving average crossover
        ma_signal = self._ma_crossover_signal(data, current_idx)
        if ma_signal:
            signals['ma'] = ma_signal
        
        # Signal 5: Volume profile
        vol_signal = self._volume_profile_signal(data, current_idx)
        if vol_signal:
            signals['volume'] = vol_signal
        
        # Ensemble voting
        if not signals:
            return None, 0.0
        
        final_signal, confidence = self._ensemble_vote(signals)
        
        # Store for analysis
        self.signal_history.append({
            'datetime': data['datetime'].iloc[current_idx],
            'signals': signals,
            'final_signal': final_signal,
            'confidence': confidence
        })
        
        return final_signal, confidence
    
    def _rsi_extreme_signal(self, data: pd.DataFrame, current_idx: int) -> Optional[str]:
        """RSI oversold/overbought extremes"""
        try:
            rsi = self._calculate_rsi(data['close'], period=14).iloc[current_idx]
            if rsi < 20:  # Very oversold
                return 'CALL'
            elif rsi > 80:  # Very overbought
                return 'PUT'
        except:
            pass
        return None
    
    def _macd_momentum_signal(self, data: pd.DataFrame, current_idx: int) -> Optional[str]:
        """MACD momentum + signal line crossover"""
        try:
            ema12 = data['close'].ewm(span=12).mean().iloc[current_idx]
            ema26 = data['close'].ewm(span=26).mean().iloc[current_idx]
            macd_line = ema12 - ema26
            
            # MACD signal line (EMA of MACD)
            if current_idx >= 9:
                macd_history = []
                for i in range(max(0, current_idx - 50), current_idx + 1):
                    e12 = data['close'].ewm(span=12).mean().iloc[i]
                    e26 = data['close'].ewm(span=26).mean().iloc[i]
                    macd_history.append(e12 - e26)
                signal_line = pd.Series(macd_history).ewm(span=9).mean().iloc[-1]
                
                if macd_line > signal_line and macd_line > 0:
                    return 'CALL'
                elif macd_line < signal_line and macd_line < 0:
                    return 'PUT'
        except:
            pass
        return None
    
    def _ma_crossover_signal(self, data: pd.DataFrame, current_idx: int) -> Optional[str]:
        """Golden cross (SMA20 > SMA50) and death cross"""
        try:
            if current_idx < 50:
                return None
            
            sma20 = data['close'].rolling(20).mean().iloc[current_idx]
            sma50 = data['close'].rolling(50).mean().iloc[current_idx]
            price = data['close'].iloc[current_idx]
            
            # Golden cross: SMA20 crosses above SMA50
            if current_idx > 0:
                sma20_prev = data['close'].rolling(20).mean().iloc[current_idx - 1]
                sma50_prev = data['close'].rolling(50).mean().iloc[current_idx - 1]
                
                if sma20_prev <= sma50_prev and sma20 > sma50:
                    return 'CALL'
                elif sma20_prev >= sma50_prev and sma20 < sma50:
                    return 'PUT'
            
            # Fallback: price relative to crossover
            if price > sma20 > sma50:
                return 'CALL'
            elif price < sma20 < sma50:
                return 'PUT'
        except:
            pass
        return None
    
    def _volume_profile_signal(self, data: pd.DataFrame, current_idx: int) -> Optional[str]:
        """Volume profile: higher volume on up moves suggests bullish"""
        try:
            if current_idx < 20:
                return None
            
            vol_recent = data['volume'].iloc[max(0, current_idx-20):current_idx+1].values
            close_recent = data['close'].iloc[max(0, current_idx-20):current_idx+1].values
            
            # Calculate volume-weighted direction
            if len(vol_recent) < 2:
                return None
            
            ups = 0
            downs = 0
            for i in range(1, len(close_recent)):
                if close_recent[i] > close_recent[i-1]:
                    ups += vol_recent[i]
                else:
                    downs += vol_recent[i]
            
            if ups > downs * 1.3:  # 30% more volume on ups
                return 'CALL'
            elif downs > ups * 1.3:
                return 'PUT'
        except:
            pass
        return None
    
    def _ensemble_vote(self, signals: Dict[str, str]) -> Tuple[Optional[str], float]:
        """Combine multiple signals using ensemble method"""
        
        if self.ensemble_method == 'consensus':
            # All signals must agree
            if len(set(signals.values())) == 1:
                signal = list(signals.values())[0]
                confidence = len(signals) / 5.0  # Max 5 signals
                return signal, min(confidence, 1.0)
            return None, 0.0
        
        elif self.ensemble_method == 'weighted_vote':
            # Weight by signal strength (Phase 3 > others)
            weights = {
                'phase3': 0.4,
                'rsi': 0.2,
                'macd': 0.2,
                'ma': 0.15,
                'volume': 0.05
            }
            
            call_score = 0
            put_score = 0
            
            for signal_name, signal_val in signals.items():
                weight = weights.get(signal_name, 0.1)
                if signal_val == 'CALL':
                    call_score += weight
                else:
                    put_score += weight
            
            if call_score > put_score:
                return 'CALL', call_score / sum(weights.values())
            elif put_score > call_score:
                return 'PUT', put_score / sum(weights.values())
            else:
                return None, 0.0
        
        elif self.ensemble_method == 'confidence_threshold':
            # Require Phase 3 + at least one other signal
            if 'phase3' not in signals:
                return None, 0.0
            
            phase3_sig = signals['phase3']
            agreement_count = sum(1 for v in signals.values() if v == phase3_sig)
            
            if agreement_count >= 2:  # Phase 3 + 1 other
                confidence = agreement_count / len(signals)
                return phase3_sig, confidence
            
            return None, 0.0
        
        return None, 0.0
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_signal_quality_stats(self) -> Dict:
        """Analyze signal quality and confidence distribution"""
        if not self.signal_history:
            return {}
        
        df_history = pd.DataFrame(self.signal_history)
        
        return {
            'total_signals': len(df_history),
            'signals_with_trades': len(df_history[df_history['final_signal'].notna()]),
            'avg_confidence': df_history[df_history['final_signal'].notna()]['confidence'].mean(),
            'confidence_distribution': {
                'high (>0.7)': len(df_history[df_history['confidence'] > 0.7]),
                'medium (0.5-0.7)': len(df_history[(df_history['confidence'] > 0.5) & (df_history['confidence'] <= 0.7)]),
                'low (0.3-0.5)': len(df_history[(df_history['confidence'] > 0.3) & (df_history['confidence'] <= 0.5)]),
            }
        }
