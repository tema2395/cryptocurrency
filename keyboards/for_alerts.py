from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_alert_settings_kb():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Вкл/выкл", callback_data="toggle_alerts"),
        types.InlineKeyboardButton(text="Настройка оповещений", callback_data="set_alerts"),
    )
    return builder.as_markup()