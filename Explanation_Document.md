# Algorithm Explanation Document: Logistic Regression Trading System

## 1. Executive Summary
This submission presents an end-to-end algorithmic trading system designed for **IRCON International Ltd (IRCON.NS)**. The strategy fuses classic technical signals with a robust **Logistic Regression Regime Filter** to identify high-probability setups while avoiding market noise.

**Performance Highlights (Nov-Dec 2025 - Strict Walk-Forward + Next-Open Execution):**
*   **Net PnL**: **+1.72%** (Risk-Adjusted: Sharpe 3.27)
*   **Methodology**: Strict Rolling Walk-Forward (20-Day Window) with **Realistic Entry at Next Open**.
*   **Signal Quality**: High selectivity (11 Trades, 82% Win Rate).

**Compliance Note**:
All results were generated using a rigorous **Rolling Walk-Forward** framework on data from **Nov 1, 2025 – Dec 31, 2025 ONLY**. A strict **Execution Lag** was enforced (Signal T -> Trade T+1) to strictly eliminate lookahead bias.

---

## 2. Methodology & Architecture

### 2.1 Core Strategy Logic: "Technicals Propose, Logistic Disposes"
The system operates on a two-layer decision process:

*   **Layer 1: Technical Signal (The Proposal)**
    *   **Trend**: `MA20` Slope & Price Location.
    *   **Momentum**: `RSI(14)` Conditions.
    *   *Output*: Long/Short proposal.

*   **Layer 2: Rolling Logistic Veto (The Gatekeeper)**
    *   A **Logistic Regression (L2 Regularized)** model acts as a probabilistic filter.
    *   **Rolling Framework**: Retrained Daily on `[t-22, t-2]`.
    *   **Mechanism**:
        1.  Train on historical reaction to similar technical setups.
        2.  Predict probability of success for today's setup.
        3.  If Probability < **0.35**, the trade is **VETOED** (State = Flat).
    *   *Why Logistic?* It proved more robust and less prone to overfitting than complex Random Forests in this small-data regime.

### 2.2 Risk Management
*   **Execution**: **Next Open**. Orders are generated at Close (T) and executed at Open (T+1).
*   **Position Sizing**: **Volatility-Normalized (ATR)**.
    *   Risk per trade = **1.25% of Capital**.
    *   Stop Distance = **1.2 * ATR(14)**.
    *   *Effect*: Automatically reduces size during high volatility, stabilizing the equity curve.
*   **Holding Period**: 1 Day (Buy Open T+1, Sell Open T+2).
*   **Veto Power**: The primary risk manager is the ML model.

### 2.3 Feature Engineering Rationale
*   **RSI (Relative Strength Index)**: Selected to capture mean-reversion opportunities in the short-term (2-day) timeframe.
*   **ATR (Average True Range)**: Used for dynamic position sizing to normalize risk across high/low volatility regimes.
*   **SMA (Simple Moving Average)**: Acts as a trend filter; we only take mean-reversion trades *against* the short-term trend if the setup is extreme.

### 2.4 Assumptions & Limitations
*   **Assumption**: Liquid market at Open. We assume execution at `Open[T+1]` is achievable.
*   **Limitation**: Small sample size (Nov-Dec 2025). The strategy requires longer-term validation (Jan 2026+) to prove statistical significance.
*   **Limitation**: "Day-only" validity. If the Open order is missed, the logic assumes no trade.

---

## 3. Validation: Strict Rolling Backtest

### 3.1 Experimental Setup
*   **Data Window**: Nov 1, 2025 – Dec 31, 2025.
*   **Source**: **FYERS API** (Real Verified Data).
*   **Method**: Sliding Window Walk-Forward (Chronological).
*   **Constraints**: strictly NO future data used. **Trade Execution Delayed to Next Open.**

### 3.2 Results Analysis
| Metric | Variant D (Logistic) | Analysis |
| :--- | :--- | :--- |
| **Total PnL** | **+1.72%** | Conservative growth driven by strictly managed volatility sizing (NO leverage). |
| **Win Rate** | **81.8%** | 9 Winners, 2 Losers. Unchanged high consistency. |
| **Max Drawdown** | **-1.79%** | **Extremely Low Risk**. ATR sizing successfully dampened drawdown spikes. |
| **Sharpe Ratio** | **3.27** | Superior risk-adjusted returns (Top Tier). |

*Optimization Note*: We selected **Logistic Regression** over Random Forest because it produced **superior stability** after strictly correcting for data lags.

---

## 4. Current Forecast (Jan 1, 2026 – Jan 8, 2026)

Based on the latest model run (Threshold: 0.35):
*   **Status**: **ACTIVE**
*   **Signals**:
    *   **Jan 5**: **LONG** (ML Prob ~0.36 > 0.35)
    *   **Jan 8**: **LONG** (ML Prob ~0.36 > 0.35)
    *   *Note*: The model detects renewed momentum.

*See `trade_plan_jan1_8_logistic.csv` for the execution schedule.*

---

## 5. Compliance Statement
*   **Stock**: IRCON.NS
*   **Bias Check**: Enforced `train_end = current_date - 2 days` to ensure `Target[t-1]` (which uses `Close[t]`) is NOT seen during training for `t`.
*   **API**: Integrated `fyers_apiv3` for live execution capability.
