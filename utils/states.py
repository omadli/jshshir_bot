from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    date = State()
    filter = State()
    