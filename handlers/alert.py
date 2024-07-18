"""Все что связано с оповещениями включая настройки"""

from aiogram import F, Router, types

router = Router()


@router.callback_query(F.data == "settings")
async def settings(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        text=f"Здесь вы можете настроить оповещения от бота.\n\nЕсли оповещения <b>выключены</b>:<blockquote>бот <b>НЕ</b> будет уведомлять вас о курсе монет</blockquote>\n\nПри <b>активации</b> данной функции:<blockquote>-Выбор интересующей вас криптовалюты\n-Выбор времени, в которое бот будет отправлять вам акутальный курс, выбранных коинов.</blockquote>",
    )
