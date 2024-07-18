"""Все что связано с криптовалютой"""

from aiogram import F, Router, types


router = Router()


@router.callback_query(F.data == "crypto_kb")
async def cryptocurrency_selection(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        text="Выберите криптовалюту, чтобы посмотреть актуальный курс",
    )
