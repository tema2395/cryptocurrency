from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from keyboards.for_alerts import get_alert_settings_kb
from states import CryptoStates
from sheduler import shedule_job

router = Router()


@router.callback_query(F.data == "settings")
async def settings(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        text=f"Здесь вы можете настроить оповещения от бота.\n\nЕсли оповещения <b>выключены</b>:<blockquote>бот <b>НЕ</b> будет уведомлять вас о курсе монет</blockquote>\n\nПри <b>активации</b> данной функции:<blockquote>-Выбор интересующей вас криптовалюты\n-Выбор времени, в которое бот будет отправлять вам акутальный курс, выбранных коинов.</blockquote>",
        reply_markup=get_alert_settings_kb(),
    )


@router.callback_query(F.data == "toggle_alerts")
async def toggle_alerts(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    alerts_enabled = user_data.get("alerts_enabled", False)
    user_data["alerts_enabled"] = not alerts_enabled
    await state.update_data(user_data)
    status = "включены" if user_data["alerts_enabled"] else "выключены"
    await callback.message.answer(f"Оповещения {status}.")


@router.callback_query(F.data == "set_alerts")
async def set_alerts(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "Введите название криптовалюты и время через запятую например: (bitcoin, 08:00):"
    )
    await state.set_state(CryptoStates.waiting_for_time)


@router.message(CryptoStates.waiting_for_time)
async def process_alert_time(message: types.Message, state: FSMContext):
    bot = message.bot
    try:
        crypto, user_time = message.text.split(",")
        crypto = crypto.strip().lower()
        hour, minute = map(int, user_time.strip().split(":"))
        await state.update_data(crypto=crypto, time=user_time)
        user_id = message.from_user.id
        shedule_job(bot, user_id, crypto, hour, minute)
        await message.answer(f"Оповещения для {crypto} установлены на{user_time}.")
        await state.clear()
    except ValueError:
        await message.answer(
            "Неправильный формат. Попробуйте снова. Введите в формате: bitcoin, 08:00"
        )
