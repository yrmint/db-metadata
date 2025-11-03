from backend.core.db import get_connection
from backend.models.stats_model import StatCount

def get_table_count_by_db(db_id: int) -> StatCount:
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
    return StatCount(db_id=db_id, count=count)

def get_column_count_by_db(db_id: int):
    """
    Returns the number of columns in database with provided db_id.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT COUNT(*) AS column_count
        FROM db_columns
        JOIN db_tables ON db_columns.table_id = db_tables.table_id
        WHERE db_tables.db_id = %s;
        """,
        (db_id,)
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    count = row["column_count"] if row and "column_count" in row else 0
    return StatCount(db_id=db_id, count=count)

def get_primary_key_count_by_db(db_id: int):
    """
    Returns the number of primary keys (constraints) in database with provided db_id.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT COUNT(*) AS key_count
        FROM constraints
        JOIN db_tables ON constraints.table_id = db_tables.table_id
        WHERE constraints.type = "PRIMARY" AND db_tables.db_id = %s;
        """,
        (db_id,)
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    count = row["key_count"] if row and "key_count" in row else 0
    return StatCount(db_id=db_id, count=count)

def get_foreign_key_count_by_db(db_id: int):
    """
    Returns the number of foreign keys (constraints) in database with provided db_id.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT COUNT(*) AS key_count
        FROM constraints
        JOIN db_tables ON constraints.table_id = db_tables.table_id
        WHERE constraints.type = "FOREIGN" AND db_tables.db_id = %s;
        """,
        (db_id,)
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    count = row["key_count"] if row and "key_count" in row else 0
    return StatCount(db_id=db_id, count=count)

def get_unique_key_count_by_db(db_id: int):
    """
    Returns the number of unique keys (constraints) in database with provided db_id.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT COUNT(*) AS key_count
        FROM constraints
        JOIN db_tables ON constraints.table_id = db_tables.table_id
        WHERE constraints.type = "UNIQUE" AND db_tables.db_id = %s;
        """,
        (db_id,)
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    count = row["key_count"] if row and "key_count" in row else 0
    return StatCount(db_id=db_id, count=count)
