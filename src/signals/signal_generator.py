# Signal generation module
"""
Trading signal generation based on technical indicators.
"""


class SignalGenerator:
    """Generates LONG/SHORT/FLAT signals based on technical rules."""
    
    def __init__(self, threshold=1.0):
        self.threshold = threshold
    
    def generate_signals(self, df):
        """
        Generate trading signals based on SMA crossover and RSI.
        
        Rules:
        - LONG: Close > SMA_20 AND RSI < 70
        - SHORT: Close < SMA_20 AND RSI > 30
        - FLAT: Otherwise
        
        Args:
            df: DataFrame with feature columns
            
        Returns:
            DataFrame with Signal and direction columns added
        """
        df = df.copy()
        df['Signal'] = 'FLAT'
        df['direction'] = 0
        
        # Long condition: price above SMA with room to run (RSI not overbought)
        long_cond = (df['Close'] > df['SMA_20']) & (df['RSI'] < 70)
        
        # Short condition: price below SMA with room to fall (RSI not oversold)
        short_cond = (df['Close'] < df['SMA_20']) & (df['RSI'] > 30)
        
        df.loc[long_cond, 'Signal'] = 'LONG'
        df.loc[long_cond, 'direction'] = 1
        df.loc[short_cond, 'Signal'] = 'SHORT'
        df.loc[short_cond, 'direction'] = -1
        
        return df
