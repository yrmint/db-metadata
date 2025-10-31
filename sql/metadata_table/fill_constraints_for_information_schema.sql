USE metadata_catalog;

-- ==========================================================
-- Resolve all table IDs from information_schema
-- ==========================================================

SELECT db_id INTO @db_id
FROM dbs WHERE db_name = 'information_schema';

-- Create a temporary table to map table names -> IDs
DROP TEMPORARY TABLE IF EXISTS tmp_tables;
CREATE TEMPORARY TABLE tmp_tables AS
SELECT table_name, table_id
FROM db_tables
WHERE db_id = @db_id;

-- Helper function-like macros (using session variables)
SET @get_table_id = 'SELECT table_id FROM tmp_tables WHERE table_name = ?';

-- ==========================================================
-- Utility Procedures
-- ==========================================================

DELIMITER $$

-- Procedure: Insert a constraint and return its ID
CREATE PROCEDURE add_constraint(
    IN p_table_name VARCHAR(64),
    IN p_constraint_name VARCHAR(64),
    IN p_type ENUM('PRIMARY','FOREIGN'),
    OUT p_constraint_id INT
)
BEGIN
    DECLARE t_id INT;
    SELECT table_id INTO t_id FROM tmp_tables WHERE table_name = p_table_name;

    INSERT INTO constraints (table_id, constraint_name, type)
    VALUES (t_id, p_constraint_name, p_type);

    SELECT constraint_id INTO p_constraint_id
    FROM constraints
    WHERE table_id = t_id AND constraint_name = p_constraint_name
    ORDER BY constraint_id DESC LIMIT 1;
END$$

-- Procedure: Add columns to a constraint in order
CREATE PROCEDURE add_constraint_columns(
    IN p_constraint_id INT,
    IN p_table_name VARCHAR(64),
    IN p_columns_csv TEXT
)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE col_name VARCHAR(128);
    DECLARE col_pos INT DEFAULT 1;
    DECLARE col_id INT;
    DECLARE cur CURSOR FOR
        SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(p_columns_csv, ',', n.n), ',', -1))
        FROM (
            SELECT 1 n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL
            SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9
        ) n
        WHERE n.n <= 1 + LENGTH(p_columns_csv) - LENGTH(REPLACE(p_columns_csv, ',', ''));

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO col_name;
        IF done THEN LEAVE read_loop; END IF;

        SELECT column_id INTO col_id
        FROM db_columns
        WHERE table_id = (SELECT table_id FROM tmp_tables WHERE table_name = p_table_name)
          AND column_name = col_name;

        INSERT INTO constraint_columns (constraint_id, column_id, position)
        VALUES (p_constraint_id, col_id, col_pos);

        SET col_pos = col_pos + 1;
    END LOOP;

    CLOSE cur;
END$$

-- Procedure: Link FK → PK
CREATE PROCEDURE link_fk_pk(
    IN fk_table_name VARCHAR(64),
    IN fk_constraint_name VARCHAR(64),
    IN pk_table_name VARCHAR(64),
    IN pk_constraint_name VARCHAR(64)
)
BEGIN
    DECLARE fk_id, pk_id INT;
    SELECT constraint_id INTO fk_id FROM constraints
    WHERE table_id = (SELECT table_id FROM tmp_tables WHERE table_name = fk_table_name)
      AND constraint_name = fk_constraint_name;

    SELECT constraint_id INTO pk_id FROM constraints
    WHERE table_id = (SELECT table_id FROM tmp_tables WHERE table_name = pk_table_name)
      AND constraint_name = pk_constraint_name;

    INSERT INTO referential_constraints (fk_constraint_id, pk_constraint_id)
    VALUES (fk_id, pk_id);
END$$

DELIMITER ;

-- ==========================================================
-- Define constraints concisely
-- ==========================================================

-- TABLE_CONSTRAINTS
CALL add_constraint('TABLE_CONSTRAINTS', 'pk_table_constraints', 'PRIMARY', @pk_table_constraints);
CALL add_constraint_columns(@pk_table_constraints, 'TABLE_CONSTRAINTS',
    'CONSTRAINT_NAME,TABLE_SCHEMA,TABLE_NAME,CONSTRAINT_TYPE');

CALL add_constraint('TABLE_CONSTRAINTS', 'fk_table_constraints_tables', 'FOREIGN', @fk_table_constraints);
CALL add_constraint_columns(@fk_table_constraints, 'TABLE_CONSTRAINTS', 'TABLE_SCHEMA,TABLE_NAME');

CALL add_constraint('TABLES', 'PRIMARY', 'PRIMARY', @pk_tables);
CALL link_fk_pk('TABLE_CONSTRAINTS', 'fk_table_constraints_tables', 'TABLES', 'PRIMARY');

-- REFERENTIAL_CONSTRAINTS
CALL add_constraint('REFERENTIAL_CONSTRAINTS', 'pk_ref_constraints', 'PRIMARY', @pk_ref_constraints);
CALL add_constraint_columns(@pk_ref_constraints, 'REFERENTIAL_CONSTRAINTS', 'CONSTRAINT_SCHEMA,CONSTRAINT_NAME');

CALL add_constraint('REFERENTIAL_CONSTRAINTS', 'fk_refconstraints_tables', 'FOREIGN', @fk_refconstraints_tables);
CALL add_constraint_columns(@fk_refconstraints_tables, 'REFERENTIAL_CONSTRAINTS', 'CONSTRAINT_SCHEMA,TABLE_NAME');

CALL add_constraint('REFERENTIAL_CONSTRAINTS', 'fk_refconstraints_schemata', 'FOREIGN', @fk_refconstraints_schemata);
CALL add_constraint_columns(@fk_refconstraints_schemata, 'REFERENTIAL_CONSTRAINTS', 'CONSTRAINT_SCHEMA');

CALL add_constraint('SCHEMATA', 'PRIMARY', 'PRIMARY', @pk_schemata);
CALL link_fk_pk('REFERENTIAL_CONSTRAINTS', 'fk_refconstraints_tables', 'TABLES', 'PRIMARY');
CALL link_fk_pk('REFERENTIAL_CONSTRAINTS', 'fk_refconstraints_schemata', 'SCHEMATA', 'PRIMARY');

-- KEY_COLUMN_USAGE
CALL add_constraint('KEY_COLUMN_USAGE', 'pk_key_column_usage', 'PRIMARY', @pk_keycolusage);
CALL add_constraint_columns(@pk_keycolusage, 'KEY_COLUMN_USAGE',
    'CONSTRAINT_NAME,TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,REFERENCED_TABLE_SCHEMA,REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME');

CALL add_constraint('KEY_COLUMN_USAGE', 'fk_keycolusage_columns', 'FOREIGN', @fk_keycolusage_columns);
CALL add_constraint_columns(@fk_keycolusage_columns, 'KEY_COLUMN_USAGE', 'TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME');

CALL add_constraint('KEY_COLUMN_USAGE', 'fk_keycolusage_refcolumns', 'FOREIGN', @fk_keycolusage_refcolumns);
CALL add_constraint_columns(@fk_keycolusage_refcolumns, 'KEY_COLUMN_USAGE', 'REFERENCED_TABLE_SCHEMA,REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME');

CALL add_constraint('KEY_COLUMN_USAGE', 'fk_keycolusage_refconstraints', 'FOREIGN', @fk_keycolusage_refconstraints);
CALL add_constraint_columns(@fk_keycolusage_refconstraints, 'KEY_COLUMN_USAGE', 'CONSTRAINT_NAME,TABLE_SCHEMA');

CALL add_constraint('COLUMNS', 'PRIMARY', 'PRIMARY', @pk_columns);
CALL link_fk_pk('KEY_COLUMN_USAGE', 'fk_keycolusage_columns', 'COLUMNS', 'PRIMARY');
CALL link_fk_pk('KEY_COLUMN_USAGE', 'fk_keycolusage_refcolumns', 'COLUMNS', 'PRIMARY');
CALL link_fk_pk('KEY_COLUMN_USAGE', 'fk_keycolusage_refconstraints', 'REFERENTIAL_CONSTRAINTS', 'pk_ref_constraints');

DROP TEMPORARY TABLE IF EXISTS tmp_tables;
