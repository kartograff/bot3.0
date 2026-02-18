from aiogram.fsm.state import State, StatesGroup

class BookingStates(StatesGroup):
    choosing_vehicle_type = State()  # выбор типа ТС
    choosing_service = State()       # выбор услуги
    choosing_car = State()           # выбор автомобиля
    choosing_tire = State()          # выбор размера шин
    choosing_date = State()          # выбор даты
    choosing_time = State()          # выбор времени
    confirmation = State()           # подтверждение записи