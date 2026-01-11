# Config module - centralized constants
"""
Configuration constants for the IRCON.NS trading strategy.
All tunable parameters in one place for easy reproducibility.
"""

# Asset
TICKER = "IRCON.NS"

# Date Range
DATA_START = "2025-11-01"
DATA_END = "2025-12-31"

# Capital & Risk
INITIAL_CAPITAL = 100000
RISK_PER_TRADE_PCT = 0.0125  # 1.25% risk per trade

# Lookback Windows
LOOKBACK_WINDOW = 20
WARMUP_DAYS = 20
WINDOW_SIZE_DAYS = 20

# Trade Parameters
HOLD_HORIZON = 1
ML_VETO_THRESHOLD = 0.35
