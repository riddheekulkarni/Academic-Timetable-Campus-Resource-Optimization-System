"""
Campus Infrastructure Resource Model
Handles Classrooms, Computer Laboratories, and Specialized Hardware Assets.
"""
from database.db import get_cursor

class ResourceModel:
    # --- Classrooms ---
    @staticmethod
    def get_rooms():
        with get_cursor() as (conn, cursor):
            cursor.execute("SELECT * FROM rooms ORDER BY room_id DESC")
            return cursor.fetchall()

    @staticmethod
    def get_room_by_id(room_id):
        with get_cursor() as (conn, cursor):
            cursor.execute("SELECT * FROM rooms WHERE room_id = %s", (room_id,))
            return cursor.fetchone()

    @staticmethod
    def create_room(room_number, building, capacity, projector=True, smart_board=False):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("""
                INSERT INTO rooms (room_number, building, capacity, projector_available, smart_board_available)
                VALUES (%s, %s, %s, %s, %s)
            """, (room_number, building, capacity, projector, smart_board))
            return cursor.lastrowid

    @staticmethod
    def update_room(room_id, room_number, building, capacity, projector=True, smart_board=False):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("""
                UPDATE rooms
                SET room_number = %s, building = %s, capacity = %s,
                    projector_available = %s, smart_board_available = %s
                WHERE room_id = %s
            """, (room_number, building, capacity, projector, smart_board, room_id))
            return True

    @staticmethod
    def delete_room(room_id):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("DELETE FROM rooms WHERE room_id = %s", (room_id,))
            return True

    # --- Laboratories ---
    @staticmethod
    def get_labs():
        with get_cursor() as (conn, cursor):
            cursor.execute("SELECT * FROM labs ORDER BY lab_id DESC")
            return cursor.fetchall()

    @staticmethod
    def get_lab_by_id(lab_id):
        with get_cursor() as (conn, cursor):
            cursor.execute("SELECT * FROM labs WHERE lab_id = %s", (lab_id,))
            return cursor.fetchone()

    @staticmethod
    def create_lab(lab_name, building, capacity, computer_count, projector=True, specs=""):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("""
                INSERT INTO labs (lab_name, building, capacity, computer_count, projector_available, specialized_equipment)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (lab_name, building, capacity, computer_count, projector, specs))
            return cursor.lastrowid

    @staticmethod
    def update_lab(lab_id, lab_name, building, capacity, computer_count, projector=True, specs=""):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("""
                UPDATE labs
                SET lab_name = %s, building = %s, capacity = %s,
                    computer_count = %s, projector_available = %s, specialized_equipment = %s
                WHERE lab_id = %s
            """, (lab_name, building, capacity, computer_count, projector, specs, lab_id))
            return True

    @staticmethod
    def delete_lab(lab_id):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("DELETE FROM labs WHERE lab_id = %s", (lab_id,))
            return True

    # --- Equipment ---
    @staticmethod
    def get_equipment():
        with get_cursor() as (conn, cursor):
            cursor.execute("""
                SELECT e.*, r.room_number, l.lab_name
                FROM equipment e
                LEFT JOIN rooms r ON e.location_room_id = r.room_id
                LEFT JOIN labs l ON e.location_lab_id = l.lab_id
                ORDER BY e.equipment_id DESC
            """)
            return cursor.fetchall()