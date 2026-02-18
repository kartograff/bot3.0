import logging
from datetime import datetime
from flask import Flask, render_template
from config import Config

logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """
    Application factory for Flask app.
    Creates and configures the Flask instance.
    """
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Load configuration
    app.config.from_object(config_class)
    app.secret_key = config_class.FLASK_SECRET_KEY

    # Register blueprints
    from web.routes.main import main_bp
    from web.routes.appointments import appointments_bp
    from web.routes.users import users_bp
    from web.routes.services import services_bp
    from web.routes.schedule import schedule_bp
    from web.routes.dictionaries import dict_bp
    from web.routes.channels import channels_bp
    from web.routes.backups import backups_bp
    from web.routes.logs import logs_bp
    from web.routes.api import api_bp
    from web.routes.settings import settings_bp
    
    app.register_blueprint(settings_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(dict_bp, url_prefix='/admin/dict')
    app.register_blueprint(channels_bp, url_prefix='/admin')
    app.register_blueprint(backups_bp, url_prefix='/admin')
    app.register_blueprint(logs_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Context processors
    @app.context_processor
    def inject_globals():
        """Inject global variables into all templates."""
        from database.crud.settings import get_setting
        return {
            'shop_name': get_setting('shop_name') or 'SharahBot',
            'current_year': datetime.now().year
        }

    # Template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%d.%m.%Y %H:%M'):
        """Format a datetime object."""
        if value is None:
            return ''
        return value.strftime(format)

    @app.template_filter('markdown')
    def markdown_filter(text):
        """Render Markdown text as HTML."""
        import markdown
        return markdown.markdown(text, extensions=['nl2br', 'extra'])

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Render custom 404 page."""
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Render custom 500 page and log error."""
        logger.error(f"Internal server error: {error}")
        return render_template('errors/500.html'), 500

    return app

# Create the Flask application instance
app = create_app()