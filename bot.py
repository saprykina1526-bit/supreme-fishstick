import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from chart import generate_chart
from strategy import check_strategy
from data_fetcher import fetch_ohlcv, calculate_ema

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_CHAT_ID = int(os.getenv("ALLOWED_CHAT_ID"))

TRACKED_FILE = "tracked_symbols.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_tracked():
    if not os.path.exists(TRACKED_FILE):
        with open(TRACKED_FILE, "w") as f:
            json.dump([], f)
    with open(TRACKED_FILE, "r") as f:
        return json.load(f)

def save_tracked(symbols):
    with open(TRACKED_FILE, "w") as f:
        json.dump(symbols, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    await update.message.reply_text("Привет! Я бот для сигналов по стратегии 2+1. Используй /add, /list и /chart.")

async def add_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    if len(context.args) != 1:
        await update.message.reply_text("Используй: /add SYMBOL (например, /add MOVE/USDT)")
        return
    symbol = context.args[0].upper()
    symbols = load_tracked()
    if symbol in symbols:
        await update.message.reply_text(f"{symbol} уже в списке отслеживаемых.")
        return
    symbols.append(symbol)
    save_tracked(symbols)
    await update.message.reply_text(f"{symbol} добавлен в список отслеживаемых.")

async def list_symbols(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    symbols = load_tracked()
    if not symbols:
        await update.message.reply_text("Список отслеживаемых активов пуст.")
    else:
        await update.message.reply_text("Отслеживаемые активы:\n" + "\n".join(symbols))

async def send_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_CHAT_ID:
        return
    if len(context.args) != 1:
        await update.message.reply_text("Используй: /chart SYMBOL")
        return
    symbol = context.args[0].upper()
    chart_path = generate_chart(symbol)
    if chart_path:
        with open(chart_path, "rb") as f:
            await update.message.reply_photo(photo=f)
    else:
        await update.message.reply_text(f"Не удалось сгенерировать график для {symbol}.")

async def send_signal(chat_id, msg, app):
    await app.bot.send_message(chat_id=chat_id, text=msg)

async def job(app):
    symbols = load_tracked()
    for symbol in symbols:
        try:
            df = fetch_ohlcv(symbol, "1h", limit=200)
            df = calculate_ema(df, [7,14,28])
            if check_strategy(df):
                price = df['close'].iloc[-1]
                msg = f"🔔 [LONG SIGNAL] — {symbol}\nЦена: {price:.4f}\n✅ Цена выше EMA 7/14/28\n✅ Bullish Engulfing\n➕ Поддержка выдержала\n📈 Рекомендуемый вход: {price:.4f}\n⛔ Стоп-лосс: {(price*0.97):.4f}\n🎯 Тейк-профит: {(price*1.07):.4f} / {(price*1.14):.4f}"
                await send_signal(ALLOWED_CHAT_ID, msg, app)
        except Exception as e:
            logger.error(f"Ошибка обработки сигнала для {symbol}: {e}")

def setup_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_symbol))
    app.add_handler(CommandHandler("list", list_symbols))
    app.add_handler(CommandHandler("chart", send_chart))
    return app
