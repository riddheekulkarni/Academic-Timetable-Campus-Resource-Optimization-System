"""
Schedule Change Requests & Faculty Availability Routes
"""
from flask import Blueprint, jsonify, request
from utils.auth import token_required, roles_required
from database.db import get_cursor
from services.rescheduler import Rescheduler

schedule_bp = Blueprint("schedule_bp", __name__)

@schedule_bp.route("/schedule/change-request", methods=["POST", "GET"])
@token_required
def handle_change_requests():
    user = request.current_user
    if request.method == "POST":
        data = request.get_json() or {}
        with get_cursor() as (conn, cursor):
            cursor.execute("SELECT faculty_id FROM faculty WHERE user_id = %s", (user["user_id"],))
            fac = cursor.fetchone()
            if not fac:
                return jsonify({"success": False, "message": "Faculty profile not found."}), 404

            cursor.execute("""
                INSERT INTO schedule_changes (timetable_id, requested_by_faculty_id, change_type, reason, status)
                VALUES (%s, %s, %s, %s, 'PENDING')
            """, (data.get("timetable_id"), fac["faculty_id"], data.get("change_type"), data.get("reason")))
            conn.commit()
        return jsonify({"success": True, "message": "Request submitted."}), 201

    with get_cursor() as (conn, cursor):
        cursor.execute("""
            SELECT sc.*, f.name AS faculty_name, sub.subject_name
            FROM schedule_changes sc
            JOIN faculty f ON sc.requested_by_faculty_id = f.faculty_id
            JOIN timetable t ON sc.timetable_id = t.timetable_id
            JOIN course_assignments ca ON t.assignment_id = ca.assignment_id
            JOIN subjects sub ON ca.subject_id = sub.subject_id
            ORDER BY sc.change_id DESC
        """)
        reqs = cursor.fetchall()
    return jsonify({"success": True, "requests": reqs}), 200

@schedule_bp.route("/schedule/change-request/<int:change_id>/action", methods=["POST"])
@roles_required("ADMIN")
def action_change_request(change_id):
    data = request.get_json() or {}
    action = data.get("action")
    ok, msg = Rescheduler.process_change_request(change_id, action)
    return jsonify({"success": ok, "message": msg}), 200 if ok else 400