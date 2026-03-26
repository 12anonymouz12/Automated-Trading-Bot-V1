import numpy as np
import pandas as pd

def ema(series, period):
    """Calculate Exponential Moving Average (EMA) for a pandas Series."""
    return series.ewm(span=period, adjust=False).mean()

def generate_signals(ohlc_data, strategy_config):
    """
    ohlc_data: dict of symbol -> list of candles (each candle: [datetime, open, high, low, close, volume])
    strategy_config: dict with keys:
        - sampling_period (int)
        - range_multiplier (float)
        - stop_loss_percent (float)  # not used here, but for future use
        - take_profit_percent (float) # not used here, but for future use

    Returns: dict symbol -> signal ("buy", "sell", "hold")
    """

    signals = {}
    sampling_period = strategy_config.get("sampling_period", 100)
    range_multiplier = strategy_config.get("range_multiplier", 3.0)

    for symbol, candles in ohlc_data.items():
        if len(candles) < sampling_period + 2:  # Need enough candles for EMA and lookback
            signals[symbol] = "hold"
            continue

        # Convert candles to DataFrame for easier processing
        df = pd.DataFrame(candles, columns=["datetime", "open", "high", "low", "close", "volume"])

        src = df["close"]

        # Step 1: Calculate absolute differences |src - src[1]|
        abs_diff = (src - src.shift(1)).abs()

        # Step 2: Calculate EMA of abs_diff with period = sampling_period (equivalent to ta.ema in Pine)
        avrng = ema(abs_diff, sampling_period)

        # Step 3: Smooth the average range by applying EMA again with period = (sampling_period*2 -1)
        wper = sampling_period * 2 - 1
        smrng = ema(avrng, wper) * range_multiplier

        # Step 4: Calculate the recursive range filter 'filt'
        filt = [np.nan] * len(df)
        filt[0] = src.iloc[0]  # Initialize first filt value as first close

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

        # Step 5: Calculate upward and downward counts (directional state)
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

        # Step 6: Define longCond and shortCond
        longCond = (
            ((src > filt) & (src > src.shift(1)) & (upward > 0)) |
            ((src > filt) & (src < src.shift(1)) & (upward > 0))
        )

        shortCond = (
            ((src < filt) & (src < src.shift(1)) & (downward > 0)) |
            ((src < filt) & (src > src.shift(1)) & (downward > 0))
        )

        # Step 7: Calculate CondIni state (1 for long, -1 for short, else previous)
        CondIni = [0] * len(df)
        for i in range(1, len(df)):
            if longCond.iloc[i]:
                CondIni[i] = 1
            elif shortCond.iloc[i]:
                CondIni[i] = -1
            else:
                CondIni[i] = CondIni[i - 1]

        CondIni = pd.Series(CondIni, index=df.index)

        # Step 8: Detect signals (longCondition and shortCondition transitions)
        longCondition = (longCond) & (CondIni.shift(1) == -1)
        shortCondition = (shortCond) & (CondIni.shift(1) == 1)

        # We'll generate signal for the last candle in the data
        if longCondition.iloc[-1]:
            signals[symbol] = "buy"
        elif shortCondition.iloc[-1]:
            signals[symbol] = "sell"
        else:
            signals[symbol] = "hold"

    return signals
