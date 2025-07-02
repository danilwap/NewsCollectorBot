from aiogram.fsm.state import StatesGroup, State

class AddChannel(StatesGroup):
    waiting_for_channel = State()
