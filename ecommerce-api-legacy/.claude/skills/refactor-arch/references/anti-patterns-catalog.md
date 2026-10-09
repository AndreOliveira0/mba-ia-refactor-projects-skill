# Anti-Patterns Catalog

## Como usar
Para cada item detectado, registrar evidencia com arquivo e linhas exatas, impacto e recomendacao.

## CRITICAL

### 1. SQL Injection por concatenacao
- Sinais: query SQL montada com +, f-string ou template literal contendo entrada de usuario.
- Exemplos: WHERE id = " + id, LIKE '%" + termo + "%'.
- Impacto: leitura/alteracao indevida de dados.
- Correcao: queries parametrizadas e validacao de tipos.

### 2. Segredos hardcoded
- Sinais: SECRET_KEY, tokens de API, senha SMTP, chaves de pagamento no codigo.
- Impacto: comprometimento total de ambiente e integracoes.
- Correcao: variaveis de ambiente + secret manager.

### 3. Execucao de SQL arbitrario vindo de request
- Sinais: endpoint que recebe "sql" no body e executa diretamente.
- Impacto: execucao remota de comandos no banco.
- Correcao: remover endpoint ou limitar a operacoes seguras predefinidas.

### 4. Senha em texto puro
- Sinais: armazenamento direto de senha ou comparacao sem hash forte.
- Impacto: comprometimento de contas e conformidade.
- Correcao: Argon2/bcrypt/scrypt + salt.

## HIGH

### 5. API de hash obsoleta/criptografia fraca
- Sinais: hashlib.md5, sha1 para senha, base64 como "hash".
- Impacto: quebra rapida por brute force/rainbow table.
- Correcao: Argon2id ou bcrypt com custo adequado.

### 6. Exposicao de dados sensiveis em resposta
- Sinais: retorno de password/hash, secret_key, tokens internos em JSON.
- Impacto: vazamento de dados e escalacao de ataque.
- Correcao: DTO/schemas para resposta e mascaramento.

### 7. Endpoint administrativo sem autenticacao/autorizacao
- Sinais: rotas /admin/* sem verificacao de identidade/perfil.
- Impacto: destruicao de dados e abuso operacional.
- Correcao: middleware de auth + RBAC.

### 8. Escalada de privilegios por mass assignment em campos sensiveis
- Sinais: endpoints publicos de atualizacao de usuario (ex.: PUT /users/<id>) aplicam diretamente o body ao registro e aceitam alterar `role` sem verificar se o solicitante e administrador. Tambem inclui confiar em `role` ou `user_id` enviado no body para decidir autorizacao.
- Impacto: um usuario autenticado pode promover a propria conta ou outra conta a admin, contornando os limites de acesso; classificar como CRITICAL quando permitir comprometimento administrativo amplo.
- Correcao: allowlist explicita de campos atualizaveis; rejeitar `role` para nao-admin com 403 Forbidden; permitir alteracao de papel somente apos verificacao RBAC no servidor. Nunca usar campos de identidade/autorizacao fornecidos pelo cliente como fonte de confianca.

### 9. Ausencia de verificacao de proprietario do recurso (IDOR)
- Sinais: usuario autenticado consegue alterar ou deletar recurso de outro usuario sem validar `current_user.id == resource.owner_id` ou `current_user.role == 'admin'`.
- Impacto: leitura, alteracao ou exclusao nao autorizada de dados alheios; pode expor dados entre contas e causar perda de dados.
- Correcao: em cada operacao mutavel, carregar o recurso e autorizar somente o proprietario ou um admin; responder 403 Forbidden quando o solicitante nao tiver permissao. Aplicar a verificacao no servidor, inclusive quando IDs forem dificeis de adivinhar.

### 10. Modo debug habilitado fora de ambiente local
- Sinais: debug=True fixo, DEBUG=True hardcoded.
- Impacto: leakage de stacktrace e info interna.
- Correcao: controlar por ambiente e defaults seguros.

## MEDIUM

### 11. God Class / God Module
- Sinais: arquivo concentra rotas + regra de negocio + persistencia.
- Impacto: baixa testabilidade e alta taxa de regressao.
- Correcao: separar em Models, Controllers e Routes.

### 12. Estado global mutavel compartilhado
- Sinais: caches/globais escritos por varias funcoes sem controle.
- Impacto: comportamento nao deterministico e bugs concorrentes.
- Correcao: encapsular estado e adotar injeção de dependencia.

### 13. Callback hell / fluxo assincrono aninhado
- Sinais: multiplos niveis de callbacks sem composicao.
- Impacto: manutencao dificil e tratamento de erro incompleto.
- Correcao: async/await, servicos e funcoes pequenas.

### 14. Falta de tratamento de erro padronizado
- Sinais: except/bare catch generico, respostas inconsistentes.
- Impacto: observabilidade baixa e UX de API inconsistente.
- Correcao: error handler central e classes de erro de dominio.

## LOW

### 15. Logs com print/console.log em producao
- Sinais: logs sem niveis/contexto e sem correlacao.
- Impacto: troubleshooting limitado.
- Correcao: logger estruturado com niveis e metadata.

### 16. Duplicacao de validacao em varias rotas
- Sinais: blocos repetidos para campos/status/prioridade.
- Impacto: manutencao custosa e inconsistencias.
- Correcao: schemas e validadores reutilizaveis.

### 17. Importacoes mortas e codigo nao utilizado
- Sinais: imports sem uso, utilitarios nao invocados.
- Impacto: ruido cognitivo e risco de divergencia.
- Correcao: limpeza automatica por lint/static analysis.

## APIs obsoletas/deprecated para sinalizar
- Python: hashlib.md5 para senha (inadequado para password hashing).
- Node.js: pseudo-hash com Base64 (nao e KDF seguro).
- Flask/SQLAlchemy: Query.get legado em algumas versoes/estilos; preferir Session.get quando aplicavel.
- Qualquer estrategia custom de token fake para autenticacao deve ser tratada como antipattern de seguranca.
