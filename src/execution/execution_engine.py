# Execution engine module
"""
Trade execution and backtesting logic.
"""

import pandas as pd
import numpy as np
from src.utils.config import RISK_PER_TRADE_PCT


class ExecutionEngine:
    """Runs backtest with ATR-based position sizing."""
    
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
    
    def run_backtest(self, df_signals, hold_horizon_days=1):
        """
        Run backtest on signals with Next-Open execution.
        
        Args:
            df_signals: DataFrame with Signal column
            hold_horizon_days: Number of days to hold each trade
            
        Returns:
            Tuple of (stats_dict, trade_log_df, equity_curve_df)
        """
        capital = self.initial_capital
        position = 0
        entry_price = 0
        days_held = 0
        position_qty = 0
        equity_curve = []
        trades = []
        
        # Prepare execution data: need 'Open' of NEXT day for signal execution
        df = df_signals.copy()
        df['NextOpen'] = df['Open'].shift(-1)
        df = df.dropna(subset=['NextOpen'])
        
        for date, row in df.iterrows():
            current_signal = row['Signal']
            exec_price = row['NextOpen']  # Price we will trade at (Tomorrow's Open)
            
            # 1. Update Equity and Check Exits
            if position != 0:
                days_held += 1
                
                # Exit after holding period
                if days_held >= hold_horizon_days:
                    qty = position_qty
                    pnl = (exec_price - entry_price) * qty * position
                    capital += pnl
                    trades.append({
                        'Date': date,
                        'Type': 'EXIT',
                        'Price': exec_price,
                        'PnL': pnl
                    })
                    position = 0
                    days_held = 0
            
            # 2. Check Entries (if flat)
            if position == 0 and current_signal != 'FLAT':
                # ATR position sizing
                risk_per_trade = RISK_PER_TRADE_PCT * capital
                atr = row.get('ATR', np.nan)
                
                if atr <= 0 or np.isnan(atr):
                    continue
                
                stop_distance = 1.2 * atr
                calc_qty = int(risk_per_trade / stop_distance)
                
                if calc_qty <= 0:
                    continue
                
                position = 1 if current_signal == 'LONG' else -1
                entry_price = exec_price
                position_qty = calc_qty
                days_held = 0
                trades.append({
                    'Date': date,
                    'Type': current_signal,
                    'Price': exec_price
                })
            
            # Record equity
            curr_equity = capital
            if position != 0:
                qty = position_qty
                curr_equity = capital + (row['Close'] - entry_price) * qty * position
            equity_curve.append({'Date': date, 'Equity': curr_equity})
        
        # Calculate performance metrics
        df_equity = pd.DataFrame(equity_curve).set_index('Date')
        if df_equity.empty:
            return {
                'Total PnL': 0,
                'Return %': 0,
                'Sharpe Ratio': 0,
                'Max Drawdown': 0,
                'Total Trades': 0,
                'Win Rate': 0
            }, pd.DataFrame(), pd.DataFrame()
        
        total_return = df_equity['Equity'].iloc[-1] - self.initial_capital
        ret_pct = (total_return / self.initial_capital) * 100
        daily_rets = df_equity['Equity'].pct_change()
        sharpe = daily_rets.mean() / daily_rets.std() * np.sqrt(252) if daily_rets.std() != 0 else 0
        cum_max = df_equity['Equity'].cummax()
        dd = (df_equity['Equity'] - cum_max) / cum_max
        max_dd = dd.min() * 100
        exits = [t for t in trades if t['Type'] == 'EXIT']
        wins = len([t for t in exits if t['PnL'] > 0])
        win_rate = (wins / len(exits) * 100) if exits else 0
        
        return {
            'Total PnL': total_return,
            'Return %': ret_pct,
            'Sharpe Ratio': sharpe,
            'Max Drawdown': max_dd,
            'Total Trades': len(exits),
            'Win Rate': win_rate
        }, pd.DataFrame(trades), df_equity
