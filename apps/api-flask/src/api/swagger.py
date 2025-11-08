"""Swagger UI and OpenAPI endpoints"""
from flask import Blueprint, send_file, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import os
import yaml

swagger_bp = Blueprint('swagger_api', __name__)

# Path to OpenAPI spec
SWAGGER_URL = '/docs'
API_URL = '/api-spec'

# Get the path to the OpenAPI spec file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPENAPI_FILE = os.path.join(BASE_DIR, 'docs', 'openapi.yaml')


@swagger_bp.route('/api-spec')
def get_openapi_spec():
    """Serve the OpenAPI specification"""
    try:
        with open(OPENAPI_FILE, 'r') as f:
            spec = yaml.safe_load(f)
        return jsonify(spec)
    except FileNotFoundError:
        return jsonify({'error': 'OpenAPI specification not found'}), 404


def register_swagger(app):
    """Register Swagger UI blueprint"""
    # Create Swagger UI blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Todo App API"
        }
    )

    # Register blueprints
    app.register_blueprint(swagger_bp)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Add redoc endpoint
    @app.route('/redoc')
    def redoc():
        """Serve ReDoc UI"""
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Todo App API - ReDoc</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                }}
            </style>
        </head>
        <body>
            <redoc spec-url='{API_URL}'></redoc>
            <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
        </body>
        </html>
        '''
