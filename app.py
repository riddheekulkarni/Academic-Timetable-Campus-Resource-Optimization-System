"""Academic Timetable & Campus Resource Optimization System
Main Flask application entry point.
"""
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
from config import Config
from database.db import test_connection

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

def create_app():
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
    app.config.from_object(Config)
    CORS(app)

    # Register All Blueprints
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.timetable_routes import timetable_bp
    from routes.schedule_routes import schedule_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api")
    app.register_blueprint(timetable_bp, url_prefix="/api")
    app.register_blueprint(schedule_bp, url_prefix="/api")

    @app.route("/api/health")
    def health_check():
        return jsonify({"success": True, "message": "Flask server is running."})

    @app.route("/api/db-check")
    def db_check():
        ok, message = test_connection()
        status_code = 200 if ok else 500
        return jsonify({"success": ok, "message": message}), status_code

    @app.route("/")
    def serve_index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:path>")
    def serve_static_files(path):
        return send_from_directory(FRONTEND_DIR, path)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)