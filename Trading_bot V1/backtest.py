import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

# Exact Range Filter Signal Generator (your code)
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def generate_signals(ohlc_data, strategy_config):
    signals = {}
    sampling_period = strategy_config.get("sampling_period", 100)
    range_multiplier = strategy_config.get("range_multiplier", 3.0)

    for symbol, candles in ohlc_data.items():
        if len(candles) < sampling_period + 2:
            signals[symbol] = "hold"
            continue

        df = pd.DataFrame(candles, columns=["datetime", "open", "high", "low", "close", "volume"])

        src = df["close"]
        abs_diff = (src - src.shift(1)).abs()
        avrng = ema(abs_diff, sampling_period)
        wper = sampling_period * 2 - 1
        smrng = ema(avrng, wper) * range_multiplier

        filt = [np.nan] * len(df)
        filt[0] = src.iloc[0]

        for i in range(1, len(df)):
            prev_filt = filt[i - 1]
            x = src.iloc[i]
            r = smrng.iloc[i]

            if np.isnan(r):
                filt[i] = prev_filt
                continue

            if x > prev_filt:
                if x - r < prev_filt:
                    filt[i] = prev_filt
                else:
                    filt[i] = x - r
            else:
                if x + r > prev_filt:
                    filt[i] = prev_filt
                else:
                    filt[i] = x + r

        filt = pd.Series(filt, index=df.index)

        upward = [0.0] * len(df)
        downward = [0.0] * len(df)

        for i in range(1, len(df)):
            if filt.iloc[i] > filt.iloc[i - 1]:
                upward[i] = upward[i - 1] + 1
            else:
                upward[i] = 0

            if filt.iloc[i] < filt.iloc[i - 1]:
                downward[i] = downward[i - 1] + 1
            else:
                downward[i] = 0

        upward = pd.Series(upward, index=df.index)
        downward = pd.Series(downward, index=df.index)

        longCond = (
            ((src > filt) & (src > src.shift(1)) & (upward > 0)) |
            ((src > filt) & (src < src.shift(1)) & (upward > 0))
        )

        shortCond = (
            ((src < filt) & (src < src.shift(1)) & (downward > 0)) |
            ((src < filt) & (src > src.shift(1)) & (downward > 0))
        )

        CondIni = [0] * len(df)
        for i in range(1, len(df)):
            if longCond.iloc[i]:
                CondIni[i] = 1
            elif shortCond.iloc[i]:
                CondIni[i] = -1
            else:
                CondIni[i] = CondIni[i - 1]

        CondIni = pd.Series(CondIni, index=df.index)

        longCondition = (longCond) & (CondIni.shift(1) == -1)
        shortCondition = (shortCond) & (CondIni.shift(1) == 1)

        if longCondition.iloc[-1]:
            signals[symbol] = "buy"
        elif shortCondition.iloc[-1]:
            signals[symbol] = "sell"
        else:
            signals[symbol] = "hold"

    return signals


# Backtest logic
def backtest(ohlc_df, symbol, strategy_config, initial_capital=10000, stop_loss_pct=1.5, take_profit_pct=4.0):
    candles = ohlc_df.values.tolist()
    capital = initial_capital
    position = None
    trade_log = []

    window_size = strategy_config["sampling_period"] + 2

    for i in range(window_size, len(candles)):
        window_candles = candles[i - window_size : i]
        signals = generate_signals({symbol: window_candles}, strategy_config)
        signal = signals[symbol]

        current_price = candles[i][4]  # close price

        if position is None and signal == "buy":
            qty = int(capital / current_price)
            if qty > 0:
                position = {"entry_price": current_price, "qty": qty, "entry_index": i}
                trade_log.append(f"Buy at {current_price:.2f} (index {i})")
        elif position is not None:
            entry_price = position["entry_price"]
            qty = position["qty"]
            stop_loss_price = entry_price * (1 - stop_loss_pct / 100)
            take_profit_price = entry_price * (1 + take_profit_pct / 100)

            exit_trade = False
            exit_reason = ""

            if signal == "sell":
                exit_trade = True
                exit_reason = "Sell Signal Exit"
            elif current_price <= stop_loss_price:
                exit_trade = True
                exit_reason = "Stop Loss Exit"
            elif current_price >= take_profit_price:
                exit_trade = True
                exit_reason = "Take Profit Exit"

            if exit_trade:
                profit = (current_price - entry_price) * qty
                capital += profit
                trade_log.append(f"{exit_reason} at {current_price:.2f} (index {i})")
                position = None

    # Close any open position at the end
    if position is not None:
        last_price = candles[-1][4]
        profit = (last_price - position["entry_price"]) * position["qty"]
        capital += profit
        trade_log.append(f"Exit at end at {last_price:.2f}")

    total_profit = capital - initial_capital
    num_trades = len([t for t in trade_log if t.startswith("Buy at")])
    wins = sum(
        1
        for idx, t in enumerate(trade_log)
        if ("Exit" in t and ("Sell Signal Exit" in t or "Take Profit Exit" in t))
        and float(t.split(" at ")[1].split(" ")[0]) > float(trade_log[idx - 1].split(" at ")[1].split(" ")[0])
    )
    win_rate = (wins / num_trades * 100) if num_trades > 0 else 0

    print("\n".join(trade_log))
    print("\nBacktest Summary:")
    print(f"Initial capital: {initial_capital}")
    print(f"Ending capital: {capital:.2f}")
    print(f"Total profit: {total_profit:.2f}")
    print(f"Number of trades: {num_trades}")
    print(f"Win rate: {win_rate:.2f}%")

    plot_trades(ohlc_df, trade_log)


def plot_trades(ohlc_df, trade_log):
    buys_x = []
    buys_y = []
    sells_x = []
    sells_y = []

    for log_entry in trade_log:
        if log_entry.startswith("Buy at") or ("Exit" in log_entry):
            # Handle exit at end specially
            if "Exit at end at" in log_entry:
                price_match = re.search(r"Exit at end at ([\d\.]+)", log_entry)
                if price_match:
                    price = float(price_match.group(1))
                    index = len(ohlc_df) - 1
                    sells_x.append(index)
                    sells_y.append(price)
                continue

            # For other entries: extract price and index
            match = re.search(r"at ([\d\.]+) \(index (\d+)\)", log_entry)
            if match:
                price = float(match.group(1))
                index = int(match.group(2))

                if log_entry.startswith("Buy at"):
                    buys_x.append(index)
                    buys_y.append(price)
                else:
                    sells_x.append(index)
                    sells_y.append(price)

    plt.figure(figsize=(14, 7))
    plt.plot(ohlc_df.index, ohlc_df['close'], label='Close Price', color='blue')
    plt.scatter(buys_x, buys_y, marker='^', color='green', label='Buy', s=100)
    plt.scatter(sells_x, sells_y, marker='v', color='red', label='Sell/Exit', s=100)
    plt.title("Backtest Trades on Close Price")
    plt.xlabel("Index")
    plt.ylabel("Price")
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    symbol = "YESBANK_ohlc"
    ohlc_df = pd.read_csv(f"{symbol}.csv")  # your 5-min data CSV file
    # Ensure columns: datetime, open, high, low, close, volume

    strategy_config = {
        "sampling_period": 100,
        "range_multiplier": 3.0,
        "stop_loss_percent": 1.5,
        "take_profit_percent": 4.0
    }

    backtest(ohlc_df, symbol, strategy_config)
