from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone as pytz_timezone
from coingecko import get_crypto_price, search_crypto
from aiogram import Bot


scheduler = AsyncIOScheduler()


async def send_crypto_prices(bot: Bot, user_id: int, cryptos: list):
    print(f"Attempting to send prices for {cryptos} to user {user_id}")
    try:
        messages = []
        for crypto in cryptos:
            results = await search_crypto(crypto)
            if results:
                price = await get_crypto_price(results[0]["id"])
                messages.append(
                    f"{results[0]['name']} ({results[0]['symbol']}): ${price:.2f}"
                )
            else:
                messages.append(f"Криптовалюта {crypto} не найдена.")

        await bot.send_message(chat_id=user_id, text="\n".join(messages))
        print(f"Prices sent successfully for {cryptos}")
    except Exception as e:
        print(f"Unexpected error in send_crypto_prices: {e}")
        await bot.send_message(
            chat_id=user_id,
            text="Произошла ошибка при получении курсов криптовалют. Пожалуйста, попробуйте позже.",
        )


def schedule_job(bot: Bot, user_id, cryptos, hour, minute, user_timezone):
    job_id = f"{user_id}_crypto_alert"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    try:
        tz = pytz_timezone(user_timezone)
        scheduler.add_job(
            send_crypto_prices,
            "cron",
            args=[bot, user_id, cryptos],
            hour=hour,
            minute=minute,
            id=job_id,
            timezone=tz,
        )
        print(
            f"Job scheduled: {job_id} at {hour}:{minute} in timezone {user_timezone} for cryptos {cryptos}"
        )
    except Exception as e:
        print(f"Error scheduling job: {e}")


def remove_user_jobs(user_id):
    for job in scheduler.get_jobs():
        if job.id.startswith(f"{user_id}_"):
            scheduler.remove_job(job.id)
