import mysql.connector
from mysql.connector import Error

# ---------- CONFIGURATION ----------
METADATA_DB = "metadata_catalog"

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root"
}
# -----------------------------------


def get_connection(database=None):
    """Create a MySQL connection (optionally to a specific DB)."""
    config = MYSQL_CONFIG.copy()
    if database:
        config["database"] = database
    return mysql.connector.connect(**config)


def collect_metadata(database):
    """Extract metadata from INFORMATION_SCHEMA for the source DB and store it in metadata_catalog."""

    try:
        src_conn = get_connection("information_schema")
        meta_conn = get_connection(METADATA_DB)
        src_cursor = src_conn.cursor(dictionary=True)
        meta_cursor = meta_conn.cursor()

        # Check if database already in metadata_catalog
        meta_cursor.execute("SELECT db_id FROM dbs WHERE db_name=%s", (database,))
        res = meta_cursor.fetchone()

        if not (res is None):
            print(f"Database {database} already in metadata_catalog")

        else:
            # Insert database record
            src_cursor.execute("""SELECT SCHEMA_NAME
                               FROM SCHEMATA
                               WHERE SCHEMA_NAME = %s""", (database,))
            try:
                db = src_cursor.fetchone()['SCHEMA_NAME']
                meta_cursor.execute("INSERT IGNORE INTO dbs (db_name) VALUES (%s)", (db,))
                meta_conn.commit()
                meta_cursor.execute("SELECT db_id FROM dbs WHERE db_name=%s", (database,))
                db_id = meta_cursor.fetchone()[0]
                print(f"Added database: {database} (db_id={db_id})")

                # Collect all tables in the source database
                src_cursor.execute("""
                    SELECT TABLE_NAME
                    FROM TABLES
                    WHERE TABLE_SCHEMA = %s
                """, (database,))
                tables = src_cursor.fetchall()

                table_id_map = {}
                for t in tables:
                    table_name = t["TABLE_NAME"]
                    meta_cursor.execute("""
                        INSERT INTO db_tables (db_id, table_name) VALUES (%s, %s)
                    """, (db_id, table_name))
                    table_id_map[table_name] = meta_cursor.lastrowid

                meta_conn.commit()
                print(f"Inserted {len(tables)} tables.")

                # Collect all columns
                src_cursor.execute("""
                    SELECT TABLE_NAME, COLUMN_NAME
                    FROM COLUMNS
                    WHERE TABLE_SCHEMA = %s
                    ORDER BY TABLE_NAME, ORDINAL_POSITION
                """, (database,))
                columns = src_cursor.fetchall()

                column_id_map = {}
                for col in columns:
                    tname = col["TABLE_NAME"]
                    cname = col["COLUMN_NAME"]
                    table_id = table_id_map[tname]
                    meta_cursor.execute("""
                        INSERT INTO db_columns (table_id, column_name)
                        VALUES (%s, %s)
                    """, (table_id, cname))
                    column_id_map[(tname, cname)] = meta_cursor.lastrowid

                meta_conn.commit()
                print(f"Inserted {len(columns)} columns.")

                # Collect constraints (keys)
                src_cursor.execute("""
                    SELECT TABLE_NAME, CONSTRAINT_NAME, CONSTRAINT_TYPE
                    FROM TABLE_CONSTRAINTS
                    WHERE TABLE_SCHEMA = %s
                """, (database,))
                constraints = src_cursor.fetchall()

                constraint_id_map = {}
                for c in constraints:
                    tname = c["TABLE_NAME"]
                    cname = c["CONSTRAINT_NAME"]
                    ctype = c["CONSTRAINT_TYPE"]

                    if ctype == "PRIMARY KEY":
                        ctype = "PRIMARY"
                    elif ctype == "UNIQUE":
                        ctype = "UNIQUE"
                    elif ctype == "FOREIGN KEY":
                        ctype = "FOREIGN"
                    else:
                        ctype = "INDEX"

                    meta_cursor.execute("""
                        INSERT INTO constraints (table_id, constraint_name, type)
                        VALUES (%s, %s, %s)
                    """, (table_id_map[tname], cname, ctype))

                    # store constraint_id keyed by (table_name, constraint_name)
                    constraint_id_map[(tname, cname)] = meta_cursor.lastrowid

                meta_conn.commit()
                print(f"Inserted {len(constraints)} constraints.")

                # Constraint columns
                src_cursor.execute("""
                    SELECT
                        CONSTRAINT_NAME,
                        TABLE_NAME,
                        COLUMN_NAME,
                        ORDINAL_POSITION
                    FROM KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = %s
                    ORDER BY CONSTRAINT_NAME, ORDINAL_POSITION
                """, (database,))
                kcols = src_cursor.fetchall()

                for kc in kcols:
                    cname = kc["CONSTRAINT_NAME"]
                    tname = kc["TABLE_NAME"]
                    colname = kc["COLUMN_NAME"]
                    pos = kc["ORDINAL_POSITION"]

                    if (tname, cname) not in constraint_id_map:
                        continue
                    if (tname, colname) not in column_id_map:
                        continue

                    meta_cursor.execute("""
                        INSERT INTO constraint_columns (constraint_id, column_id, position)
                        VALUES (%s, %s, %s)
                    """, (
                        constraint_id_map[(tname, cname)],
                        column_id_map[(tname, colname)],
                        pos
                    ))

                meta_conn.commit()
                print(f"Inserted {len(kcols)} constraint-column links.")

                # Referential constraints (foreign key → primary key)
                # Get all foreign key relationships with referenced tables
                src_cursor.execute("""
                    SELECT
                        rc.CONSTRAINT_NAME AS fk_name,
                        rc.CONSTRAINT_SCHEMA AS fk_schema,
                        kcu.TABLE_NAME AS fk_table_name,
                        kcu.REFERENCED_TABLE_NAME AS referenced_table_name
                    FROM REFERENTIAL_CONSTRAINTS rc
                    JOIN KEY_COLUMN_USAGE kcu
                      ON rc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                     AND rc.CONSTRAINT_SCHEMA = kcu.CONSTRAINT_SCHEMA
                    WHERE rc.CONSTRAINT_SCHEMA = %s
                    GROUP BY rc.CONSTRAINT_NAME, kcu.TABLE_NAME, kcu.REFERENCED_TABLE_NAME
                """, (database,))

                fks = src_cursor.fetchall()
                inserted = 0

                for fk in fks:
                    fk_name = fk["fk_name"]
                    fk_table = fk["fk_table_name"]
                    ref_table = fk["referenced_table_name"]

                    # Get foreign key constraint ID
                    fk_id = constraint_id_map.get((fk_table, fk_name))
                    if fk_id is None:
                        continue

                    # Get referenced table ID
                    ref_table_id = table_id_map.get(ref_table)
                    if ref_table_id is None:
                        continue

                    # Get primary key constraint ID for referenced table
                    pk_id = None
                    for (tname, cname), cid in constraint_id_map.items():
                        if tname == ref_table and cname == "PRIMARY":
                            pk_id = cid
                            break

                    if pk_id is None:
                        continue

                    # Insert into referential_constraints
                    meta_cursor.execute("""
                        INSERT INTO referential_constraints (fk_constraint_id, pk_constraint_id)
                        VALUES (%s, %s)
                    """, (fk_id, pk_id))
                    inserted += 1

                meta_conn.commit()
                print(f"Inserted {inserted} referential constraints.")

                print("Metadata successfully imported into metadata_catalog.")

            except TypeError as _:
                print(f"Database {database} not found")

    except Error as e:
        print(f"Error: {e}")

    finally:
        for c in (src_cursor, meta_cursor):
            if c: c.close()
        for conn in (src_conn, meta_conn):
            if conn and conn.is_connected():
                conn.close()


if __name__ == "__main__":
    print("Enter databases to store information in metadata_catalog:")
    s = input()
    databases = s.split()
    for db in databases:
        collect_metadata(db)
