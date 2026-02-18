SharahBot/
├── .venv/                          # Виртуальное окружение
├── .env                             # Переменные окружения (токены, ключи)
├── .env.example                      # Пример .env
├── .gitignore
├── requirements.txt                  # Зависимости Python
├── README.md
├── start.py                          # Точка входа (запуск бота и веб-сервера)
├── config.py                         # Общая конфигурация (загрузка из .env)
│
├── bot/                              # Telegram-бот (aiogram)
│   ├── __init__.py
│   ├── bot.py                         # Инициализация bot и dispatcher
│   ├── middlewares/                    # Middleware
│   │   ├── __init__.py
│   │   ├── logging.py                   # Логирование действий
│   │   ├── auth.py                       # Проверка прав доступа
│   │   └── throttling.py                 # Анти-флуд
│   ├── handlers/                        # Хендлеры (по функциональности)
│   │   ├── __init__.py
│   │   ├── common.py                      # /start, /help
│   │   ├── registration.py                 # Регистрация (контакт)
│   │   ├── main_menu.py                    # Главное меню
│   │   ├── my_cars.py                      # Управление автомобилями (CRUD)
│   │   ├── booking.py                      # Запись на услуги
│   │   ├── my_appointments.py               # Просмотр записей
│   │   ├── about.py                         # Информация "О нас"
│   │   └── admin/                           # Админские команды
│   │       ├── __init__.py
│   │       ├── broadcast.py
│   │       └── statistics.py
│   ├── keyboards/                       # Клавиатуры (inline/reply)
│   │   ├── __init__.py
│   │   ├── main_menu.py
│   │   ├── cars.py                         # Выбор марок, моделей и т.д.
│   │   ├── booking.py
│   │   └── common.py                        # Кнопки "Назад", отмена
│   ├── states/                           # FSM состояния
│   │   ├── __init__.py
│   │   ├── registration.py
│   │   ├── add_car.py
│   │   ├── add_tire.py
│   │   └── booking.py
│   └── utils/                            # Утилиты для бота
│       ├── __init__.py
│       ├── validators.py                   # Валидация телефона, года и т.п.
│       └── formatters.py                    # Форматирование сообщений
│
├── web/                               # Веб-интерфейс (Flask 3.0)
│   ├── __init__.py
│   ├── app.py                           # Создание Flask-приложения
│   ├── routes/                           # Маршруты (blueprints)
│   │   ├── __init__.py
│   │   ├── main.py                         # Главная страница
│   │   ├── appointments.py                  # Управление записями
│   │   ├── users.py                         # Пользователи
│   │   ├── services.py                      # Услуги
│   │   ├── schedule.py                      # Календарь
│   │   ├── dictionaries.py                   # Справочники (марки, модели, шины)
│   │   ├── channels.py                      # Управление Telegram-каналами
│   │   ├── backups.py                       # Бекапы
│   │   ├── logs.py                          # Просмотр логов
│   │   └── api/                             # API для AJAX
│   │       ├── __init__.py
│   │       ├── stats.py
│   │       └── notifications.py
│   ├── templates/                        # HTML-шаблоны (Jinja2)
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── appointments.html
│   │   ├── users.html
│   │   ├── services.html
│   │   ├── schedule.html
│   │   ├── dictionaries/                    # Шаблоны справочников
│   │   │   ├── brands.html
│   │   │   ├── models.html
│   │   │   ├── vehicle_types.html
│   │   │   └── tire_sizes.html
│   │   ├── admin/                            # Админ-панель
│   │   │   ├── channels.html
│   │   │   ├── backups.html
│   │   │   └── logs.html
│   │   └── macros/                           # Макросы
│   │       └── forms.html
│   ├── static/                           # Статические файлы (CSS, JS, img)
│   │   ├── css/
│   │   │   ├── notion.css
│   │   │   └── components.css
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   ├── calendar.js
│   │   │   ├── statistics.js
│   │   │   └── dictionaries.js
│   │   └── img/
│   └── utils/                            # Утилиты для веба
│       ├── __init__.py
│       ├── decorators.py                    # Декораторы (admin_required)
│       ├── filters.py                        # Пользовательские фильтры Jinja2
│       └── context_processors.py             # Процессоры контекста
│
├── database/                           # Работа с PostgreSQL
│   ├── __init__.py
│   ├── connection.py                      # Подключение к БД (пул)
│   ├── models/                             # Описание таблиц (если используем ORM)
│   │   └── __init__.py
│   ├── crud/                               # Функции для работы с таблицами
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── appointments.py
│   │   ├── services.py
│   │   ├── settings.py
│   │   ├── logs.py
│   │   ├── error_logs.py
│   │   ├── backups.py
│   │   ├── channels.py
│   │   ├── car_brands.py
│   │   ├── car_models.py
│   │   ├── car_years.py
│   │   ├── tire_sizes.py
│   │   ├── user_cars.py
│   │   ├── user_car_tires.py
│   │   ├── vehicle_types.py
│   │   ├── reviews.py
│   │   ├── images.py
│   │   ├── pages.py
│   │   └── silenced_notifications.py
│   └── migrations/                         # SQL-миграции (версионирование)
│       ├── v1_initial.sql
│       ├── v2_add_user_fields.sql
│       ├── v3_admin_status.sql
│       ├── v4_reviews_and_settings.sql
│       ├── v5_add_about_info.sql
│       ├── v6_add_images.sql
│       ├── v7_cms_pages.sql
│       ├── v8_telegram_channels.sql
│       ├── v9_backups.sql
│       ├── v10_error_logs.sql
│       ├── v11_auto_catalog.sql
│       ├── v12_cleanup_unused_tables.sql
│       ├── v13_silent_hours.sql
│       ├── v14_delayed_notifications.sql
│       └── v15_add_vehicle_type_to_models.sql
│
├── services/                           # Внешние сервисы и фоновые задачи
│   ├── __init__.py
│   ├── openrouter_client.py               # Клиент для OpenRouter API
│   ├── channel_publisher.py                # Публикация в Telegram-каналы
│   ├── notifications.py                    # Отправка уведомлений (с учётом тихих часов)
│   ├── delayed_notifications.py            # Обработчик отложенных уведомлений
│   ├── silent_hours.py                     # Логика тихих часов
│   └── scheduler.py                        # Планировщик (APScheduler)
│
├── utils/                              # Общие утилиты
│   ├── __init__.py
│   ├── logger.py                          # Настройка логирования
│   ├── cache.py                           # Кеширование (TTLCache)
│   ├── backup.py                          # Резервное копирование
│   └── validators.py                      # Общие валидаторы
│
└── tests/                              # Тесты
    ├── __init__.py
    ├── conftest.py
    ├── test_bot/
    ├── test_web/
    └── test_database/