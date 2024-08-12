from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from coingecko import get_crypto_price, search_crypto
from states import CryptoStates
from keyboards.for_crypto import get_crypto_kb


router = Router()

popular_cryptos = [
    "bitcoin",
    "ethereum",
    "solana",
    "the-open-network",
]


@router.callback_query(F.data == "crypto_kb")
async def cryptocurrency_selection(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        text="Выберите криптовалюту из списка или нажмите 'Другое', чтобы ввести вручную:",
        reply_markup=get_crypto_kb(popular_cryptos),
    )
    await state.set_state(CryptoStates.waiting_for_crypto)


@router.callback_query(F.data.startswith("crypto_"))
async def selected_crypto(callback: types.CallbackQuery):
    crypto = callback.data.split("_")[1]
    price = await get_crypto_price(crypto)
    await callback.message.answer(f"Текущий курс {crypto}: ${price:.2f}")


@router.callback_query(F.data == "other_crypto")
async def other_crypto(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "Введите название одной или нескольких монет через пробел"
    )
    await state.set_state(CryptoStates.waiting_for_crypto)


@router.message(CryptoStates.waiting_for_crypto)
async def process_other_crypto(message: types.Message, state: FSMContext):
    queries = message.text.strip().lower().split()
    all_results = []
    not_found = []

    for query in queries:
        results = await search_crypto(query)
        if results:
            all_results.append(results[0])
        else:
            not_found.append(query)

    if not all_results:
        await message.answer(
            "Ни одна из указанных криптовалют не найдена. Попробуйте еще раз."
        )
        return

    prices = []
    for coin in all_results:
        price = await get_crypto_price(coin["id"])
        prices.append(f"{coin['name']} ({coin['symbol']}): ${price:.2f}")

    response = "\n".join(prices)
    if not_found:
        response += f"\n\nНе найдены: {', '.join(not_found)}"

    await message.answer(response)
    await state.clear()
