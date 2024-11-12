import plotly.graph_objects as go
import pandas as pd


import plotly.graph_objects as go

def add_anchored_volume_profile(fig, df, anchor_price, period=20):
    # Calculate volume profile
    df['PriceBin'] = pd.cut(df['Close'], bins=20)  # Adjust bins as needed
    volume_profile = df.groupby('PriceBin')['Volume'].sum()

    # Create bar trace for volume profile
    fig.add_trace(go.Bar(
        x=volume_profile.index.astype(str),  # Convert intervals to strings for plotting
        y=volume_profile.values,
        yaxis='y2',  # Use a secondary y-axis
        name='Volume Profile',
        opacity=0.5,
        marker=dict(color='lightblue')
    ))

    # Add a vertical line at the anchor price
    fig.add_shape(go.layout.Shape(
        type="line",
        x0=anchor_price,
        x1=anchor_price,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",
        line=dict(color="red", width=2)
    ))

    # Update layout for secondary y-axis
    fig.update_layout(
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right',
            showgrid=False
        )
    )

    return fig

def add_open_shape_indicator(fig, spike_days):
    spike_dates, spike_prices = zip(*spike_days) if spike_days else ([], [])
    fig.add_trace(go.Scatter(
        x=spike_dates, y=spike_prices, mode='markers',
        marker=dict(symbol='circle-open', size=15, color='black', line=dict(width=2)),  # Customize as needed
        name='Volume & Price Spike'
    ))
    return fig


# plot_helpers.py - add_sequence_stars function
def add_sequence_stars(fig, sequence_stars):
    for color in set([star[3] for star in sequence_stars]):
        star_x = [date for date, price, size, c in sequence_stars if c == color]
        star_y = [price for date, price, size, c in sequence_stars if c == color]
        star_sizes = [size for date, price, size, c in sequence_stars if c == color]  # Extract sizes
        fig.add_trace(go.Scatter(
            x=star_x, y=star_y, mode='markers',
            marker=dict(symbol='star', size=star_sizes, color=color),  # Use star_sizes here
            name=f'{color.capitalize()} Stars'
        ))
    return fig


def plot_intersection_marker(fig, date_intersect, y_intersect):
    """
    Plots concentric circles at the intersection point.
    """
    for i, radius in enumerate([10, 15, 20], start=1):
        fig.add_trace(go.Scatter(
            x=[date_intersect], y=[y_intersect],
            mode="markers",
            marker=dict(symbol="circle-open", size=radius, color="red", line=dict()),  # Corrected line
            name=f"Intersection Circle {i}",
        ))

def create_candlestick_chart(df):
    fig = go.Figure()

    # Add volume trace as a bar chart with conditional coloring
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name='Volume',
        marker=dict(
            color=df['Close'] > df['Open'],  # Condition for red/green
            colorscale=[[0, 'red'], [1, 'green']],  # Colors for False/True
            opacity=0.2  # Adjust opacity for transparency
        ),
        yaxis='y2'
    ))

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick'
    ))

    # Update layout for secondary y-axis
    fig.update_layout(
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right',
            showgrid=False,
        ),
        barmode='overlay'  # Ensure bars are overlaid on the candlestick chart
    )

    return fig


def add_moving_averages(fig, df):
    for ma in ['SMA_10', 'SMA_20', 'SMA_50', 'SMA_100', 'SMA_200']:
        if ma in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[ma], mode='lines', name=ma))
    return fig

def add_buy_signals(fig, buy_signals):
    buy_dates, buy_prices = zip(*buy_signals) if buy_signals else ([], [])
    fig.add_trace(go.Scatter(
        x=buy_dates, y=buy_prices, mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'),
        name='Buy Signals'
    ))
    return fig

def add_sell_signals(fig, sell_signals):
    sell_dates, sell_prices = zip(*sell_signals) if sell_signals else ([], [])
    fig.add_trace(go.Scatter(
        x=sell_dates, y=sell_prices, mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'),
        name='Sell Signals'
    ))
    return fig

def add_fibonacci_levels(fig, fib_levels, df):
    # Define the typical Fibonacci percentage levels and their colors
    fib_percentages = [23.6, 38.2, 50, 61.8, 78.6]
    fib_colors = ['purple', 'green', 'blue', 'red', 'orange']

    fib_x = [df.index[0], df.index[-1]]  # Start and end dates for plotting horizontal lines

    for i, (level, percentage) in enumerate(zip(fib_levels['Fibonacci Levels'], fib_percentages)):
        rounded_price = round(level)  # Round the price to the nearest integer
        color = fib_colors[i % len(fib_colors)]
        
        # Update the legend text to include the Fibonacci percentage and rounded price
        fig.add_trace(go.Scatter(
            x=fib_x, y=[level, level], mode="lines",
            line=dict(dash="dash", color=color),
            name=f"{percentage}% @ {rounded_price}"  # Legend text with percentage and rounded price
        ))

    return fig



def add_fibonacci_levelsOLDNOPERCENTS(fig, fib_levels, df):  # Add df as an argument
    fib_colors = ['purple', 'green', 'blue', 'red', 'orange', 'cyan', 'magenta']
    fib_x = [df.index[0], df.index[-1]]
    for i, level in enumerate(fib_levels['Fibonacci Levels']):
        color = fib_colors[i % len(fib_colors)]
        fig.add_trace(go.Scatter(
            x=fib_x * 2, y=[level, level] * 2, mode="lines",
            line=dict(dash="dash", color=color), name=f'Fibonacci Level {level}'
        ))
    return fig



def add_linear_regression(fig, slope, intercept, df):
    fig.add_trace(go.Scatter(
        x=[df.index[0], df.index[-1]],
        y=[slope * 0 + intercept, slope * (len(df) - 1) + intercept],
        mode='lines', line=dict(color='black', dash='solid'), name='Regression Line'
    ))
    return fig

def add_deviation_bands(fig, deviations, df, touched_devs):
    # Loop through each deviation level and plot only if it's touched by a wick
    for dev_name, dev_prices in deviations.items():
        if dev_name not in touched_devs:
            continue  # Skip bands that were not touched by a wick

        # Determine color and label for the band
        if 'upper' in dev_name:
            color = 'blue'
            line_name = f"Upper {dev_name.split('_')[1]} Sigma"
        elif 'lower' in dev_name:
            color = 'orange'
            line_name = f"Lower {dev_name.split('_')[1]} Sigma"
        else:
            continue

        # Plot each touched deviation band independently
        fig.add_trace(go.Scatter(
            x=df.index[-len(dev_prices):], y=dev_prices, mode='lines',
            line=dict(color=color, dash='dot'), name=line_name
        ))


def add_deviation_bandsSecondCandidate(fig, deviations, df):
    # Loop through each deviation level and plot it as an independent line
    for dev_name, dev_prices in deviations.items():
        if 'upper' in dev_name:
            color = 'blue'
            line_name = f"Upper {dev_name.split('_')[1]} Sigma"
        elif 'lower' in dev_name:
            color = 'orange'
            line_name = f"Lower {dev_name.split('_')[1]} Sigma"
        else:
            continue

        # Plot each deviation level independently for better clarity
        fig.add_trace(go.Scatter(
            x=df.index[-len(dev_prices):], y=dev_prices, mode='lines',
            line=dict(color=color, dash='dot'), name=line_name
        ))



def add_deviation_bandsOriginal(fig, deviations, df):
    upper_x, upper_y = [], []
    lower_x, lower_y = [], []
    for dev_name, dev_prices in deviations.items():
        if 'upper' in dev_name:
            upper_x.extend(df.index[-len(dev_prices):])
            upper_y.extend(dev_prices)
        elif 'lower' in dev_name:
            lower_x.extend(df.index[-len(dev_prices):])
            lower_y.extend(dev_prices)

    fig.add_trace(go.Scatter(
        x=upper_x, y=upper_y, mode='lines', line=dict(color='blue', dash='dot'), name='Upper Deviation Bands'
    ))
    fig.add_trace(go.Scatter(
        x=lower_x, y=lower_y, mode='lines', line=dict(color='orange', dash='dot'), name='Lower Deviation Bands'
    ))
    return fig

def add_wick_touches(fig, wick_touches):
    wick_x = [date for date, (level, price) in wick_touches]
    wick_y = [price for date, (level, price) in wick_touches]
    fig.add_trace(go.Scatter(
        x=wick_x, y=wick_y, mode='markers',
        marker=dict(symbol='x', color='blue', size=8),
        name='Wick Touches'
    ))
    return fig

def add_fib_wick_touches(fig, fib_wick_touches):
    fib_wick_x = [date for date, (level, price) in fib_wick_touches]
    fib_wick_y = [price for date, (level, price) in fib_wick_touches]
    fig.add_trace(go.Scatter(
        x=fib_wick_x, y=fib_wick_y, mode='markers',
        marker=dict(symbol='circle', color='purple', size=6),
        name='Fib Wick Touches'
    ))
    return fig

def add_ma_touches(fig, ma_touches):
    ma_x = [date for date, (ma, price) in ma_touches]
    ma_y = [price for date, (ma, price) in ma_touches]
    fig.add_trace(go.Scatter(
        x=ma_x, y=ma_y, mode='markers',
        marker=dict(symbol='cross', color='black', size=8),
        name='MA Touches'
    ))
    return fig

def finalize_layout(fig, ticker):
    fig.update_layout(
        title=f'{ticker} Candlestick Chart with Interactive Signal Toggles',
        xaxis_title='Date',
        yaxis_title='Price',
        legend=dict(itemsizing='constant'),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig
def plot_signals_with_candlestick_refactored(
    df, buy_signals, sell_signals, fib_levels,
    wick_touches, fib_wick_touches, ma_touches,
    sequence_stars, slope, intercept, ticker, deviations, touched_devs,
    spike_days
):
    fig = create_candlestick_chart(df)
    add_moving_averages(fig, df)
    add_buy_signals(fig, buy_signals)
    add_sell_signals(fig, sell_signals)
    add_fibonacci_levels(fig, fib_levels, df)
    add_sequence_stars(fig, sequence_stars)
    add_linear_regression(fig, slope, intercept, df)
    add_open_shape_indicator(fig, spike_days)

    # Ensure touched_devs is passed to add_deviation_bands
    add_deviation_bands(fig, deviations, df, touched_devs)

    add_wick_touches(fig, wick_touches)
    add_fib_wick_touches(fig, fib_wick_touches)
    add_ma_touches(fig, ma_touches)
    finalize_layout(fig, ticker)
    return fig


def plot_signals_with_candlestick_refactoredBroken(
    df, buy_signals, sell_signals, fib_levels,
    wick_touches, fib_wick_touches, ma_touches,
    sequence_stars, slope, intercept, ticker, deviations
):
    fig = create_candlestick_chart(df)
    add_moving_averages(fig, df)
    add_buy_signals(fig, buy_signals)
    add_sell_signals(fig, sell_signals)
    add_fibonacci_levels(fig, fib_levels, df)
    add_sequence_stars(fig, sequence_stars)
    add_linear_regression(fig, slope, intercept, df)

    # Ensure touched_devs is passed to add_deviation_bands
    add_deviation_bands(fig, deviations, df, touched_devs)  # <-- Add touched_devs here

    add_wick_touches(fig, wick_touches)
    add_fib_wick_touches(fig, fib_wick_touches)
    add_ma_touches(fig, ma_touches)
    finalize_layout(fig, ticker)
    return fig



def plot_signals_with_candlestick_refactoredOrig(
    df, buy_signals, sell_signals, fib_levels,
    wick_touches, fib_wick_touches, ma_touches,
    sequence_stars, slope, intercept, ticker, deviations
):
    fig = create_candlestick_chart(df)
    add_moving_averages(fig, df)
    add_buy_signals(fig, buy_signals)
    add_sell_signals(fig, sell_signals)
    add_fibonacci_levels(fig, fib_levels,df)
    add_sequence_stars(fig, sequence_stars)
    add_linear_regression(fig, slope, intercept, df)
    add_deviation_bands(fig, deviations, df)  # Assuming 'deviations' is defined
    add_wick_touches(fig, wick_touches)
    add_fib_wick_touches(fig, fib_wick_touches)
    add_ma_touches(fig, ma_touches)
    finalize_layout(fig, ticker)
    return fig
