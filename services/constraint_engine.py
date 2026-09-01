"""
Constraint Engine
Evaluates Hard Constraints and calculates Soft Constraint optimization penalty scores.
"""
class ConstraintEngine:
    @staticmethod
    def validate_hard_constraints(current_schedule, assignment, slot_id, resource):
        """
        Validates whether placing an assignment into (slot_id, resource) causes hard clashes.
        current_schedule: list of dicts with keys: assignment_id, faculty_id, section_id, slot_id, room_id, lab_id
        """
        req_room_type = assignment.get("required_room_type")
        students_count = assignment.get("student_count", 0)

        # 1. Room / Lab Type Match
        if req_room_type == "Classroom" and resource.get("type") != "room":
            return False, "Lecture requires a Classroom"
        if req_room_type == "Computer Lab" and resource.get("type") != "lab":
            return False, "Lab requires a Computer Laboratory"

        # 2. Capacity Constraint
        if resource.get("capacity", 0) < students_count:
            return False, f"Resource capacity ({resource.get('capacity')}) is less than batch size ({students_count})"

        # 3. Computer Count Constraint (for Labs)
        if resource.get("type") == "lab":
            min_computers = assignment.get("min_computers", 0)
            if resource.get("computer_count", 0) < min_computers:
                return False, f"Lab computer count ({resource.get('computer_count')}) insufficient for requirement ({min_computers})"

        # 4. Check Against Existing Schedule Allocations
        for entry in current_schedule:
            if entry["slot_id"] == slot_id:
                # Faculty Conflict
                if entry["faculty_id"] == assignment["faculty_id"]:
                    return False, "Faculty clash detected"
                # Batch / Section Conflict
                if entry["section_id"] == assignment["section_id"]:
                    return False, "Student batch clash detected"
                # Room Conflict
                if resource.get("type") == "room" and entry.get("room_id") == resource.get("id"):
                    return False, "Classroom double booking detected"
                # Lab Conflict
                if resource.get("type") == "lab" and entry.get("lab_id") == resource.get("id"):
                    return False, "Laboratory double booking detected"

        return True, "Valid"

    @staticmethod
    def calculate_score(schedule, total_assignments):
        """
        Calculates score out of 100 based on resource wastage and gap minimization.
        """
        if not schedule:
            return 0

        score = 100
        capacity_wastage_penalty = 0
        
        for entry in schedule:
            capacity = entry.get("resource_capacity", 60)
            students = entry.get("student_count", 30)
            diff = capacity - students
            if diff > 25:  # Overly large room assigned to small batch
                capacity_wastage_penalty += 2

        score -= min(capacity_wastage_penalty, 20)
        return max(score, 0)