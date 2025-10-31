DROP SCHEMA metadata_catalog;

-- ==========================
-- DATABASE METADATA CATALOG
-- ==========================
CREATE DATABASE IF NOT EXISTS metadata_catalog
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE metadata_catalog;

-- ==========================
-- TABLE: dbs
-- ==========================
CREATE TABLE IF NOT EXISTS dbs (
    db_id INT AUTO_INCREMENT PRIMARY KEY,
    db_name VARCHAR(64) NOT NULL UNIQUE
) ENGINE=InnoDB;


-- ==========================
-- TABLE: db_tables
-- ==========================
CREATE TABLE IF NOT EXISTS db_tables (
    table_id INT AUTO_INCREMENT PRIMARY KEY,
    db_id INT NOT NULL,
    table_name VARCHAR(64) NOT NULL,
    FOREIGN KEY (db_id) REFERENCES dbs(db_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==========================
-- TABLE: db_columns
-- ==========================
CREATE TABLE IF NOT EXISTS db_columns (
    column_id INT AUTO_INCREMENT PRIMARY KEY,
    table_id INT NOT NULL,
    column_name VARCHAR(64) NOT NULL,
    FOREIGN KEY (table_id) REFERENCES db_tables(table_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==========================
-- TABLE: constraints
-- ==========================
CREATE TABLE IF NOT EXISTS constraints (
    constraint_id INT AUTO_INCREMENT PRIMARY KEY,
    table_id INT NOT NULL,
    constraint_name VARCHAR(64) NOT NULL,
    type ENUM('PRIMARY', 'UNIQUE', 'FOREIGN', 'INDEX') NOT NULL,
    FOREIGN KEY (table_id) REFERENCES db_tables(table_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==========================
-- TABLE: constraint_columns
-- ==========================
CREATE TABLE IF NOT EXISTS constraint_columns (
    constraint_column_id INT AUTO_INCREMENT PRIMARY KEY,
    constraint_id INT NOT NULL,
    column_id INT NOT NULL,
    position INT NOT NULL,
    FOREIGN KEY (constraint_id) REFERENCES constraints(constraint_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (column_id) REFERENCES db_columns(column_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ==========================
-- TABLE: referential_constraints
-- ==========================
CREATE TABLE IF NOT EXISTS referential_constraints (
    rc_id INT AUTO_INCREMENT PRIMARY KEY,
    fk_constraint_id INT NOT NULL,
    pk_constraint_id INT NOT NULL,
    FOREIGN KEY (fk_constraint_id) REFERENCES constraints(constraint_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (pk_constraint_id) REFERENCES constraints(constraint_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;
