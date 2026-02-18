from aiogram.fsm.state import State, StatesGroup

class AddCarStates(StatesGroup):
    choosing_vehicle_type = State()  # выбор типа ТС
    choosing_letter = State()        # выбор первой буквы марки
    choosing_brand = State()         # выбор марки
    choosing_model = State()         # выбор модели
    choosing_year = State()          # выбор года
    choosing_tire_action = State()   # выбор: существующий размер или новый
    choosing_existing_tire = State() # выбор из существующих размеров