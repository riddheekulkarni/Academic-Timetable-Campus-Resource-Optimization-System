"""
Authentication Routes
Endpoints for user authentication:
- POST /api/login: Validate credentials and return JWT token
- GET  /api/me: Return information about the currently logged-in user
"""
from flask import Blueprint, request, jsonify
from database.db import get_cursor
from utils.auth import verify_password, generate_token, token_required

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Validates user credentials against database and returns role & JWT token.
    Payload expected: { "email": "...", "password": "..." }
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    with get_cursor() as (conn, cursor):
        cursor.execute("SELECT user_id, email, password_hash, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user or not verify_password(user["password_hash"], password):
            return jsonify({"success": False, "message": "Invalid email or password."}), 401

        token = generate_token(user["user_id"], user["email"], user["role"])

        # Fetch detailed profile ID based on role
        profile = {}
        if user["role"] == "STUDENT":
            cursor.execute("SELECT student_id, name, section_id FROM students WHERE user_id = %s", (user["user_id"],))
            profile = cursor.fetchone() or {}
        elif user["role"] == "FACULTY":
            cursor.execute("SELECT faculty_id, name, designation FROM faculty WHERE user_id = %s", (user["user_id"],))
            profile = cursor.fetchone() or {}
        elif user["role"] == "ADMIN":
            profile = {"name": "System Administrator"}

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "token": token,
            "user": {
                "user_id": user["user_id"],
                "email": user["email"],
                "role": user["role"],
                "profile": profile
            }
        }), 200

@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user_info():
    """Returns details of currently authenticated user using JWT token."""
    user_info = request.current_user
    with get_cursor() as (conn, cursor):
        cursor.execute("SELECT user_id, email, role FROM users WHERE user_id = %s", (user_info["user_id"],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"success": False, "message": "User record not found."}), 404

        profile = {}
        if user["role"] == "STUDENT":
            cursor.execute("SELECT student_id, name, student_code, dept_id, academic_year, section_id FROM students WHERE user_id = %s", (user["user_id"],))
            profile = cursor.fetchone() or {}
        elif user["role"] == "FACULTY":
            cursor.execute("SELECT faculty_id, name, faculty_code, dept_id, designation FROM faculty WHERE user_id = %s", (user["user_id"],))
            profile = cursor.fetchone() or {}

        return jsonify({
            "success": True,
            "user": {
                "user_id": user["user_id"],
                "email": user["email"],
                "role": user["role"],
                "profile": profile
            }
        }), 200