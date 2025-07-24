
import os
import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import ccxt
import pandas as pd
import pandas_ta as ta

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = Bot(token=TOKEN)

EMA_PERIODS = [7, 14, 28]
assets = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("Бот запущен. Используй /add XPR/USDT для отслеживания.")

def fetch_data(symbol):
    exchange = ccxt.binance()
    bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    for p in EMA_PERIODS:
        df[f'EMA_{p}'] = ta.ema(df['close'], length=p)
    return df

def check_long_signal(df):
    latest = df.iloc[-1]
    if all(latest['close'] > latest[f'EMA_{p}'] for p in EMA_PERIODS):
        return "✅ LONG сигнал (все EMA ниже цены)"
    return "❌ Нет LONG сигнала"

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    for symbol in assets.keys():
        df = fetch_data(symbol)
        signal = check_long_signal(df)
        await update.message.reply_text(f"{symbol} → {signal}")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    try:
        symbol = context.args[0].upper()
        if "/" not in symbol:
            await update.message.reply_text("Формат: /add XPR/USDT")
            return
        assets[symbol] = {'tf': '1h'}
        await update.message.reply_text(f"Актив {symbol} добавлен.")
    except IndexError:
        await update.message.reply_text("Формат: /add XPR/USDT")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("add", add))
    app.run_polling()
