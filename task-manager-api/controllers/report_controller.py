from datetime import datetime, timedelta

from flask import g, jsonify, request

from database import db
from models.category import Category
from models.task import Task
from models.user import User


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    p1 = Task.query.filter_by(priority=1).count()
    p2 = Task.query.filter_by(priority=2).count()
    p3 = Task.query.filter_by(priority=3).count()
    p4 = Task.query.filter_by(priority=4).count()
    p5 = Task.query.filter_by(priority=5).count()

    overdue_count = 0
    overdue_list = []
    for task in Task.query.all():
        if task.is_overdue():
            overdue_count += 1
            overdue_list.append({
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date),
                'days_overdue': (datetime.now().replace(microsecond=0) - task.due_date).days,
            })

    seven_days_ago = datetime.now().replace(microsecond=0) - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(Task.status == 'done', Task.updated_at >= seven_days_ago).count()

    user_stats = []
    for user in User.query.all():
        user_tasks = Task.query.filter_by(user_id=user.id).all()
        total = len(user_tasks)
        completed = sum(1 for task in user_tasks if task.status == 'done')
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
        })

    report = {
        'generated_at': str(datetime.now().replace(microsecond=0)),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
        },
        'tasks_by_priority': {
            'critical': p1,
            'high': p2,
            'medium': p3,
            'low': p4,
            'minimal': p5,
        },
        'overdue': {
            'count': overdue_count,
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }
    return jsonify(report), 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    done = sum(1 for task in tasks if task.status == 'done')
    pending = sum(1 for task in tasks if task.status == 'pending')
    in_progress = sum(1 for task in tasks if task.status == 'in_progress')
    cancelled = sum(1 for task in tasks if task.status == 'cancelled')
    overdue = sum(1 for task in tasks if task.is_overdue())
    high_priority = sum(1 for task in tasks if task.priority <= 2)

    report = {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        },
    }
    return jsonify(report), 200


def get_categories():
    categories = Category.query.all()
    result = []
    for category in categories:
        data = category.to_dict()
        data['task_count'] = Task.query.filter_by(category_id=category.id).count()
        result.append(data)
    return jsonify(result), 200


def create_category():
    data = request.get_json() or {}
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    name = data.get('name')
    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400

    current_user = getattr(g, 'current_user', None)
    if current_user and current_user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    category = Category(name=name, description=data.get('description', ''), color=data.get('color', '#000000'))
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201


def update_category(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    current_user = getattr(g, 'current_user', None)
    if current_user and current_user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json() or {}
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        category.color = data['color']

    db.session.commit()
    return jsonify(category.to_dict()), 200


def delete_category(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    current_user = getattr(g, 'current_user', None)
    if current_user and current_user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Categoria deletada'}), 200
