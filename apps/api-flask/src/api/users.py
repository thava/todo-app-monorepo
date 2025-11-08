"""User profile endpoints"""
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, validate

from ..app import db
from ..api.decorators import jwt_required_with_user

users_bp = Blueprint('users', __name__)


# Schemas
class UpdateProfileSchema(Schema):
    fullName = fields.Str(validate=validate.Length(min=1, max=255))


@users_bp.route('', methods=['GET'])
@jwt_required_with_user
def get_profile(user):
    """Get current user profile"""
    return jsonify(user.to_dict())


@users_bp.route('', methods=['PATCH'])
@jwt_required_with_user
def update_profile(user):
    """Update current user profile"""
    data = UpdateProfileSchema().load(request.json)

    if 'fullName' in data:
        user.full_name = data['fullName']

    db.session.commit()

    return jsonify(user.to_dict())
