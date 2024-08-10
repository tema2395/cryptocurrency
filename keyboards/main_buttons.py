from aiogram import types
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_back_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="Назад🔙", callback_data="settings"),
    )
    return builder.as_markup()

def get_location_kb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить местоположение", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard