import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot import setup_bot, job

async def main():
    app = setup_bot()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(job(app)), "interval", minutes=30)
    scheduler.start()
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
