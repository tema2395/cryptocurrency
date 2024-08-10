from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone as pytz_timezone
from coingecko import get_crypto_price
from aiogram import Bot


scheduler = AsyncIOScheduler()


async def send_crypto_price(bot: Bot, user_id: int, crypto: str):
    print(f"Attempting to send price for {crypto} to user {user_id}")
    try:
        price = await get_crypto_price(crypto)
        await bot.send_message(
            chat_id=user_id, text=f"Текущий курс {crypto}: ${price:.2f}"
        )
        print(f"Price sent successfully: {crypto} - ${price:.2f}")
    except KeyError:
        error_message = f"Не удалось получить курс для {crypto}. Пожалуйста, проверьте правильность написания."
        await bot.send_message(chat_id=user_id, text=error_message)
        print(f"Error sending price: {error_message}")
    except Exception as e:
        print(f"Unexpected error in send_crypto_price: {e}")


def schedule_job(bot: Bot, user_id, crypto, hour, minute, user_timezone):
    job_id = f"{user_id}_{crypto}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    try:
        tz = pytz_timezone(user_timezone)
        scheduler.add_job(
            send_crypto_price,
            "cron",
            args=[bot, user_id, crypto],
            hour=hour,
            minute=minute,
            id=job_id,
            timezone=tz
        )
        print(f"Job scheduled: {job_id} in timezone {user_timezone}")
    except Exception as e:
        print(f"Error scheduling job: {e}")


def remove_user_jobs(user_id):
    for job in scheduler.get_jobs():
        if job.id.startswith(f"{user_id}_"):
            scheduler.remove_job(job.id)
