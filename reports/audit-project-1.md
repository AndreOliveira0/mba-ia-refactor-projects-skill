## Header
- Project: code-smells-project
- Stack: Python + Flask
- Date: 2026-09-29
- Files analyzed: 4

## Summary
- CRITICAL: 4
- HIGH: 3
- MEDIUM: 2
- LOW: 3
- Total findings: 12

## Architecture Snapshot
- Current architecture: monolitica/script-centric com separacao parcial em modulos (app/controllers/models/database), mas com fortes violacoes de fronteira.
- Persistence: SQLite via sqlite3 com SQL bruto.
- Main domain: e-commerce (produtos, usuarios, pedidos e relatorio de vendas).

## Findings (ordenados por severidade)

### [CRITICAL] Execucao de SQL arbitrario vindo de request
- File: app.py:59-76
- Category: security
- Evidence: Endpoint /admin/query recebe `sql` via body (`query = dados.get("sql", "")`) e executa diretamente com `cursor.execute(query)`.
- Impact: atacante pode ler, alterar ou apagar dados, alem de executar comandos destrutivos no banco.
- Recommendation: remover endpoint ou restringir a operacoes whitelisted com autenticacao forte e autorizacao admin.

### [CRITICAL] SQL Injection por concatenacao de entradas em queries
- File: models.py:47-50,57-61,109-111,126-129,289-299
- Category: security
- Evidence: queries montadas por concatenacao de strings com dados de entrada (`nome`, `descricao`, `email`, `senha`, `termo`, `categoria` etc.).
- Impact: injecao SQL, vazamento/alteracao de dados e comprometimento de integridade.
- Recommendation: substituir por queries parametrizadas (`?`) em todas as operacoes.

### [CRITICAL] Segredos hardcoded no codigo e expostos em endpoint
- File: app.py:7; controllers.py:289
- Category: security
- Evidence: SECRET_KEY hardcoded (`"minha-chave-super-secreta-123"`) e retornada no payload do health check.
- Impact: comprometimento de sessao/token e takeover de ambiente.
- Recommendation: mover segredos para variaveis de ambiente e nunca retornar segredos em respostas HTTP.

### [CRITICAL] Senhas em texto puro (armazenamento e autenticacao)
- File: database.py:75-78; models.py:109-111,126-129
- Category: security
- Evidence: seeds com senhas em texto puro, insercao direta de senha e comparacao por igualdade sem hash forte.
- Impact: exposicao total de contas em caso de vazamento do banco.
- Recommendation: usar hash de senha forte (bcrypt/argon2) com salt e comparar via API segura.

### [HIGH] Endpoint administrativo sem autenticacao/autorizacao
- File: app.py:47-57,59-76
- Category: security
- Evidence: rotas /admin/reset-db e /admin/query sem qualquer validacao de identidade ou role.
- Impact: qualquer cliente pode apagar dados e executar operacoes administrativas.
- Recommendation: proteger com middleware de autenticacao + RBAC, ou remover em producao.

### [HIGH] Exposicao de dados sensiveis em respostas
- File: models.py:83,99; controllers.py:128-140,264-290
- Category: security
- Evidence: retorno de campo `senha` em listagem/busca de usuarios e retorno de `secret_key` no health check.
- Impact: vazamento de credenciais e segredos internos.
- Recommendation: usar DTOs de resposta sem campos sensiveis e restringir dados do health.

### [HIGH] Modo debug habilitado em configuracao de producao
- File: app.py:8,88; controllers.py:286-289
- Category: security
- Evidence: DEBUG ligado (`app.config["DEBUG"] = True`, `debug=True`) enquanto health indica `ambiente: "producao"`.
- Impact: stack traces e detalhes internos podem vazar para usuarios.
- Recommendation: controlar debug por variavel de ambiente com default seguro (`False`).

### [MEDIUM] God Module com responsabilidades misturadas
- File: controllers.py:1-292
- Category: architecture
- Evidence: mesmo modulo concentra parse HTTP, validacao, orquestracao de negocio, logs e chamadas de persistencia para varios dominios.
- Impact: baixa testabilidade, alto acoplamento e maior risco de regressao.
- Recommendation: separar por contexto (produtos/usuarios/pedidos) e mover regra de negocio para services/controllers menores.

### [MEDIUM] Falta de tratamento de erro padronizado
- File: app.py:77-78; controllers.py:10-12,21-22,60-62,95-96,108-109,125-126,133-134,143-144,164-165,185-186,218-220,226-227,234-235,254-255,261-262,291-292
- Category: code smell
- Evidence: multiplos `except Exception as e` retornando payloads diferentes com `str(e)` diretamente.
- Impact: respostas inconsistentes, vazamento de detalhe interno e observabilidade fraca.
- Recommendation: criar handler global de erros com estrutura unica (`error_code`, `message`, `trace_id`).

### [LOW] Logs com print em fluxo de aplicacao
- File: app.py:56,83-86; controllers.py:8,11,57,106,161,179,182,208-210,219,248-250
- Category: code smell
- Evidence: uso extensivo de `print` para eventos operacionais e erros.
- Impact: logs sem nivel/contexto e dificulta troubleshooting em ambiente real.
- Recommendation: adotar logger estruturado com niveis (INFO/WARN/ERROR) e metadata.

### [LOW] Duplicacao de validacao ad-hoc
- File: controllers.py:28-55,72-90
- Category: code smell
- Evidence: validacoes de produto repetidas em criar_produto e atualizar_produto.
- Impact: manutencao mais custosa e chance de divergencia de regra.
- Recommendation: extrair schema/validador reutilizavel para payload de produto.

### [LOW] Importacoes mortas / nao utilizadas
- File: database.py:2; models.py:2
- Category: code smell
- Evidence: `os` em database.py e `sqlite3` em models.py sem uso.
- Impact: ruido cognitivo e manutencao desnecessaria.
- Recommendation: remover imports nao utilizados e ativar lint.

## Deprecated API Notes
- API/Pattern: Nao foi identificado uso explicito de API de criptografia deprecated (ex.: md5/sha1) neste codigo.
- Location: N/A
- Why obsolete/risky: Embora sem API deprecated, o uso de senha em texto puro e comparacao direta e inseguro.
- Modern equivalent: `werkzeug.security.generate_password_hash` / `check_password_hash` (ou bcrypt/argon2).

## Quick Wins
- 1) Remover/fechar imediatamente /admin/query e /admin/reset-db em runtime de producao.
- 2) Trocar todas as queries concatenadas por parametrizadas no models.
- 3) Parar de retornar `senha`, `secret_key` e indicadores internos no health.

## Refactoring Readiness
- Blocking issues before refactor: SQL arbitrario, SQL injection generalizado, segredos hardcoded/expostos, senha em texto puro, rotas admin sem auth.
- Estimated complexity: high
- Suggested order: (1) seguranca critica, (2) auth/RBAC, (3) hash de senha, (4) MVC por dominio, (5) error handling central, (6) observabilidade e limpeza.

## Mandatory Checkpoint Output
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
