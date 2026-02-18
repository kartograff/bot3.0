# web/routes/api/stats.py
from flask import Blueprint, jsonify, request

api_stats_bp = Blueprint('api_stats', __name__)

@api_stats_bp.route('/appointments/dates')
def appointments_dates():
    """
    Возвращает список дат, на которые есть записи (для подсветки в календаре).
    Пока заглушка, возвращаем пустой список.
    """
    # Здесь можно будет позже сделать реальный запрос к БД
    # Например, получить все даты из таблицы appointments
    return jsonify([])

@api_stats_bp.route('/stats/appointments')
def appointments_stats():
    """
    Возвращает статистику по записям за последние N дней.
    Пока заглушка.
    """
    days = request.args.get('days', 30, type=int)
    # Здесь можно будет сделать запрос к БД
    return jsonify([])

@api_stats_bp.route('/stats/services')
def services_stats():
    """
    Возвращает статистику по услугам (популярность).
    Пока заглушка.
    """
    return jsonify([])