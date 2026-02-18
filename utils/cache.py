from cachetools import TTLCache

# Кеш с максимальным размером 1000 элементов и временем жизни 300 секунд (5 минут)
_cache = TTLCache(maxsize=1000, ttl=300)

def get_cache(key):
    """Получить значение из кеша по ключу."""
    return _cache.get(key)

def set_cache(key, value):
    """Установить значение в кеш."""
    _cache[key] = value

def delete_cache(key):
    """Удалить значение из кеша, если оно существует."""
    if key in _cache:
        del _cache[key]

def get_user_registration_status(user_id: int) -> bool:
    """
    Проверяет, зарегистрирован ли пользователь, с кешированием на 5 минут.
    Если в кеше нет, запрашивает из БД и сохраняет.
    """
    from database.crud.users import is_user_registered
    cache_key = f'user_registered_{user_id}'
    cached = get_cache(cache_key)
    if cached is not None:
        return cached
    status = is_user_registered(user_id)
    set_cache(cache_key, status)
    return status