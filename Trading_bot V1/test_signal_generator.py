import pandas as pd

# Your OHLC data
ohlc = [
    {"date":"2023-05-01 09:15","open":113.8,"high":114.2,"low":113.6,"close":114.1},
    {"date":"2023-05-01 09:20","open":114.2,"high":114.4,"low":114.1,"close":114.3},
    {"date":"2023-05-01 09:25","open":114.3,"high":114.5,"low":114.2,"close":114.4},
    {"date":"2023-05-01 09:30","open":114.4,"high":114.6,"low":114.3,"close":114.2},
    {"date":"2023-05-01 09:35","open":114.2,"high":114.5,"low":114.1,"close":114.4},
    {"date":"2023-05-01 09:40","open":114.5,"high":114.7,"low":114.4,"close":114.6},
    {"date":"2023-05-01 09:45","open":114.6,"high":114.8,"low":114.5,"close":114.7},
    {"date":"2023-05-01 09:50","open":114.7,"high":115.0,"low":114.6,"close":114.9},
    {"date":"2023-05-01 09:55","open":114.9,"high":115.1,"low":114.7,"close":115.0},
    {"date":"2023-05-01 10:00","open":115.0,"high":115.2,"low":114.9,"close":115.1},
]

# Parameters for the Range Filter
range_multiplier = 3.0  # multiplier for ATR or range, from your config
stop_loss_pct = 1.5 / 100
take_profit_pct = 4.0 / 100
initial_capital = 30000

# Convert list to DataFrame
df = pd.DataFrame(ohlc)
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# Calculate typical range (high - low)
df['range'] = df['high'] - df['low']

# Calculate smoothed range filter bands using simple moving average of range * multiplier
window = 3  # short window to smooth range, can be tuned

df['range_smooth'] = df['range'].rolling(window).mean() * range_multiplier

# Initialize columns
df['upper_band'] = 0.0
df['lower_band'] = 0.0
df['position'] = 0  # 1 for long, -1 for short, 0 for no position
df['signal'] = 0  # 1 buy, -1 sell, 0 no signal

# Calculate bands based on close price +/- smoothed range
for i in range(len(df)):
    if i == 0 or pd.isna(df['range_smooth'].iloc[i]):
        df['upper_band'].iloc[i] = df['close'].iloc[i]
        df['lower_band'].iloc[i] = df['close'].iloc[i]
    else:
        df['upper_band'].iloc[i] = df['close'].iloc[i-1] + df['range_smooth'].iloc[i]
        df['lower_band'].iloc[i] = df['close'].iloc[i-1] - df['range_smooth'].iloc[i]

# Generate signals
for i in range(1, len(df)):
    # Buy signal: close crosses above upper band
    if df['close'].iloc[i] > df['upper_band'].iloc[i] and df['close'].iloc[i-1] <= df['upper_band'].iloc[i-1]:
        df['signal'].iloc[i] = 1
        df['position'].iloc[i] = 1
    # Sell signal: close crosses below lower band
    elif df['close'].iloc[i] < df['lower_band'].iloc[i] and df['close'].iloc[i-1] >= df['lower_band'].iloc[i-1]:
        df['signal'].iloc[i] = -1
        df['position'].iloc[i] = 0
    else:
        # Carry forward position
        df['position'].iloc[i] = df['position'].iloc[i-1]

# Backtest logic
capital = initial_capital
position_size = 0
entry_price = 0
trade_log = []

for i in range(len(df)):
    sig = df['signal'].iloc[i]
    price = df['close'].iloc[i]
    date = df.index[i]
    pos = df['position'].iloc[i]

    # Enter long
    if sig == 1 and position_size == 0:
        position_size = capital // price  # buy max shares possible
        entry_price = price
        invested = position_size * price
        capital -= invested
        trade_log.append({'date': date, 'action': 'BUY', 'price': price, 'shares': position_size})

    # Exit long
    elif sig == -1 and position_size > 0:
        capital += position_size * price
        trade_log.append({'date': date, 'action': 'SELL', 'price': price, 'shares': position_size})
        position_size = 0
        entry_price = 0

    # Check stop loss or take profit
    if position_size > 0:
        change_pct = (price - entry_price) / entry_price
        if change_pct <= -stop_loss_pct:
            # Stop loss triggered - exit position
            capital += position_size * price
            trade_log.append({'date': date, 'action': 'STOP LOSS SELL', 'price': price, 'shares': position_size})
            position_size = 0
            entry_price = 0
        elif change_pct >= take_profit_pct:
            # Take profit triggered - exit position
            capital += position_size * price
            trade_log.append({'date': date, 'action': 'TAKE PROFIT SELL', 'price': price, 'shares': position_size})
            position_size = 0
            entry_price = 0

# If position still open at end, close it
if position_size > 0:
    price = df['close'].iloc[-1]
    date = df.index[-1]
    capital += position_size * price
    trade_log.append({'date': date, 'action': 'SELL AT END', 'price': price, 'shares': position_size})
    position_size = 0

# Show trade log
print("Trade Log:")
for t in trade_log:
    print(f"{t['date']} | {t['action']} | Price: {t['price']} | Shares: {t['shares']}")

print(f"\nInitial Capital: ₹{initial_capital}")
print(f"Ending Capital: ₹{capital:.2f}")
print(f"Net Profit/Loss: ₹{capital - initial_capital:.2f}")
