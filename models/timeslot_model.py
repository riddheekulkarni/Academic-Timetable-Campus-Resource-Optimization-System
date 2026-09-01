"""
Time Slot Model
Manages operational period schedules.
"""
from database.db import get_cursor

class TimeSlotModel:
    @staticmethod
    def get_all():
        with get_cursor() as (conn, cursor):
            cursor.execute("SELECT * FROM time_slots ORDER BY slot_id ASC")
            return cursor.fetchall()

    @staticmethod
    def create(day, start, end, order):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("""
                INSERT INTO time_slots (day_of_week, start_time, end_time, slot_order)
                VALUES (%s, %s, %s, %s)
            """, (day, start, end, order))
            return cursor.lastrowid