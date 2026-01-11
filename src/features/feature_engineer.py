# Feature engineering module
"""
Technical indicator calculations for trading signals.
"""

import pandas as pd
import numpy as np


class FeatureEngineer:
    """Adds technical indicators to OHLCV data."""
    
    def add_features(self, df):
        """
        Add RSI, SMA, ATR, and Bollinger Bands to the dataframe.
        
        Args:
            df: DataFrame with OHLCV columns
            
        Returns:
            DataFrame with added feature columns
        """
        df = df.copy()
        if df.empty:
            return df
        
        # RSI (14-period)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # SMA (using 20-day for both due to small dataset)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=20).mean()  # Use 20 as proxy
        
        # ATR (14-period)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(14).mean()
        
        # Bollinger Bands
        df['BB_Mid'] = df['Close'].rolling(20).mean()
        df['BB_Std'] = df['Close'].rolling(20).std()
        df['BB_Upper'] = df['BB_Mid'] + 2 * df['BB_Std']
        df['BB_Lower'] = df['BB_Mid'] - 2 * df['BB_Std']
        
        # Forward fill then drop remaining NaNs
        df = df.ffill().dropna()
        return df
