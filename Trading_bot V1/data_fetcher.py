import json
from SmartApi import SmartConnect
import datetime as dt
import pyotp
import time
import csv

# Load config
with open("config.json") as f:
    config = json.load(f)

creds = config["api_credentials"]
API_KEY = creds["api_key"]
CLIENT_CODE = creds["client_code"]
MPIN = creds["mpin"]
TOTP_SECRET = creds["totp_secret"]

stocks = config["stocks"]
interval_map = {
    "1m": "ONE_MINUTE",
    "3m": "THREE_MINUTE",
    "5m": "FIVE_MINUTE",
    "10m": "TEN_MINUTE",
    "15m": "FIFTEEN_MINUTE",
    "30m": "THIRTY_MINUTE",
    "1h": "ONE_HOUR",
    "1d": "ONE_DAY"
}

timeframe = config.get("trade_settings", {}).get("timeframe", "5m")
interval = interval_map.get(timeframe, "FIVE_MINUTE")

# Initialize API and login
smart_api = SmartConnect(api_key=API_KEY)
totp = pyotp.TOTP(TOTP_SECRET).now()
login_data = smart_api.generateSession(CLIENT_CODE, MPIN, totp)

if not login_data.get("status"):
    print("❌ Login failed:", login_data)
    exit()

print("✅ Logged in successfully for data fetching.")

def get_ohlc(symbol, exchange, interval, days=5):
    try:
        now = dt.datetime.now()
        from_date = (now - dt.timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
        to_date = now.strftime("%Y-%m-%d %H:%M")

        scrip_data = smart_api.searchScrip(exchange, symbol)
        if not scrip_data["status"]:
            print(f"❌ Could not find symbol token for {symbol} on {exchange}")
            return None

        # Filter for equity symbols ending with -EQ
        eq_symbols = [item for item in scrip_data["data"] if item["tradingsymbol"].endswith("-EQ")]
        if not eq_symbols:
            print(f"❌ No equity symbol found for {symbol} on {exchange}")
            return None

        token = eq_symbols[0].get("symboltoken")
        if not token:
            print(f"❌ Token key missing in symbol data for {symbol}")
            return None

        params = {
            "exchange": exchange,
            "symboltoken": token,
            "interval": interval,
            "fromdate": from_date,
            "todate": to_date
        }

        ohlc_data = smart_api.getCandleData(params)
        if ohlc_data["status"]:
            return ohlc_data["data"]
        else:
            print(f"❌ Failed to fetch OHLC data for {symbol}")
            return None

    except Exception as e:
        print(f"❌ Error fetching OHLC for {symbol}: {e}")
        return None

def save_ohlc_to_csv(symbol, ohlc_data):
    filename = f"{symbol}_ohlc.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # Write rows
        for candle in ohlc_data:
            writer.writerow(candle)

# Fetch, print, and save OHLC for each stock with retry and delay to avoid rate limit
for stock in stocks:
    symbol = stock["symbol"]
    exchange = stock["exchange"]
    print(f"\nFetching OHLC for {symbol} on {exchange}")

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        ohlc = get_ohlc(symbol, exchange, interval, days=5)
        if ohlc is not None:
            # Success, break retry loop
            for candle in ohlc[:5]:  # print first 5 candles for quick view
                print(candle)
            save_ohlc_to_csv(symbol, ohlc)
            print(f"✅ Saved OHLC data for {symbol} to CSV.")
            break
        else:
            if attempt < max_retries:
                print(f"⚠️ Attempt {attempt} failed for {symbol}. Retrying after 15 seconds...")
                time.sleep(15)
            else:
                print(f"❌ All {max_retries} attempts failed for {symbol}. Moving on.")

    # Delay between different stock fetches to avoid rate limits
    time.sleep(3)

# Terminate session
smart_api.terminateSession(CLIENT_CODE)
