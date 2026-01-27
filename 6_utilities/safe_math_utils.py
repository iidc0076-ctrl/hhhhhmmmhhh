"""
Safe Math Utilities
Provides safe mathematical operations with error handling
"""

import numpy as np
import pandas as pd

def safe_mean(data, default=0.0):
    """Safely calculate mean with fallback"""
    try:
        if data is None or len(data) == 0:
            return default
        if isinstance(data, (list, np.ndarray, pd.Series)):
            clean_data = [x for x in data if x is not None and not (isinstance(x, float) and np.isnan(x))]
            if len(clean_data) == 0:
                return default
            return np.mean(clean_data)
        return float(data) if data is not None else default
    except:
        return default

def safe_std(data, default=1.0):
    """Safely calculate standard deviation with fallback"""
    try:
        if data is None or len(data) < 2:
            return default
        if isinstance(data, (list, np.ndarray, pd.Series)):
            clean_data = [x for x in data if x is not None and not (isinstance(x, float) and np.isnan(x))]
            if len(clean_data) < 2:
                return default
            return np.std(clean_data)
        return default
    except:
        return default

def safe_divide(numerator, denominator, default=0.0):
    """Safely divide with fallback for zero division"""
    try:
        if denominator == 0 or denominator is None:
            return default
        if numerator is None:
            return default
        result = numerator / denominator
        if np.isnan(result) or np.isinf(result):
            return default
        return result
    except:
        return default