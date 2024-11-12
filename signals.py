import pandas as pd
import numpy as np
from scipy.signal import argrelextrema


import pandas as pd
import numpy as np

def detect_volume_price_spikes(df, volume_std_threshold=1.5, price_std_threshold=2, rolling_window=20):
    # Calculate daily changes
    df['VolumeChange'] = df['Volume'].diff()
    df['PriceChange'] = df['High'] - df['Low']  # Or your preferred metric

    # Calculate rolling means and standard deviations
    df['VolumeMean'] = df['VolumeChange'].rolling(window=rolling_window).mean()
    df['VolumeStd'] = df['VolumeChange'].rolling(window=rolling_window).std()
    df['PriceMean'] = df['PriceChange'].rolling(window=rolling_window).mean()
    df['PriceStd'] = df['PriceChange'].rolling(window=rolling_window).std()

    spike_days = []
    for i in range(rolling_window, len(df)):
        if (
            abs(df['VolumeChange'].iloc[i] - df['VolumeMean'].iloc[i]) > volume_std_threshold * df['VolumeStd'].iloc[i]
            and abs(df['PriceChange'].iloc[i] - df['PriceMean'].iloc[i]) > price_std_threshold * df['PriceStd'].iloc[i]
        ):
            spike_days.append((df.index[i], df['Close'].iloc[i]))  # Date and closing price

    return spike_days

def detect_wick_touches(df, deviations, len_regression):
    """Detect wick touches on standard deviation bands."""
    wick_touches = []
    touched_devs = set()  # Track touched deviation bands

    for i in range(-len_regression, 0):
        high_touched = False
        low_touched = False
        for dev, prices in deviations.items():
            price = prices[i + len_regression]
            if not high_touched and df['High'].iloc[i] >= price and df['High'].iloc[i - 1] < price:
                wick_touches.append((df.index[i], (dev, price)))
                touched_devs.add(dev)
                high_touched = True
            elif not low_touched and df['Low'].iloc[i] <= price and df['Low'].iloc[i - 1] > price:
                wick_touches.append((df.index[i], (dev, price)))
                touched_devs.add(dev)
                low_touched = True

    return wick_touches, touched_devs  # Return both wick touches and touched deviations


def add_sequence_stars(fig, sequence_stars):
    for color in set([star[3] for star in sequence_stars]):
        star_x = [date for date, price, size, c in sequence_stars if c == color]
        star_y = [price for date, price, size, c in sequence_stars if c == color]
        star_sizes = [size for date, price, size, c in sequence_stars if c == color]
        fig.add_trace(go.Scatter(
            x=star_x, y=star_y, mode='markers',
            marker=dict(symbol='star', size=star_sizes, color=color),
            name=f'{color.capitalize()} Stars'
        ))
    return fig


def detect_signals(df):
    """
    Detect buy and sell signals based on specific conditions.
    """
    buy_signals = []
    sell_signals = []
    
    for i in range(1, len(df) - 1):
        if df['Close'].iloc[i] > df['Open'].iloc[i] and df['Close'].iloc[i] > df['Close'].iloc[i - 1]:
            buy_signals.append((df.index[i], df['Close'].iloc[i]))
        elif df['Close'].iloc[i] < df['Open'].iloc[i] and df['Close'].iloc[i] < df['Close'].iloc[i - 1]:
            sell_signals.append((df.index[i], df['Close'].iloc[i]))

    return buy_signals, sell_signals

def calculate_fibonacci_levels(df):
    """
    Calculate Fibonacci retracement levels based on the high and low of the dataset.
    """
    high_price = df['High'].max()
    low_price = df['Low'].min()
    diff = high_price - low_price
    
    levels = [high_price - diff * ratio for ratio in [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]]
    fib_levels = pd.DataFrame(data=levels, columns=['Fibonacci Levels'])
    
    return fib_levels, high_price, low_price

def detect_wick_touches(df, deviations, len_regression):
    """
    Detect wick touches on standard deviation bands.
    """
    wick_touches = []
    touched_devs = set()
    
    for i in range(-len_regression, 0):
        high_touched = False
        low_touched = False
        for dev, prices in deviations.items():
            price = prices[i + len_regression]
            if not high_touched and df['High'].iloc[i] >= price and df['High'].iloc[i - 1] < price:
                wick_touches.append((df.index[i], (dev, price)))
                touched_devs.add(dev)
                high_touched = True
            elif not low_touched and df['Low'].iloc[i] <= price and df['Low'].iloc[i - 1] > price:
                wick_touches.append((df.index[i], (dev, price)))
                touched_devs.add(dev)
                low_touched = True

    return wick_touches, touched_devs

def detect_fib_wick_touches(df, fib_levels):
    """
    Detect wick touches on Fibonacci levels.
    """
    fib_wick_touches = []
    touched_fibs = set()
    
    for i in range(len(df)):
        for level in fib_levels['Fibonacci Levels']:
            price = level
            if df['High'].iloc[i] >= price and df['Low'].iloc[i] <= price:
                fib_wick_touches.append((df.index[i], (round(level, 3), round(price, 2))))
                touched_fibs.add(level)

    return fib_wick_touches, touched_fibs

def detect_body_ma_touches(df):
    """
    Detect body touches on moving averages.
    """
    ma_touches = []
    touched_mas = set()
    
    for i in range(len(df)):
        for ma in ['SMA_10', 'SMA_20', 'SMA_50', 'SMA_100', 'SMA_200']:
            price = df[ma].iloc[i]
            if df['Open'].iloc[i] <= price <= df['Close'].iloc[i] or df['Close'].iloc[i] <= price <= df['Open'].iloc[i]:
                ma_touches.append((df.index[i], (ma, price)))
                touched_mas.add(ma)

    return ma_touches, touched_mas

def detect_consecutive_days(df):
    """
    Detect consecutive sequences of up or down days and returns information for sequence stars.
    """
    sequence_stars = []
    current_sequence = 1
    up_down = 'neutral'

    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Open'].iloc[i]:
            if up_down == 'up':
                current_sequence += 1
            else:
                up_down = 'up'
                current_sequence = 1
        elif df['Close'].iloc[i] < df['Open'].iloc[i]:
            if up_down == 'down':
                current_sequence += 1
            else:
                up_down = 'down'
                current_sequence = 1
        else:
            up_down = 'neutral'
            current_sequence = 1

        if current_sequence >= 2:
            size = 8 + (current_sequence - 1) * 5  # Adjust base size and increment as needed
            color = 'green' if up_down == 'up' else 'red'
            sequence_stars.append((df.index[i], df['Close'].iloc[i], size, color))

    return sequence_stars



