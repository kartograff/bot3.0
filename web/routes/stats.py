from flask import Blueprint, jsonify

api_stats_bp = Blueprint('api_stats', __name__)

@api_stats_bp.route('/stats/appointments')
def appointments_stats():
    """Заглушка для статистики записей."""
    return jsonify([])

@api_stats_bp.route('/stats/services')
def services_stats():
    """Заглушка для статистики услуг."""
    return jsonify([])