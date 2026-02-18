# This file makes the routes directory a Python package.# This file makes the api directory a Python package.
from .stats import api_stats_bp
from .notifications import api_notifications_bp

__all__ = ['api_stats_bp', 'api_notifications_bp']