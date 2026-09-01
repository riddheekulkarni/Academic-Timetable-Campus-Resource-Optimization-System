"""
Central configuration for the Academic Scheduler application.

All values can be overridden with environment variables, so the same
code works across different machines without editing this file.
On Windows/VS Code you can set these in a `.env` file (see README)
or directly in your terminal before running `python app.py`.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    # ---------------------------------------------------------------
    # Flask
    # ---------------------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"

    # ---------------------------------------------------------------
    # MySQL connection settings
    # ---------------------------------------------------------------
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "academic_scheduler")

    # ---------------------------------------------------------------
    # Auth / session settings (used starting Phase 3)
    # ---------------------------------------------------------------
    TOKEN_EXPIRY_HOURS = int(os.environ.get("TOKEN_EXPIRY_HOURS", 12))