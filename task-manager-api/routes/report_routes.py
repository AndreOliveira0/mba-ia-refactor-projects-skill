from flask import Blueprint

from controllers.report_controller import (
    create_category,
    delete_category,
    get_categories,
    summary_report,
    update_category,
    user_report,
)
from middlewares.auth import require_auth

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report_route():
    return summary_report()


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report_route(user_id):
    return user_report(user_id)


@report_bp.route('/categories', methods=['GET'])
def get_categories_route():
    return get_categories()


@report_bp.route('/categories', methods=['POST'])
@require_auth
def create_category_route():
    return create_category()


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@require_auth
def update_category_route(cat_id):
    return update_category(cat_id)


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@require_auth
def delete_category_route(cat_id):
    return delete_category(cat_id)
