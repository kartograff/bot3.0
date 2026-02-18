from flask import Blueprint, render_template, request, jsonify, abort
from database.crud.users import get_users, get_user, update_user, delete_user
from database.crud.user_cars import get_user_cars
import logging
import math

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__)

@users_bp.route('/users')
def users_list():
    """
    Отображает список пользователей с пагинацией и поиском.
    Query params:
      - page: int, default 1
      - per_page: int, default 20 (1..100)
      - search: str, default ""
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = (request.args.get('search') or '').strip()

        # Валидация и ограничение значений
        page = max(1, page)
        per_page = min(max(1, per_page), 100)

        users, total = get_users(page=page, per_page=per_page, search=search)
        
        total_pages = math.ceil(total / per_page) if per_page > 0 else 0

    except Exception:
        logger.exception("Ошибка при получении списка пользователей")
        users, total, page, per_page, total_pages, search = [], 0, 1, 20, 0, ''
        # Можно показать страницу с ошибкой, но пока просто пустой список
    
    return render_template(
        'users.html',
        users=users,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        search=search
    )


@users_bp.route('/users/<int:user_id>')
def user_detail(user_id: int):
    """
    Детальная информация о пользователе и его автомобилях.
    """
    try:
        user = get_user(user_id)
    except Exception:
        logger.exception("Ошибка при получении пользователя %s", user_id)
        abort(500) # Внутренняя ошибка сервера

    if not user:
        abort(404) # Пользователь не найден

    try:
        cars = get_user_cars(user_id)
    except Exception:
        logger.exception("Ошибка при получении автомобилей пользователя %s", user_id)
        cars = []

    return render_template('user_detail.html', user=user, cars=cars)


@users_bp.route('/users/<int:user_id>/note', methods=['POST'])
def update_user_note(user_id: int):
    """
    Обновляет заметку (notes) о пользователе.
    Ожидает JSON: {"notes": "текст"} или {"note": "текст"}.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON'}), 400

    # Принимаем оба ключа, предпочитаем "notes"
    note = data.get('notes', data.get('note'))

    if note is None or not isinstance(note, str):
        return jsonify({'success': False, 'error': 'Key "notes" must be a string'}), 400

    try:
        updated_user = update_user(user_id, {'notes': note})
        if not updated_user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        return jsonify({'success': True})
    except Exception as e:
        logger.exception("Ошибка при обновлении заметки пользователя %s", user_id)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@users_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user_route(user_id: int):
    """
    Удаляет пользователя.
    """
    try:
        result = delete_user(user_id)
        if not result:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        return jsonify({'success': True})
    except Exception as e:
        logger.exception("Ошибка при удалении пользователя %s", user_id)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500