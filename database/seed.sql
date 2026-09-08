-- Demonstration dataset. Default password for every account: Password123
USE academic_scheduler;
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE schedule_changes; TRUNCATE TABLE room_allocations; TRUNCATE TABLE timetable;
TRUNCATE TABLE course_assignments; TRUNCATE TABLE subject_requirements; TRUNCATE TABLE faculty_availability;
TRUNCATE TABLE time_slots; TRUNCATE TABLE equipment; TRUNCATE TABLE labs; TRUNCATE TABLE rooms;
TRUNCATE TABLE subjects; TRUNCATE TABLE students; TRUNCATE TABLE sections; TRUNCATE TABLE faculty;
TRUNCATE TABLE departments; TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO departments (dept_code, dept_name) VALUES
('CSE','Computer Science & Engineering'),('ECE','Electronics & Communication Engineering'),('MECH','Mechanical Engineering');

SET @pw = 'scrypt:32768:8:1$ub4zXILQG9FPG9aJ$4aa96097dabe57ab39c87b7d40422e02eeaf7341326d7ff16f42a4e584607205637b452929cc755cf872c9af2224f514c253627c75512613a20549c19ecb5039';
INSERT INTO users (email,password_hash,role) VALUES
('admin@gmail.com',@pw,'ADMIN'),
('ananya.sharma@campus.edu',@pw,'FACULTY'),('rohit.patel@campus.edu',@pw,'FACULTY'),('kavita.iyer@campus.edu',@pw,'FACULTY'),('sandeep.verma@campus.edu',@pw,'FACULTY'),('meera.nair@campus.edu',@pw,'FACULTY'),('arjun.reddy@campus.edu',@pw,'FACULTY'),('pooja.kulkarni@campus.edu',@pw,'FACULTY'),('vikram.singh@campus.edu',@pw,'FACULTY'),('neha.gupta@campus.edu',@pw,'FACULTY'),('priyanka.das@campus.edu',@pw,'FACULTY'),('rakesh.joshi@campus.edu',@pw,'FACULTY'),('sneha.menon@campus.edu',@pw,'FACULTY'),('aditya.chavan@campus.edu',@pw,'FACULTY'),('deepa.bansal@campus.edu',@pw,'FACULTY'),('manish.yadav@campus.edu',@pw,'FACULTY'),
('aarya.mehta@student.edu',@pw,'STUDENT'),('vivaan.shah@student.edu',@pw,'STUDENT'),('ishita.rao@student.edu',@pw,'STUDENT'),('krish.malhotra@student.edu',@pw,'STUDENT'),('diya.kapoor@student.edu',@pw,'STUDENT'),('aarav.naik@student.edu',@pw,'STUDENT'),('anika.sen@student.edu',@pw,'STUDENT'),('dhruv.jain@student.edu',@pw,'STUDENT'),('kavya.pillai@student.edu',@pw,'STUDENT'),('reyansh.mishra@student.edu',@pw,'STUDENT'),('saanvi.desai@student.edu',@pw,'STUDENT'),('advait.kulkarni@student.edu',@pw,'STUDENT'),('nisha.menon@student.edu',@pw,'STUDENT'),('arjun.sethi@student.edu',@pw,'STUDENT'),('tanvi.bose@student.edu',@pw,'STUDENT'),('yash.dubey@student.edu',@pw,'STUDENT'),('riya.chopra@student.edu',@pw,'STUDENT'),('kabir.saxena@student.edu',@pw,'STUDENT'),('shreya.nambiar@student.edu',@pw,'STUDENT'),('atharv.pawar@student.edu',@pw,'STUDENT'),('mira.shetty@student.edu',@pw,'STUDENT'),('pranav.goyal@student.edu',@pw,'STUDENT'),('isha.agrawal@student.edu',@pw,'STUDENT'),('omkar.patil@student.edu',@pw,'STUDENT'),('aadhya.rana@student.edu',@pw,'STUDENT');

INSERT INTO faculty (user_id,faculty_code,name,dept_id,designation) VALUES
(2,'CSE101','Dr. Ananya Sharma',1,'Professor'),(3,'CSE102','Prof. Rohit Patel',1,'Associate Professor'),(4,'CSE103','Dr. Kavita Iyer',1,'Assistant Professor'),(5,'CSE104','Prof. Sandeep Verma',1,'Associate Professor'),(6,'CSE105','Dr. Meera Nair',1,'Assistant Professor'),(7,'CSE106','Prof. Arjun Reddy',1,'Professor'),
(8,'ECE101','Dr. Pooja Kulkarni',2,'Professor'),(9,'ECE102','Prof. Vikram Singh',2,'Associate Professor'),(10,'ECE103','Dr. Neha Gupta',2,'Assistant Professor'),(11,'ECE104','Prof. Priyanka Das',2,'Associate Professor'),(12,'ECE105','Dr. Rakesh Joshi',2,'Assistant Professor'),
(13,'ME101','Dr. Sneha Menon',3,'Professor'),(14,'ME102','Prof. Aditya Chavan',3,'Associate Professor'),(15,'ME103','Dr. Deepa Bansal',3,'Assistant Professor'),(16,'ME104','Prof. Manish Yadav',3,'Assistant Professor');

INSERT INTO sections (section_name,dept_id,academic_year,semester,student_count) VALUES
('CSE-3A',1,3,5,4),('CSE-3B',1,3,5,4),('CSE-2A',1,2,3,4),('ECE-2A',2,2,3,4),('ECE-3A',2,3,5,3),('MECH-4A',3,4,7,3),('MECH-3A',3,3,5,3);
INSERT INTO students (user_id,student_code,name,dept_id,academic_year,section_id) VALUES
(17,'CSE23001','Aarya Mehta',1,3,1),(18,'CSE23002','Vivaan Shah',1,3,1),(19,'CSE23003','Ishita Rao',1,3,1),(20,'CSE23004','Krish Malhotra',1,3,1),(21,'CSE23005','Diya Kapoor',1,3,2),(22,'CSE23006','Aarav Naik',1,3,2),(23,'CSE23007','Anika Sen',1,3,2),(24,'CSE23008','Dhruv Jain',1,3,2),(25,'CSE24001','Kavya Pillai',1,2,3),(26,'CSE24002','Reyansh Mishra',1,2,3),(27,'CSE24003','Saanvi Desai',1,2,3),(28,'CSE24004','Advait Kulkarni',1,2,3),
(29,'ECE24001','Nisha Menon',2,2,4),(30,'ECE24002','Arjun Sethi',2,2,4),(31,'ECE24003','Tanvi Bose',2,2,4),(32,'ECE24004','Yash Dubey',2,2,4),(33,'ECE23001','Riya Chopra',2,3,5),(34,'ECE23002','Kabir Saxena',2,3,5),(35,'ECE23003','Shreya Nambiar',2,3,5),(36,'ME22001','Atharv Pawar',3,4,6),(37,'ME22002','Mira Shetty',3,4,6),(38,'ME22003','Pranav Goyal',3,4,6),(39,'ME23001','Isha Agrawal',3,3,7),(40,'ME23002','Omkar Patil',3,3,7),(41,'ME23003','Aadhya Rana',3,3,7);

INSERT INTO subjects (subject_code,subject_name,dept_id,type,lectures_per_week,duration_hours,required_room_type) VALUES
('CS501','Database Management Systems',1,'Lecture',3,1,'Classroom'),('CS501L','DBMS Laboratory',1,'Lab',1,2,'Computer Lab'),('CS502','Computer Networks',1,'Lecture',3,1,'Classroom'),('CS503','Operating Systems',1,'Lecture',3,1,'Classroom'),('CS503L','Operating Systems Laboratory',1,'Lab',1,2,'Computer Lab'),('CS504','Artificial Intelligence',1,'Lecture',3,1,'Classroom'),('CS401','Data Structures',1,'Lecture',3,1,'Classroom'),('CS401L','Data Structures Laboratory',1,'Lab',1,2,'Computer Lab'),
('EC301','Digital Signal Processing',2,'Lecture',3,1,'Classroom'),('EC301L','DSP Laboratory',2,'Lab',1,2,'Computer Lab'),('EC302','Microprocessors and Controllers',2,'Lecture',3,1,'Classroom'),('EC303','Embedded Systems',2,'Lecture',3,1,'Classroom'),('EC303L','Embedded Systems Laboratory',2,'Lab',1,2,'Computer Lab'),('EC304','Communication Systems',2,'Lecture',3,1,'Classroom'),
('ME701','Thermodynamics',3,'Lecture',3,1,'Classroom'),('ME701L','CAD and CAM Laboratory',3,'Lab',1,2,'Computer Lab'),('ME702','Machine Design',3,'Lecture',3,1,'Classroom'),('ME703','Robotics and Automation',3,'Lecture',3,1,'Classroom'),('ME703L','Robotics Laboratory',3,'Lab',1,2,'Computer Lab'),('ME704L','Manufacturing Processes Laboratory',3,'Lab',1,2,'Computer Lab');
INSERT INTO subject_requirements (subject_id,min_capacity,requires_projector,requires_smart_board,min_computers) SELECT subject_id,4,TRUE,CASE WHEN subject_code IN ('CS504','EC303','ME703') THEN TRUE ELSE FALSE END,CASE WHEN type='Lab' THEN 4 ELSE 0 END FROM subjects;

INSERT INTO rooms (room_number,building,capacity,projector_available,smart_board_available,is_active) VALUES
('CR-101','Main Academic Block',60,TRUE,TRUE,TRUE),('CR-102','Main Academic Block',60,TRUE,FALSE,TRUE),('CR-103','Main Academic Block',50,TRUE,TRUE,TRUE),('CR-104','Main Academic Block',45,TRUE,FALSE,TRUE),('CR-105','Main Academic Block',40,FALSE,FALSE,TRUE),('CR-201','Science Block',70,TRUE,TRUE,TRUE),('CR-202','Science Block',60,TRUE,FALSE,TRUE),('CR-203','Science Block',50,TRUE,TRUE,TRUE),('CR-204','Science Block',45,TRUE,FALSE,TRUE),('CR-301','Engineering Block',80,TRUE,TRUE,TRUE),('CR-302','Engineering Block',55,TRUE,FALSE,TRUE),('CR-303','Engineering Block',40,TRUE,TRUE,TRUE);
INSERT INTO labs (lab_name,building,capacity,computer_count,projector_available,specialized_equipment,is_active) VALUES
('Database and OS Lab','Tech Block',40,40,TRUE,'MySQL and Linux workstations',TRUE),('AI and Networks Lab','Tech Block',40,40,TRUE,'GPU workstations and Cisco routers',TRUE),('Programming Lab','Tech Block',35,35,TRUE,'Python, Java and C++ tools',TRUE),('Electronics Lab','Science Block',30,30,TRUE,'Oscilloscopes and microcontroller kits',TRUE),('CAD CAM Lab','Engineering Block',35,35,TRUE,'AutoCAD, ANSYS and CNC simulator',TRUE),('Robotics Lab','Engineering Block',30,30,TRUE,'Arduino, PLC and robotic arm kits',TRUE);
INSERT INTO equipment (equipment_name,quantity,location_lab_id,status) VALUES ('Cisco Router Rack',2,2,'Functional'),('GPU Workstation',12,2,'Functional'),('Digital Oscilloscope',15,4,'Functional'),('Robotic Arm Training Kit',6,6,'Functional'),('CNC Simulator Station',8,5,'Functional');

INSERT INTO time_slots (day_of_week,start_time,end_time,slot_order) VALUES
('Monday','08:30','09:30',1),('Monday','09:30','10:30',2),('Monday','10:30','11:30',3),('Monday','11:30','12:30',4),('Monday','12:30','13:30',5),('Monday','13:30','14:30',6),('Monday','14:30','15:30',7),('Monday','15:30','16:30',8),('Monday','16:30','17:30',9),
('Tuesday','08:30','09:30',1),('Tuesday','09:30','10:30',2),('Tuesday','10:30','11:30',3),('Tuesday','11:30','12:30',4),('Tuesday','12:30','13:30',5),('Tuesday','13:30','14:30',6),('Tuesday','14:30','15:30',7),('Tuesday','15:30','16:30',8),('Tuesday','16:30','17:30',9),
('Wednesday','08:30','09:30',1),('Wednesday','09:30','10:30',2),('Wednesday','10:30','11:30',3),('Wednesday','11:30','12:30',4),('Wednesday','12:30','13:30',5),('Wednesday','13:30','14:30',6),('Wednesday','14:30','15:30',7),('Wednesday','15:30','16:30',8),('Wednesday','16:30','17:30',9),
('Thursday','08:30','09:30',1),('Thursday','09:30','10:30',2),('Thursday','10:30','11:30',3),('Thursday','11:30','12:30',4),('Thursday','12:30','13:30',5),('Thursday','13:30','14:30',6),('Thursday','14:30','15:30',7),('Thursday','15:30','16:30',8),('Thursday','16:30','17:30',9),
('Friday','08:30','09:30',1),('Friday','09:30','10:30',2),('Friday','10:30','11:30',3),('Friday','11:30','12:30',4),('Friday','12:30','13:30',5),('Friday','13:30','14:30',6),('Friday','14:30','15:30',7),('Friday','15:30','16:30',8),('Friday','16:30','17:30',9);
INSERT INTO faculty_availability (faculty_id,slot_id,is_available) VALUES (1,1,FALSE),(2,9,FALSE),(7,17,FALSE),(12,25,FALSE);
INSERT INTO course_assignments (subject_id,faculty_id,section_id) VALUES
(1,1,1),(2,1,1),(3,2,1),(4,3,2),(5,3,2),(6,4,2),(7,5,3),(8,5,3),(9,7,4),(10,7,4),(11,8,5),(12,9,5),(13,9,5),(14,10,4),(15,12,6),(16,12,6),(17,13,7),(18,14,7),(19,14,7),(20,15,6);
