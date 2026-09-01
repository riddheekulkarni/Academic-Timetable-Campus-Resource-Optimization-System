"""
Dynamic Rescheduling Service
Handles live schedule updates and request approvals without breaking constraints.
"""
from database.db import get_cursor

class Rescheduler:
    @staticmethod
    def process_change_request(change_id, action):
        with get_cursor(commit=True) as (conn, cursor):
            cursor.execute("SELECT * FROM schedule_changes WHERE change_id = %s", (change_id,))
            req = cursor.fetchone()
            if not req:
                return False, "Request not found."

            if action == "REJECT":
                cursor.execute("UPDATE schedule_changes SET status = 'REJECTED' WHERE change_id = %s", (change_id,))
                return True, "Request rejected."

            if action == "APPROVE":
                tt_id = req["timetable_id"]
                if req["target_slot_id"]:
                    cursor.execute("UPDATE timetable SET slot_id = %s WHERE timetable_id = %s", (req["target_slot_id"], tt_id))
                
                if req["target_room_id"] or req["target_lab_id"]:
                    cursor.execute(
                        "UPDATE room_allocations SET room_id = %s, lab_id = %s WHERE timetable_id = %s",
                        (req["target_room_id"], req["target_lab_id"], tt_id)
                    )

                cursor.execute("UPDATE schedule_changes SET status = 'APPROVED' WHERE change_id = %s", (change_id,))
                return True, "Schedule modified successfully."

        return False, "Invalid action."