from flask import Blueprint, jsonify

api_notifications_bp = Blueprint('api_notifications', __name__)

@api_notifications_bp.route('/check-notification-time')
def check_notification_time():
    return jsonify({'silent_hours_now': False})

@api_notifications_bp.route('/silenced-notifications/<int:notification_id>/send', methods=['POST'])
def send_silenced_notification(notification_id):
    return jsonify({'success': True})