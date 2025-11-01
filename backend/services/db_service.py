from typing import List
from backend.core.db import get_connection
from backend.models.db_models import DatabaseItem

def get_all_databases() -> List[DatabaseItem]:
    """Returns list of all databases from metadata_catalog.dbs."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT db_id, db_name FROM dbs ORDER BY db_name;")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [DatabaseItem(**row) for row in rows]
