# SONATSOFTW.NS Trading Strategy - Setup & Execution Guide

## 📁 Folder Structure

```
submit_quant/
├── run_strategy.py              ← 🚀 MAIN ENTRY POINT - Run this
├── requirements.txt
├── Explanation_Document.md
├── README.md
│
├── src/
│   ├── data/
│   │   └── data_loader.py       # Data loading (Fyers/yfinance)
│   ├── features/
│   │   └── feature_engineer.py  # Technical indicators
│   ├── signals/
│   │   └── signal_generator.py  # Signal generation
│   ├── models/
│   │   └── logistic_filter.py   # ML filter
│   ├── execution/
│   │   └── execution_engine.py  # Backtest engine
│   ├── backtest/
│   │   └── backtester.py        # Trade plan generator
│   ├── utils/
│   │   └── config.py            # ⚙️ All configuration constants
│   └── modules/
│       └── fyers_data_client.py # Fyers API integration
│
├── backtest_results/
│   ├── trade_log.csv
│   ├── trade_plan_jan1_8_logistic.csv
│   └── strategy_results_summary.txt  
└── logs/                        # Fyers API logs (exclude from submission)
```

---

## ⚙️ Prerequisites

| Requirement | Version |
|-------------|---------|
| Python      | 3.8+    |
| pip         | Latest  |

---

## 🛠️ Step-by-Step Setup

### Step 1: Clone/Download the Repository

```bash
git clone <repository-url>
cd submit_quant
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure FYERS Credentials (Optional)

Create `fyers_secrets.json` in the root folder:

```json
{
    "client_id": "YOUR_CLIENT_ID-100",
    "secret_key": "YOUR_SECRET_KEY",
    "redirect_uri": "https://trade.fyers.in/api-login/redirect-url",
    "fy_id": "YOUR_FY_ID",
    "totp_key": "YOUR_TOTP_SECRET",
    "pin": "YOUR_4DIGIT_PIN"
}
```

**Without FYERS credentials:** Uses `yfinance` for historical data (free).

### Step 5: Run the Strategy

```bash
python run_strategy.py
```

**Expected Output:**
```
============================================================
 VARIANT D (LOGISTIC REGRESSION) - STRICT ROLLING
============================================================
Asset: SONATSOFTW.NS
...
--- PERFORMANCE METRICS ---
Total PnL: 1793.75
Sharpe Ratio: 3.25
Max Drawdown: -1.58%
Total Trades: 14
Win Rate: 57.1%

--- BUY & HOLD COMPARISON ---
B&H Return: 0.29% (292.64)
B&H Max Drawdown: -7.07%
B&H Sharpe Ratio: 0.26
Strategy vs B&H: +1.50% alpha
...
FINISHED_LOGISTIC
```

---

## 📤 Output Files

| File | Description |
|------|-------------|
| `backtest_results/trade_log.csv` | Complete trade history |
| `backtest_results/strategy_results_summary.txt` | Performance summary |
| `trade_plan_jan1_8_logistic.csv` | Forecast signals for Jan 1-8 |

---

## 🔧 Configuration Parameters

Edit `src/utils/config.py` to customize:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TICKER` | `"SONATSOFTW.NS"` | Stock symbol |
| `INITIAL_CAPITAL` | `100000` | Starting capital (INR) |
| `DATA_START` | `'2025-11-01'` | Backtest start date |
| `DATA_END` | `'2025-12-31'` | Backtest end date |
| `WARMUP_DAYS` | `20` | Days before ML starts |
| `WINDOW_SIZE_DAYS` | `20` | ML training window |
| `ML_VETO_THRESHOLD` | `0.40` | Probability cutoff |
| `HOLD_HORIZON` | `1` | Days to hold each trade |

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `yfinance` rate limit | Wait 1 minute and retry |
| FYERS auth failed | Check `fyers_secrets.json` values |
| Empty data | Ensure market was open on requested dates |


