#!/usr/bin/env python
"""
SONATSOFTW.NS Trading Strategy - Main Entry Point

End-to-end ML-driven trading system using rolling logistic regression
and ATR-based risk management.

Usage:
    python run_strategy.py
"""

import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Import configuration
from src.utils.config import (
    TICKER, DATA_START, DATA_END, INITIAL_CAPITAL,
    WARMUP_DAYS, WINDOW_SIZE_DAYS, LOOKBACK_WINDOW,
    HOLD_HORIZON, ML_VETO_THRESHOLD
)

# Import modules
from src.data.data_loader import load_data
from src.features.feature_engineer import FeatureEngineer
from src.signals.signal_generator import SignalGenerator
from src.models.logistic_filter import MLFilter
from src.execution.execution_engine import ExecutionEngine
from src.backtest.backtester import TradePlanGenerator


def main():
    """Run the full trading strategy pipeline."""
    print("=" * 60)
    print(" VARIANT D (LOGISTIC REGRESSION) - STRICT ROLLING")
    print("=" * 60)
    print(f"Asset: {TICKER}")
    
    # ============================================================
    # STEP 1: Load Data
    # ============================================================
    secrets_path = os.path.join(os.path.dirname(__file__), 'fyers_secrets.json')
    df_full = load_data(TICKER, start_date='2025-11-01', end_date='2025-12-31', fyers_secrets_path=secrets_path)
    
    # Slice to backtest period
    mask_stress = (df_full.index >= DATA_START) & (df_full.index <= DATA_END)
    df = df_full[mask_stress].copy()
    print(f"Nov-Dec slice: {len(df)} rows")
    
    # ============================================================
    # STEP 2: Feature Engineering
    # ============================================================
    print("Running Feature Engineering...")
    fe_engine = FeatureEngineer()
    df_features = fe_engine.add_features(df)
    print(f"After features: {len(df_features)} rows")
    
    if df_features.empty:
        print("ERROR: No data after feature engineering. Exiting.")
        return
    
    # ============================================================
    # STEP 3: Generate Signals
    # ============================================================
    sig_engine = SignalGenerator(threshold=1)
    df_signals = sig_engine.generate_signals(df_features)
    print(f"After signals: {len(df_signals)} rows")
    
    # ============================================================
    # STEP 4: Apply ML Filter (Rolling Walk-Forward)
    # ============================================================
    ml_filter = MLFilter(lookback_window=LOOKBACK_WINDOW)
    experiment_signals = df_signals.copy()
    experiment_signals['veto'] = False
    experiment_signals['ml_prob'] = 0.5
    
    print("Running Rolling Walk-Forward ML Loop (Logistic Regression)...")
    valid_dates = sorted(df_signals.index[df_signals.index >= (df_signals.index[0] + pd.Timedelta(days=WARMUP_DAYS))])
    print(f"Valid dates for rolling: {len(valid_dates)}")
    
    for current_date in valid_dates:
        # Lag 2 days to avoid Lookahead Bias
        train_end = current_date - pd.Timedelta(days=2)
        train_start = current_date - pd.Timedelta(days=WINDOW_SIZE_DAYS + 10)
        train_mask = (df_signals.index >= train_start) & (df_signals.index <= train_end)
        df_train = df_signals[train_mask]
        if len(df_train) < 5:
            continue
        ml_filter.train(df_train)
        
        current_row = df_signals.loc[[current_date]]
        probs = ml_filter.predict_probs(current_row)
        prob = probs[0] if len(probs) > 0 else 0.5
        
        experiment_signals.loc[current_date, 'ml_prob'] = prob
        if prob < ML_VETO_THRESHOLD:
            experiment_signals.loc[current_date, 'veto'] = True
            experiment_signals.loc[current_date, 'Signal'] = 'FLAT'
            experiment_signals.loc[current_date, 'direction'] = 0
    
    print(f"Rolling Loop Complete. Vetoed {experiment_signals['veto'].sum()} Signals.")
    
    # ============================================================
    # STEP 5: Run Backtest
    # ============================================================
    exec_engine = ExecutionEngine(initial_capital=INITIAL_CAPITAL)
    print(f"Running Backtest on {DATA_START} to {DATA_END}...")
    final_stats, trade_log, equity_curve = exec_engine.run_backtest(experiment_signals, hold_horizon_days=HOLD_HORIZON)
    
    print("\n--- PERFORMANCE METRICS ---")
    print(f"Total PnL: {final_stats['Total PnL']:.2f}")
    print(f"Sharpe Ratio: {final_stats['Sharpe Ratio']:.2f}")
    print(f"Max Drawdown: {final_stats['Max Drawdown']:.2f}%")
    print(f"Total Trades: {final_stats['Total Trades']}")
    print(f"Win Rate: {final_stats['Win Rate']:.1f}%")
    
    # Buy & Hold Comparison
    import numpy as np
    bh_start_price = experiment_signals['Close'].iloc[0]
    bh_end_price = experiment_signals['Close'].iloc[-1]
    bh_return_pct = ((bh_end_price - bh_start_price) / bh_start_price) * 100
    bh_return_abs = (bh_end_price - bh_start_price) / bh_start_price * INITIAL_CAPITAL
    
    # Buy & Hold Drawdown
    bh_equity = (experiment_signals['Close'] / bh_start_price) * INITIAL_CAPITAL
    bh_cummax = bh_equity.cummax()
    bh_dd = ((bh_equity - bh_cummax) / bh_cummax).min() * 100
    
    # Buy & Hold Sharpe
    bh_daily_rets = experiment_signals['Close'].pct_change().dropna()
    bh_sharpe = (bh_daily_rets.mean() / bh_daily_rets.std() * np.sqrt(252)) if bh_daily_rets.std() != 0 else 0
    
    print("\n--- BUY & HOLD COMPARISON ---")
    print(f"B&H Return: {bh_return_pct:.2f}% ({bh_return_abs:.2f})")
    print(f"B&H Max Drawdown: {bh_dd:.2f}%")
    print(f"B&H Sharpe Ratio: {bh_sharpe:.2f}")
    print(f"Strategy vs B&H: {final_stats['Return %'] - bh_return_pct:+.2f}% alpha")
    
    # Save results
    results_dir = os.path.join(os.path.dirname(__file__), 'backtest_results')
    os.makedirs(results_dir, exist_ok=True)
    trade_log.to_csv(os.path.join(results_dir, 'trade_log.csv'))
    print(f"Results saved to: {results_dir}")
    
    # ============================================================
    # STEP 6: Generate Trade Plan (Jan Forecast)
    # ============================================================
    planner = TradePlanGenerator()
    print("\nTraining Final Logistic Model on Full Nov-Dec Data...")
    ml_filter_final = MLFilter()
    ml_filter_final.train(df_signals)
    
    # Load Jan data
    df_jan = load_data(TICKER, start_date='2025-11-01', end_date='2026-01-10', fyers_secrets_path=secrets_path)
    df_jan = FeatureEngineer().add_features(df_jan)
    df_jan_signals = SignalGenerator(threshold=1).generate_signals(df_jan)
    
    print("\n--- JAN 1-8 SIGNAL INSPECTION (LOGISTIC REGRESSION) ---")
    jan_slice = df_jan_signals[(df_jan_signals.index >= '2026-01-01')]
    if not jan_slice.empty:
        probs = ml_filter_final.predict_probs(jan_slice)
        for i, date in enumerate(jan_slice.index):
            raw_sig = jan_slice.loc[date, 'direction']
            prob = probs[i] if i < len(probs) else 0.5
            status = "VETO" if prob < ML_VETO_THRESHOLD else "PASS"
            if raw_sig == 0:
                status = "NO_SIGNAL"
            print(f"Date: {date.date()} | Raw: {raw_sig} | ML Prob: {prob:.4f} | Thr: {ML_VETO_THRESHOLD} | Status: {status}")
    print("---------------------------------\n")
    
    df_jan_final = ml_filter_final.apply_veto(df_jan_signals, threshold=ML_VETO_THRESHOLD)
    trade_plan = planner.generate_plan(df_jan_final, exec_engine, start_date='2026-01-01', end_date='2026-01-08')
    plan_path = os.path.join(os.path.dirname(__file__), 'trade_plan_jan1_8_logistic.csv')
    trade_plan.to_csv(plan_path, index=False)
    print(f"Trade Plan saved to: {plan_path}")
    
    print("\nFINISHED_LOGISTIC")


if __name__ == "__main__":
    main()
