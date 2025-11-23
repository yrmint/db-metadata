import mysql.connector
from backend.core import mysql_config

def get_connection(database: str = "metadata_catalog"):
    """Create MySQL connection"""
    return mysql.connector.connect(
        host=mysql_config.MYSQL_HOST,
        user=mysql_config.MYSQL_USER,
        password=mysql_config.MYSQL_PASSWORD,
        database=database
    )
