CREATE DATABASE IF NOT EXISTS composite_key_example
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE composite_key_example;


-- =====================================
-- TABLE: departments
-- =====================================
CREATE TABLE departments (
    dept_code VARCHAR(10) NOT NULL,
    region_code VARCHAR(5) NOT NULL,
    dept_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (dept_code, region_code)
) ENGINE=InnoDB;


-- =====================================
-- TABLE: employees
-- =====================================
CREATE TABLE employees (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_code VARCHAR(10) NOT NULL,
    region_code VARCHAR(5) NOT NULL,
    emp_name VARCHAR(100) NOT NULL,
    position VARCHAR(50),
    FOREIGN KEY (dept_code, region_code)
        REFERENCES departments(dept_code, region_code)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- =====================================
-- TABLE: projects
-- =====================================
CREATE TABLE projects (
    dept_code VARCHAR(10) NOT NULL,
    region_code VARCHAR(5) NOT NULL,
    project_code VARCHAR(20) NOT NULL,
    project_name VARCHAR(150),
    PRIMARY KEY (dept_code, region_code, project_code),
    FOREIGN KEY (dept_code, region_code)
        REFERENCES departments(dept_code, region_code)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- =====================================
-- TABLE: employee_projects
-- =====================================
CREATE TABLE employee_projects (
    emp_id INT NOT NULL,
    dept_code VARCHAR(10) NOT NULL,
    region_code VARCHAR(5) NOT NULL,
    project_code VARCHAR(20) NOT NULL,
    assigned_date DATE,
    PRIMARY KEY (emp_id, dept_code, region_code, project_code),
    FOREIGN KEY (emp_id)
        REFERENCES employees(emp_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (dept_code, region_code, project_code)
        REFERENCES projects(dept_code, region_code, project_code)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

