"""
Timetable API Routes
Exposes endpoints for generation, validation, and role-based fetching.
"""
from flask import Blueprint, jsonify, request
from utils.auth import token_required, roles_required
from services.timetable_generator import TimetableGenerator
from database.db import get_cursor

timetable_bp = Blueprint("timetable_bp", __name__)

@timetable_bp.route("/timetable/generate", methods=["POST"])
@roles_required("ADMIN")
def generate_timetable():
    res = TimetableGenerator.generate_all()
    return jsonify(res), 200

@timetable_bp.route("/timetable", methods=["GET"])
@token_required
def get_timetable():
    user = request.current_user
    role = user["role"]
    user_id = user["user_id"]

    query = """
        SELECT t.timetable_id, ts.day_of_week, ts.start_time, ts.end_time, ts.slot_order,
               sub.subject_code, sub.subject_name, sub.type AS subject_type,
               f.name AS faculty_name, sec.section_name,
               r.room_number, l.lab_name
        FROM timetable t
        JOIN time_slots ts ON t.slot_id = ts.slot_id
        JOIN course_assignments ca ON t.assignment_id = ca.assignment_id
        JOIN subjects sub ON ca.subject_id = sub.subject_id
        JOIN faculty f ON ca.faculty_id = f.faculty_id
        JOIN sections sec ON ca.section_id = sec.section_id
        LEFT JOIN room_allocations ra ON t.timetable_id = ra.timetable_id
        LEFT JOIN rooms r ON ra.room_id = r.room_id
        LEFT JOIN labs l ON ra.lab_id = l.lab_id
    """
    params = []

    if role == "STUDENT":
        query += " JOIN students stu ON stu.section_id = sec.section_id WHERE stu.user_id = %s"
        params.append(user_id)
    elif role == "FACULTY":
        query += " WHERE f.user_id = %s"
        params.append(user_id)

    query += " ORDER BY ts.slot_order ASC"

    with get_cursor() as (conn, cursor):
        cursor.execute(query, params)
        schedule = cursor.fetchall()

    # Format time strings for frontend readability (HH:MM:SS)
    for row in schedule:
        st = str(row["start_time"])
        et = str(row["end_time"])
        if len(st.split(":")[0]) == 1:
            st = "0" + st
        if len(et.split(":")[0]) == 1:
            et = "0" + et
        row["start_time"] = st
        row["end_time"] = et

    return jsonify({"success": True, "timetable": schedule}), 200