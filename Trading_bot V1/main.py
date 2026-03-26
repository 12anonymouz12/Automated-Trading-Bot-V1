import json
import time
from SmartApi import SmartConnect
import pyotp
from data_fetcher import get_ohlc
from signal_generator import generate_signals
from order_manager import OrderManager

def main():
    # Load config
    with open("config.json") as f:
        config = json.load(f)

    creds = config["api_credentials"]

    # Initialize API and login
    smart_api = SmartConnect(api_key=creds["api_key"])
    totp = pyotp.TOTP(creds["totp_secret"]).now()
    login_data = smart_api.generateSession(creds["client_code"], creds["mpin"], totp)

    if not login_data.get("status"):
        print("❌ Login failed:", login_data)
        return

    print("✅ Logged in successfully!")

    # Initialize OrderManager
    order_manager = OrderManager(smart_api, config)

    # Get interval string for API
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

    stocks = config["stocks"]

    while True:
        print("\nFetching latest OHLC data...")
        ohlc_data = {}
        for stock in stocks:
            data = get_ohlc(stock["symbol"], stock["exchange"], interval, days=1)
            if data:
                ohlc_data[stock["symbol"]] = data
            else:
                print(f"⚠️ No data for {stock['symbol']}")

        if not ohlc_data:
            print("❌ No OHLC data fetched. Retrying in 1 minute.")
            time.sleep(60)
            continue

        print("\nGenerating signals...")
        signals = generate_signals(ohlc_data, config["strategy"])
        print("Signals:", signals)

        print("\nProcessing orders...")
        order_manager.process_signals(signals)

        # Sleep between cycles — adjust based on your strategy time frame
        print("Sleeping for 5 minutes...\n")
        time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    main()
