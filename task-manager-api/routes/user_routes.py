from flask import Blueprint

from controllers.user_controller import (
    create_user,
    delete_user,
    get_user,
    get_user_tasks,
    list_users,
    login,
    update_user,
)
from middlewares.auth import require_auth

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users_route():
    return list_users()


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_route(user_id):
    return get_user(user_id)


@user_bp.route('/users', methods=['POST'])
def create_user_route():
    return create_user()


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_auth
def update_user_route(user_id):
    return update_user(user_id)


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_auth
def delete_user_route(user_id):
    return delete_user(user_id)


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks_route(user_id):
    return get_user_tasks(user_id)


@user_bp.route('/login', methods=['POST'])
def login_route():
    return login()
