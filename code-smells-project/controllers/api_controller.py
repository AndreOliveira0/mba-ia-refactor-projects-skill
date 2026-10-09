from flask import jsonify, request

from middlewares.errors import AppError
from models import repositories as repo


VALID_PRODUCT_CATEGORIES = {
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
}

VALID_PEDIDO_STATUS = {"pendente", "aprovado", "enviado", "entregue", "cancelado"}


def _success(data=None, message=None, status=200, extra=None):
    payload = {"sucesso": True}
    if data is not None:
        payload["dados"] = data
    if message:
        payload["mensagem"] = message
    if extra:
        payload.update(extra)
    return jsonify(payload), status


def _parse_json_payload():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise AppError("Dados invalidos", 400, "VALIDATION_ERROR")
    return dados


def _validate_product_payload(dados):
    required = ["nome", "preco", "estoque"]
    missing = [field for field in required if field not in dados]
    if missing:
        raise AppError("Campos obrigatorios ausentes: " + ", ".join(missing), 400, "VALIDATION_ERROR")

    nome = str(dados["nome"]).strip()
    if len(nome) < 2 or len(nome) > 200:
        raise AppError("Nome deve ter entre 2 e 200 caracteres", 400, "VALIDATION_ERROR")

    try:
        preco = float(dados["preco"])
        estoque = int(dados["estoque"])
    except (TypeError, ValueError):
        raise AppError("Preco deve ser numerico e estoque deve ser inteiro", 400, "VALIDATION_ERROR")

    if preco < 0:
        raise AppError("Preco nao pode ser negativo", 400, "VALIDATION_ERROR")
    if estoque < 0:
        raise AppError("Estoque nao pode ser negativo", 400, "VALIDATION_ERROR")

    descricao = str(dados.get("descricao", "")).strip()
    categoria = str(dados.get("categoria", "geral")).strip().lower()
    if categoria not in VALID_PRODUCT_CATEGORIES:
        raise AppError(
            "Categoria invalida. Validas: " + ", ".join(sorted(VALID_PRODUCT_CATEGORIES)),
            400,
            "VALIDATION_ERROR",
        )

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo a API da Loja",
            "versao": "1.1.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )


def listar_produtos():
    return _success(data=repo.get_todos_produtos())


def buscar_produto(produto_id):
    produto = repo.get_produto_por_id(produto_id)
    if not produto:
        raise AppError("Produto nao encontrado", 404, "NOT_FOUND")
    return _success(data=produto)


def criar_produto():
    dados = _parse_json_payload()
    payload = _validate_product_payload(dados)
    produto_id = repo.criar_produto(**payload)
    return _success(data={"id": produto_id}, message="Produto criado", status=201)


def atualizar_produto(produto_id):
    if not repo.get_produto_por_id(produto_id):
        raise AppError("Produto nao encontrado", 404, "NOT_FOUND")
    dados = _parse_json_payload()
    payload = _validate_product_payload(dados)
    repo.atualizar_produto(produto_id=produto_id, **payload)
    return _success(message="Produto atualizado")


def deletar_produto(produto_id):
    if not repo.get_produto_por_id(produto_id):
        raise AppError("Produto nao encontrado", 404, "NOT_FOUND")
    repo.deletar_produto(produto_id)
    return _success(message="Produto deletado")


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = request.args.get("preco_min")
    preco_max = request.args.get("preco_max")

    try:
        preco_min = float(preco_min) if preco_min is not None else None
        preco_max = float(preco_max) if preco_max is not None else None
    except ValueError:
        raise AppError("preco_min e preco_max devem ser numericos", 400, "VALIDATION_ERROR")

    resultados = repo.buscar_produtos(termo, categoria, preco_min, preco_max)
    return _success(data=resultados, extra={"total": len(resultados)})


def listar_usuarios():
    return _success(data=repo.get_todos_usuarios())


def buscar_usuario(usuario_id):
    usuario = repo.get_usuario_por_id(usuario_id)
    if not usuario:
        raise AppError("Usuario nao encontrado", 404, "NOT_FOUND")
    return _success(data=usuario)


def criar_usuario():
    dados = _parse_json_payload()
    nome = str(dados.get("nome", "")).strip()
    email = str(dados.get("email", "")).strip().lower()
    senha = str(dados.get("senha", ""))

    if not nome or not email or not senha:
        raise AppError("Nome, email e senha sao obrigatorios", 400, "VALIDATION_ERROR")
    if "@" not in email:
        raise AppError("Email invalido", 400, "VALIDATION_ERROR")
    if len(senha) < 6:
        raise AppError("Senha deve ter ao menos 6 caracteres", 400, "VALIDATION_ERROR")

    user_id = repo.criar_usuario(nome, email, senha)
    return _success(data={"id": user_id}, status=201)


def login():
    dados = _parse_json_payload()
    email = str(dados.get("email", "")).strip().lower()
    senha = str(dados.get("senha", ""))

    if not email or not senha:
        raise AppError("Email e senha sao obrigatorios", 400, "VALIDATION_ERROR")

    usuario = repo.login_usuario(email, senha)
    if not usuario:
        raise AppError("Email ou senha invalidos", 401, "UNAUTHORIZED")

    return _success(data=usuario, message="Login OK")


def criar_pedido():
    dados = _parse_json_payload()
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise AppError("usuario_id e obrigatorio", 400, "VALIDATION_ERROR")
    if not isinstance(itens, list) or len(itens) == 0:
        raise AppError("Pedido deve ter pelo menos 1 item", 400, "VALIDATION_ERROR")

    resultado = repo.criar_pedido(usuario_id, itens)
    if "erro" in resultado:
        raise AppError(resultado["erro"], 400, "BUSINESS_RULE_VIOLATION")

    return _success(data=resultado, message="Pedido criado com sucesso", status=201)


def listar_pedidos_usuario(usuario_id):
    return _success(data=repo.get_pedidos_usuario(usuario_id))


def listar_todos_pedidos():
    return _success(data=repo.get_todos_pedidos())


def atualizar_status_pedido(pedido_id):
    dados = _parse_json_payload()
    novo_status = str(dados.get("status", "")).strip().lower()
    if novo_status not in VALID_PEDIDO_STATUS:
        raise AppError("Status invalido", 400, "VALIDATION_ERROR")

    repo.atualizar_status_pedido(pedido_id, novo_status)
    return _success(message="Status atualizado")


def relatorio_vendas():
    return _success(data=repo.relatorio_vendas())


def health_check():
    return jsonify({"status": "ok", "database": "connected", "counts": repo.db_stats(), "versao": "1.1.0"}), 200


def reset_database():
    repo.reset_database()
    return _success(message="Banco de dados resetado")


def admin_query():
    dados = request.get_json(silent=True) or {}
    sql = dados.get("sql", "")
    if sql:
        result = repo.run_admin_whitelisted_query(sql)
        if result is None:
            raise AppError("Operacao administrativa nao permitida", 400, "VALIDATION_ERROR")
        return _success(data=result)

    job = dados.get("job", "")
    if job != "db_stats":
        raise AppError("Operacao administrativa nao permitida", 400, "VALIDATION_ERROR")
    return _success(data=repo.db_stats())
