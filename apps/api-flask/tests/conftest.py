"""Pytest configuration and fixtures"""
import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path for src module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.app import create_app, db
from src.models.user import User, RoleEnum
from src.services.password_service import PasswordService


@pytest.fixture(scope='function')
def app():
    """
    Create and configure a test app instance

    NOTE: Tests require PostgreSQL. SQLite is not supported due to:
    - UUID type compatibility
    - JSONB type (PostgreSQL-specific)
    - Enum types

    Set TEST_DATABASE_URL environment variable to use a test database:
    export TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_test_db
    """
    import os

    # Check if we should use PostgreSQL for tests
    test_db_url = os.getenv('TEST_DATABASE_URL')

    if test_db_url:
        # Use PostgreSQL test database
        app = create_app('development')  # Use dev config
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = test_db_url
    else:
        # Skip tests that require database
        pytest.skip("PostgreSQL test database not configured. Set TEST_DATABASE_URL environment variable.")

    # Create tables
    with app.app_context():
        db.create_all()

    yield app

    # Cleanup
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def auth_headers(app, client):
    """Create a verified user and return auth headers"""
    with app.app_context():
        # Create verified user
        password_hash = PasswordService.hash_password('Test1234')
        user = User(
            email='test@example.com',
            full_name='Test User',
            password_hash_primary=password_hash,
            role=RoleEnum.guest,
            email_verified_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()

    # Login
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test1234'
    })
    assert response.status_code == 200

    data = response.get_json()
    access_token = data['accessToken']

    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture(scope='function')
def admin_headers(app, client):
    """Create a verified admin user and return auth headers"""
    with app.app_context():
        # Create verified admin
        password_hash = PasswordService.hash_password('Admin1234')
        admin = User(
            email='admin@example.com',
            full_name='Admin User',
            password_hash_primary=password_hash,
            role=RoleEnum.admin,
            email_verified_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()

    # Login
    response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'Admin1234'
    })
    assert response.status_code == 200

    data = response.get_json()
    access_token = data['accessToken']

    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture(scope='function')
def sysadmin_headers(app, client):
    """Create a verified sysadmin user and return auth headers"""
    with app.app_context():
        # Create verified sysadmin
        password_hash = PasswordService.hash_password('Sysadmin1234')
        sysadmin = User(
            email='sysadmin@example.com',
            full_name='Sysadmin User',
            password_hash_primary=password_hash,
            role=RoleEnum.sysadmin,
            email_verified_at=datetime.utcnow()
        )
        db.session.add(sysadmin)
        db.session.commit()

    # Login
    response = client.post('/auth/login', json={
        'email': 'sysadmin@example.com',
        'password': 'Sysadmin1234'
    })
    assert response.status_code == 200

    data = response.get_json()
    access_token = data['accessToken']

    return {'Authorization': f'Bearer {access_token}'}
