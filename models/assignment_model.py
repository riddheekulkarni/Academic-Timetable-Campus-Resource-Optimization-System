"""
Course Assignment Model
Maps Subjects to Faculty and Student Sections/Batches.
"""
from database.db import get_cursor

class AssignmentModel:
    @staticmethod
    def get_all():
        with get_cursor() as (conn, cursor):
            cursor.execute("""
                SELECT ca.assignment_id, ca.subject_id, ca.faculty_id, ca.section_id,
                       s.subject_code, s.subject_name, s.type AS subject_type, s.lectures_per_week,
                       f.name AS faculty_name, f.faculty_code,
                       sec.section_name, sec.academic_year, sec.student_count,
                       d.dept_name
                FROM course_assignments ca
                JOIN subjects s ON ca.subject_id = s.subject_id
                JOIN faculty f ON ca.faculty_id = f.faculty_id
                JOIN sections sec ON ca.section_id = sec.section_id
                JOIN departments d ON s.dept_id = d.dept_id
                ORDER BY ca.assignment_id DESC
            """)
            return cursor.fetchall()

    @staticmethod
    def create(subject_id, faculty_id, section_id):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("""
                INSERT INTO course_assignments (subject_id, faculty_id, section_id)
                VALUES (%s, %s, %s)
            """, (subject_id, faculty_id, section_id))
            return cursor.lastrowid

    @staticmethod
    def update(assignment_id, subject_id, faculty_id, section_id):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("""
                UPDATE course_assignments
                SET subject_id = %s, faculty_id = %s, section_id = %s
                WHERE assignment_id = %s
            """, (subject_id, faculty_id, section_id, assignment_id))
            return True

    @staticmethod
    def delete(assignment_id):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("DELETE FROM course_assignments WHERE assignment_id = %s", (assignment_id,))
            return True
