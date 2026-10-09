from datetime import datetime

from flask import g, jsonify, request

from database import db
from middlewares.auth import create_auth_token
from models.task import Task
from models.user import User
from utils.validators import is_valid_email, is_valid_password, is_valid_role


def list_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'active': user.active,
            'created_at': str(user.created_at),
            'task_count': len(user.tasks),
        })
    return jsonify(result), 200


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).all()
    data['tasks'] = [task.to_dict() for task in tasks]
    return jsonify(data), 200


def create_user():
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if 'role' in data and data['role'] != 'user':
        return jsonify({'error': 'Forbidden'}), 403

    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    if not email:
        return jsonify({'error': 'Email é obrigatório'}), 400
    if not password:
        return jsonify({'error': 'Senha é obrigatória'}), 400
    if not is_valid_email(email):
        return jsonify({'error': 'Email inválido'}), 400
    if not is_valid_password(password):
        return jsonify({'error': 'Senha deve ter no mínimo 4 caracteres'}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({'error': 'Email já cadastrado'}), 409
    user = User(name=name, email=email, role='user')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    current_user = getattr(g, 'current_user', None)
    if current_user and current_user.id != user.id and current_user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not is_valid_email(data['email']):
            return jsonify({'error': 'Email inválido'}), 400
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email já cadastrado'}), 409
        user.email = data['email']

    if 'password' in data:
        if not is_valid_password(data['password']):
            return jsonify({'error': 'Senha muito curta'}), 400
        user.set_password(data['password'])

    if 'role' in data:
        if current_user is None or current_user.role != 'admin':
            return jsonify({'error': 'Forbidden'}), 403
        if not is_valid_role(data['role']):
            return jsonify({'error': 'Role inválida'}), 400
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    db.session.commit()
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    current_user = getattr(g, 'current_user', None)
    if current_user and current_user.id != user.id and current_user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    tasks = Task.query.filter_by(user_id=user_id).all()
    for task in tasks:
        db.session.delete(task)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for task in tasks:
        item = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'created_at': str(task.created_at),
            'due_date': str(task.due_date) if task.due_date else None,
            'overdue': task.is_overdue(),
        }
        result.append(item)
    return jsonify(result), 200


def login():
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Credenciais inválidas'}), 401
    if not user.active:
        return jsonify({'error': 'Usuário inativo'}), 403

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': create_auth_token(user),
    }), 200
