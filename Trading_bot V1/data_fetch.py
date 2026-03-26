import json
from SmartApi import SmartConnect
import datetime as dt
import pyotp
import time
import csv

# Load config.json (make sure it has your API credentials & stocks)
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

# Login to Angel One API
smart_api = SmartConnect(api_key=API_KEY)
totp = pyotp.TOTP(TOTP_SECRET).now()
login_data = smart_api.generateSession(CLIENT_CODE, MPIN, totp)

if not login_data.get("status"):
    print("❌ Login failed:", login_data)
    exit()

print("✅ Logged in successfully for data fetching.")

def get_ohlc(symbol, exchange, interval):
    now = dt.datetime.now()
    yesterday = now - dt.timedelta(days=1)
    
    from_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M")
    to_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=0).strftime("%Y-%m-%d %H:%M")

    scrip_data = smart_api.searchScrip(exchange, symbol)
    if not scrip_data["status"]:
        print(f"❌ Could not find symbol token for {symbol} on {exchange}")
        return None

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

def save_ohlc_to_csv(symbol, ohlc_data):
    filename = f"{symbol}_ohlc.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        for candle in ohlc_data:
            writer.writerow(candle)

# Fetch and save yesterday's OHLC for each stock
for stock in stocks:
    print(f"\nFetching OHLC for {stock['symbol']} on {stock['exchange']} for yesterday only...")
    ohlc = get_ohlc(stock["symbol"], stock["exchange"], interval)
    if ohlc:
        save_ohlc_to_csv(stock["symbol"], ohlc)
        print(f"✅ Saved OHLC for {stock['symbol']} to CSV.")
    time.sleep(1.5)  # Avoid rate limits

# Terminate session
smart_api.terminateSession(CLIENT_CODE)
print("Session terminated.")
