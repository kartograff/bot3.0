import logging
import psycopg2
from psycopg2 import pool
from config import Config

logger = logging.getLogger(__name__)

# Connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    database=Config.DB_NAME,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    client_encoding='UTF8'   # <-- добавьте эту строку
)

def init_connection_pool():
    """Initialize the connection pool."""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,  # min and max connections
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        logger.info("Database connection pool created successfully.")
    except Exception as e:
        logger.error(f"Failed to create connection pool: {e}", exc_info=True)
        raise

def get_db_connection():
    """Get a connection from the pool."""
    global connection_pool
    if connection_pool is None:
        init_connection_pool()
    try:
        conn = connection_pool.getconn()
        return conn
    except Exception as e:
        logger.error(f"Error getting connection from pool: {e}", exc_info=True)
        raise

def return_db_connection(conn):
    """Return a connection to the pool."""
    global connection_pool
    if connection_pool:
        try:
            connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error returning connection to pool: {e}", exc_info=True)

def close_all_connections():
    """Close all connections in the pool."""
    global connection_pool
    if connection_pool:
        try:
            connection_pool.closeall()
            logger.info("All database connections closed.")
        except Exception as e:
            logger.error(f"Error closing connections: {e}", exc_info=True)