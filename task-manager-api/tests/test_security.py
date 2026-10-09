import pytest

from app import app, db
from models.user import User
from models.task import Task
from models.category import Category


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(name='Admin', email='admin@test.com', role='admin')
        admin.set_password('1234')
        user = User(name='User', email='user@test.com', role='user')
        user.set_password('abcd')
        other = User(name='Other', email='other@test.com', role='user')
        other.set_password('xyz1')
        db.session.add_all([admin, user, other])
        db.session.commit()
        category = Category(name='General', description='General tasks')
        db.session.add(category)
        db.session.commit()
        task = Task(title='Owned task', description='Mine', status='pending', priority=2, user_id=user.id, category_id=category.id)
        db.session.add(task)
        db.session.commit()
    with app.test_client() as client:
        yield client


def _token(client, email, password):
    response = client.post('/login', json={'email': email, 'password': password})
    assert response.status_code == 200
    return response.get_json()['token']


def test_user_to_dict_does_not_expose_password(client):
    with app.app_context():
        user = User.query.filter_by(email='user@test.com').first()
        payload = user.to_dict()
    assert 'password' not in payload
    assert app.config['SECRET_KEY'] != 'dev-secret-key'


def test_non_admin_cannot_change_role(client):
    token = _token(client, 'user@test.com', 'abcd')
    response = client.put('/users/2', json={'role': 'admin'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403


def test_public_signup_cannot_assign_privileged_role(client):
    response = client.post('/users', json={
        'name': 'Escalation',
        'email': 'escalation@test.com',
        'password': 'pass',
        'role': 'admin',
    })
    assert response.status_code == 403
    assert User.query.filter_by(email='escalation@test.com').first() is None


def test_task_mutations_require_authentication(client):
    response = client.post('/tasks', json={'title': 'No token task'})
    assert response.status_code == 401


def test_user_and_category_mutations_require_authentication(client):
    responses = [
        client.put('/users/2', json={'name': 'No token'}),
        client.delete('/users/2'),
        client.post('/categories', json={'name': 'No token'}),
        client.put('/categories/1', json={'name': 'No token'}),
        client.delete('/categories/1'),
    ]
    assert all(response.status_code == 401 for response in responses)


def test_malformed_task_status_returns_bad_request(client):
    token = _token(client, 'admin@test.com', '1234')
    response = client.post(
        '/tasks',
        json={'title': 'Malformed status', 'status': []},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 400


def test_other_user_cannot_update_task_but_admin_can(client):
    other_token = _token(client, 'other@test.com', 'xyz1')
    forbidden = client.put(
        '/tasks/1',
        json={'title': 'Changed by non-owner'},
        headers={'Authorization': f'Bearer {other_token}'},
    )
    assert forbidden.status_code == 403

    admin_token = _token(client, 'admin@test.com', '1234')
    allowed = client.put(
        '/tasks/1',
        json={'title': 'Changed by admin'},
        headers={'Authorization': f'Bearer {admin_token}'},
    )
    assert allowed.status_code == 200


def test_owner_can_update_own_task(client):
    token = _token(client, 'user@test.com', 'abcd')
    response = client.put('/tasks/1', json={'title': 'Updated own task'}, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
