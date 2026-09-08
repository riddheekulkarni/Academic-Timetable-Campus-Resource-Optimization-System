"""
Admin API Routes
Provides full CRUD endpoints for administrative data management and optimization metrics.
"""
from flask import Blueprint, request, jsonify
from utils.auth import roles_required
from models.student_model import StudentModel
from models.faculty_model import FacultyModel
from models.subject_model import SubjectModel
from models.resource_model import ResourceModel
from models.assignment_model import AssignmentModel
from database.db import get_cursor

admin_bp = Blueprint("admin_bp", __name__)

# --- Admin Dashboard Metrics ---
@admin_bp.route("/admin/stats", methods=["GET"])
@roles_required("ADMIN")
def get_dashboard_stats():
    with get_cursor() as (conn, cursor):
        cursor.execute("SELECT COUNT(*) AS total FROM students")
        students = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM faculty")
        faculty = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM subjects")
        subjects = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM rooms")
        rooms = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM labs")
        labs = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM course_assignments")
        assignments = cursor.fetchone()["total"]

    return jsonify({
        "success": True,
        "stats": {
            "students": students,
            "faculty": faculty,
            "subjects": subjects,
            "rooms": rooms,
            "labs": labs,
            "assignments": assignments
        }
    }), 200

# --- Department List Endpoint ---
@admin_bp.route("/departments", methods=["GET"])
@roles_required("ADMIN")
def get_departments():
    with get_cursor() as (conn, cursor):
        cursor.execute("SELECT * FROM departments ORDER BY dept_id ASC")
        deps = cursor.fetchall()
    return jsonify({"success": True, "departments": deps}), 200

# --- Sections List Endpoint ---
@admin_bp.route("/sections", methods=["GET"])
@roles_required("ADMIN")
def get_sections():
    with get_cursor() as (conn, cursor):
        cursor.execute("""
            SELECT s.*, d.dept_name 
            FROM sections s 
            JOIN departments d ON s.dept_id = d.dept_id 
            ORDER BY s.section_id ASC
        """)
        secs = cursor.fetchall()
    return jsonify({"success": True, "sections": secs}), 200

# --- Students CRUD ---
@admin_bp.route("/students", methods=["GET", "POST"])
@roles_required("ADMIN")
def handle_students():
    if request.method == "GET":
        return jsonify({"success": True, "students": StudentModel.get_all()}), 200
    
    data = request.get_json() or {}
    try:
        sid = StudentModel.create(
            name=data.get("name"),
            email=data.get("email"),
            password=data.get("password", "Password123"),
            student_code=data.get("student_code"),
            dept_id=data.get("dept_id"),
            academic_year=data.get("academic_year"),
            section_id=data.get("section_id")
        )
        return jsonify({"success": True, "message": "Student created successfully.", "student_id": sid}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@admin_bp.route("/students/<int:student_id>", methods=["GET", "PUT", "DELETE"])
@roles_required("ADMIN")
def student_detail(student_id):
    if request.method == "GET":
        student = StudentModel.get_by_id(student_id)
        if student:
            return jsonify({"success": True, "student": student}), 200
        return jsonify({"success": False, "message": "Student not found."}), 404

    if request.method == "PUT":
        data = request.get_json() or {}
        try:
            ok = StudentModel.update(
                student_id=student_id,
                name=data.get("name"),
                email=data.get("email"),
                student_code=data.get("student_code"),
                dept_id=data.get("dept_id"),
                academic_year=data.get("academic_year"),
                section_id=data.get("section_id"),
                password=data.get("password")
            )
            if ok:
                return jsonify({"success": True, "message": "Student updated successfully."}), 200
            return jsonify({"success": False, "message": "Student record not found."}), 404
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    if request.method == "DELETE":
        if StudentModel.delete(student_id):
            return jsonify({"success": True, "message": "Student removed."}), 200
        return jsonify({"success": False, "message": "Student record not found."}), 404

# --- Faculty CRUD ---
@admin_bp.route("/faculty", methods=["GET", "POST"])
@roles_required("ADMIN")
def handle_faculty():
    if request.method == "GET":
        return jsonify({"success": True, "faculty": FacultyModel.get_all()}), 200
    
    data = request.get_json() or {}
    try:
        fid = FacultyModel.create(
            name=data.get("name"),
            email=data.get("email"),
            password=data.get("password", "Password123"),
            faculty_code=data.get("faculty_code"),
            dept_id=data.get("dept_id"),
            designation=data.get("designation", "Assistant Professor")
        )
        return jsonify({"success": True, "message": "Faculty member registered.", "faculty_id": fid}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@admin_bp.route("/faculty/<int:faculty_id>", methods=["GET", "PUT", "DELETE"])
@roles_required("ADMIN")
def faculty_detail(faculty_id):
    if request.method == "GET":
        fac = FacultyModel.get_by_id(faculty_id)
        if fac:
            return jsonify({"success": True, "faculty": fac}), 200
        return jsonify({"success": False, "message": "Faculty not found."}), 404

    if request.method == "PUT":
        data = request.get_json() or {}
        try:
            ok = FacultyModel.update(
                faculty_id=faculty_id,
                name=data.get("name"),
                email=data.get("email"),
                faculty_code=data.get("faculty_code"),
                dept_id=data.get("dept_id"),
                designation=data.get("designation"),
                password=data.get("password")
            )
            if ok:
                return jsonify({"success": True, "message": "Faculty member updated."}), 200
            return jsonify({"success": False, "message": "Faculty record not found."}), 404
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    if request.method == "DELETE":
        if FacultyModel.delete(faculty_id):
            return jsonify({"success": True, "message": "Faculty member removed."}), 200
        return jsonify({"success": False, "message": "Faculty record not found."}), 404

# --- Subjects CRUD ---
@admin_bp.route("/subjects", methods=["GET", "POST"])
@roles_required("ADMIN")
def handle_subjects():
    if request.method == "GET":
        return jsonify({"success": True, "subjects": SubjectModel.get_all()}), 200
    
    data = request.get_json() or {}
    try:
        sub_id = SubjectModel.create(
            code=data.get("subject_code"),
            name=data.get("subject_name"),
            dept_id=data.get("dept_id"),
            s_type=data.get("type", "Lecture"),
            lectures_per_week=int(data.get("lectures_per_week", 3)),
            duration_hours=int(data.get("duration_hours", 1)),
            req_room_type=data.get("required_room_type", "Classroom"),
            min_cap=int(data.get("min_capacity", 30)),
            proj=bool(data.get("requires_projector", True)),
            smart=bool(data.get("requires_smart_board", False)),
            min_comp=int(data.get("min_computers", 0))
        )
        return jsonify({"success": True, "message": "Subject added successfully.", "subject_id": sub_id}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@admin_bp.route("/subjects/<int:subject_id>", methods=["GET", "PUT", "DELETE"])
@roles_required("ADMIN")
def subject_detail(subject_id):
    if request.method == "GET":
        sub = SubjectModel.get_by_id(subject_id)
        if sub:
            return jsonify({"success": True, "subject": sub}), 200
        return jsonify({"success": False, "message": "Subject not found."}), 404

    if request.method == "PUT":
        data = request.get_json() or {}
        try:
            ok = SubjectModel.update(
                subject_id=subject_id,
                code=data.get("subject_code"),
                name=data.get("subject_name"),
                dept_id=data.get("dept_id"),
                s_type=data.get("type", "Lecture"),
                lectures_per_week=int(data.get("lectures_per_week", 3)),
                duration_hours=int(data.get("duration_hours", 1)),
                req_room_type=data.get("required_room_type", "Classroom"),
                min_cap=int(data.get("min_capacity", 30)),
                proj=bool(data.get("requires_projector", True)),
                smart=bool(data.get("requires_smart_board", False)),
                min_comp=int(data.get("min_computers", 0))
            )
            if ok:
                return jsonify({"success": True, "message": "Subject updated successfully."}), 200
            return jsonify({"success": False, "message": "Subject record not found."}), 404
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    if request.method == "DELETE":
        if SubjectModel.delete(subject_id):
            return jsonify({"success": True, "message": "Subject removed."}), 200
        return jsonify({"success": False, "message": "Subject record not found."}), 404

# --- Classrooms CRUD ---
@admin_bp.route("/rooms", methods=["GET", "POST"])
@roles_required("ADMIN")
def handle_rooms():
    if request.method == "GET":
        return jsonify({"success": True, "rooms": ResourceModel.get_rooms()}), 200
    
    data = request.get_json() or {}
    try:
        rid = ResourceModel.create_room(
            room_number=data.get("room_number"),
            building=data.get("building", "Main Block"),
            capacity=int(data.get("capacity", 40)),
            projector=bool(data.get("projector_available", True)),
            smart_board=bool(data.get("smart_board_available", False))
        )
        return jsonify({"success": True, "message": "Classroom added.", "room_id": rid}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@admin_bp.route("/rooms/<int:room_id>", methods=["GET", "PUT", "DELETE"])
@roles_required("ADMIN")
def room_detail(room_id):
    if request.method == "GET":
        r = ResourceModel.get_room_by_id(room_id)
        if r:
            return jsonify({"success": True, "room": r}), 200
        return jsonify({"success": False, "message": "Room not found."}), 404

    if request.method == "PUT":
        data = request.get_json() or {}
        try:
            ok = ResourceModel.update_room(
                room_id=room_id,
                room_number=data.get("room_number"),
                building=data.get("building"),
                capacity=int(data.get("capacity", 40)),
                projector=bool(data.get("projector_available", True)),
                smart_board=bool(data.get("smart_board_available", False))
            )
            if ok:
                return jsonify({"success": True, "message": "Classroom updated."}), 200
            return jsonify({"success": False, "message": "Room not found."}), 404
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    if request.method == "DELETE":
        if ResourceModel.delete_room(room_id):
            return jsonify({"success": True, "message": "Classroom deleted."}), 200
        return jsonify({"success": False, "message": "Room not found."}), 404

# --- Laboratories CRUD ---
@admin_bp.route("/labs", methods=["GET", "POST"])
@roles_required("ADMIN")
def handle_labs():
    if request.method == "GET":
        return jsonify({"success": True, "labs": ResourceModel.get_labs()}), 200
    
    data = request.get_json() or {}
    try:
        lid = ResourceModel.create_lab(
            lab_name=data.get("lab_name"),
            building=data.get("building", "Tech Block"),
            capacity=int(data.get("capacity", 30)),
            computer_count=int(data.get("computer_count", 30)),
            projector=bool(data.get("projector_available", True)),
            specs=data.get("specialized_equipment", "")
        )
        return jsonify({"success": True, "message": "Laboratory added.", "lab_id": lid}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@admin_bp.route("/labs/<int:lab_id>", methods=["GET", "PUT", "DELETE"])
@roles_required("ADMIN")
def lab_detail(lab_id):
    if request.method == "GET":
        l = ResourceModel.get_lab_by_id(lab_id)
        if l:
            return jsonify({"success": True, "lab": l}), 200
        return jsonify({"success": False, "message": "Laboratory not found."}), 404

    if request.method == "PUT":
        data = request.get_json() or {}
        try:
            ok = ResourceModel.update_lab(
                lab_id=lab_id,
                lab_name=data.get("lab_name"),
                building=data.get("building"),
                capacity=int(data.get("capacity", 30)),
                computer_count=int(data.get("computer_count", 30)),
                projector=bool(data.get("projector_available", True)),
                specs=data.get("specialized_equipment", "")
            )
            if ok:
                return jsonify({"success": True, "message": "Laboratory updated."}), 200
            return jsonify({"success": False, "message": "Laboratory not found."}), 404
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

    if request.method == "DELETE":
        if ResourceModel.delete_lab(lab_id):
            return jsonify({"success": True, "message": "Laboratory deleted."}), 200
        return jsonify({"success": False, "message": "Laboratory not found."}), 404

# --- Course Assignments CRUD (Subject -> Faculty -> Section) ---
@admin_bp.route("/assignments", methods=["GET", "POST"])
@roles_required("ADMIN")
def handle_assignments():
    if request.method == "GET":
        return jsonify({"success": True, "assignments": AssignmentModel.get_all()}), 200

    data = request.get_json() or {}
    try:
        aid = AssignmentModel.create(
            subject_id=int(data.get("subject_id")),
            faculty_id=int(data.get("faculty_id")),
            section_id=int(data.get("section_id"))
        )
        return jsonify({"success": True, "message": "Course mapped successfully.", "assignment_id": aid}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@admin_bp.route("/assignments/<int:assignment_id>", methods=["DELETE"])
@roles_required("ADMIN")
def delete_assignment(assignment_id):
    if AssignmentModel.delete(assignment_id):
        return jsonify({"success": True, "message": "Course mapping deleted."}), 200
    return jsonify({"success": False, "message": "Mapping record not found."}), 404
