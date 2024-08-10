from aiogram.fsm.state import StatesGroup, State


class CryptoStates(StatesGroup):
    waiting_for_location = State()
    waiting_for_manual_timezone = State()
    waiting_for_crypto = State()
    waiting_for_time = State()