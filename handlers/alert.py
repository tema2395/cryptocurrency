import pytz
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from coingecko import search_crypto
from database.crud import create_notification, get_notification, update_notification
from database.database import SessionLocal
from database import schemas
from datetime import datetime, timedelta
from keyboards.for_alerts import get_alert_settings_kb
from keyboards.main_buttons import get_back_kb, get_location_kb
from states import CryptoStates
from scheduler import schedule_job, remove_user_jobs
from timezonefinder import TimezoneFinder


router = Router()


@router.callback_query(F.data == "settings")
async def settings(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    db = SessionLocal()
    notification = get_notification(db, user_id)
    db.close()

    text = f"Здесь вы можете настроить оповещения от бота.\n\nЕсли оповещения <b>выключены</b>:<blockquote>бот <b>НЕ</b> будет уведомлять вас о курсе монет</blockquote>\n\nПри <b>активации</b> данной функции:<blockquote>-Выбор интересующей вас криптовалюты\n-Выбор времени, в которое бот будет отправлять вам акутальный курс, выбранных коинов.</blockquote>\n\n"
    if notification and notification.notifications_are_active:
        text += "Оповещения включены. Вы можете настроить их или выключить."
    else:
        text += "Оповещения выключены. Вы можете включить их для получения уведомлений о курсах криптовалют."

    await callback.message.edit_text(
        text=text,
        reply_markup=get_alert_settings_kb(
            notification and notification.notifications_are_active
        ),
    )


@router.message(Command("settings"))
async def settings(message: types.Message):
    await message.delete()
    user_id = message.from_user.id
    db = SessionLocal()
    notification = get_notification(db, user_id)
    db.close()

    text = f"Здесь вы можете настроить оповещения от бота.\n\n"
    if notification and notification.notifications_are_active:
        text += "Оповещения включены. Вы можете настроить их или выключить."
    else:
        text += "Оповещения выключены. Вы можете включить их для получения уведомлений о курсах криптовалют."

    await message.edit_text(
        text=text,
        reply_markup=get_alert_settings_kb(
            notification and notification.notifications_are_active
        ),
    )


@router.callback_query(F.data == "enable_alerts")
async def enable_alerts(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    db = SessionLocal()
    notification = get_notification(db, user_id)
    if notification:
        update_notification(
            db, user_id, schemas.NotificationUpdate(notifications_are_active=True)
        )
    else:
        create_notification(
            db, schemas.NotificationCreate(id=user_id, notifications_are_active=True)
        )
    db.close()
    await state.update_data(alerts_enabled=True)
    await callback.answer("Оповещения включены")
    await callback.message.edit_text(
        "Оповещения включены. Используйте 'Настройки оповещений' для выбора криптовалюты и установки времени",
        reply_markup=get_alert_settings_kb(
            notification and notification.notifications_are_active
        ),
    )


@router.callback_query(F.data == "disable_alerts")
async def disable_alerts(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    db = SessionLocal()
    notification = get_notification(db, user_id)
    if notification:
        update_notification(
            db, user_id, schemas.NotificationUpdate(notifications_are_active=False)
        )
    db.close()
    await state.update_data(alerts_enabled=False)
    remove_user_jobs(user_id)
    await callback.answer("Оповещения выключены")
    await callback.message.edit_text(
        "Оповещения выключены. Вы можете включить их снова в любое время.",
        reply_markup=get_alert_settings_kb(
            notification and notification.notifications_are_active
        ),
    )


@router.callback_query(F.data == "set_alerts")
async def set_alerts(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    db = SessionLocal()
    notification = get_notification(db, user_id)
    db.close()

    if notification and notification.notifications_are_active:
        await callback.message.edit_text(
            text="Для определения вашего часового пояса, пожалуйста, отправьте свое местоположение."
        )
        await callback.message.answer(
            text="Отправьте свое местоположение:",
            reply_markup=get_location_kb(),
        )
        await state.set_state(CryptoStates.waiting_for_location)
    else:
        await callback.answer("Сначала включите оповещения")
        await callback.message.edit_text(
            "Для настройки оповещений сначала необходимо их включить.",
            reply_markup=get_alert_settings_kb(
                notification and notification.notifications_are_active
            ),
        )


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
        user_id = message.from_user.id
        db = SessionLocal()
        notification = get_notification(db, user_id)
        if notification:
            update_notification(
                db, user_id, schemas.NotificationUpdate(timezone=timezone_str)
            )
        else:
            create_notification(
                db,
                schemas.NotificationCreate(
                    id=user_id, notifications_are_active=True, timezone=timezone_str
                ),
            )
        db.close()
        await message.answer(
            f"Ваш часовой пояс определен как {timezone_str}. Текущее время:{current_time.strftime('%H:%M')}",
            reply_markup=ReplyKeyboardRemove(),
        )
        await message.answer(
            "Теперь введите криптовалюту через пробел, по которой хотите получать курс:"
        )
        await state.set_state(CryptoStates.waiting_for_crypto_alert)
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
        await message.answer("Теперь введите название криптовалюты через пробел:")
        await state.set_state(CryptoStates.waiting_for_crypto)
    except pytz.exceptions.UnknownTimeZoneError:
        await message.answer(
            "Неизвестный часовой пояс. Пожалуйста, попробуйте еще раз."
        )


@router.message(CryptoStates.waiting_for_crypto_alert)
async def handle_process_crypto(message: types.Message, state: FSMContext):
    queries = message.text.strip().lower().split()
    all_results = []
    not_found = []

    for query in queries:
        results = await search_crypto(query)
        if results:
            all_results.extend(results[:3])
        else:
            not_found.append(query)

    if not all_results:
        await message.answer(
            "Ни одна из указанных криптовалют не найдена. Попробуйте еще раз."
        )
        return

    all_results = list({v["id"]: v for v in all_results}.values())

    keyboard = InlineKeyboardBuilder()
    for coin in all_results:
        keyboard.button(
            text=f"{coin['name']} ({coin['symbol'].upper()})",
            callback_data=f"select_crypto:{coin['id']}",
        )
    keyboard.adjust(2)
    keyboard.row(
        types.InlineKeyboardButton(
            text="Подтвердить выбор", callback_data="confirm_crypto_selection"
        )
    )

    await state.update_data(available_cryptos=all_results)
    await message.answer(
        "Выберите криптовалюты из списка (можно выбрать несколько):",
        reply_markup=keyboard.as_markup(),
    )

    if not_found:
        await message.answer(f"Не найдены: {', '.join(not_found)}")


@router.callback_query(F.data.startswith("select_crypto:"))
async def select_crypto(callback: types.CallbackQuery, state: FSMContext):
    crypto_id = callback.data.split(":")[1]
    user_data = await state.get_data()
    selected_cryptos = user_data.get("selected_cryptos", [])

    if crypto_id in selected_cryptos:
        selected_cryptos.remove(crypto_id)
    else:
        selected_cryptos.append(crypto_id)

    await state.update_data(selected_cryptos=selected_cryptos)

    keyboard = InlineKeyboardBuilder()
    for coin in user_data["available_cryptos"]:
        mark = "✅ " if coin["id"] in selected_cryptos else ""
        keyboard.button(
            text=f"{mark}{coin['name']} ({coin['symbol']})",
            callback_data=f"select_crypto:{coin['id']}",
        )
    keyboard.adjust(2)
    keyboard.button(text="Подтвердить выбор", callback_data="confirm_crypto_selection")

    await callback.message.edit_reply_markup(reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "confirm_crypto_selection")
async def confirm_crypto_selection(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    selected_cryptos = user_data.get("selected_cryptos", [])

    if not selected_cryptos:
        await callback.answer("Выберите хотя бы одну криптовалюту", show_alert=True)
        return

    selected_names = [
        coin["name"]
        for coin in user_data["available_cryptos"]
        if coin["id"] in selected_cryptos
    ]
    await callback.message.edit_text(
        f"Вы выбрали: {', '.join(selected_names)}\nТеперь введите время для оповещений в формате ЧЧ:ММ:"
    )

    await state.set_state(CryptoStates.waiting_for_time)


@router.message(CryptoStates.waiting_for_time)
async def process_time(message: types.Message, state: FSMContext):
    await message.delete()
    try:
        time_str = message.text.strip()
        hour, minute = map(int, time_str.split(":"))
        user_data = await state.get_data()
        user_id = message.from_user.id
        selected_cryptos = user_data.get("selected_cryptos", [])

        db = SessionLocal()
        notification_data = {
            "selected_time": int(f"{hour:02d}{minute:02d}"),
            "selected_crypto": ",".join(selected_cryptos),
        }

        existing_notification = get_notification(db, user_id)
        if existing_notification:
            update_notification(
                db, user_id, schemas.NotificationUpdate(**notification_data)
            )
        else:
            create_notification(
                db, schemas.NotificationCreate(id=user_id, **notification_data)
            )
        db.close()

        schedule_job(
            message.bot,
            user_id,
            selected_cryptos,
            hour,
            minute,
            user_data["user_timezone"],
        )

        selected_names = [
            coin["name"]
            for coin in user_data["available_cryptos"]
            if coin["id"] in selected_cryptos
        ]
        await message.answer(
            f"Оповещения установлены:\nКриптовалюты: {', '.join(selected_names)}\nВремя: {hour:02d}:{minute:02d}\nЧасовой пояс: {user_data['user_timezone']}",
            reply_markup=get_back_kb(),
        )
        await state.clear()
    except ValueError:
        await message.answer(
            "Неправильный формат времени. Попробуйте снова в формате ЧЧ:ММ"
        )
