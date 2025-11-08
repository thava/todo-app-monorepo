"""Application configuration"""
import os
from datetime import timedelta


class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/todo_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # JWT - Using separate secrets for access and refresh tokens (matches NestJS)
    # Note: Flask-JWT-Extended requires JWT_SECRET_KEY for access tokens
    JWT_ACCESS_SECRET_KEY = os.getenv('JWT_ACCESS_SECRET', 'jwt-access-secret-change-in-production')
    JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET', 'jwt-refresh-secret-change-in-production')

    # Flask-JWT-Extended uses JWT_SECRET_KEY for access token verification
    # We set it to the access secret for consistency
    JWT_SECRET_KEY = JWT_ACCESS_SECRET_KEY

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # Email (placeholder - will use console output for development)
    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
    EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@todo-app.local')

    # Application
    APP_NAME = 'Todo App API'
    APP_VERSION = '1.0'
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # SQLite doesn't support these PostgreSQL-specific options
    SQLALCHEMY_ENGINE_OPTIONS = {}


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': DevelopmentConfig
}
