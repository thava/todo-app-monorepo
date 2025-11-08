"""Todo endpoints"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from marshmallow import Schema, fields, validate

from ..app import db
from ..models.todo import Todo, PriorityEnum
from ..models.user import RoleEnum
from ..api.decorators import jwt_required_with_user

todos_bp = Blueprint('todos', __name__)


# Schemas
class CreateTodoSchema(Schema):
    description = fields.Str(required=True)
    dueDate = fields.DateTime(allow_none=True, load_default=None)
    priority = fields.Str(load_default='medium', validate=validate.OneOf(['low', 'medium', 'high']))


class UpdateTodoSchema(Schema):
    description = fields.Str()
    dueDate = fields.DateTime(allow_none=True)
    priority = fields.Str(validate=validate.OneOf(['low', 'medium', 'high']))


@todos_bp.route('', methods=['POST'])
@jwt_required_with_user
def create(user):
    """Create a new todo"""
    data = CreateTodoSchema().load(request.json)

    todo = Todo(
        owner_id=user.id,
        description=data['description'],
        due_date=data.get('dueDate'),
        priority=PriorityEnum[data.get('priority', 'medium')]
    )
    db.session.add(todo)
    db.session.commit()

    # Reload to get owner relationship
    db.session.refresh(todo)

    return jsonify(todo.to_dict(include_owner_info=True)), 201


@todos_bp.route('', methods=['GET'])
@jwt_required_with_user
def find_all(user):
    """Get all todos (scoped by user role)"""
    if user.role in [RoleEnum.admin, RoleEnum.sysadmin]:
        # Admin and sysadmin see all todos
        todos = Todo.query.order_by(Todo.created_at.desc()).all()
    else:
        # Regular users see only their own todos
        todos = Todo.query.filter_by(owner_id=user.id).order_by(Todo.created_at.desc()).all()

    return jsonify([todo.to_dict(include_owner_info=True) for todo in todos])


@todos_bp.route('/<uuid:todo_id>', methods=['GET'])
@jwt_required_with_user
def find_one(user, todo_id):
    """Get a todo by ID"""
    todo = db.session.get(Todo, todo_id)

    if not todo:
        return jsonify({'message': 'Todo not found'}), 404

    # Check authorization
    if user.role == RoleEnum.guest and todo.owner_id != user.id:
        return jsonify({'message': 'You can only view your own todos'}), 403

    return jsonify(todo.to_dict(include_owner_info=True))


@todos_bp.route('/<uuid:todo_id>', methods=['PATCH'])
@jwt_required_with_user
def update(user, todo_id):
    """Update a todo"""
    todo = db.session.get(Todo, todo_id)

    if not todo:
        return jsonify({'message': 'Todo not found'}), 404

    # Check authorization
    if user.role != RoleEnum.sysadmin and todo.owner_id != user.id:
        return jsonify({'message': 'You can only update your own todos'}), 403

    data = UpdateTodoSchema().load(request.json)

    # Update only provided fields
    if 'description' in data:
        todo.description = data['description']
    if 'dueDate' in data:
        todo.due_date = data['dueDate']
    if 'priority' in data:
        todo.priority = PriorityEnum[data['priority']]

    todo.updated_at = datetime.utcnow()
    db.session.commit()

    db.session.refresh(todo)
    return jsonify(todo.to_dict(include_owner_info=True))


@todos_bp.route('/<uuid:todo_id>', methods=['DELETE'])
@jwt_required_with_user
def remove(user, todo_id):
    """Delete a todo"""
    todo = db.session.get(Todo, todo_id)

    if not todo:
        return jsonify({'message': 'Todo not found'}), 404

    # Check authorization
    if user.role != RoleEnum.sysadmin and todo.owner_id != user.id:
        return jsonify({'message': 'You can only delete your own todos'}), 403

    db.session.delete(todo)
    db.session.commit()

    return '', 204
