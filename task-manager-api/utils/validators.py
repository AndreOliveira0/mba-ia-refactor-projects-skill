import re


EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')
VALID_ROLES = {'user', 'admin', 'manager'}
VALID_TASK_STATUSES = {'pending', 'in_progress', 'done', 'cancelled'}


def is_valid_email(value):
    return isinstance(value, str) and EMAIL_PATTERN.fullmatch(value) is not None


def is_valid_password(value):
    return isinstance(value, str) and len(value) >= 4


def task_title_error(value):
    if not isinstance(value, str):
        return 'Título inválido'
    if len(value) < 3:
        return 'Título muito curto'
    if len(value) > 200:
        return 'Título muito longo'
    return None


def is_valid_task_status(value):
    return isinstance(value, str) and value in VALID_TASK_STATUSES


def is_valid_task_priority(value):
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 5


def is_valid_role(value):
    return isinstance(value, str) and value in VALID_ROLES