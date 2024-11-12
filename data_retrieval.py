import yfinance as yf
import pandas as pd
import numpy as np

def get_stock_data(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    return stock.history(period=period)

def add_moving_averages(df):
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_100'] = df['Close'].rolling(window=100).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['SMA_300'] = df['Close'].rolling(window=300).mean()
    return df

