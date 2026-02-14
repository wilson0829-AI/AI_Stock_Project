import pandas as pd
import numpy as np

def calculate_rsi(series, period=14):
    delta = series.diff(); gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, min_periods=period).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, min_periods=period).mean()
    return 100 - (100 / (1 + gain/loss))

def calculate_all_indicators(df):
    df = df.copy()
    df['SMA5'] = df['Close'].rolling(5).mean(); df['SMA10'] = df['Close'].rolling(10).mean()
    df['SMA20'] = df['Close'].rolling(20).mean(); df['SMA60'] = df['Close'].rolling(60).mean()
    df['LongShortLine'] = df['Close'].rolling(25).mean()
    df['Change'] = df['Close'].diff(); df['PctChange'] = (df['Change'] / df['Close'].shift(1) * 100)
    df['RSI'] = calculate_rsi(df['Close'], 14)
    lm = df['Low'].rolling(9).min(); hm = df['High'].rolling(9).max(); rsv = (df['Close'] - lm) / (hm - lm) * 100
    df['K'] = rsv.ewm(com=2).mean(); df['D'] = df['K'].ewm(com=2).mean()
    e1 = df['Close'].ewm(span=12, adjust=False).mean(); e2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = e1 - e2; df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean(); df['MACD_HIST'] = df['DIF'] - df['DEA']
    return df

def calculate_trend_line_data(df):
    y = df['Close'].values; x = np.arange(len(y)); slope, intercept = np.polyfit(x, y, 1)
    return (slope * x + intercept).tolist(), slope
