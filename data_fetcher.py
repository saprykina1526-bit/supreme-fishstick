import ccxt
import pandas as pd

exchange = ccxt.binance()

def fetch_ohlcv(symbol, timeframe='1h', limit=200):
    try:
        # Binance использует формат без слеша, например 'MOVEUSDT'
        symbol_binance = symbol.replace('/', '')
        ohlcv = exchange.fetch_ohlcv(symbol_binance, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Ошибка fetch_ohlcv: {e}")
        return pd.DataFrame()

def calculate_ema(df, periods):
    for p in periods:
        df[f'ema_{p}'] = df['close'].ewm(span=p, adjust=False).mean()
    return df
