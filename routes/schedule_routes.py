"""
Schedule Change Requests & Faculty Availability Routes
"""
from flask import Blueprint, jsonify, request
from utils.auth import token_required, roles_required
from database.db import get_cursor
from services.rescheduler import Rescheduler
from services.timetable_generator import TimetableGenerator

schedule_bp = Blueprint("schedule_bp", __name__)


def _format_availability_rows(rows):
    for row in rows:
        row["start_time"] = str(row["start_time"])[:5]
        row["end_time"] = str(row["end_time"])[:5]
        row["is_available"] = bool(row["is_available"])
    return rows


def _get_faculty_id(user_id):
    with get_cursor() as (conn, cursor):
        cursor.execute("SELECT faculty_id FROM faculty WHERE user_id = %s", (user_id,))
        faculty = cursor.fetchone()
    return faculty["faculty_id"] if faculty else None


def _get_availability_rows(faculty_id):
    with get_cursor() as (conn, cursor):
        cursor.execute("""
            SELECT ts.slot_id, ts.day_of_week, ts.start_time, ts.end_time,
                   COALESCE(fa.is_available, TRUE) AS is_available
            FROM time_slots ts
            LEFT JOIN faculty_availability fa
              ON fa.slot_id = ts.slot_id AND fa.faculty_id = %s
            ORDER BY FIELD(ts.day_of_week, 'Monday', 'Tuesday', 'Wednesday',
                           'Thursday', 'Friday'), ts.slot_order
        """, (faculty_id,))
        return _format_availability_rows(cursor.fetchall())


@schedule_bp.route("/faculty/availability", methods=["GET", "PUT"])
@roles_required("FACULTY")
def faculty_availability():
    faculty_id = _get_faculty_id(request.current_user["user_id"])
    if not faculty_id:
        return jsonify({"success": False, "message": "Faculty profile not found."}), 404

    if request.method == "GET":
        return jsonify({"success": True, "slots": _get_availability_rows(faculty_id)}), 200

    data = request.get_json() or {}
    unavailable_ids = data.get("unavailable_slot_ids", [])
    if not isinstance(unavailable_ids, list):
        return jsonify({"success": False, "message": "unavailable_slot_ids must be a list."}), 400

    try:
        unavailable_ids = sorted({int(slot_id) for slot_id in unavailable_ids})
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Availability contains an invalid time slot."}), 400

    with get_cursor(commit=True) as (conn, cursor):
        if unavailable_ids:
            placeholders = ",".join(["%s"] * len(unavailable_ids))
            cursor.execute(
                f"SELECT slot_id FROM time_slots WHERE slot_id IN ({placeholders})",
                tuple(unavailable_ids)
            )
            valid_ids = {row["slot_id"] for row in cursor.fetchall()}
        else:
            valid_ids = set()

        cursor.execute("DELETE FROM faculty_availability WHERE faculty_id = %s", (faculty_id,))
        if valid_ids:
            cursor.executemany(
                """
                INSERT INTO faculty_availability (faculty_id, slot_id, is_available)
                VALUES (%s, %s, FALSE)
                """,
                [(faculty_id, slot_id) for slot_id in sorted(valid_ids)]
            )

    generation = TimetableGenerator.generate_all()
    return jsonify({
        "success": True,
        "message": "Availability saved and timetable regenerated.",
        "unavailable_slot_ids": sorted(valid_ids),
        "total_assigned": generation.get("total_assigned", 0)
    }), 200


@schedule_bp.route("/faculty/<int:faculty_id>/availability", methods=["GET"])
@roles_required("ADMIN")
def admin_faculty_availability(faculty_id):
    with get_cursor() as (conn, cursor):
        cursor.execute("SELECT faculty_id, name FROM faculty WHERE faculty_id = %s", (faculty_id,))
        faculty = cursor.fetchone()

    if not faculty:
        return jsonify({"success": False, "message": "Faculty member not found."}), 404

    return jsonify({
        "success": True,
        "faculty": faculty,
        "slots": _get_availability_rows(faculty_id)
    }), 200

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