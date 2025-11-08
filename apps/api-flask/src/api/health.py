"""Health check endpoints"""
from flask import Blueprint, jsonify
from datetime import datetime
from sqlalchemy import text

from ..app import db

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health():
    """Basic health check"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


@health_bp.route('/readiness', methods=['GET'])
def readiness():
    """Readiness check with database connectivity"""
    status = 'ok'
    db_status = 'ok'

    try:
        # Check database connectivity
        db.session.execute(text('SELECT 1'))
    except Exception as e:
        db_status = 'fail'
        status = 'degraded'

    return jsonify({
        'status': status,
        'checks': {
            'database': db_status
        },
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })
