from datetime import datetime

from flask import jsonify, request, g

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.validators import is_valid_task_priority, is_valid_task_status, task_title_error


def list_tasks():
    tasks = Task.query.all()
    result = []
    for task in tasks:
        item = task.to_dict()
        item['user_name'] = task.user.name if task.user else None
        item['category_name'] = task.category.name if task.category else None
        item['overdue'] = task.is_overdue()
        result.append(item)
    return jsonify(result), 200


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404

    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return jsonify(data), 200


def create_task():
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    title = data.get('title')
    if not title:
        return jsonify({'error': 'Título é obrigatório'}), 400
    title_error = task_title_error(title)
    if title_error:
        return jsonify({'error': title_error}), 400

    description = data.get('description', '')
    status = data.get('status', 'pending')
    priority = data.get('priority', 3)
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    due_date = data.get('due_date')
    tags = data.get('tags')

    current_user = getattr(g, 'current_user', None)
    if current_user and current_user.role != 'admin':
        if user_id is None:
            user_id = current_user.id
        elif int(user_id) != current_user.id:
            return jsonify({'error': 'Forbidden'}), 403

    if not is_valid_task_status(status):
        return jsonify({'error': 'Status inválido'}), 400
    if not is_valid_task_priority(priority):
        return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400

    if user_id:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
    if category_id:
        category = db.session.get(Category, category_id)
        if not category:
            return jsonify({'error': 'Categoria não encontrada'}), 404

    task = Task()
    task.title = title
    task.description = description
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404

    current_user = getattr(g, 'current_user', None)
    if current_user and current_user.role != 'admin' and task.user_id != current_user.id:
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    if 'title' in data:
        title = data['title']
        title_error = task_title_error(title)
        if title_error:
            return jsonify({'error': title_error}), 400
        task.title = title

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if not is_valid_task_status(data['status']):
            return jsonify({'error': 'Status inválido'}), 400
        task.status = data['status']

    if 'priority' in data:
        if not is_valid_task_priority(data['priority']):
            return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id']:
            user = db.session.get(User, data['user_id'])
            if not user:
                return jsonify({'error': 'Usuário não encontrado'}), 404
        if current_user and current_user.role != 'admin' and data['user_id'] not in (None, current_user.id):
            return jsonify({'error': 'Forbidden'}), 403
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id']:
            cat = db.session.get(Category, data['category_id'])
            if not cat:
                return jsonify({'error': 'Categoria não encontrada'}), 404
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Formato de data inválido'}), 400
        else:
            task.due_date = None

    if 'tags' in data:
        task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

    task.updated_at = datetime.now().replace(microsecond=0)
    db.session.commit()
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404

    current_user = getattr(g, 'current_user', None)
    if current_user and current_user.role != 'admin' and task.user_id != current_user.id:
        return jsonify({'error': 'Forbidden'}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    user_id = request.args.get('user_id', '')

    tasks = Task.query

    if query:
        tasks = tasks.filter(db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%')))
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    output = [task.to_dict() for task in tasks.all()]
    return jsonify(output), 200


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    overdue_count = 0
    for task in Task.query.all():
        if task.is_overdue():
            overdue_count += 1

    stats = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
    return jsonify(stats), 200
