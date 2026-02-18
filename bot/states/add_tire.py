from aiogram.fsm.state import State, StatesGroup

class AddTireStates(StatesGroup):
    adding_diameter = State()   # ввод диаметра диска (R)
    adding_width = State()      # ввод ширины шины
    adding_profile = State()    # ввод высоты профиля
    adding_quantity = State()   # ввод количества шин