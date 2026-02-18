import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(app_name='sharahbot', log_file='app.log', level=logging.INFO):
    """
    Configure logging for the application.
    Sets up both console and file handlers with rotation.
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation (10 MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger