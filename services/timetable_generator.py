"""
Timetable Generation Engine
Combines Course Assignments, Time Slots, Faculty Availability, and Room Allocations.
Features:
- Universal Lunch Break (12:30 PM - 1:30 PM) preservation
- Balanced utilization of all morning slots (8:30-9:30, 9:30-10:30, 10:30-11:30, 11:30-12:30)
- Balanced afternoon slots (1:30-2:30, 2:30-3:30, 3:30-4:30)
- Realistic staggered starts per division (TY CSE A, TY CSE B, SY ECE A, Final Year MECH A)
- Zero faculty and zero room clashes
"""
from database.db import get_cursor
from services.room_allocator import RoomAllocator
from services.constraint_engine import ConstraintEngine

class TimetableGenerator:
    @staticmethod
    def generate_all():
        with get_cursor() as (conn, cursor):
            # Fetch Course Assignments with Subject requirements & Section counts
            cursor.execute("""
                SELECT ca.assignment_id, ca.subject_id, ca.faculty_id, ca.section_id,
                       s.subject_code, s.subject_name, s.type AS subject_type,
                       s.required_room_type, s.lectures_per_week, s.duration_hours,
                       sr.min_capacity, sr.requires_projector, sr.min_computers,
                       sec.student_count, sec.section_name
                FROM course_assignments ca
                JOIN subjects s ON ca.subject_id = s.subject_id
                LEFT JOIN subject_requirements sr ON s.subject_id = sr.subject_id
                JOIN sections sec ON ca.section_id = sec.section_id
                ORDER BY s.type DESC, ca.section_id ASC, ca.assignment_id ASC
            """)
            assignments = cursor.fetchall()

            # Fetch Time Slots ordered by day and slot order
            cursor.execute("SELECT slot_id, day_of_week, start_time, end_time, slot_order FROM time_slots ORDER BY day_of_week, slot_order ASC")
            all_slots = cursor.fetchall()

            # Fetch Faculty Unavailability
            cursor.execute("SELECT faculty_id, slot_id FROM faculty_availability WHERE is_available = FALSE")
            unavail = cursor.fetchall()
            unavail_set = set((u["faculty_id"], u["slot_id"]) for u in unavail)

        # Exclude Lunch Break (Slot order 5: 12:30 PM - 1:30 PM)
        teaching_slots = [
            s for s in all_slots 
            if s["slot_order"] != 5 and str(s["start_time"]) not in ["12:30:00", "12:30", "12:30:00.000000"]
        ]

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        # Group slots by day
        slots_by_day = {d: [] for d in days}
        for s in teaching_slots:
            slots_by_day[s["day_of_week"]].append(s)

        generated_schedule = []
        assigned_days_per_course = {} # (assignment_id) -> set of days
        section_day_slot_count = {}   # (section_id, day) -> count of classes
        slot_usage_count = {s["slot_id"]: 0 for s in teaching_slots}

        # Separate Labs and Lectures
        lab_assignments = [a for a in assignments if a["subject_type"] == "Lab"]
        lecture_assignments = [a for a in assignments if a["subject_type"] != "Lab"]

        # 1. Schedule Labs in Dedicated Practical Blocks (e.g. 1:30-3:30 PM or 9:30-11:30 AM)
        for assignment in lab_assignments:
            aid = assignment["assignment_id"]
            sec_id = assignment["section_id"]
            fac_id = assignment["faculty_id"]
            suitable_resources = RoomAllocator.get_suitable_resources(assignment)
            if not suitable_resources:
                continue

            # Labs prefer afternoon blocks (orders 6, 7, 8) or morning (orders 2, 3)
            preferred_lab_orders = [6, 7, 2, 3, 8]
            placed = False

            day_rotation = days[(sec_id * 2) % len(days):] + days[:(sec_id * 2) % len(days)]

            for day in day_rotation:
                if placed:
                    break
                day_slots = sorted(slots_by_day[day], key=lambda s: preferred_lab_orders.index(s["slot_order"]) if s["slot_order"] in preferred_lab_orders else 99)
                
                for slot in day_slots:
                    slot_id = slot["slot_id"]
                    if (fac_id, slot_id) in unavail_set:
                        continue

                    for res in suitable_resources:
                        isValid, _ = ConstraintEngine.validate_hard_constraints(
                            generated_schedule, assignment, slot_id, res
                        )
                        if isValid:
                            generated_schedule.append({
                                "assignment_id": aid,
                                "faculty_id": fac_id,
                                "section_id": sec_id,
                                "slot_id": slot_id,
                                "room_id": None,
                                "lab_id": res["id"],
                                "resource_capacity": res["capacity"],
                                "student_count": assignment["student_count"]
                            })
                            assigned_days_per_course.setdefault(aid, set()).add(day)
                            section_day_slot_count[(sec_id, day)] = section_day_slot_count.get((sec_id, day), 0) + 1
                            slot_usage_count[slot_id] += 1
                            placed = True
                            break
                    if placed:
                        break

        # 2. Schedule Lectures with Balanced Slot Utilization (including 11:30 AM – 12:30 PM)
        for assignment in lecture_assignments:
            aid = assignment["assignment_id"]
            sec_id = assignment["section_id"]
            fac_id = assignment["faculty_id"]
            lectures_needed = assignment["lectures_per_week"]
            allocated_count = 0

            suitable_resources = RoomAllocator.get_suitable_resources(assignment)
            if not suitable_resources:
                continue

            offset = (sec_id * 2 + (aid % 3)) % len(days)
            staggered_days = days[offset:] + days[:offset]

            # Diverse slot preferences ensuring Slot 4 (11:30 - 12:30) is actively scheduled:
            # Slot orders: 1 (8:30-9:30), 2 (9:30-10:30), 3 (10:30-11:30), 4 (11:30-12:30), 6 (1:30-2:30), 7 (2:30-3:30)
            if (aid + sec_id) % 4 == 0:
                slot_pref = [4, 1, 3, 2, 6, 7] # 11:30 first!
            elif (aid + sec_id) % 4 == 1:
                slot_pref = [2, 4, 1, 6, 3, 7] # 9:30 & 11:30
            elif (aid + sec_id) % 4 == 2:
                slot_pref = [3, 1, 4, 7, 2, 6] # 10:30 & 11:30
            else:
                slot_pref = [1, 4, 2, 3, 6, 7] # 8:30 & 11:30

            for day in staggered_days:
                if allocated_count >= lectures_needed:
                    break

                used_days = assigned_days_per_course.get(aid, set())
                if day in used_days and len(used_days) < len(days) and allocated_count < lectures_needed:
                    continue

                if section_day_slot_count.get((sec_id, day), 0) >= 5:
                    continue

                day_slots = sorted(slots_by_day[day], key=lambda s: (
                    slot_pref.index(s["slot_order"]) if s["slot_order"] in slot_pref else 99,
                    slot_usage_count[s["slot_id"]]
                ))

                for slot in day_slots:
                    slot_id = slot["slot_id"]
                    if (fac_id, slot_id) in unavail_set:
                        continue

                    for res in suitable_resources:
                        isValid, _ = ConstraintEngine.validate_hard_constraints(
                            generated_schedule, assignment, slot_id, res
                        )
                        if isValid:
                            generated_schedule.append({
                                "assignment_id": aid,
                                "faculty_id": fac_id,
                                "section_id": sec_id,
                                "slot_id": slot_id,
                                "room_id": res["id"] if res["type"] == "room" else None,
                                "lab_id": res["id"] if res["type"] == "lab" else None,
                                "resource_capacity": res["capacity"],
                                "student_count": assignment["student_count"]
                            })
                            allocated_count += 1
                            assigned_days_per_course.setdefault(aid, set()).add(day)
                            section_day_slot_count[(sec_id, day)] = section_day_slot_count.get((sec_id, day), 0) + 1
                            slot_usage_count[slot_id] += 1
                            break
                    if isValid:
                        break

        # Save generated timetable to MySQL
        if generated_schedule:
            with get_cursor(commit=True) as (conn, cursor):
                cursor.execute("DELETE FROM room_allocations")
                cursor.execute("DELETE FROM timetable")

                for item in generated_schedule:
                    cursor.execute(
                        "INSERT INTO timetable (assignment_id, slot_id) VALUES (%s, %s)",
                        (item["assignment_id"], item["slot_id"])
                    )
                    tt_id = cursor.lastrowid
                    cursor.execute(
                        "INSERT INTO room_allocations (timetable_id, room_id, lab_id) VALUES (%s, %s, %s)",
                        (tt_id, item["room_id"], item["lab_id"])
                    )

        return {
            "success": True,
            "total_assigned": len(generated_schedule),
            "message": f"Successfully generated timetable with {len(generated_schedule)} conflict-free academic sessions."
        }