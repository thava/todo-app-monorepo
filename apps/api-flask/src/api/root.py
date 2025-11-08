"""Root endpoint"""
from flask import Blueprint, jsonify

root_bp = Blueprint('root', __name__)


@root_bp.route('/', methods=['GET'])
def get_hello():
    """Root endpoint"""
    return jsonify({'message': 'Hello from Todo App API'})
