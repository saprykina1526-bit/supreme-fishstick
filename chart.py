import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from data_fetcher import fetch_ohlcv, calculate_ema

def find_support_resistance(df):
    lows = df['low']
    highs = df['high']
    support = lows.rolling(window=10, center=True).min().dropna()
    resistance = highs.rolling(window=10, center=True).max().dropna()
    support_levels = support.tail(2).values
    resistance_levels = resistance.tail(2).values
    return support_levels, resistance_levels

def generate_chart(symbol):
    try:
        df = fetch_ohlcv(symbol, "1h", limit=200)
        df = calculate_ema(df, [7,14,28])
        df.set_index('timestamp', inplace=True)
        support_levels, resistance_levels = find_support_resistance(df)
        apds = [mpf.make_addplot(df[f'ema_{p}']) for p in [7,14,28]]
        fig, axlist = mpf.plot(df, type='candle', style='yahoo', addplot=apds, returnfig=True)
        ax = axlist[0]
        for lvl in support_levels:
            ax.axhline(lvl, color='green', linestyle='--', linewidth=1)
        for lvl in resistance_levels:
            ax.axhline(lvl, color='red', linestyle='--', linewidth=1)
        path = f"{symbol.replace('/','_')}_chart.png"
        fig.savefig(path)
        plt.close(fig)
        return path
    except Exception as e:
        print(f"Ошибка генерации графика для {symbol}: {e}")
        return None
