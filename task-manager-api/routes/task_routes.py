from flask import Blueprint

from controllers.task_controller import (
    create_task,
    delete_task,
    get_task,
    list_tasks,
    search_tasks,
    task_stats,
    update_task,
)
from middlewares.auth import require_auth

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return list_tasks()


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task_route(task_id):
    return get_task(task_id)


@task_bp.route('/tasks', methods=['POST'])
@require_auth
def create_task_route():
    return create_task()


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@require_auth
def update_task_route(task_id):
    return update_task(task_id)


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@require_auth
def delete_task_route(task_id):
    return delete_task(task_id)


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks_route():
    return search_tasks()


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats_route():
    return task_stats()
