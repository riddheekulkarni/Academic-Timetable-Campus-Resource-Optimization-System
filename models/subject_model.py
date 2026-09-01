"""
Subject & Curriculum Data Model
Handles subject definitions, lecture/lab types, and room/equipment prerequisites.
"""
from database.db import get_cursor

class SubjectModel:
    @staticmethod
    def get_all():
        with get_cursor() as (conn, cursor):
            cursor.execute("""
                SELECT s.*, d.dept_name, r.min_capacity, r.requires_projector, 
                       r.requires_smart_board, r.min_computers, r.special_equipment_needed
                FROM subjects s
                JOIN departments d ON s.dept_id = d.dept_id
                LEFT JOIN subject_requirements r ON s.subject_id = r.subject_id
                ORDER BY s.subject_id DESC
            """)
            return cursor.fetchall()

    @staticmethod
    def get_by_id(subject_id):
        with get_cursor() as (conn, cursor):
            cursor.execute("""
                SELECT s.*, d.dept_name, r.min_capacity, r.requires_projector, 
                       r.requires_smart_board, r.min_computers, r.special_equipment_needed
                FROM subjects s
                JOIN departments d ON s.dept_id = d.dept_id
                LEFT JOIN subject_requirements r ON s.subject_id = r.subject_id
                WHERE s.subject_id = %s
            """, (subject_id,))
            return cursor.fetchone()

    @staticmethod
    def create(code, name, dept_id, s_type, lectures_per_week=3, duration_hours=1, req_room_type="Classroom", min_cap=30, proj=False, smart=False, min_comp=0):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("""
                INSERT INTO subjects (subject_code, subject_name, dept_id, type, lectures_per_week, duration_hours, required_room_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (code, name, dept_id, s_type, lectures_per_week, duration_hours, req_room_type))
            subject_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO subject_requirements (subject_id, min_capacity, requires_projector, requires_smart_board, min_computers)
                VALUES (%s, %s, %s, %s, %s)
            """, (subject_id, min_cap, proj, smart, min_comp))
            return subject_id

    @staticmethod
    def update(subject_id, code, name, dept_id, s_type, lectures_per_week=3, duration_hours=1, req_room_type="Classroom", min_cap=30, proj=False, smart=False, min_comp=0):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("""
                UPDATE subjects
                SET subject_code = %s, subject_name = %s, dept_id = %s, type = %s,
                    lectures_per_week = %s, duration_hours = %s, required_room_type = %s
                WHERE subject_id = %s
            """, (code, name, dept_id, s_type, lectures_per_week, duration_hours, req_room_type, subject_id))

            cursor.execute("""
                INSERT INTO subject_requirements (subject_id, min_capacity, requires_projector, requires_smart_board, min_computers)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                min_capacity = VALUES(min_capacity),
                requires_projector = VALUES(requires_projector),
                requires_smart_board = VALUES(requires_smart_board),
                min_computers = VALUES(min_computers)
            """, (subject_id, min_cap, proj, smart, min_comp))
            return True

    @staticmethod
    def delete(subject_id):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("DELETE FROM subjects WHERE subject_id = %s", (subject_id,))
            return True