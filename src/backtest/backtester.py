# Backtester module
"""
Trade plan generation for forward forecasts.
"""

import pandas as pd
import numpy as np
from src.utils.config import RISK_PER_TRADE_PCT


class TradePlanGenerator:
    """Generates actionable trade plans for future dates."""
    
    def generate_plan(self, df_signals, exec_engine, start_date, end_date):
        """
        Generate a trade plan for the given date range.
        
        Args:
            df_signals: DataFrame with signals and features
            exec_engine: ExecutionEngine instance for capital reference
            start_date: Start date for plan
            end_date: End date for plan
            
        Returns:
            DataFrame with Date, Signal, Qty, EntryPrice, StopLoss, etc.
        """
        # Prepare data with NextOpen for entry price projection
        df_plan = df_signals.copy()
        df_plan['NextOpen'] = df_plan['Open'].shift(-1)
        
        mask = (df_plan.index >= start_date) & (df_plan.index <= end_date)
        plan_df = df_plan[mask].copy()
        output = []
        
        capital = exec_engine.initial_capital
        
        for date, row in plan_df.iterrows():
            sig = row['Signal']
            qty = 0
            entry = 0
            sl = '-'
            target = '-'
            exit_cond = '-'
            
            if sig in ['LONG', 'SHORT']:
                atr = row.get('ATR', 0)
                if atr > 0:
                    # Calculate Qty based on Risk
                    risk_amt = capital * RISK_PER_TRADE_PCT
                    stop_dist = 1.2 * atr
                    qty = int(risk_amt / stop_dist)
                    
                    # Projected Entry
                    next_open = row.get('NextOpen', np.nan)
                    if pd.notna(next_open):
                        entry = next_open
                    else:
                        entry = row['Close']  # Estimate
                    
                    # Calculate Levels
                    if sig == 'LONG':
                        stop_price = entry - stop_dist
                        sl = round(stop_price, 2)
                    else:
                        stop_price = entry + stop_dist
                        sl = round(stop_price, 2)
                    
                    exit_cond = "Hold 1 Day"
                    target = "Open T+2"
            
            output.append({
                'Date': date.date(),
                'Signal': sig,
                'Qty': qty,
                'EntryPrice': round(entry, 2) if isinstance(entry, (int, float)) else entry,
                'ExitCondition': exit_cond,
                'StopLoss': sl,
                'Target': target
            })
        
        return pd.DataFrame(output)
