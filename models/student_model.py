"""
Student Data Management Model
Handles CRUD operations for students and associated user auth accounts.
"""
from database.db import get_cursor
from utils.auth import hash_password

class StudentModel:
    @staticmethod
    def get_all():
        with get_cursor() as (conn, cursor):
            cursor.execute("""
                SELECT s.student_id, s.user_id, s.student_code, s.name, s.dept_id, 
                       d.dept_name, s.academic_year, s.section_id, sec.section_name, u.email
                FROM students s
                JOIN users u ON s.user_id = u.user_id
                JOIN departments d ON s.dept_id = d.dept_id
                LEFT JOIN sections sec ON s.section_id = sec.section_id
                ORDER BY s.student_id DESC
            """)
            return cursor.fetchall()

    @staticmethod
    def get_by_id(student_id):
        with get_cursor() as (conn, cursor):
            cursor.execute("""
                SELECT s.student_id, s.user_id, s.student_code, s.name, s.dept_id, 
                       d.dept_name, s.academic_year, s.section_id, sec.section_name, u.email
                FROM students s
                JOIN users u ON s.user_id = u.user_id
                JOIN departments d ON s.dept_id = d.dept_id
                LEFT JOIN sections sec ON s.section_id = sec.section_id
                WHERE s.student_id = %s
            """, (student_id,))
            return cursor.fetchone()

    @staticmethod
    def create(name, email, password, student_code, dept_id, academic_year, section_id=None):
        hashed = hash_password(password or "password123")
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, 'STUDENT')",
                (email, hashed)
            )
            user_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO students (user_id, student_code, name, dept_id, academic_year, section_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, student_code, name, dept_id, academic_year, section_id or None))
            return cursor.lastrowid

    @staticmethod
    def update(student_id, name, email, student_code, dept_id, academic_year, section_id=None, password=None):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT user_id FROM students WHERE student_id = %s", (student_id,))
            row = cursor.fetchone()
            if not row:
                return False
            user_id = row["user_id"]

            # Update student record
            cursor.execute("""
                UPDATE students 
                SET student_code = %s, name = %s, dept_id = %s, academic_year = %s, section_id = %s
                WHERE student_id = %s
            """, (student_code, name, dept_id, academic_year, section_id or None, student_id))

            # Update user email and optionally password
            if password:
                hashed = hash_password(password)
                cursor.execute("UPDATE users SET email = %s, password_hash = %s WHERE user_id = %s", (email, hashed, user_id))
            else:
                cursor.execute("UPDATE users SET email = %s WHERE user_id = %s", (email, user_id))
            return True

    @staticmethod
    def delete(student_id):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT user_id FROM students WHERE student_id = %s", (student_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute("DELETE FROM users WHERE user_id = %s", (row["user_id"],))
                return True
            return False
            