from aiogram import Router, F
from aiogram import Dispatcher, types
from aiogram.filters import Command
from keyboards.for_start import get_settings_crypto_kb

router = Router()


@router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        f"Выберите криптовалюту, чтобы получить <b>актуальный курс</b>\n\nНастройте систему оповещений",
        reply_markup=get_settings_crypto_kb(),
    )


