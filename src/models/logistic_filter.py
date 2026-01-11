# ML Filter module
"""
Logistic Regression filter for trade signal veto.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier


class MLFilter:
    """Rolling Logistic Regression filter to veto low-probability trades."""
    
    def __init__(self, lookback_window=20):
        self.lookback_window = lookback_window
        self.model = OneVsRestClassifier(
            LogisticRegression(
                penalty='l2',
                C=0.1,
                solver='liblinear',
                max_iter=1000,
                random_state=42
            )
        )
        self.is_trained = False
    
    def train(self, df):
        """Train the model on historical data."""
        X, y = self._prepare_data(df)
        if len(X) >= 5 and len(y.unique()) > 1:
            self.model.fit(X, y)
            self.is_trained = True
        else:
            self.is_trained = False
    
    def apply_veto(self, df, threshold=0.55):
        """Apply ML veto to signals below probability threshold."""
        df = df.copy()
        if not self.is_trained:
            return df
        
        try:
            X, _ = self._prepare_data(df, training=False)
            common_idx = df.index.intersection(X.index)
            if common_idx.empty:
                return df
            
            probs_all = self.model.predict_proba(X.loc[common_idx])
            classes = list(self.model.classes_)
            
            if 1.0 in classes:
                col_idx = classes.index(1.0)
                probs = probs_all[:, col_idx]
            else:
                probs = np.full(len(common_idx), 0.5)
            
            for i, date in enumerate(common_idx):
                sig = df.loc[date, 'direction']
                prob = probs[i]
                if sig == 1 and prob < threshold:
                    df.loc[date, 'Signal'] = 'FLAT'
                    df.loc[date, 'direction'] = 0
                if sig == -1 and prob > (1 - threshold):
                    df.loc[date, 'Signal'] = 'FLAT'
                    df.loc[date, 'direction'] = 0
        except Exception as e:
            print(f"Veto error (safe): {e}")
        
        return df
    
    def predict_probs(self, df):
        """Return probability predictions for the dataframe."""
        if not self.is_trained:
            return [0.5] * len(df)
        
        try:
            X, _ = self._prepare_data(df, training=False)
            common_idx = df.index.intersection(X.index)
            if common_idx.empty:
                return [0.5] * len(df)
            
            probs_all = self.model.predict_proba(X.loc[common_idx])
            classes = list(self.model.classes_)
            if 1.0 in classes:
                col_idx = classes.index(1.0)
                return list(probs_all[:, col_idx])
            else:
                return [0.5] * len(common_idx)
        except Exception as e:
            print(f"Predict error (safe): {e}")
            return [0.5] * len(df)
    
    def _prepare_data(self, df, training=True):
        """Prepare features and target for ML model."""
        df = df.copy()
        df['Target'] = np.sign(df['Close'].shift(-1) - df['Close'])
        df['SMA_Diff'] = (df['Close'] - df['SMA_20']) / df['SMA_20']
        features = ['RSI', 'ATR', 'SMA_Diff', 'BB_Std']
        data = df[features].dropna()
        
        if training:
            y = df['Target'].loc[data.index].dropna()
            common = data.index.intersection(y.index)
            return data.loc[common], y.loc[common]
        else:
            return data, None
