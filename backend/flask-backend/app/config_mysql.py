"""
HealthFit AI - MySQL-specific Configuration Helper
Provides utilities for MySQL connection management and testing
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL connection parameters
MYSQL_CONFIG = {
    'host':     os.environ.get('MYSQL_HOST',     'localhost'),
    'port':     int(os.environ.get('MYSQL_PORT', 3306)),
    'user':     os.environ.get('MYSQL_USER',     'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'root123'),
    'database': os.environ.get('MYSQL_DATABASE', 'healthfit_db'),
    'charset':  'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}


def get_direct_connection():
    """
    Get a direct PyMySQL connection (outside SQLAlchemy).
    Useful for bulk operations or raw SQL.
    """
    return pymysql.connect(**MYSQL_CONFIG)


def test_connection() -> dict:
    """
    Test MySQL connection and return status info.
    Returns dict with 'success', 'version', and 'error' keys.
    """
    try:
        conn = get_direct_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION() as version")
            result = cursor.fetchone()
        conn.close()
        return {
            "success": True,
            "version": result['version'],
            "database": MYSQL_CONFIG['database'],
            "host": MYSQL_CONFIG['host'],
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def ensure_database_exists():
    """
    Create the database if it doesn't exist.
    Run this before starting the app for the first time.
    """
    config_no_db = {k: v for k, v in MYSQL_CONFIG.items() if k != 'database' and k != 'cursorclass'}
    config_no_db['cursorclass'] = pymysql.cursors.DictCursor
    
    conn = pymysql.connect(**config_no_db)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{MYSQL_CONFIG['database']}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        print(f"✅ Database '{MYSQL_CONFIG['database']}' ready")
    finally:
        conn.close()
