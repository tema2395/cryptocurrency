from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from keyboards.for_alerts import get_alert_settings_kb
from states import CryptoStates
from sheduler import shedule_job, remove_user_jobs

router = Router()


@router.callback_query(F.data == "settings")
async def settings(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        text=f"Здесь вы можете настроить оповещения от бота.\n\nЕсли оповещения <b>выключены</b>:<blockquote>бот <b>НЕ</b> будет уведомлять вас о курсе монет</blockquote>\n\nПри <b>активации</b> данной функции:<blockquote>-Выбор интересующей вас криптовалюты\n-Выбор времени, в которое бот будет отправлять вам акутальный курс, выбранных коинов.</blockquote>",
        reply_markup=get_alert_settings_kb(),
    )


@router.callback_query(F.data == "enable_alerts")
async def enable_alerts(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(alerts_enabled=True)
    await callback.answer("Оповещения включены")
    await callback.message.edit_text(
        "Оповещения включены. Используйте 'Настройки оповещений' для выбора криптовалюты и установки времени",
        reply_markup=get_alert_settings_kb(),
    )


@router.callback_query(F.data == "disable_alerts")
async def disable_alerts(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await state.update_data(alerts_enabled=False)
    remove_user_jobs(user_id)
    await callback.answer("Оповещения выключены")
    await callback.message.edit_text(
        "Оповещения выключены. Вы можете включить их снова в любое время.",
        reply_markup=get_alert_settings_kb(),
    )


@router.callback_query(F.data == "set_alerts")
async def set_alerts(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    if not user_data.get("alerts_enabled", False):
        await callback.answer("Сначала включите оповещения")
        return
    await callback.message.edit_text(
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

        user_data = await state.get_data()
        if user_data.get("alerts_enabled", False):
            shedule_job(bot, user_id, crypto, hour, minute)
            await message.answer(f"Оповещения для {crypto} установлены на {user_time}.")
        else:
            await message.answer("Оповещения выключены. Включите их в настройках.")

        await state.clear()
    except ValueError:
        await message.answer(
            "Неправильный формат. Попробуйте снова. Введите в формате: bitcoin, 08:00"
        )
