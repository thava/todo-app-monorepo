"""Flask application factory"""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv
import os

from .config import config

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Configure JWT
    # Flask-JWT-Extended reads config from app.config automatically:
    # - app.config['JWT_SECRET_KEY'] is used for access token signing/verification
    #   (this is set to JWT_ACCESS_SECRET_KEY in config.py)
    # - app.config['JWT_ACCESS_TOKEN_EXPIRES'] for access token expiry
    # - Refresh tokens are manually created using JWT_REFRESH_SECRET_KEY (see token_service.py)
    app.config['JWT_DECODE_ALGORITHMS'] = ['HS256']
    jwt.init_app(app)  # Reads JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRES, etc. from app.config

    ma.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Register blueprints
    from .api import register_blueprints
    register_blueprints(app)

    # Register Swagger/OpenAPI documentation
    from .api.swagger import register_swagger
    register_swagger(app)

    # Register error handlers
    from .api.errors import register_error_handlers
    register_error_handlers(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
