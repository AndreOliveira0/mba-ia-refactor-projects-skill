import pytest

from app import app, db
from models.category import Category
from models.task import Task
from models.user import User


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(name='Admin', email='admin@test.com', role='admin')
        admin.set_password('1234')
        owner = User(name='Owner', email='owner@test.com', role='user')
        owner.set_password('abcd')
        other = User(name='Other', email='other@test.com', role='user')
        other.set_password('xyz1')
        db.session.add_all([admin, owner, other])
        db.session.commit()

        cat = Category(name='General', description='General tasks')
        db.session.add(cat)
        db.session.commit()

        task = Task(title='Own task', description='Owned by owner', status='pending', priority=2, user_id=owner.id, category_id=cat.id)
        db.session.add(task)
        db.session.commit()

    with app.test_client() as client:
        yield client


def _login(client, email, password):
    res = client.post('/login', json={'email': email, 'password': password})
    assert res.status_code == 200, res.get_data(as_text=True)
    return res.get_json()['token']


def test_root_and_health(client):
    assert client.get('/').status_code == 200
    assert client.get('/health').status_code == 200


def test_task_crud_and_query(client):
    token = _login(client, 'owner@test.com', 'abcd')
    create = client.post('/tasks', json={'title': 'Task New', 'description': 'desc', 'status': 'pending', 'priority': 2}, headers={'Authorization': f'Bearer {token}'})
    assert create.status_code == 201
    task_id = create.get_json()['id']

    list_resp = client.get('/tasks')
    assert list_resp.status_code == 200
    assert len(list_resp.get_json()) >= 1

    detail = client.get(f'/tasks/{task_id}')
    assert detail.status_code == 200

    update = client.put(f'/tasks/{task_id}', json={'title': 'Task Updated'}, headers={'Authorization': f'Bearer {token}'})
    assert update.status_code == 200

    search = client.get('/tasks/search?q=Updated')
    assert search.status_code == 200

    stats = client.get('/tasks/stats')
    assert stats.status_code == 200

    delete = client.delete(f'/tasks/{task_id}', headers={'Authorization': f'Bearer {token}'})
    assert delete.status_code == 200


def test_user_and_auth_flow(client):
    login = client.post('/login', json={'email': 'owner@test.com', 'password': 'abcd'})
    assert login.status_code == 200
    token = login.get_json()['token']

    users = client.get('/users')
    assert users.status_code == 200
    owner_id = next(u['id'] for u in users.get_json() if u['email'] == 'owner@test.com')

    created = client.post('/users', json={'name': 'Alice', 'email': 'alice@test.com', 'password': '1234', 'role': 'user'})
    assert created.status_code == 201
    other_user_id = created.get_json()['id']

    self_get = client.get(f'/users/{owner_id}', headers={'Authorization': f'Bearer {token}'})
    assert self_get.status_code == 200

    self_update = client.put(f'/users/{owner_id}', json={'name': 'Owner Updated'}, headers={'Authorization': f'Bearer {token}'})
    assert self_update.status_code == 200

    forbid_other = client.put(f'/users/{other_user_id}', json={'name': 'Alice Updated'}, headers={'Authorization': f'Bearer {token}'})
    assert forbid_other.status_code == 403

    forbid_role = client.put(f'/users/{owner_id}', json={'role': 'admin'}, headers={'Authorization': f'Bearer {token}'})
    assert forbid_role.status_code == 403


def test_reports_and_categories(client):
    token = _login(client, 'admin@test.com', '1234')

    summary = client.get('/reports/summary')
    assert summary.status_code == 200

    user_report = client.get('/reports/user/2')
    assert user_report.status_code == 200

    categories = client.get('/categories')
    assert categories.status_code == 200

    cat = client.post('/categories', json={'name': 'Ops'}, headers={'Authorization': f'Bearer {token}'})
    assert cat.status_code == 201
    cat_id = cat.get_json()['id']

    patch = client.put(f'/categories/{cat_id}', json={'description': 'Operations'}, headers={'Authorization': f'Bearer {token}'})
    assert patch.status_code == 200

    delete = client.delete(f'/categories/{cat_id}', headers={'Authorization': f'Bearer {token}'})
    assert delete.status_code == 200
