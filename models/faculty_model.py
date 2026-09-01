"""
Faculty Data Management Model
Handles CRUD operations for teaching staff.
"""
from database.db import get_cursor
from utils.auth import hash_password

class FacultyModel:
    @staticmethod
    def get_all():
        with get_cursor() as (conn, cursor):
            cursor.execute("""
                SELECT f.faculty_id, f.user_id, f.faculty_code, f.name, f.dept_id, 
                       d.dept_name, f.designation, u.email
                FROM faculty f
                JOIN users u ON f.user_id = u.user_id
                JOIN departments d ON f.dept_id = d.dept_id
                ORDER BY f.faculty_id DESC
            """)
            return cursor.fetchall()

    @staticmethod
    def get_by_id(faculty_id):
        with get_cursor() as (conn, cursor):
            cursor.execute("""
                SELECT f.faculty_id, f.user_id, f.faculty_code, f.name, f.dept_id, 
                       d.dept_name, f.designation, u.email
                FROM faculty f
                JOIN users u ON f.user_id = u.user_id
                JOIN departments d ON f.dept_id = d.dept_id
                WHERE f.faculty_id = %s
            """, (faculty_id,))
            return cursor.fetchone()

    @staticmethod
    def create(name, email, password, faculty_code, dept_id, designation):
        hashed = hash_password(password or "password123")
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, 'FACULTY')",
                (email, hashed)
            )
            user_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO faculty (user_id, faculty_code, name, dept_id, designation)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, faculty_code, name, dept_id, designation))
            return cursor.lastrowid

    @staticmethod
    def update(faculty_id, name, email, faculty_code, dept_id, designation, password=None):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT user_id FROM faculty WHERE faculty_id = %s", (faculty_id,))
            row = cursor.fetchone()
            if not row:
                return False
            user_id = row["user_id"]

            cursor.execute("""
                UPDATE faculty
                SET faculty_code = %s, name = %s, dept_id = %s, designation = %s
                WHERE faculty_id = %s
            """, (faculty_code, name, dept_id, designation, faculty_id))

            if password:
                hashed = hash_password(password)
                cursor.execute("UPDATE users SET email = %s, password_hash = %s WHERE user_id = %s", (email, hashed, user_id))
            else:
                cursor.execute("UPDATE users SET email = %s WHERE user_id = %s", (email, user_id))
            return True

    @staticmethod
    def delete(faculty_id):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT user_id FROM faculty WHERE faculty_id = %s", (faculty_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute("DELETE FROM users WHERE user_id = %s", (row["user_id"],))
                return True
            return False