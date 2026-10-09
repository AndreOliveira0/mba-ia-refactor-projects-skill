from functools import wraps

from flask import current_app, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from database import db
from models.user import User


def create_auth_token(user):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='task-manager-auth')
    return serializer.dumps({
        'user_id': user.id,
        'role': user.role,
        'email': user.email,
    })


def decode_auth_token(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='task-manager-auth')
    try:
        return serializer.loads(token, max_age=86400)
    except (BadSignature, SignatureExpired):
        return None


def require_auth(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token ausente ou inválido'}), 401

        token = auth_header.split(' ', 1)[1].strip()
        payload = decode_auth_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido ou expirado'}), 401

        user = db.session.get(User, payload.get('user_id'))
        if not user or not user.active:
            return jsonify({'error': 'Usuário inválido'}), 401

        g.current_user = user
        return view_func(*args, **kwargs)

    return wrapper


def require_admin(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not getattr(g, 'current_user', None):
            return jsonify({'error': 'Autenticação obrigatória'}), 401

        if g.current_user.role != 'admin':
            return jsonify({'error': 'Forbidden'}), 403

        return view_func(*args, **kwargs)

    return wrapper
