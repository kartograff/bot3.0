from flask import Blueprint
from .stats import api_stats_bp
from .notifications import api_notifications_bp

api_bp = Blueprint('api', __name__, url_prefix='/api')
api_bp.register_blueprint(api_stats_bp)
api_bp.register_blueprint(api_notifications_bp)