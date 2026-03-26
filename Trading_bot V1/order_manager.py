class OrderManager:
    def __init__(self, smart_api, config):
        self.smart_api = smart_api
        self.config = config
        self.open_trades = {}

    def process_signals(self, signals):
        for symbol, signal in signals.items():
            # signal is expected to be "buy", "sell", or "hold"
            if signal == "buy":
                if symbol not in self.open_trades:
                    self.place_order(symbol, "BUY")
                else:
                    print(f"Already have an open trade for {symbol}, skipping buy.")
            elif signal == "sell":
                if symbol in self.open_trades:
                    self.place_order(symbol, "SELL")
                else:
                    print(f"No open trade to close for {symbol}, skipping sell.")
            else:
                print(f"Holding position for {symbol}.")

    def place_order(self, symbol, transaction_type):
        # Example: Fetch exchange and symbol token
        stock_info = next((s for s in self.config["stocks"] if s["symbol"] == symbol), None)
        if not stock_info:
            print(f"Stock info for {symbol} not found in config.")
            return

        exchange = stock_info["exchange"]
        qty = self.calculate_quantity(symbol)
        order_type = self.config["trade_settings"].get("order_type", "MARKET")

        # Prepare order params based on Angel One SmartAPI docs
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": self.get_symbol_token(symbol, exchange),
            "transactiontype": transaction_type,
            "exchange": exchange,
            "ordertype": order_type,
            "producttype": "MIS",  # You can make this configurable
            "duration": "DAY",
            "price": 0,  # For market orders price=0
            "quantity": qty,
            "disclosedquantity": 0,
            "triggerprice": 0,
            "stoploss": 0,
            "squareoff": 0,
            "trailingstoploss": 0
        }

        try:
            response = self.smart_api.placeOrder(order_params)
            if response.get("status"):
                print(f"✅ Order placed for {transaction_type} {symbol} qty {qty}")
                if transaction_type == "BUY":
                    self.open_trades[symbol] = qty
                elif transaction_type == "SELL" and symbol in self.open_trades:
                    del self.open_trades[symbol]
            else:
                print(f"❌ Order failed for {symbol}: {response.get('message')}")
        except Exception as e:
            print(f"❌ Exception placing order for {symbol}: {e}")

    def calculate_quantity(self, symbol):
        # Basic qty calc: max_capital_per_trade / last_close_price
        max_capital = self.config["risk_management"]["max_capital_per_trade"]
        ohlc_data = self.get_latest_ohlc(symbol)
        if not ohlc_data:
            print(f"❌ Cannot calculate qty - no OHLC data for {symbol}")
            return 0

        last_close = ohlc_data[-1][4]  # Close price index
        qty = int(max_capital / last_close)
        if qty == 0:
            qty = 1  # minimum 1 share
        return qty

    def get_latest_ohlc(self, symbol):
        # You may want to pass this data from main instead of fetching here.
        # Placeholder returns None; implement as needed.
        return None

    def get_symbol_token(self, symbol, exchange):
        # This should search and cache symbol tokens like in data_fetcher.py
        scrip_data = self.smart_api.searchScrip(exchange, symbol)
        if scrip_data["status"]:
            eq_symbols = [item for item in scrip_data["data"] if item["tradingsymbol"].endswith("-EQ")]
            if eq_symbols:
                return eq_symbols[0].get("symboltoken")
        print(f"❌ Could not find symbol token for {symbol}")
        return None
