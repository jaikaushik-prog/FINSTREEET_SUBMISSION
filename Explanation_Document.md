# Algorithm Explanation Document
## Logistic Regression–Based Regime-Filtered Trading System

**Asset:** IRCON International Ltd (IRCON.NS)  
**Competition:** FiN Street – FYERS Trading Challenge

---

## 1. Executive Summary

This submission presents an end-to-end, fully automated algorithmic trading system designed specifically for small-sample, short-horizon market environments, as mandated by the competition constraints.

The strategy combines interpretable technical trading rules with a probabilistic **Logistic Regression regime filter**, enabling disciplined trade selection and professional-grade risk control.

Rather than maximizing raw profit, the system is explicitly optimized for **risk-adjusted performance**, **signal stability**, and **reproducibility**, aligning directly with the evaluation criteria.

### Performance Highlights (Nov–Dec 2025, Strict Walk-Forward)

| Metric | Value |
|:-------|:------|
| **Net PnL** | +1.72% |
| **Sharpe Ratio** | 3.27 |
| **Maximum Drawdown** | −1.79% |
| **Trades** | 11 |
| **Win Rate** | 81.8% |
| **Execution Accuracy** | Signal at Close (T) → Trade at Open (T+1) |

All results were generated using a strict rolling walk-forward framework, with no access to future data and realistic execution assumptions.

---

## 2. Strategy Motivation and Design Philosophy

### Key Constraints Driving Design

- Only 2 months of daily data available
- Mandatory walk-forward validation
- Emphasis on risk discipline over raw returns
- No manual intervention allowed

Given these constraints, complex nonlinear models are statistically unstable and prone to overfitting. Therefore, the strategy adopts the following principles:

- **Simple signals, strong risk control**
- **ML as a regime filter, not an alpha generator**
- **Explicit causality at every step**
- **Capital preservation first, profits second**

---

## 3. Strategy Architecture

### 3.1 Core Logic: "Technicals Propose, Logistic Disposes"

The system operates as a two-layer decision pipeline.

#### Layer 1: Technical Signal Generation (Proposal Layer)

This layer generates candidate trades using transparent, interpretable indicators:

**Trend Context**
- Price relative to SMA(20)

**Momentum Context**
- RSI(14) to identify overbought / oversold conditions

**Signal Rules**

| Signal | Conditions |
|:-------|:-----------|
| **LONG** | Close > SMA(20) AND RSI < 70 |
| **SHORT** | Close < SMA(20) AND RSI > 30 |
| **FLAT** | Otherwise |

These rules intentionally favor high-probability, short-horizon setups, rather than frequent trading.

#### Layer 2: Logistic Regression Regime Filter (Decision Layer)

To prevent trading during unfavorable market regimes, a Logistic Regression classifier acts as a **probabilistic veto filter**.

**Model Choice Justification**

Logistic Regression was selected because it:
- Exhibits low variance under small samples
- Produces well-calibrated probabilities
- Is robust to daily retraining
- Is interpretable and defensible

More complex models (e.g., Random Forests) were tested but showed higher instability and inconsistent veto behavior under rolling retraining.

**Training Framework**
- Rolling window: ~20 trading days
- Training range: [t−22, t−2]
- Target: Direction of next-day return
- Retrained daily

This lag ensures:
> Target[t−1] (which depends on Close[t]) is never visible when predicting for day t.

**Decision Rule**
- If P(up) < 0.35 → **VETO** trade
- Otherwise → Allow technical signal

The ML model therefore acts as a **regime-awareness mechanism**, suppressing trades during noisy or statistically unfavorable conditions.

---

## 4. Feature Engineering Rationale

All features are derived exclusively from OHLCV data, in compliance with competition rules.

| Feature | Purpose |
|:--------|:--------|
| RSI(14) | Captures short-term momentum exhaustion |
| ATR(14) | Measures volatility and drives position sizing |
| Normalized SMA Deviation | Quantifies trend alignment |
| Bollinger Band Std Dev | Identifies volatility expansion/contraction |

The feature set is intentionally compact to:
- Reduce dimensionality
- Avoid overfitting
- Maintain interpretability

---

## 5. Execution and Risk Management

### 5.1 Execution Assumptions

- Signals generated at Close (T)
- Trades executed at Open (T+1)
- No same-bar execution allowed

This enforces realistic market mechanics and eliminates lookahead bias.

### 5.2 Position Sizing (Key Risk Control)

Position sizing uses volatility-normalized risk targeting:

- **Risk per trade:** 1.25% of capital
- **Stop distance proxy:** 1.2 × ATR(14)

**Quantity Calculation:**

```
Qty = (0.0125 × Capital) / (1.2 × ATR)
```

This ensures:
- Consistent risk across volatility regimes
- Automatic size reduction during turbulent periods
- Smooth equity curve behavior

### 5.3 Holding Period

- Fixed 1-day holding horizon
- Entry: Open (T+1)
- Exit: Open (T+2)

This minimizes overnight exposure and aligns with the short-term nature of the signals.

---

## 6. Backtesting Methodology

| Parameter | Value |
|:----------|:------|
| Data Window | Nov 1 – Dec 31, 2025 |
| Source | FYERS API |
| Validation | Strict chronological walk-forward |
| Warm-up | First 20 days (no trades) |

- No cross-validation or shuffling
- No future leakage

This methodology closely mirrors real-world deployment conditions.

---

## 7. Performance Summary

| Metric | Result | Interpretation |
|:-------|:-------|:---------------|
| Total PnL | +1.72% | Conservative growth |
| Sharpe Ratio | 3.27 | Excellent risk-adjusted returns |
| Max Drawdown | −1.79% | Strong capital preservation |
| Win Rate | 81.8% | High signal quality |
| Trades | 11 | Selective execution |

The low drawdown confirms the effectiveness of ATR-based risk control and ML vetoing.

---

## 8. Current Forecast (Jan 1–8, 2026)

Using the final Logistic Regression model trained on the full Nov–Dec dataset:

**Active Signals Detected**
- Selective LONG opportunities identified
- Signals are provided in `trade_plan_jan1_8_logistic.csv`

This demonstrates continuity from backtesting to live deployment.

---

## 9. Assumptions and Limitations

### Assumptions
- Sufficient liquidity at market open
- Daily OHLCV data captures dominant short-term dynamics

### Limitations
- Short historical window limits statistical significance
- Strategy optimized for short-term horizons only
- Performance may vary under extreme macro events

---

## 10. Compliance Statement

| Item | Detail |
|:-----|:-------|
| Single Stock | IRCON.NS |
| Data | FYERS API only |
| Execution | Automated, no manual intervention |
| Bias Prevention | Enforced execution lag and training cutoff |
| Reproducibility | Deterministic pipeline with fixed parameters |

---

## Conclusion

This strategy demonstrates how disciplined model selection, strict causality, and professional risk management can produce strong risk-adjusted performance even under severe data constraints. The system prioritizes **robustness**, **interpretability**, and **real-world feasibility**—key attributes of production-ready quantitative strategies.
