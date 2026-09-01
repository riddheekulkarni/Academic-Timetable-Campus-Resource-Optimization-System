"""
Database connection helper.

Provides:
- get_connection(): returns a new MySQL connection using settings from Config
- get_cursor(): convenience context manager that yields a (conn, cursor) pair
                and commits/closes automatically
- test_connection(): used by /api/db-check to verify MySQL is reachable
"""

from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error as MySQLError

from config import Config


def get_connection():
    """
    Creates and returns a new MySQL connection.
    Raises mysql.connector.Error if the connection fails.
    """
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
    )


@contextmanager
def get_cursor(dictionary=True, commit=False):
    """
    Usage:
        with get_cursor() as (conn, cursor):
            cursor.execute("SELECT * FROM students")
            rows = cursor.fetchall()

    Set commit=True for INSERT/UPDATE/DELETE statements so changes
    are saved automatically.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield conn, cursor
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def test_connection():
    """
    Attempts a lightweight connection + query to confirm MySQL is
    reachable and the configured database exists.

    Returns: (success: bool, message: str)
    """
    try:
        conn = get_connection()
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            return True, "Successfully connected to MySQL database '{}'.".format(
                Config.MYSQL_DATABASE
            )
        return False, "Could not establish a connection to MySQL."
    except MySQLError as err:
        return False, "MySQL connection error: {}".format(str(err))