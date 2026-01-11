# Data loading module
"""
Handles data loading from Fyers API or yfinance fallback.
all the computations and results are from data from fyers and kindly put the access token and appid and secretid
in fyers_secrets.json to use fyers to backtest
"""

import os
import pandas as pd
import yfinance as yf


def load_data(ticker, start_date, end_date, fyers_secrets_path=None):
    """
    Load historical OHLCV data for the given ticker.
    
    Attempts Fyers API first, falls back to yfinance.
    
    Returns:
        pd.DataFrame with Date index and OHLCV columns.
    """
    df = pd.DataFrame()
    
    # Try Fyers API first
    if fyers_secrets_path and os.path.exists(fyers_secrets_path):
        try:
            from src.modules.fyers_data_client import FyersBridge
            print("FYERS Secrets found. Loading ALL data via FYERS API...")
            bridge = FyersBridge(secrets_path=fyers_secrets_path)
            if bridge.authenticate():
                print("Fetching historical data via FYERS API...")
                df = bridge.fetch_historical_data(ticker, start_date=start_date, end_date=end_date)
                if df is not None and not df.empty:
                    print(f"FYERS Data: {len(df)} rows loaded successfully.")
                else:
                    print("FYERS returned empty data. Falling back to yfinance...")
                    df = pd.DataFrame()
            else:
                print("FYERS Authentication Failed. Falling back to yfinance...")
        except ImportError as e:
            print(f"FYERS Bridge not available ({e}). Using yfinance...")
        except Exception as e:
            print(f"FYERS Error: {e}. Falling back to yfinance...")
    
    # Fallback to yfinance
    if df is None or df.empty:
        print(f"Downloading historical data for {ticker} via yfinance...")
        df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
    
    df.index = pd.to_datetime(df.index)
    print(f"Downloaded {len(df)} rows total")
    return df

