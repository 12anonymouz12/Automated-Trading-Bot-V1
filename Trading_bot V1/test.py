from signal_generator import range_filter_signals

# Sample OHLC data format: [timestamp, open, high, low, close, volume]
ohlc_sample = [
    ['2025-08-01T10:00:00', 100, 102, 99, 101, 1000],
    ['2025-08-01T10:05:00', 101, 103, 100, 102, 1100],
    ['2025-08-01T10:10:00', 102, 104, 101, 103, 1050],
    ['2025-08-01T10:15:00', 103, 105, 102, 104, 1200],
    ['2025-08-01T10:20:00', 104, 106, 103, 105, 1300],
    ['2025-08-01T10:25:00', 105, 107, 104, 106, 1250],
    ['2025-08-01T10:30:00', 106, 108, 105, 107, 1400],
    ['2025-08-01T10:35:00', 107, 109, 106, 108, 1500],
    ['2025-08-01T10:40:00', 108, 110, 107, 109, 1600],
    ['2025-08-01T10:45:00', 109, 111, 108, 110, 1700],
]

# Test parameters
sampling_period = 3
range_multiplier = 1.5

signals = range_filter_signals(ohlc_sample, sampling_period, range_multiplier)

for ts, sig in signals:
    if sig:
        print(f"{ts}: {sig}")
