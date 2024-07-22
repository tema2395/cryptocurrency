from apscheduler.schedulers.asyncio import AsyncIOScheduler
from coingecko import get_crypto_price
from aiogram import Bot


sheduler = AsyncIOScheduler()


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


def shedule_job(bot: Bot, user_id, crypto, hour, minute):
    job_id = f"{user_id}_{crypto}"

    if sheduler.get_job(job_id):
        sheduler.remove_job(job_id)

    try:
        sheduler.add_job(
            send_crypto_price,
            "cron",
            args=[bot, user_id, crypto],
            hour=hour,
            minute=minute,
            id=job_id,
        )
        print(f"Job scheduled: {job_id}")
    except Exception as e:
        print(f"Error scheduling job: {e}")


def remove_user_jobs(user_id):
    for job in sheduler.get_jobs():
        if job.id.startswith(f"{user_id}_"):
            sheduler.remove_job(job.id)
