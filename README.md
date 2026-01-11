# SONATSOFTW.NS Algorithmic Trading System

## Overview
End-to-end ML-driven trading system for SONATSOFTW.NS using rolling logistic regression and ATR-based risk management.

**Performance (Nov-Dec 2025):**
- **Net PnL**: +1.79% (Risk-Managed)
- **Sharpe Ratio**: 3.25
- **Win Rate**: 57.1%
- **Max Drawdown**: -1.58%
- **Alpha vs Buy & Hold**: +1.50%
- **Method**: Strict Rolling Walk-Forward (Next-Open Execution)

---

## Buy & Hold Comparison

| Metric | Strategy | Buy & Hold |
|:-------|:--------:|:----------:|
| Return | +1.79% | +0.29% |
| Sharpe | 3.25 | 0.26 |
| Max DD | -1.58% | -7.07% |

---

## Project Structure

```
submit_quant/
├── run_strategy.py              ← Main entry point
├── requirements.txt
├── README.md
├── SETUP_GUIDE.md
├── Explanation_Document.md
│
├── src/
│   ├── data/
│   │   └── data_loader.py       # Fyers/yfinance data loading
│   ├── features/
│   │   └── feature_engineer.py  # RSI, SMA, ATR, Bollinger
│   ├── signals/
│   │   └── signal_generator.py  # Signal generation logic
│   ├── models/
│   │   └── logistic_filter.py   # ML veto filter
│   ├── execution/
│   │   └── execution_engine.py  # Backtest engine
│   ├── backtest/
│   │   └── backtester.py        # Trade plan generator
│   ├── utils/
│   │   └── config.py            # All configuration constants
│   └── modules/
│       └── fyers_data_client.py # Fyers API integration
│
├── backtest_results/
│   ├── trade_log.csv
│   ├── trade_plan_jan1_8_logistic.csv
│   └── strategy_results_summary.txt
└── logs/                        # Fyers API logs
```

---

## How to Run

```bash
pip install -r requirements.txt
python run_strategy.py
```

---

## Strategy Summary

- **Signal**: SMA crossover + RSI filter
- **ML Filter**: Rolling logistic regression with 2-day lag (no lookahead)
- **Position Sizing**: ATR-based (1.25% risk per trade)
- **Execution**: Next-day open entry, 1-day hold
- **Veto Threshold**: 0.40 probability cutoff

---

## Reproducibility

- Fixed random seeds (42)
- Deterministic walk-forward training
- No external data dependencies
- Configurable via `src/utils/config.py`


