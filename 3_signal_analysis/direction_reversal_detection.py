"""
Direction Reversal Detection Module
Detects trend reversals and integrates with signal analysis
"""

import pandas as pd
import numpy as np

def detect_direction_reversals(data, period=14):
    """Detect potential direction reversals in price data"""
    try:
        if data is None or len(data) < period:
            return []
        
        reversals = []
        close_prices = data['close'] if 'close' in data else data
        
        # Simple reversal detection based on price momentum
        for i in range(period, len(close_prices)):
            recent_high = close_prices[i-period:i].max()
            recent_low = close_prices[i-period:i].min()
            current_price = close_prices.iloc[i]
            
            # Potential bullish reversal
            if current_price <= recent_low * 1.02 and current_price > close_prices.iloc[i-1]:
                reversals.append({
                    'index': i,
                    'type': 'bullish',
                    'strength': (current_price - recent_low) / recent_low,
                    'price': current_price
                })
            
            # Potential bearish reversal
            elif current_price >= recent_high * 0.98 and current_price < close_prices.iloc[i-1]:
                reversals.append({
                    'index': i,
                    'type': 'bearish', 
                    'strength': (recent_high - current_price) / recent_high,
                    'price': current_price
                })
        
        return reversals
        
    except Exception as e:
        print(f"Error in direction reversal detection: {e}")
        return []

def integrate_reversal_with_signals(signals, reversals):
    """Integrate reversal data with existing signals"""
    try:
        if not signals or not reversals:
            return signals
        
        # Ensure signals is a list of dictionaries, not strings
        if isinstance(signals, str):
            print(f"Warning: signals parameter is a string: {signals}")
            return []
        
        enhanced_signals = signals.copy() if isinstance(signals, list) else []
        
        for reversal in reversals:
            # Find closest signal to reversal
            for signal in enhanced_signals:
                # Ensure signal is a dictionary, not a string
                if isinstance(signal, str):
                    print(f"Warning: signal is a string instead of dict: {signal}")
                    continue
                    
                if isinstance(signal, dict) and abs(signal.get('index', 0) - reversal['index']) <= 3:
                    signal['reversal_confirmed'] = True
                    signal['reversal_type'] = reversal['type']
                    signal['reversal_strength'] = reversal['strength']
                    
                    # Boost confidence for confirmed reversals
                    if 'confidence' in signal:
                        signal['confidence'] = min(100, signal['confidence'] * 1.2)
        
        return enhanced_signals
        
    except Exception as e:
        print(f"Error integrating reversals with signals: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return signals if signals else []