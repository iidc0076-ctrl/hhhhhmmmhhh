#!/usr/bin/env python3
"""
Phase 3: Enhanced Signal System with Regime Filters
- Volatility regime detection (Bollinger Bands)
- Time-of-day filters (avoid low liquidity)
- RSI divergence detection (reversal signals)
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple


class Phase3SignalEngine:
    """Enhanced signal generator with regime awareness and filters"""
    
    def __init__(self, params: dict):
        """
        Initialize with optimized parameters from grid search
        
        Expected params keys: rsi_period, rsi_oversold, rsi_overbought,
        sma_short, sma_long, macd_fast, macd_slow, vote_threshold
        """
        self.params = params
        
    def generate_signal(self, data: pd.DataFrame, current_idx: int, pair: str = 'EUR/USD') -> Optional[str]:
        """
        Generate signal with regime awareness and filters
        
        Returns:
            'CALL', 'PUT', or None
        """
        if current_idx < 100:
            return None
        
        # Pre-check: apply regime and time filters first
        if not self._pass_regime_filter(data, current_idx):
            return None
        
        if not self._pass_time_filter(data, current_idx):
            return None
        
        # Generate base signal
        signal = self._technical_signal_with_params(data, current_idx)
        if signal is None:
            return None
        
        # Enhance with divergence detection
        divergence_signal = self._detect_divergence(data, current_idx)
        
        # If divergence contradicts main signal, return None (wait for clarity)
        if divergence_signal and divergence_signal != signal:
            return None
        
        # If divergence confirms signal, boost confidence
        if divergence_signal and divergence_signal == signal:
            return signal
        
        return signal
    
    def _pass_regime_filter(self, data: pd.DataFrame, current_idx: int) -> bool:
        """
        Volatility regime filter: only trade when volatility is reasonable
        
        Avoid: ultra-low vol (< 0.2%) and panic spikes (> 5%)
        """
        if current_idx < 50:
            return True
        
        # Bollinger Bands (20-period, 2 std dev)
        sma20 = data['close'].rolling(20).mean().iloc[current_idx]
        std20 = data['close'].rolling(20).std().iloc[current_idx]
        
        # Normalized volatility
        bb_width = 4 * std20 / sma20 if sma20 > 0 else 0
        
        # Relaxed: 0.2% to 5% volatility range
        return 0.002 <= bb_width <= 0.05
    
    def _pass_time_filter(self, data: pd.DataFrame, current_idx: int) -> bool:
        """
        Time-of-day filter: trade during reasonable hours with liquidity
        
        Avoid: 21:00-05:00 UTC (graveyard shift, wide spreads)
        Trade: 05:00-21:00 UTC (covers all major sessions)
        """
        dt = data['datetime'].iloc[current_idx]
        hour = dt.hour
        
        # Avoid graveyard shift (21:00-04:59 UTC)
        return 5 <= hour < 21
    
    def _detect_divergence(self, data: pd.DataFrame, current_idx: int) -> Optional[str]:
        """
        RSI Divergence detection: price makes new high/low but RSI doesn't
        
        Bullish div: price low < prev low, RSI low > prev RSI → expect bounce UP
        Bearish div: price high > prev high, RSI high < prev RSI → expect bounce DOWN
        
        Returns:
            'CALL' if bullish divergence, 'PUT' if bearish divergence, None otherwise
        """
        if current_idx < 20:
            return None
        
        # Look back window (last 5-20 candles for recent divergence)
        lookback = 15
        if current_idx < lookback + 1:
            lookback = current_idx - 2
        
        close_recent = data['close'].iloc[current_idx - lookback:current_idx + 1].values
        rsi_recent = self._calculate_rsi(data['close'].iloc[:current_idx + 1], period=14)[-lookback:].values
        
        if len(close_recent) < 3 or len(rsi_recent) < 3:
            return None
        
        current_close = close_recent[-1]
        current_rsi = rsi_recent[-1]
        
        # Find recent swing low/high
        swing_low_idx = np.argmin(close_recent[:-1])
        swing_high_idx = np.argmax(close_recent[:-1])
        
        swing_low = close_recent[swing_low_idx]
        swing_low_rsi = rsi_recent[swing_low_idx]
        swing_high = close_recent[swing_high_idx]
        swing_high_rsi = rsi_recent[swing_high_idx]
        
        try:
            # Bullish divergence: price low < swing low, RSI low > swing low RSI
            if current_close < swing_low and current_rsi > swing_low_rsi and current_rsi < 30:
                return 'CALL'
            
            # Bearish divergence: price high > swing high, RSI high < swing high RSI
            if current_close > swing_high and current_rsi < swing_high_rsi and current_rsi > 70:
                return 'PUT'
        except:
            pass
        
        return None
    
    def _technical_signal_with_params(self, data: pd.DataFrame, current_idx: int) -> Optional[str]:
        """Core technical signal (RSI + MACD + MA voting)"""
        try:
            # RSI
            rsi = self._calculate_rsi(data['close'], period=int(self.params.get('rsi_period', 14))).iloc[current_idx]
            
            # MACD (EMAs)
            ema_fast = data['close'].ewm(span=int(self.params.get('macd_fast', 12))).mean().iloc[current_idx]
            ema_slow = data['close'].ewm(span=int(self.params.get('macd_slow', 26))).mean().iloc[current_idx]
            macd_val = ema_fast - ema_slow
            
            # Moving averages
            sma_short = data['close'].rolling(window=int(self.params.get('sma_short', 20))).mean().iloc[current_idx]
            sma_long = data['close'].rolling(window=int(self.params.get('sma_long', 50))).mean().iloc[current_idx]
            price = data['close'].iloc[current_idx]
            
            # Voting with weights
            votes_call = 0
            votes_put = 0
            
            if pd.notna(rsi):
                if rsi < self.params.get('rsi_oversold', 30):
                    votes_call += 40
                elif rsi > self.params.get('rsi_overbought', 70):
                    votes_put += 40
            
            if pd.notna(macd_val):
                if macd_val > 0:
                    votes_call += 30
                else:
                    votes_put += 30
            
            if pd.notna(sma_short) and pd.notna(sma_long):
                if price > sma_short > sma_long:
                    votes_call += 30
                elif price < sma_short < sma_long:
                    votes_put += 30
            
            # Threshold
            vote_threshold = self.params.get('vote_threshold', 50)
            if votes_call == votes_put or max(votes_call, votes_put) < vote_threshold:
                return None
            
            return 'CALL' if votes_call > votes_put else 'PUT'
        except Exception:
            return None
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi
