from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_settings_crypto_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Криптовалюта", callback_data="crypto_kb"),
        types.InlineKeyboardButton(text="Настройки", callback_data="settings"),
    )
    return builder.as_markup()
