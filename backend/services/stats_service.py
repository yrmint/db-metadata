from backend.core.db import get_connection
from backend.models.stats_model import TableCount

def get_table_count_by_db(db_id: int) -> TableCount:
    """
    Returns number of tables in database with provided db_id.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT COUNT(*) AS table_count
        FROM db_tables
        WHERE db_id = %s;
        """,
        (db_id,)
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    # if no database then table_count = 0
    count = row["table_count"] if row and "table_count" in row else 0
    return TableCount(db_id=db_id, table_count=count)
