from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from coingecko import get_crypto_price
from states import CryptoStates
from keyboards.for_crypto import get_crypto_kb


router = Router()

popular_cryptos = [
    "bitcoin",
    "ethereum",
    "solana",
    "the-open-network",
    "litecoin",
    "aptos",
    "maker",
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
        "Введите название одной или нескольких монет через запятую"
    )
    await state.set_state(CryptoStates.waiting_for_crypto)


@router.message(CryptoStates.waiting_for_crypto)
async def process_other_crypto(message: types.Message, state: FSMContext):
    cryptos = [crypto.strip().lower() for crypto in message.text.split(",")]
    prices = {crypto: await get_crypto_price(crypto) for crypto in cryptos}
    response = "\n.".join(
        [f"{crypto}: ${price:.2f}" for crypto, price in prices.items()]
    )
    await message.answer(response)
    await state.clear()
