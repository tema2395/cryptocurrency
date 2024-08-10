from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from keyboards.for_alerts import get_alert_settings_kb
from states import CryptoStates
from scheduler import schedule_job, remove_user_jobs
from keyboards.main_buttons import get_back_kb, get_location_kb
from database.crud import create_notification
from database.database import SessionLocal
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

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
        text="Для определения вашего часового пояса, пожалуйста, отправьте свое местоположение."
    )
    await callback.message.answer(
        text="Отправьте свое местоположение:",
        reply_markup=get_location_kb(),
    )
    await state.set_state(CryptoStates.waiting_for_location)


@router.message(CryptoStates.waiting_for_location, F.content_type == "location")
async def handle_location(message: types.Message, state: FSMContext):
    tf = TimezoneFinder()
    latitude = message.location.latitude
    longitude = message.location.longitude
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
    if timezone_str:
        timezone = pytz.timezone(timezone_str)
        current_time = datetime.now(timezone)
        await state.update_data(user_timezone=timezone_str)
        await message.answer(
            f"Ваш часовой пояс определен как {timezone_str}. Текущее время:{current_time.strftime('%H:%M')}"
        )
        await message.answer("Теперь введите название криптовалюты:")
        await state.set_state(CryptoStates.waiting_for_crypto)
    else:
        await message.answer(
            "Не удалось определить ваш часовой пояс. Пожалуйста, введите его вручную в формате 'Europe/Moscow'."
        )
        await state.set_state(CryptoStates.waiting_for_manual_timezone)


@router.message(CryptoStates.waiting_for_manual_timezone)
async def handle_manual_timezone(message: types.Message, state: FSMContext):
    try:
        timezone = pytz.timezone(message.text)
        await message.answer(f"Часовой пояс установлен как {message.text}")
        await message.answer("Теперь введите название криптовалюты:")
        await state.set_state(CryptoStates.waiting_for_crypto)
    except pytz.exceptions.UnknownTimeZoneError:
        await message.answer(
            "Неизвестный часовой пояс. Пожалуйста, попробуйте еще раз."
        )


@router.message(CryptoStates.waiting_for_crypto)
async def handle_process_crypto(message: types.Message, state: FSMContext):
    crypto = message.text.strip().lower()
    await state.update_data(crypto=crypto)
    await message.answer("Теперь введите время для оповещений в формате ЧЧ:ММ:")
    await state.set_state(CryptoStates.waiting_for_time)


@router.message(CryptoStates.waiting_for_time)
async def process_time(message: types.Message, state: FSMContext):
    try:
        hour, minute = map(int, message.text.strip().split(":"))
        user_data = await state.get_data()
        user_id = message.from_user.id

        db = SessionLocal()
        notification_data = {
            "id": user_id,
            "notifications_are_active": True,
            "selected_crypto": user_data["crypto"],
            "selected_time": int(f"{hour:02d}{minute:02d}"),
            "timezone": user_data["user_timezone"],
        }

        create_notification(db, notification_data)
        db.close()

        schedule_job(
            message.bot,
            user_id,
            user_data["crypto"],
            hour,
            minute,
            user_data["user_timezone"],
        )

        await message.answer(
            f"Оповещения установлены:\nКриптовалюта: {user_data['crypto']}\nВремя: {hour:02d}:{minute:02d}\nЧасовой пояс: {user_data['user_timezone']}",
            reply_markup=get_back_kb(),
        )
        await state.clear()
    except ValueError:
        await message.answer(
            "Неправильный формат времени. Попробуйте снова в формате ЧЧ:ММ"
        )
