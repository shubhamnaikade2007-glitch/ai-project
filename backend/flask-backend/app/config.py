"""
HealthFit AI - Flask Configuration
Loads settings from environment variables with sensible defaults
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class"""
    
    # ── Flask ──────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-abc123xyz')
    DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'
    
    # ── MySQL Database ─────────────────────────────────────
    MYSQL_HOST     = os.environ.get('MYSQL_HOST',     'localhost')
    MYSQL_PORT     = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER     = os.environ.get('MYSQL_USER',     'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root123')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'healthfit_db')
    
    # SQLAlchemy connection string for MySQL via PyMySQL
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        f"?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,      # Recycle connections every 5 minutes
        'pool_pre_ping': True,    # Verify connection before using
        'pool_size': 10,
        'max_overflow': 20,
    }
    
    # ── JWT Authentication ─────────────────────────────────
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-me-xyz789abc')
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # ── AI Models API ──────────────────────────────────────
    AI_API_URL = (
        f"http://{os.environ.get('AI_API_HOST', 'localhost')}"
        f":{os.environ.get('AI_API_PORT', '8001')}"
    )
    
    # ── Mail (optional) ────────────────────────────────────
    MAIL_SERVER   = os.environ.get('MAIL_SERVER',   'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    
    # ── File Upload ────────────────────────────────────────
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}


class DevelopmentConfig(Config):
    """Development-specific config"""
    DEBUG = True


class ProductionConfig(Config):
    """Production-specific config"""
    DEBUG = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'pool_size': 20,
        'max_overflow': 40,
    }


# Active config based on FLASK_ENV
config_map = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
}

# Default to development
Config = config_map.get(os.environ.get('FLASK_ENV', 'development'), DevelopmentConfig)
