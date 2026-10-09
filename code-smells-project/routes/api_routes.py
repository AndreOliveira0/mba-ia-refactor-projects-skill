from functools import wraps

from flask import Blueprint, current_app, request

from controllers import api_controller as ctl
from middlewares.errors import AppError


api_bp = Blueprint("api", __name__)


def require_admin_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        configured = current_app.config.get("ADMIN_TOKEN", "")
        if not configured:
            raise AppError("ADMIN_TOKEN nao configurado", 503, "SERVICE_MISCONFIGURATION")

        token = request.headers.get("X-Admin-Token", "")
        if token != configured:
            raise AppError("Nao autorizado", 401, "UNAUTHORIZED")

        return func(*args, **kwargs)

    return wrapper


api_bp.add_url_rule("/", "index", ctl.index, methods=["GET"])

api_bp.add_url_rule("/produtos", "listar_produtos", ctl.listar_produtos, methods=["GET"])
api_bp.add_url_rule("/produtos/busca", "buscar_produtos", ctl.buscar_produtos, methods=["GET"])
api_bp.add_url_rule("/produtos/<int:produto_id>", "buscar_produto", ctl.buscar_produto, methods=["GET"])
api_bp.add_url_rule("/produtos", "criar_produto", ctl.criar_produto, methods=["POST"])
api_bp.add_url_rule("/produtos/<int:produto_id>", "atualizar_produto", ctl.atualizar_produto, methods=["PUT"])
api_bp.add_url_rule("/produtos/<int:produto_id>", "deletar_produto", ctl.deletar_produto, methods=["DELETE"])

api_bp.add_url_rule("/usuarios", "listar_usuarios", ctl.listar_usuarios, methods=["GET"])
api_bp.add_url_rule("/usuarios/<int:usuario_id>", "buscar_usuario", ctl.buscar_usuario, methods=["GET"])
api_bp.add_url_rule("/usuarios", "criar_usuario", ctl.criar_usuario, methods=["POST"])
api_bp.add_url_rule("/login", "login", ctl.login, methods=["POST"])

api_bp.add_url_rule("/pedidos", "criar_pedido", ctl.criar_pedido, methods=["POST"])
api_bp.add_url_rule("/pedidos", "listar_todos_pedidos", ctl.listar_todos_pedidos, methods=["GET"])
api_bp.add_url_rule("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", ctl.listar_pedidos_usuario, methods=["GET"])
api_bp.add_url_rule("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", ctl.atualizar_status_pedido, methods=["PUT"])

api_bp.add_url_rule("/relatorios/vendas", "relatorio_vendas", ctl.relatorio_vendas, methods=["GET"])
api_bp.add_url_rule("/health", "health_check", ctl.health_check, methods=["GET"])

api_bp.add_url_rule("/admin/reset-db", "reset_database", require_admin_token(ctl.reset_database), methods=["POST"])
api_bp.add_url_rule("/admin/query", "admin_query", require_admin_token(ctl.admin_query), methods=["POST"])
