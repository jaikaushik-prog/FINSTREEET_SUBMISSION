import os
import json
import pandas as pd
import datetime as dt
import time
from fyers_apiv3 import fyersModel
import pyotp

class FyersBridge:
    def __init__(self, secrets_path='fyers_secrets.json'):
        self.secrets_path = secrets_path
        self.fyers = None
        self.secrets = self._load_secrets()
        
    def _load_secrets(self):
        try:
            if not os.path.exists(self.secrets_path):
                print(f"Warning: Secrets file {self.secrets_path} not found.")
                return {}
            with open(self.secrets_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading secrets: {e}")
            return {}

    def authenticate(self):
        """
        Authenticate with FYERS API.
        Attempts Auto-Login using TOTP if keys are available.
        Otherwise, expects 'access_token' to be manually set or valid.
        """
        try:
            client_id = self.secrets.get('client_id')
            secret_key = self.secrets.get('secret_key')
            redirect_uri = self.secrets.get('redirect_uri')
            totp_key = self.secrets.get('totp_key')
            pin = self.secrets.get('pin')
            
            if not client_id or not secret_key:
                print("Error: Missing client_id or secret_key for FYERS Auth.")
                return False

            # 1. Create Session Model
            # Note: Full OAuth implementation requires browser interaction or TOTP
            # For competition submission, we assume a generated token or simple flow
            
            # Simple check if we can mock or need real auth
            # Implementing the Totp flow logic as standard practice
            
            if totp_key and pin:
                print("Attempting Auto-Login with TOTP...")
                # Start Session
                session = fyersModel.SessionModel(
                    client_id=client_id,
                    secret_key=secret_key,
                    redirect_uri=redirect_uri,
                    response_type='code',
                    grant_type='authorization_code'
                )
                
                # Generate URL
                response = session.generate_authcode()
                
                # This part (Headless Auth) usually requires Selenium or manual intervention
                # But fyers-apiv3 often requires the 'auth_code' directly.
                # For this submission, we will create the instance ONLY if we have an access_token
                # OR we will guide the user to paste it.
                
                # However, many algorithmic traders reuse a saved access_token.
                # Ensure logs directory exists
                log_dir = os.path.join(os.getcwd(), 'logs')
                os.makedirs(log_dir, exist_ok=True)

                if 'access_token' in self.secrets:
                     self.fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=self.secrets['access_token'], log_path=log_dir)
                     print("Authenticated using saved Access Token.")
                     return True
                     
                print("Please create an 'access_token' entry in secrets file after manual login.")
                return False
                
            elif 'access_token' in self.secrets:
                 self.fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=self.secrets['access_token'], log_path="./logs")
                 print("Authenticated using saved Access Token.")
                 return True

            else:
                print("Authentication Failed: No TOTP or Access Token provided.")
                return False
                
        except Exception as e:
            print(f"Auth Error: {e}")
            return False

    def fetch_historical_data(self, symbol, start_date, end_date, interval="D"):
        """
        Fetch historical data from FYERS and return as DataFrame matching yfinance format.
        """
        if not self.fyers:
            print("Error: FYERS Client not initialized.")
            return pd.DataFrame()

        try:
            # FYERS format: "NSE:IRCON-EQ"
            # Symbol mapping: IRCON.NS -> NSE:IRCON-EQ
            fyers_symbol = f"NSE:{symbol.replace('.NS', '-EQ')}"
            
            # Date format: YYYY-MM-DD
            # Fyers History API requires 'range_from' and 'range_to'
            # Note: API limits history fetch per call. Need to chunk if range is large.
            # But for Nov-Dec 2025 (2 months), one call is fine.
            
            data = {
                "symbol": fyers_symbol,
                "resolution": "1D", # Daily
                "date_format": "1",
                "range_from": start_date,
                "range_to": end_date,
                "cont_flag": "1"
            }

            response = self.fyers.history(data=data)
            
            if response.get('s') != 'ok':
                print(f"FYERS History Error: {response.get('message')}")
                return pd.DataFrame()
            
            candles = response.get('candles', [])
            if not candles:
                return pd.DataFrame()

            # Convert to DataFrame
            # Format: [timestamp, open, high, low, close, volume]
            df = pd.DataFrame(candles, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            
            # Convert Timestamp (Epoch) to Datetime
            # Fyers sends epoch? check docs. Usually epoch.
            # Assuming Epoch, convert.
            df['Date'] = pd.to_datetime(df['Date'], unit='s')
            
            # Set Index
            df.set_index('Date', inplace=True)
            
            # Clean up
            # remove timezone if any
            df.index = df.index.normalize() # Keep Date part

            return df

        except Exception as e:
            print(f"Data Fetch Error: {e}")
            return pd.DataFrame()

    def place_order(self, symbol, qty, side, order_type="MARKET", product="CNCS"):
        """
        Place order via FYERS.
        side: 1 (Buy), -1 (Sell)
        """
        if not self.fyers:
            print("Error: FYERS Client not initialized.")
            return None

        try:
            fyers_symbol = f"NSE:{symbol.replace('.NS', '-EQ')}"
            fyers_side = 1 if side == 1 else -1 
            # Fyers API: Side 1=Buy, -1=Sell
            
            data = {
                "symbol": fyers_symbol,
                "qty": int(qty),
                "type": 2 if order_type == "MARKET" else 1, # 2=Market, 1=Limit
                "side": fyers_side,
                "productType": "CNC", # For Equity Delivery. Options: CNC, INTRADAY, MARGIN
                "limitPrice": 0,
                "stopPrice": 0,
                "validity": "DAY",
                "disclosedQty": 0,
                "offlineOrder": False,
            }

            response = self.fyers.place_order(data=data)
            print(f"FYERS Order Response: {response}")
            return response

        except Exception as e:
            print(f"Order Placement Error: {e}")
            return None
