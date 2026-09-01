"""
Authentication Utilities
Provides password hashing checks, JWT token generation, token verification,
and route decoration for Role-Based Access Control (RBAC).
"""
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from config import Config

def hash_password(password: str) -> str:
    """Generates a Werkzeug password hash."""
    return generate_password_hash(password)

def verify_password(stored_hash: str, password: str) -> bool:
    """Verifies a plain-text password against a stored Werkzeug/scrypt hash."""
    return check_password_hash(stored_hash, password)

def generate_token(user_id: int, email: str, role: str) -> str:
    """Generates a JWT token signed with Config.SECRET_KEY."""
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=Config.TOKEN_EXPIRY_HOURS)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

def decode_token(token: str):
    """
    Decodes and validates a JWT token.
    Returns payload dict if valid, or (None, error_message) if invalid/expired.
    """
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired. Please log in again."
    except jwt.InvalidTokenError:
        return None, "Invalid authentication token."

def token_required(f):
    """Decorator ensuring request contains a valid Bearer JWT in Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"success": False, "message": "Authorization header missing."}), 401
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"success": False, "message": "Invalid Authorization header format. Use 'Bearer <token>'."}), 401

        token = parts[1]
        payload, error = decode_token(token)
        if error:
            return jsonify({"success": False, "message": error}), 401

        # Pass current user payload to route function
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated

def roles_required(*allowed_roles):
    """Decorator restricting route access to specified user roles (ADMIN, FACULTY, STUDENT)."""
    def decorator(f):
        @wraps(f)

        @token_required
        def decorated(*args, **kwargs):
            user_role = request.current_user.get("role")
            if user_role not in allowed_roles:
                return jsonify({
                    "success": False, 
                    "message": f"Access denied. Requires one of the following roles: {', '.join(allowed_roles)}"
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator