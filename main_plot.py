from data_retrieval import get_stock_data, add_moving_averages
#from plot_helpers import add_open_shape_indicator
from plot_helpers import add_open_shape_indicator, plot_signals_with_candlestick_refactored, plot_intersection_marker, add_anchored_volume_profile
#from plot_helpers import add_open_shape_indicator, plot_signals_with_candlestick_refactored, plot_intersection_marker  
from signals import detect_signals, calculate_fibonacci_levels, detect_wick_touches, detect_fib_wick_touches, detect_body_ma_touches, detect_consecutive_days
from geometry import find_two_peaks, find_two_high_peaks, find_two_low_troughs, calculate_intersection, plot_projection_line
from plot_helpers import plot_signals_with_candlestick_refactored, plot_intersection_marker
from signals import detect_volume_price_spikes
from summary import generate_summary_output
from datetime import timedelta
from geometry import calculate_linear_regression_and_deviations
import plotly.io as pio
import yfinance as yf
import os
from datetime import datetime

def create_output_directory(ticker):
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime('%Y-%m-%d')

    # Create the directory path: data/YYYY-MM-DD/ticker
    directory = os.path.join('data', today, ticker)

    # Create the directories if they don't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory



def main():


    # Configuration and user input
    ticker = input("Enter the stock ticker: ")

    # Create the output directory at the beginning of the main function
    output_directory = create_output_directory(ticker) 

    # Allow the user to specify either a time period (e.g., '1y') or a date range (e.g., '2020-01-02,2021-06-22')
    date_range_input = input("Enter the time period (e.g., '1y') or date range (e.g., '2020-01-02,2021-06-22'): ")

    # Parse date range input
    if ',' in date_range_input:
        start_date, end_date = date_range_input.split(',')
        start_date = start_date.strip()
        end_date = end_date.strip()
        period = None  # No period since we're using specific dates
    else:
        start_date = None
        end_date = None
        period = date_range_input.strip()

    # Data Retrieval
    if start_date and end_date:
        # Fetch data for the specified date range
        df = yf.download(ticker, start=start_date, end=end_date)
    else:
        # Fetch data for the specified period (e.g., '1y')
        df = yf.download(ticker, period=period)
    
    # Add moving averages (if needed)
    df = add_moving_averages(df)

    # Get the most recent date and closing price for the watermark
    latest_date = df.index[-1].strftime("%Y-%m-%d")
    current_price = df['Close'].iloc[-1]

    # Signal Calculations
    buy_signals, sell_signals = detect_signals(df)
    fib_levels, high_price, low_price = calculate_fibonacci_levels(df)
    len_regression = 144  # Set regression length for calculations

    # Calculate Linear Regression and Deviation Bands
    slope, intercept, start_price, end_price, deviations = calculate_linear_regression_and_deviations(df, len_regression)
    wick_touches, touched_devs = detect_wick_touches(df, deviations, len_regression)
    fib_wick_touches, touched_fibs = detect_fib_wick_touches(df, fib_levels)
    ma_touches, touched_mas = detect_body_ma_touches(df)
    sequence_stars = detect_consecutive_days(df)

    # Calculate spikes
    spike_days = detect_volume_price_spikes(df)

    # Generate Detailed Summary Output
    generate_summary_output(ticker, buy_signals, sell_signals, sequence_stars, wick_touches, fib_wick_touches, ma_touches, output_directory)

    # Initial Peaks and Troughs Calculation
    high_peaks = find_two_high_peaks(df)
    low_troughs = find_two_low_troughs(df)
    
    slope, intercept, start_price, end_price, deviations = calculate_linear_regression_and_deviations(df, len_regression)

    # Create Figure and Plot Initial Signals with Candlestick Chart
    fig = plot_signals_with_candlestick_refactored(
        df, buy_signals, sell_signals, fib_levels, 
        wick_touches, fib_wick_touches, ma_touches, 
        sequence_stars, slope, intercept, ticker, deviations, touched_devs,
        spike_days=spike_days  # Add spike_days
    )

    # Add the open shape indicator
    add_open_shape_indicator(fig, spike_days)

    # Add anchored volume profile
    #fig = add_anchored_volume_profile(fig, df, anchor_price=df['Close'].iloc[-1], period=20)  # Customize anchor_price and period as needed

    # Plot Projection Lines
    slope_high, intercept_high = plot_projection_line(df, fig, high_peaks['High'], color='green', line_name='High Peak Line')
    slope_low, intercept_low = plot_projection_line(df, fig, low_troughs['Low'], color='red', line_name='Low Trough Line')

    # Try to Calculate Intersection and Plot Concentric Circles
    try:
        date_intersect, y_intersect = calculate_intersection(slope_high, intercept_high, slope_low, intercept_low)
        plot_intersection_marker(fig, date_intersect, y_intersect)
    except ValueError as e:
        print("Skipping intersection marker:", e)

    # Get the Date After the First Peak to Start New Calculation for Secondary Peaks and Troughs
    start_date_new_peaks = high_peaks.index[0] + timedelta(days=1)
    df_after_first_peak = df[df.index > start_date_new_peaks]

    # Calculate the Second Set of Peaks and Troughs Only if Enough Data Points Are Available
    try:
        new_high_peaks = find_two_high_peaks(df_after_first_peak)
        new_low_troughs = find_two_low_troughs(df_after_first_peak)

        # Plot New Projections with Dotted Lines in Blue and Yellow
        plot_projection_line(df, fig, new_high_peaks['High'], color='blue', line_name='Secondary High Peak Line', project_until=None)
        plot_projection_line(df, fig, new_low_troughs['Low'], color='yellow', line_name='Secondary Low Trough Line', project_until=None)

    except ValueError as e:
        print("Skipping secondary lines:", e)

    # Add watermark with ticker, date, and current price
    fig.add_annotation(
        text=f"{ticker.upper()} - {latest_date} - ${current_price:.2f}",
        xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=40, color="rgba(128, 128, 128, 0.3)"),
        opacity=0.2
    )

    # Display the interactive plot with full legend and range slider
    fig.show()

    # Create a copy of the figure for saving
    fig_for_saving = fig.full_figure_for_development(warn=False)
    
    # Remove the legend and range slider from the saved figure
    fig_for_saving.update_layout(showlegend=False, xaxis_rangeslider_visible=False)

    # Save the plot as a PNG with the ticker and period in the filename
    #filename = f"{ticker}_{date_range_input.replace(',', '_')}_plot.png"
    #pio.write_image(fig_for_saving, filename, format="png")
    #print(f"Plot saved as {filename}")
    # Save the plot
    plot_filename = os.path.join(output_directory, f"{ticker}_{date_range_input.replace(',', '_')}_plot.png")
    pio.write_image(fig_for_saving, plot_filename, format="png")
    print(f"Plot saved as {plot_filename}")


if __name__ == "__main__":
    main()

