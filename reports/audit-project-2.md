# Audit Report

## Header
- Project: ecommerce-api-legacy
- Stack: Node.js + Express
- Date: 2026-09-29
- Files analyzed: 3

## Summary
- CRITICAL: 2
- HIGH: 2
- MEDIUM: 2
- LOW: 2
- Total findings: 8

## Architecture Snapshot
- Current architecture: monolitica / script-centric
- Persistence: SQLite in-memory com SQL bruto
- Main domain: LMS/e-commerce de checkout de cursos, matriculas e relatorio financeiro

## Findings (ordenados por severidade)

### [CRITICAL] Segredos hardcoded em configuracao e credenciais
- File: src/utils.js:1-6
- Category: security
- Evidence: `dbUser`, `dbPass`, `paymentGatewayKey` e `smtpUser` estao definidos diretamente no objeto `config`.
- Impact: expõe credenciais de banco, gateway de pagamento e email, permitindo comprometimento de ambientes e integracoes.
- Recommendation: mover todos os segredos para variaveis de ambiente e carregar via modulo central de configuracao.

### [CRITICAL] Senha armazenada em texto puro no seed inicial
- File: src/AppManager.js:18
- Category: security
- Evidence: o seed insere `pass` com o valor literal `'123'` no usuario inicial.
- Impact: qualquer acesso ao banco revela credenciais reutilizaveis e viola boas praticas basicas de seguranca.
- Recommendation: remover seeds com senha em texto puro e usar hash forte para qualquer persistencia de senha.

### [HIGH] API de hash fraca baseada em Base64 para senha
- File: src/utils.js:17-22
- Category: security
- Evidence: `badCrypto` converte a senha para Base64 repetidamente e recorta o resultado como se fosse hash.
- Impact: o esquema e trivialmente reversivel/forcavel e nao protege credenciais de usuario.
- Recommendation: trocar por bcrypt ou Argon2 com custo adequado e salt.

### [HIGH] Endpoint administrativo sem autenticacao/autorizacao
- File: src/AppManager.js:80-129
- Category: security
- Evidence: `/api/admin/financial-report` expõe relatorio financeiro completo sem qualquer middleware de auth ou verificacao de perfil.
- Impact: qualquer cliente pode consultar receita e dados de alunos, causando vazamento operacional e de privacidade.
- Recommendation: proteger a rota com autenticacao, RBAC e, idealmente, middleware dedicado para admin.

### [MEDIUM] God module concentra rotas, negocio e persistencia
- File: src/AppManager.js:10-141
- Category: architecture
- Evidence: o mesmo arquivo cria schema, inicializa seeds e declara todas as rotas com acesso direto ao SQLite.
- Impact: baixa testabilidade, manutencao dificil e alto risco de regressao ao alterar qualquer fluxo.
- Recommendation: separar em models, controllers e routes, mantendo o entry point apenas como composition root.

### [MEDIUM] Fluxo assincrono aninhado e dificil de manter
- File: src/AppManager.js:28-137
- Category: code smell
- Evidence: o checkout e o relatorio financeiro usam multiplos callbacks aninhados com contadores manuais de conclusao.
- Impact: aumenta complexidade ciclomatica, dificulta tratamento de erro e favorece bugs de concorrencia/logica.
- Recommendation: reestruturar com funcoes pequenas e uma camada de repositorio/servico; se possivel, migrar para async/await.

### [LOW] Logs diretos com console.log em fluxo de producao
- File: src/AppManager.js:45,59 e src/utils.js:13; src/app.js:13
- Category: code smell
- Evidence: o checkout loga a chave do gateway, o cache usa console.log e o bootstrap imprime mensagem fixa ao subir.
- Impact: observabilidade inconsistente e risco de expor informacao sensivel em logs.
- Recommendation: substituir por logger estruturado com niveis e mascaramento de dados sensiveis.

### [LOW] Importacao e estado global nao utilizados em utilitarios
- File: src/AppManager.js:2 e src/utils.js:10,25
- Category: code smell
- Evidence: `totalRevenue` e exportado/importeado, mas nao ha uso real no fluxo; o estado global tambem nao possui dono claro.
- Impact: ruido cognitivo e indicio de acumulacao de estado compartilhado dificil de controlar.
- Recommendation: remover simbolos mortos e encapsular estado em uma responsabilidade explicita.

## Deprecated API Notes
- API/Pattern: Base64 como pseudo-hash de senha
- Location: src/utils.js:17-22
- Why obsolete/risky: nao e um algoritmo de derivacao de chave nem protege contra forca bruta.
- Modern equivalent: bcrypt ou Argon2id.

## Quick Wins
- 1) Mover `config` sensivel para variaveis de ambiente.
- 2) Trocar `badCrypto` por bcrypt/Argon2 e remover seed com senha em texto puro.
- 3) Proteger `/api/admin/financial-report` com autenticao/autorizacao.

## Refactoring Readiness
- Blocking issues before refactor: segredos hardcoded, senha fraca/texto puro, endpoint admin aberto
- Estimated complexity: medium
- Suggested order: configurar ambiente -> corrigir seguranca -> separar MVC -> centralizar erros -> validar boot e contratos

## Mandatory Checkpoint Output
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
