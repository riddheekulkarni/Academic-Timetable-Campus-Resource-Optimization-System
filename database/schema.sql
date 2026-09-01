-- ============================================================================
-- Academic Timetable & Campus Resource Optimization System
-- Phase 2: Database Schema (schema.sql)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS academic_scheduler;
USE academic_scheduler;

-- Drop tables cleanly
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS schedule_changes;
DROP TABLE IF EXISTS room_allocations;
DROP TABLE IF EXISTS timetable;
DROP TABLE IF EXISTS course_assignments;
DROP TABLE IF EXISTS subject_requirements;
DROP TABLE IF EXISTS faculty_availability;
DROP TABLE IF EXISTS time_slots;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS labs;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS sections;
DROP TABLE IF EXISTS faculty;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- 1. Users (Central authentication table)
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'FACULTY', 'STUDENT') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 2. Departments
-- ----------------------------------------------------------------------------
CREATE TABLE departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_code VARCHAR(10) NOT NULL UNIQUE,
    dept_name VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 3. Students
-- ----------------------------------------------------------------------------
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    student_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    dept_id INT NOT NULL,
    academic_year INT NOT NULL CHECK (academic_year BETWEEN 1 AND 4),
    section_id INT, -- Linked after sections table creation via ALTER or constraint
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 4. Faculty
-- ----------------------------------------------------------------------------
CREATE TABLE faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    faculty_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    dept_id INT NOT NULL,
    designation VARCHAR(50) DEFAULT 'Assistant Professor',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 5. Sections / Batches
-- ----------------------------------------------------------------------------
CREATE TABLE sections (
    section_id INT AUTO_INCREMENT PRIMARY KEY,
    section_name VARCHAR(50) NOT NULL,
    dept_id INT NOT NULL,
    academic_year INT NOT NULL CHECK (academic_year BETWEEN 1 AND 4),
    semester INT NOT NULL CHECK (semester BETWEEN 1 AND 8),
    student_count INT NOT NULL DEFAULT 0,
    CONSTRAINT uq_section UNIQUE (dept_id, academic_year, semester, section_name),
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add deferred foreign key constraint to students
ALTER TABLE students 
    ADD CONSTRAINT fk_students_section 
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE SET NULL;

-- ----------------------------------------------------------------------------
-- 6. Subjects
-- ----------------------------------------------------------------------------
CREATE TABLE subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_code VARCHAR(20) NOT NULL UNIQUE,
    subject_name VARCHAR(100) NOT NULL,
    dept_id INT NOT NULL,
    type ENUM('Lecture', 'Lab') NOT NULL DEFAULT 'Lecture',
    lectures_per_week INT NOT NULL DEFAULT 3,
    duration_hours INT NOT NULL DEFAULT 1,
    required_room_type ENUM('Classroom', 'Computer Lab') NOT NULL DEFAULT 'Classroom',
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 7. Classrooms
-- ----------------------------------------------------------------------------
CREATE TABLE rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(20) NOT NULL UNIQUE,
    building VARCHAR(50) DEFAULT 'Main Block',
    capacity INT NOT NULL,
    projector_available BOOLEAN DEFAULT TRUE,
    smart_board_available BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 8. Laboratories
-- ----------------------------------------------------------------------------
CREATE TABLE labs (
    lab_id INT AUTO_INCREMENT PRIMARY KEY,
    lab_name VARCHAR(50) NOT NULL UNIQUE,
    building VARCHAR(50) DEFAULT 'Tech Block',
    capacity INT NOT NULL,
    computer_count INT NOT NULL DEFAULT 0,
    projector_available BOOLEAN DEFAULT TRUE,
    specialized_equipment TEXT,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 9. Equipment
-- ----------------------------------------------------------------------------
CREATE TABLE equipment (
    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    location_room_id INT,
    location_lab_id INT,
    status ENUM('Functional', 'Maintenance', 'Decommissioned') DEFAULT 'Functional',
    FOREIGN KEY (location_room_id) REFERENCES rooms(room_id) ON DELETE SET NULL,
    FOREIGN KEY (location_lab_id) REFERENCES labs(lab_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 10. Time Slots
-- ----------------------------------------------------------------------------
CREATE TABLE time_slots (
    slot_id INT AUTO_INCREMENT PRIMARY KEY,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_order INT NOT NULL,
    CONSTRAINT uq_time_slot UNIQUE (day_of_week, start_time, end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 11. Faculty Availability
-- ----------------------------------------------------------------------------
CREATE TABLE faculty_availability (
    availability_id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    slot_id INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    CONSTRAINT uq_faculty_slot UNIQUE (faculty_id, slot_id),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (slot_id) REFERENCES time_slots(slot_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 12. Subject Requirements
-- ----------------------------------------------------------------------------
CREATE TABLE subject_requirements (
    requirement_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL UNIQUE,
    min_capacity INT NOT NULL,
    requires_projector BOOLEAN DEFAULT FALSE,
    requires_smart_board BOOLEAN DEFAULT FALSE,
    min_computers INT DEFAULT 0,
    special_equipment_needed TEXT,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 13. Course Assignments (Subject -> Faculty -> Section map)
-- ----------------------------------------------------------------------------
CREATE TABLE course_assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    faculty_id INT NOT NULL,
    section_id INT NOT NULL,
    CONSTRAINT uq_assignment UNIQUE (subject_id, section_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 14. Timetable (The generated master schedule)
-- ----------------------------------------------------------------------------
CREATE TABLE timetable (
    timetable_id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT NOT NULL,
    slot_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_timetable_assignment_slot UNIQUE (assignment_id, slot_id),
    FOREIGN KEY (assignment_id) REFERENCES course_assignments(assignment_id) ON DELETE CASCADE,
    FOREIGN KEY (slot_id) REFERENCES time_slots(slot_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 15. Room Allocations
-- ----------------------------------------------------------------------------
CREATE TABLE room_allocations (
    allocation_id INT AUTO_INCREMENT PRIMARY KEY,
    timetable_id INT NOT NULL UNIQUE,
    room_id INT,
    lab_id INT,
    CONSTRAINT chk_room_or_lab CHECK (
        (room_id IS NOT NULL AND lab_id IS NULL) OR 
        (room_id IS NULL AND lab_id IS NOT NULL)
    ),
    FOREIGN KEY (timetable_id) REFERENCES timetable(timetable_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE,
    FOREIGN KEY (lab_id) REFERENCES labs(lab_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------
-- 16. Schedule Changes (Dynamic rescheduling request workflow)
-- ----------------------------------------------------------------------------
CREATE TABLE schedule_changes (
    change_id INT AUTO_INCREMENT PRIMARY KEY,
    timetable_id INT NOT NULL,
    requested_by_faculty_id INT NOT NULL,
    change_type ENUM('Room Change', 'Faculty Unavailable', 'Lab Maintenance', 'Slot Swap') NOT NULL,
    target_slot_id INT,
    target_room_id INT,
    target_lab_id INT,
    reason TEXT NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (timetable_id) REFERENCES timetable(timetable_id) ON DELETE CASCADE,
    FOREIGN KEY (requested_by_faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (target_slot_id) REFERENCES time_slots(slot_id) ON DELETE SET NULL,
    FOREIGN KEY (target_room_id) REFERENCES rooms(room_id) ON DELETE SET NULL,
    FOREIGN KEY (target_lab_id) REFERENCES labs(lab_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;