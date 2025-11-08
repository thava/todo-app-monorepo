"""Error handlers"""
from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle marshmallow validation errors"""
        return jsonify({
            'message': 'Validation error',
            'errors': error.messages
        }), 400

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        """Handle database errors"""
        app.logger.error(f'Database error: {str(error)}')
        return jsonify({
            'message': 'Database error occurred'
        }), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle HTTP exceptions"""
        return jsonify({
            'message': error.description
        }), error.code

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Handle generic errors"""
        app.logger.error(f'Unhandled error: {str(error)}')
        return jsonify({
            'message': 'An unexpected error occurred'
        }), 500
