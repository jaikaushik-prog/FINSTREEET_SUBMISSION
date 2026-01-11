# IRCON.NS Algorithmic Trading System

## Overview
End-to-end ML-driven trading system for IRCON.NS using rolling logistic regression and ATR-based risk management.

**Performance (Nov-Dec 2025):**
- **Net PnL**: +1.72% (Risk-Managed)
- **Sharpe Ratio**: 3.27
- **Win Rate**: 81.8%
- **Method**: Strict Rolling Walk-Forward (Next-Open Execution)

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
├── backtest_results/            # Trade logs
├── experiments/                 # Debug & research files
└── logs/                        # API logs
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
- **Veto Threshold**: 0.35 probability cutoff

---

## Reproducibility

- Fixed random seeds (42)
- Deterministic walk-forward training
- No external data dependencies
- Configurable via `src/utils/config.py`
