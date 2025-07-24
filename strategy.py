def bullish_engulfing(df):
    # Простая проверка bullish engulfing на последних 2 свечах
    if len(df) < 2:
        return False
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    if (curr['close'] > curr['open'] and
        prev['close'] < prev['open'] and
        curr['open'] < prev['close'] and
        curr['close'] > prev['open']):
        return True
    return False

def price_above_emas(df):
    # Проверяем, что цена закрытия выше всех EMA (7,14,28)
    last = df.iloc[-1]
    return last['close'] > last['ema_7'] and last['close'] > last['ema_14'] and last['close'] > last['ema_28']

def check_strategy(df):
    return bullish_engulfing(df) and price_above_emas(df)
