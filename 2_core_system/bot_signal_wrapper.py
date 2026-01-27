#!/usr/bin/env python3
"""
Synchronous Bot Signal Wrapper for Walk-Forward Backtesting
Wraps UnifiedConfidenceEngine async methods for use in backtesting
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import warnings

warnings.filterwarnings('ignore')

# Try to import the bot engine
try:
    from unified_confidence_system import UnifiedConfidenceEngine
    BOT_ENGINE_AVAILABLE = True
except ImportError:
    BOT_ENGINE_AVAILABLE = False
    UnifiedConfidenceEngine = None


class SyncBotSignalWrapper:
    """Synchronous wrapper for bot signal generation in backtest environment"""
    
    def __init__(self):
        self.bot_available = BOT_ENGINE_AVAILABLE
        self.signal_cache = {}
        
        if self.bot_available:
            try:
                self.engine = UnifiedConfidenceEngine()
                print("✓ Bot engine loaded")
            except Exception as e:
                print(f"⚠️  Bot engine failed to initialize: {e}")
                self.bot_available = False
    
    def get_signal(self, data: pd.DataFrame, current_idx: int, pair: str = 'EUR/USD') -> Optional[Dict]:
        """
        Generate bot signal for current candle (synchronous)
        
        Returns:
            Dict with 'signal' (CALL/PUT), 'confidence' (0-100)
            or None if no signal
        """
        
        if not self.bot_available or current_idx < 50:
            return None
        
        try:
            # Prepare data - use recent history (100 candles)
            lookback = min(100, current_idx)
            df_window = data.iloc[current_idx - lookback:current_idx + 1].copy()
            
            # Build indicators dict from data
            indicators = self._calculate_indicators(df_window)
            
            # Calculate primary signals (synchronous parts only)
            primary_results = self.engine._calculate_primary_signals(
                df_window, indicators, pair, '5min'
            )
            
            # Get signal and confidence
            signal = primary_results.get('primary_signal')
            confidence = primary_results.get('primary_confidence', 50)
            
            if signal not in ['CALL', 'PUT']:
                return None
            
            return {
                'signal': signal,
                'confidence': float(confidence),
                'source': 'bot_engine'
            }
            
        except Exception as e:
            return None
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate basic indicators from OHLCV data"""
        
        indicators = {}
        
        try:
            close = df['close'].values
            
            # RSI
            indicators['rsi'] = self._calculate_rsi(close)
            
            # MACD
            ema12 = self._ema(close, 12)
            ema26 = self._ema(close, 26)
            macd = ema12 - ema26
            indicators['macd'] = macd
            
            # Moving Averages
            indicators['sma20'] = self._sma(close, 20)
            indicators['sma50'] = self._sma(close, 50)
            indicators['ema20'] = self._ema(close, 20)
            
            # Bollinger Bands
            sma = self._sma(close, 20)
            std = np.std(close[-20:]) if len(close) >= 20 else 0
            indicators['bb_upper'] = sma + (2 * std)
            indicators['bb_lower'] = sma - (2 * std)
            
            # ATR
            high = df['high'].values
            low = df['low'].values
            tr = np.maximum(
                np.maximum(high - low, np.abs(high - close[:-1])),
                np.abs(low - close[:-1])
            ) if len(close) > 1 else high - low
            indicators['atr'] = np.mean(tr[-14:]) if len(tr) >= 14 else np.mean(tr)
            
            # Volume
            indicators['volume_sma'] = self._sma(df['volume'].values, 20)
            
        except Exception as e:
            pass
        
        return indicators
    
    @staticmethod
    def _calculate_rsi(prices, period=14):
        """Calculate RSI"""
        if len(prices) < period:
            return np.zeros_like(prices)
        
        delta = np.diff(prices)
        seed = delta[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / (down + 1e-10)
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100. / (1. + rs)
        
        for i in range(period, len(prices)):
            delta_val = prices[i] - prices[i-1]
            up = (up * (period - 1) + (delta_val if delta_val > 0 else 0)) / period
            down = (down * (period - 1) + (-delta_val if delta_val < 0 else 0)) / period
            rs = up / (down + 1e-10)
            rsi[i] = 100. - 100. / (1. + rs)
        
        return rsi
    
    @staticmethod
    def _ema(prices, period):
        """Calculate EMA"""
        if len(prices) < period:
            return np.array([prices[-1]] * len(prices))
        
        ema = np.zeros_like(prices, dtype=float)
        ema[:period] = np.mean(prices[:period])
        
        multiplier = 2 / (period + 1)
        
        for i in range(period, len(prices)):
            ema[i] = prices[i] * multiplier + ema[i-1] * (1 - multiplier)
        
        return ema
    
    @staticmethod
    def _sma(prices, period):
        """Calculate SMA"""
        if len(prices) < period:
            return np.array([np.mean(prices)] * len(prices))
        
        sma = np.convolve(prices, np.ones(period) / period, mode='valid')
        return np.concatenate([np.full(period - 1, np.mean(prices[:period])), sma])


class HybridSignalGenerator:
    """
    Hybrid signal generator: Tries bot first, falls back to technical analysis
    """
    
    def __init__(self):
        self.bot_wrapper = SyncBotSignalWrapper()
        self.fallback_enabled = True
    
    def generate_signal(self, data: pd.DataFrame, current_idx: int, pair: str = 'EUR/USD') -> Optional[str]:
        """
        Generate trading signal: tries bot engine first, falls back to technical analysis
        
        Returns:
            'CALL', 'PUT', or None
        """
        
        # Try bot signal first (higher threshold for quality)
        bot_signal = self.bot_wrapper.get_signal(data, current_idx, pair)
        
        if bot_signal and bot_signal['confidence'] >= 55:  # Lowered from 65 for more signals
            return bot_signal['signal']
        
        # Fall back to technical analysis (lower quality than bot, use lower threshold)
        if self.fallback_enabled and current_idx >= 100:
            return self._technical_signal(data, current_idx)
        
        return None
    
    def _technical_signal(self, data: pd.DataFrame, current_idx: int) -> Optional[str]:
        """
        Technical analysis fallback: RSI + MACD + Moving Averages
        """
        
        try:
            close = data['close'].values
            
            # RSI
            rsi = SyncBotSignalWrapper._calculate_rsi(close)[-1]
            
            # MACD
            ema12 = SyncBotSignalWrapper._ema(close, 12)[-1]
            ema26 = SyncBotSignalWrapper._ema(close, 26)[-1]
            macd_line = ema12 - ema26
            
            # Moving Averages
            sma20 = SyncBotSignalWrapper._sma(close, 20)[-1]
            sma50 = SyncBotSignalWrapper._sma(close, 50)[-1]
            current_price = close[-1]
            
            # Signal scoring
            score = 0
            signal_votes = {}
            
            # RSI component (40 points)
            if rsi < 30:
                signal_votes['CALL'] = signal_votes.get('CALL', 0) + 40
            elif rsi > 70:
                signal_votes['PUT'] = signal_votes.get('PUT', 0) + 40
            
            # MACD component (30 points)
            if macd_line > 0:
                signal_votes['CALL'] = signal_votes.get('CALL', 0) + 30
            else:
                signal_votes['PUT'] = signal_votes.get('PUT', 0) + 30
            
            # Moving Average component (30 points)
            if current_price > sma20 > sma50:
                signal_votes['CALL'] = signal_votes.get('CALL', 0) + 30
            elif current_price < sma20 < sma50:
                signal_votes['PUT'] = signal_votes.get('PUT', 0) + 30
            
            # Determine signal
            if signal_votes.get('CALL', 0) > signal_votes.get('PUT', 0):
                return 'CALL'
            elif signal_votes.get('PUT', 0) > signal_votes.get('CALL', 0):
                return 'PUT'
            
            return None
            
        except Exception as e:
            return None
