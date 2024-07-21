from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_crypto_kb(cryptos: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for crypto in cryptos:
        builder.add(types.InlineKeyboardButton(text=crypto.capitalize(), callback_data=f"crypto_{crypto}"))
    builder.add(types.InlineKeyboardButton(text="Другое", callback_data="other_crypto"))
    return builder.as_markup()
