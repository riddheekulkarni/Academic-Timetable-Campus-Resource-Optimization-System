"""
Room & Laboratory Allocator
Selects the best available classroom/lab for a given assignment and time slot.
"""
from database.db import get_cursor

class RoomAllocator:
    @staticmethod
    def get_suitable_resources(assignment):
        """Fetches all active rooms or labs satisfying capacity and hardware requirements."""
        req_type = assignment.get("required_room_type")
        students = assignment.get("student_count", 0)
        min_computers = assignment.get("min_computers", 0)
        requires_proj = assignment.get("requires_projector", False)

        resources = []
        with get_cursor() as (conn, cursor):
            if req_type == "Classroom":
                query = "SELECT room_id AS id, room_number AS name, capacity, projector_available, 'room' AS type FROM rooms WHERE is_active = TRUE AND capacity >= %s"
                params = [students]
                if requires_proj:
                    query += " AND projector_available = TRUE"
                query += " ORDER BY capacity ASC"
                cursor.execute(query, params)
                resources = cursor.fetchall()
            else:
                query = "SELECT lab_id AS id, lab_name AS name, capacity, computer_count, 'lab' AS type FROM labs WHERE is_active = TRUE AND capacity >= %s AND computer_count >= %s ORDER BY capacity ASC"
                cursor.execute(query, (students, min_computers))
                resources = cursor.fetchall()

        return resources