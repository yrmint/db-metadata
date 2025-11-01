import mysql.connector
from backend.core import config

def get_connection():
    """Create MySQL connection"""
    return mysql.connector.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE
    )
