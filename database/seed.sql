-- ============================================================================
-- Academic Timetable & Campus Resource Optimization System
-- Phase 2: Seed Data (seed.sql)
-- Default Password for all seeded users: password123
-- ============================================================================

USE academic_scheduler;

-- Disable foreign key checks during batch seed
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE schedule_changes;
TRUNCATE TABLE room_allocations;
TRUNCATE TABLE timetable;
TRUNCATE TABLE course_assignments;
TRUNCATE TABLE subject_requirements;
TRUNCATE TABLE faculty_availability;
TRUNCATE TABLE time_slots;
TRUNCATE TABLE equipment;
TRUNCATE TABLE labs;
TRUNCATE TABLE rooms;
TRUNCATE TABLE subjects;
TRUNCATE TABLE students;
TRUNCATE TABLE sections;
TRUNCATE TABLE faculty;
TRUNCATE TABLE departments;
TRUNCATE TABLE users;

SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- 1. Departments
-- ----------------------------------------------------------------------------
INSERT INTO departments (dept_id, dept_code, dept_name) VALUES
(1, 'CSE', 'Computer Science & Engineering'),
(2, 'ECE', 'Electronics & Communication Engineering'),
(3, 'MECH', 'Mechanical Engineering');

-- ----------------------------------------------------------------------------
-- 2. Users (Password for all: password123)
-- Hash generated via Werkzeug security generating 'password123'
-- ----------------------------------------------------------------------------
INSERT INTO users (user_id, email, password_hash, role) VALUES
-- Admin
(1, 'admin@gmail.com', 'scrypt:32768:8:1$bh96xmkhp4tyVlD8$0e947a0d36d0e6cc1ad03c1542481dd35326d15b712bd206959842d57c219d37d7f74885fc544e3860e8974fccf23d9934fc3d69f001a0852346813c4355a6a4', 'ADMIN'),

-- Faculty Users
(2, 'dr.smith@gmail.com', 'scrypt:32768:8:1$bh96xmkhp4tyVlD8$0e947a0d36d0e6cc1ad03c1542481dd35326d15b712bd206959842d57c219d37d7f74885fc544e3860e8974fccf23d9934fc3d69f001a0852346813c4355a6a4', 'FACULTY'),
(3, 'prof.johnson@gmail.com', 'scrypt:32768:8:1$bh96xmkhp4tyVlD8$0e947a0d36d0e6cc1ad03c1542481dd35326d15b712bd206959842d57c219d37d7f74885fc544e3860e8974fccf23d9934fc3d69f001a0852346813c4355a6a4', 'FACULTY'),
(4, 'dr.williams@gmail.com', 'scrypt:32768:8:1$bh96xmkhp4tyVlD8$0e947a0d36d0e6cc1ad03c1542481dd35326d15b712bd206959842d57c219d37d7f74885fc544e3860e8974fccf23d9934fc3d69f001a0852346813c4355a6a4', 'FACULTY'),
(5, 'prof.brown@gmail.com', 'scrypt:32768:8:1$bh96xmkhp4tyVlD8$0e947a0d36d0e6cc1ad03c1542481dd35326d15b712bd206959842d57c219d37d7f74885fc544e3860e8974fccf23d9934fc3d69f001a0852346813c4355a6a4', 'FACULTY'),
(6, 'dr.jones@gmail.com', 'scrypt:32768:8:1$bh96xmkhp4tyVlD8$0e947a0d36d0e6cc1ad03c1542481dd35326d15b712bd206959842d57c219d37d7f74885fc544e3860e8974fccf23d9934fc3d69f001a0852346813c4355a6a4', 'FACULTY'),
(7, 'prof.miller@gmail.com', 'scrypt:32768:8:1$bh96xmkhp4tyVlD8$0e947a0d36d0e6cc1ad03c1542481dd35326d15b712bd206959842d57c219d37d7f74885fc544e3860e8974fccf23d9934fc3d69f001a0852346813c4355a6a4', 'FACULTY'),
(8, 'dr.davis@gmail.com', 'scrypt:32768:8:1$bh96xmkhp4tyVlD8$0e947a0d36d0e6cc1ad03c1542481dd35326d15b712bd206959842d57c219d37d7f74885fc544e3860e8974fccf23d9934fc3d69f001a0852346813c4355a6a4', 'FACULTY'),
(9, 'prof.garcia@gmail.com', 'scrypt:32768:8:1$bh96xmkhp4tyVlD8$0e947a0d36d0e6cc1ad03c1542481dd35326d15b712bd206959842d57c219d37d7f74885fc544e3860e8974fccf23d9934fc3d69f001a0852346813c4355a6a4', 'FACULTY'),

-- Student Users
(10, 'alice@gmail.com', 'scrypt:32768:8:1$bh96xmkhp4tyVlD8$0e947a0d36d0e6cc1ad03c1542481dd35326d15b712bd206959842d57c219d37d7f74885fc544e3860e8974fccf23d9934fc3d69f001a0852346813c4355a6a4', 'STUDENT'),
(11, 'bob@gmail.com', 'scrypt:32768:8:1$bh96xmkhp4tyVlD8$0e947a0d36d0e6cc1ad03c1542481dd35326d15b712bd206959842d57c219d37d7f74885fc544e3860e8974fccf23d9934fc3d69f001a0852346813c4355a6a4', 'STUDENT'),
(12, 'charlie@gmail.com', 'scrypt:32768:8:1$bh96xmkhp4tyVlD8$0e947a0d36d0e6cc1ad03c1542481dd35326d15b712bd206959842d57c219d37d7f74885fc544e3860e8974fccf23d9934fc3d69f001a0852346813c4355a6a4', 'STUDENT');

-- ----------------------------------------------------------------------------
-- 3. Faculty
-- ----------------------------------------------------------------------------
INSERT INTO faculty (faculty_id, user_id, faculty_code, name, dept_id, designation) VALUES
(1, 2, 'FAC101', 'Dr. Alan Smith', 1, 'Professor'),
(2, 3, 'FAC102', 'Prof. Sarah Johnson', 1, 'Associate Professor'),
(3, 4, 'FAC103', 'Dr. Robert Williams', 1, 'Assistant Professor'),
(4, 5, 'FAC104', 'Prof. Emily Brown', 2, 'Professor'),
(5, 6, 'FAC105', 'Dr. Michael Jones', 2, 'Associate Professor'),
(6, 7, 'FAC106', 'Prof. David Miller', 3, 'Professor'),
(7, 8, 'FAC107', 'Dr. Jessica Davis', 3, 'Assistant Professor'),
(8, 9, 'FAC108', 'Prof. Carlos Garcia', 1, 'Assistant Professor');

-- ----------------------------------------------------------------------------
-- 4. Sections / Batches
-- ----------------------------------------------------------------------------
INSERT INTO sections (section_id, section_name, dept_id, academic_year, semester, student_count) VALUES
(1, 'CSE-3A', 1, 3, 5, 55),
(2, 'CSE-3B', 1, 3, 5, 50),
(3, 'ECE-2A', 2, 2, 3, 45),
(4, 'MECH-4A', 3, 4, 7, 40);

-- ----------------------------------------------------------------------------
-- 5. Students (Numeric Roll Numbers: 1012411001, 1012411002, etc.)
-- ----------------------------------------------------------------------------
INSERT INTO students (student_id, user_id, student_code, name, dept_id, academic_year, section_id) VALUES
(1, 10, '1012411001', 'Alice Vance', 1, 3, 1),
(2, 11, '1012411002', 'Bob Smith', 1, 3, 1),
(3, 12, '1012411003', 'Charlie Brown', 2, 2, 3);

-- ----------------------------------------------------------------------------
-- 6. Subjects
-- ----------------------------------------------------------------------------
INSERT INTO subjects (subject_id, subject_code, subject_name, dept_id, type, lectures_per_week, duration_hours, required_room_type) VALUES
(1, 'CS501', 'Database Management Systems', 1, 'Lecture', 3, 1, 'Classroom'),
(2, 'CS501L', 'DBMS Laboratory', 1, 'Lab', 1, 2, 'Computer Lab'),
(3, 'CS502', 'Computer Networks', 1, 'Lecture', 3, 1, 'Classroom'),
(4, 'CS503', 'Operating Systems', 1, 'Lecture', 3, 1, 'Classroom'),
(5, 'CS503L', 'OS Laboratory', 1, 'Lab', 1, 2, 'Computer Lab'),
(6, 'EC301', 'Digital Signal Processing', 2, 'Lecture', 3, 1, 'Classroom'),
(7, 'EC301L', 'DSP Laboratory', 2, 'Lab', 1, 2, 'Computer Lab'),
(8, 'ME701', 'Finite Element Analysis', 3, 'Lecture', 3, 1, 'Classroom'),
(9, 'ME701L', 'CAD/CAM Laboratory', 3, 'Lab', 1, 2, 'Computer Lab'),
(10, 'CS504', 'Artificial Intelligence', 1, 'Lecture', 3, 1, 'Classroom');

-- ----------------------------------------------------------------------------
-- 7. Subject Requirements
-- ----------------------------------------------------------------------------
INSERT INTO subject_requirements (requirement_id, subject_id, min_capacity, requires_projector, requires_smart_board, min_computers, special_equipment_needed) VALUES
(1, 1, 50, TRUE, FALSE, 0, NULL),
(2, 2, 30, TRUE, FALSE, 30, 'MySQL Server Workbench'),
(3, 3, 50, TRUE, FALSE, 0, NULL),
(4, 4, 50, FALSE, FALSE, 0, NULL),
(5, 5, 30, TRUE, FALSE, 30, 'Linux OS Environment'),
(6, 6, 40, TRUE, FALSE, 0, NULL),
(7, 7, 25, TRUE, FALSE, 25, 'MATLAB Software Kits'),
(8, 8, 35, TRUE, FALSE, 0, NULL),
(9, 9, 30, TRUE, FALSE, 30, 'AutoCAD / ANSYS Workstations'),
(10, 10, 50, TRUE, TRUE, 0, NULL);

-- ----------------------------------------------------------------------------
-- 8. Classrooms
-- ----------------------------------------------------------------------------
INSERT INTO rooms (room_id, room_number, building, capacity, projector_available, smart_board_available, is_active) VALUES
(1, 'CR-101', 'Main Academic Block', 60, TRUE, TRUE, TRUE),
(2, 'CR-102', 'Main Academic Block', 60, TRUE, FALSE, TRUE),
(3, 'CR-103', 'Main Academic Block', 45, TRUE, FALSE, TRUE),
(4, 'CR-104', 'Main Academic Block', 40, FALSE, FALSE, TRUE),
(5, 'CR-201', 'Science Block', 70, TRUE, TRUE, TRUE),
(6, 'CR-202', 'Science Block', 35, FALSE, FALSE, TRUE);

-- ----------------------------------------------------------------------------
-- 9. Laboratories
-- ----------------------------------------------------------------------------
INSERT INTO labs (lab_id, lab_name, building, capacity, computer_count, projector_available, specialized_equipment, is_active) VALUES
(1, 'CompLab-1 (Database & OS)', 'Tech Block', 35, 35, TRUE, 'Linux/MySQL Installed', TRUE),
(2, 'CompLab-2 (AI & Networks)', 'Tech Block', 35, 35, TRUE, 'GPU Workstations, Cisco Routers', TRUE),
(3, 'CAD/CAM Lab', 'Engineering Block', 40, 40, TRUE, 'High Performance ANSYS Nodes', TRUE);

-- ----------------------------------------------------------------------------
-- 10. Equipment
-- ----------------------------------------------------------------------------
INSERT INTO equipment (equipment_id, equipment_name, quantity, location_room_id, location_lab_id, status) VALUES
(1, 'HD Ceiling Projector', 1, 1, NULL, 'Functional'),
(2, 'Interactive Smart Board', 1, 1, NULL, 'Functional'),
(3, 'Cisco Router Rack Unit', 2, NULL, 2, 'Functional'),
(4, 'High Performance GPU Workstation', 10, NULL, 2, 'Functional'),
(5, 'Digital Oscilloscope Unit', 15, NULL, 3, 'Functional');

-- ----------------------------------------------------------------------------
-- 11. Time Slots
-- ----------------------------------------------------------------------------
INSERT INTO time_slots (slot_id, day_of_week, start_time, end_time, slot_order) VALUES
(1, 'Monday', '09:00:00', '10:00:00', 1),
(2, 'Monday', '10:00:00', '11:00:00', 2),
(3, 'Monday', '11:00:00', '12:00:00', 3),
(4, 'Monday', '12:00:00', '13:00:00', 4),
(5, 'Monday', '14:00:00', '15:00:00', 5),
(6, 'Monday', '15:00:00', '16:00:00', 6),
(7, 'Tuesday', '09:00:00', '10:00:00', 1),
(8, 'Tuesday', '10:00:00', '11:00:00', 2),
(9, 'Tuesday', '11:00:00', '12:00:00', 3),
(10, 'Tuesday', '12:00:00', '13:00:00', 4),
(11, 'Tuesday', '14:00:00', '15:00:00', 5),
(12, 'Tuesday', '15:00:00', '16:00:00', 6),
(13, 'Wednesday', '09:00:00', '10:00:00', 1),
(14, 'Wednesday', '10:00:00', '11:00:00', 2),
(15, 'Wednesday', '11:00:00', '12:00:00', 3),
(16, 'Wednesday', '12:00:00', '13:00:00', 4),
(17, 'Wednesday', '14:00:00', '15:00:00', 5),
(18, 'Wednesday', '15:00:00', '16:00:00', 6),
(19, 'Thursday', '09:00:00', '10:00:00', 1),
(20, 'Thursday', '10:00:00', '11:00:00', 2),
(21, 'Thursday', '11:00:00', '12:00:00', 3),
(22, 'Thursday', '12:00:00', '13:00:00', 4),
(23, 'Thursday', '14:00:00', '15:00:00', 5),
(24, 'Thursday', '15:00:00', '16:00:00', 6),
(25, 'Friday', '09:00:00', '10:00:00', 1),
(26, 'Friday', '10:00:00', '11:00:00', 2),
(27, 'Friday', '11:00:00', '12:00:00', 3),
(28, 'Friday', '12:00:00', '13:00:00', 4),
(29, 'Friday', '14:00:00', '15:00:00', 5),
(30, 'Friday', '15:00:00', '16:00:00', 6);

-- ----------------------------------------------------------------------------
-- 12. Faculty Availability
-- ----------------------------------------------------------------------------
INSERT INTO faculty_availability (faculty_id, slot_id, is_available) VALUES
(1, 1, FALSE),
(1, 2, TRUE),
(2, 1, TRUE),
(2, 2, TRUE);

-- ----------------------------------------------------------------------------
-- 13. Course Assignments
-- ----------------------------------------------------------------------------
INSERT INTO course_assignments (assignment_id, subject_id, faculty_id, section_id) VALUES
(1, 1, 1, 1), -- CS501 (DBMS Lecture) -> Dr. Smith -> CSE-3A
(2, 2, 1, 1), -- CS501L (DBMS Lab) -> Dr. Smith -> CSE-3A
(3, 3, 2, 1), -- CS502 (CN Lecture) -> Prof. Johnson -> CSE-3A
(4, 4, 3, 1), -- CS503 (OS Lecture) -> Dr. Williams -> CSE-3A
(5, 5, 3, 1), -- CS503L (OS Lab) -> Dr. Williams -> CSE-3A
(6, 6, 4, 3), -- EC301 (DSP Lecture) -> Prof. Brown -> ECE-2A
(7, 7, 5, 3), -- EC301L (DSP Lab) -> Dr. Jones -> ECE-2A
(8, 8, 6, 4), -- ME701 (FEA Lecture) -> Prof. Miller -> MECH-4A
(9, 9, 7, 4), -- ME701L (CAD Lab) -> Dr. Davis -> MECH-4A
(10, 10, 8, 2);-- CS504 (AI Lecture) -> Prof. Garcia -> CSE-3B