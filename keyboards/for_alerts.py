from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_alert_settings_kb(notifications_active: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if not notifications_active:
        builder.add(
            types.InlineKeyboardButton(text="Включить🔔", callback_data="enable_alerts")
        )
    else:
        builder.add(
            types.InlineKeyboardButton(
                text="Выключить🔕", callback_data="disable_alerts"
            ),
            types.InlineKeyboardButton(
                text="Настройка оповещений⚙️", callback_data="set_alerts"
            ),
        )
    builder.row(types.InlineKeyboardButton(text="Назад🔙", callback_data="back_menu"))
    return builder.as_markup()
