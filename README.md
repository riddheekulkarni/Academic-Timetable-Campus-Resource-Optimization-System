# 📅 Academic Timetable & Campus Resource Optimization System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.3-black?style=for-the-badge&logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-blue?style=for-the-badge&logo=mysql)
![JWT](https://img.shields.io/badge/JWT-Authentication-orange?style=for-the-badge&logo=jsonwebtokens)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

An intelligent, full-stack enterprise solution for automated academic timetable generation, campus resource allocation, and schedule conflict resolution. Built with **Flask**, **MySQL**, and **Vanilla JavaScript**, the system leverages a **Constraint Satisfaction Engine** to construct conflict-free class and laboratory schedules across departments, faculties, and student cohorts.

---

## 🌟 Table of Contents

- [Key Features](#-key-features)
- [Architecture & System Overview](#-architecture--system-overview)
- [Technology Stack](#-technology-stack)
- [Algorithmic & Constraint Engine Specifications](#-algorithmic--constraint-engine-specifications)
- [Database Schema](#-database-schema)
- [Project Directory Structure](#-project-directory-structure)
- [Installation & Environment Setup](#-installation--environment-setup)
- [API Reference](#-api-reference)
- [User Roles & Dashboard Capabilities](#-user-roles--dashboard-capabilities)
- [License & Acknowledgments](#-license--acknowledgments)

---

## 🔑 Key Features

### 🤖 1. Automated Timetable Generation
* **Zero Clashes Guarantee**: Evaluates hard constraints to prevent faculty double-booking, student section overlap, and classroom/lab room collisions.
* **Universal Lunch Break**: Automatically reserves 12:30 PM – 1:30 PM for lunch across all programs.
* **Lab vs. Lecture Prioritization**: Intelligently allocates 2-hour practical lab slots in dedicated morning/afternoon blocks while distributing lectures evenly across available time slots.
* **Staggered Scheduling**: Avoids bottlenecks by balancing morning (8:30 AM – 12:30 PM) and afternoon (1:30 PM – 4:30 PM) sessions per section.

### 🏛️ 2. Smart Campus Resource Allocation
* **Capacity & Feature Matching**: Matches course requirements (batch size, projector requirement, lab computer count) with appropriate classrooms and computer labs.
* **Wastage Optimization**: Applies soft penalty scoring to minimize underutilization of high-capacity halls for small batches.

### 🔄 3. Dynamic Rescheduling & Request Workflow
* **Faculty Change Requests**: Faculty can request session swaps or reschedules with reason tracking.
* **Admin Approval Workflow**: Admins review, approve, or decline pending schedule requests with automated database state updating.

### 🔐 4. Role-Based Access Control (RBAC) & JWT Auth
* Secure authentication using **PyJWT** and **Werkzeug** PBKDF2 password hashing.
* Multi-tenant authorization boundaries tailored for **Admins**, **Faculty**, and **Students**.

---

## 🏗️ Architecture & System Overview

```
                          ┌──────────────────────────────┐
                          │   Frontend UI Dashboard      │
                          │ (Admin / Faculty / Student)  │
                          └──────────────┬───────────────┘
                                         │ HTTP REST (JSON + JWT)
                                         ▼
                          ┌──────────────────────────────┐
                          │       Flask Application      │
                          │          (`app.py`)          │
                          └──────────────┬───────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
┌──────────────┐                 ┌──────────────┐                 ┌──────────────┐
│  Auth & RBAC │                 │ REST Routers │                 │ Scheduler    │
│ (`utils/auth`)                 │ (`/routes`)  │                 │ Engine       │
└──────────────┘                 └──────────────┘                 └──────┬───────┘
                                                                         │
                                         ┌───────────────────────────────┴───────────────────────────────┐
                                         ▼                                                               ▼
                          ┌──────────────────────────────┐                               ┌──────────────────────────────┐
                          │     Constraint Engine        │                               │       Room Allocator         │
                          │(`services/constraint_engine`)│                               │  (`services/room_allocator`) │
                          └──────────────────────────────┘                               └──────────────────────────────┘
                                         │                                                               │
                                         └───────────────────────────────┬───────────────────────────────┘
                                                                         ▼
                                                          ┌──────────────────────────────┐
                                                          │   MySQL Relational Database  │
                                                          │     (`database/db.py`)       │
                                                          └──────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.9+, Flask 3.0 | Web application framework & REST API server |
| **Database** | MySQL 8.0+ | Relational data persistence & transactional integrity |
| **Database Connector** | `mysql-connector-python` | Native Python driver for MySQL connection pooling |
| **Authentication** | PyJWT, Werkzeug Security | Secure token-based auth & PBKDF2 password hashing |
| **Frontend** | HTML5, CSS3 (Vanilla), JavaScript | Responsive UI with modern dark mode styling & dynamic fetching |
| **Cross-Origin** | Flask-Cors | CORS middleware configuration |

---

## 🧮 Algorithmic & Constraint Engine Specifications

The core engine ([`services/timetable_generator.py`](file:///c:/Users/hp/Desktop/Riddhee/Projects/Academic_Scheduler/services/timetable_generator.py)) applies a Constraint Satisfaction Problem (CSP) heuristic approach to timetable generation:

### Hard Constraints (Must be satisfied 100%)
1. **Room & Lab Feature Compatibility**: Course types strictly dictate resource assignment (Lectures $\rightarrow$ Classrooms; Labs $\rightarrow$ Computer Laboratories with minimum required computers).
2. **Capacity Bounds**: $Capacity_{Resource} \ge Section\_Student\_Count$.
3. **Faculty Non-Overlap**: No faculty member can be assigned to multiple sessions during the same time slot ($Slot_{ID}$).
4. **Student Batch Non-Overlap**: No student section can attend multiple classes simultaneously.
5. **Resource Double-Booking**: Classrooms and labs cannot host overlapping sessions.

### Soft Constraints (Optimized via Penalty Scoring)
* **Capacity Wastage Penalty**: Penalizes assigning large lecture halls ($Capacity > Section + 25$) to small sections to preserve room availability.
* **Balanced Slot Distribution**: Prefers spreading section classes across all days of the week rather than clustering on single days.

---

## 🗄️ Database Schema

The database consists of 15 normalized tables ([`database/schema.sql`](file:///c:/Users/hp/Desktop/Riddhee/Projects/Academic_Scheduler/database/schema.sql)):

* `users` – Core credentials & role definitions (`ADMIN`, `FACULTY`, `STUDENT`).
* `departments` & `sections` – Academic organizational units & batch student counts.
* `students` & `faculty` – Role profiles linked to `users`.
* `subjects` & `subject_requirements` – Course codes, lecture counts, lab specs, required equipment.
* `rooms` & `labs` – Campus infrastructure, seat capacities, computer counts, projector flags.
* `time_slots` – Weekly periods (Monday–Friday, 8:30 AM to 4:30 PM).
* `faculty_availability` – Faculty slot preference matrix.
* `course_assignments` – Mapping of Subject $\leftrightarrow$ Faculty $\leftrightarrow$ Section.
* `timetable` & `room_allocations` – Generated schedule output with allocated rooms/labs.
* `schedule_changes` – Change request history & approval status.

---

## 📁 Project Directory Structure

```
Academic_Scheduler/
├── app.py                      # Main Flask application initialization & static routes
├── config.py                   # Centralized configuration & environment loader
├── requirements.txt            # Python dependency specifications
├── .env.example                # Sample environment configuration template
├── database/
│   ├── db.py                   # Database connection helper & context manager
│   ├── schema.sql              # Complete DDL script for database creation
│   └── seed.sql                # Initial seed data (users, courses, rooms, slots)
├── models/                     # Data access layer modules
│   ├── assignment_model.py
│   ├── faculty_model.py
│   ├── resource_model.py
│   ├── student_model.py
│   ├── subject_model.py
│   └── timeslot_model.py
├── routes/                     # REST API Blueprint controllers
│   ├── admin_routes.py         # Admin management & CRUD endpoints
│   ├── auth_routes.py          # Authentication & token verification endpoints
│   ├── schedule_routes.py      # Rescheduling & availability endpoints
│   └── timetable_routes.py     # Timetable generation & fetching endpoints
├── services/                   # Business logic & scheduling algorithms
│   ├── constraint_engine.py    # Hard & soft constraint evaluation engine
│   ├── rescheduler.py          # Dynamic schedule change workflow handler
│   ├── room_allocator.py       # Resource matching logic
│   └── timetable_generator.py  # CSP timetable generation algorithm
├── utils/
│   └── auth.py                 # JWT token generation & verification decorators
└── frontend/                   # Client UI assets
    ├── index.html              # Landing / Login page
    ├── admin/                  # Admin dashboard & management interfaces
    ├── faculty/                # Faculty timetable & request interface
    ├── student/                # Student timetable viewer interface
    ├── css/                    # Custom stylesheets
    └── js/                     # Client-side JavaScript modules
```

---

## 💻 Installation & Environment Setup

### Prerequisites
* **Python 3.9+** installed.
* **MySQL Server 8.0+** running locally or accessible over network.

### 1. Clone & Setup Workspace
```bash
git clone https://github.com/your-repo/academic-scheduler.git
cd academic-scheduler
```

### 2. Create Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Activate on Linux / macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Initialization
Log into MySQL terminal or use MySQL Workbench to run the database setup scripts:

```bash
# Execute schema setup
mysql -u root -p < database/schema.sql

# Load sample dataset
mysql -u root -p academic_scheduler < database/seed.sql
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your database credentials:

```ini
SECRET_KEY=your-super-secret-jwt-key
FLASK_DEBUG=True

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=YourPassword123
MYSQL_DATABASE=academic_scheduler

TOKEN_EXPIRY_HOURS=12
```

### 5. Run the Application Server
```bash
python app.py
```
The server will start at `http://localhost:5000`. Access the web portal directly in your browser.

---

## 📡 API Reference

### Auth Endpoints (`/api`)
| Endpoint | Method | Role | Description |
| :--- | :--- | :--- | :--- |
| `/api/login` | `POST` | Public | Authenticates user & returns JWT token |
| `/api/me` | `GET` | Authenticated | Retrieves current authenticated profile |
| `/api/health` | `GET` | Public | System status health check |
| `/api/db-check` | `GET` | Public | Database connection check |

### Timetable Endpoints (`/api`)
| Endpoint | Method | Role | Description |
| :--- | :--- | :--- | :--- |
| `/api/timetable/generate` | `POST` | `ADMIN` | Triggers timetable generation engine |
| `/api/timetable` | `GET` | Authenticated | Fetches role-scoped schedule matrix |

### Admin Data Endpoints (`/api`)
| Endpoint | Method | Role | Description |
| :--- | :--- | :--- | :--- |
| `/api/admin/stats` | `GET` | `ADMIN` | Dashboard counters & optimization metrics |
| `/api/students` | `GET`, `POST` | `ADMIN` | List all or add new student profile |
| `/api/students/<id>` | `GET`, `PUT`, `DELETE` | `ADMIN` | Student record management |
| `/api/faculty` | `GET`, `POST` | `ADMIN` | List all or add new faculty member |
| `/api/subjects` | `GET`, `POST` | `ADMIN` | Subject catalog management |
| `/api/rooms` | `GET`, `POST` | `ADMIN` | Classroom inventory management |
| `/api/labs` | `GET`, `POST` | `ADMIN` | Laboratory inventory management |
| `/api/assignments` | `GET`, `POST` | `ADMIN` | Course assignment allocations |

### Rescheduling Endpoints (`/api`)
| Endpoint | Method | Role | Description |
| :--- | :--- | :--- | :--- |
| `/api/schedule/change-request` | `GET`, `POST` | Authenticated | View or submit schedule change request |
| `/api/schedule/change-request/<id>/action` | `POST` | `ADMIN` | Approve or decline change request |

---

## 👤 User Roles & Dashboard Capabilities

### 🛡️ System Administrator
* Execute the automatic timetable generator.
* Full CRUD access for Faculty, Students, Subjects, Rooms, Labs, and Course Assignments.
* Review dashboard analytics and manage schedule change requests.

### 👨‍🏫 Faculty Member
* Access personal weekly teaching schedule.
* View room and lab allocations per lecture.
* Submit schedule modification and swap requests to the administration.

### 🎓 Student
* View personalized section timetable based on enrolled academic year and division.
* Check daily class locations, time slots, and assigned instructors.

---

## 📄 License & Acknowledgments

This project is licensed under the **MIT License**.

Built for academic institutions seeking an open, extensible, and high-performance solution for automated schedule generation and resource optimization.
