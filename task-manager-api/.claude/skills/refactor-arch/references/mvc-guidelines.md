# MVC Guidelines

## Objetivo
Definir o estado alvo para refatoracao com separacao de responsabilidades.

## Camadas

### Models
- Responsabilidade: persistencia, mapeamento de entidades, queries/repositorios.
- Nao deve: conhecer detalhes HTTP (request/response).
- Saida: entidades, DTOs internos ou objetos de dominio.

### Views/Routes
- Responsabilidade: contrato HTTP (rotas, status code, parse basico).
- Nao deve: conter regra de negocio complexa nem SQL direto.
- Encaminha dados para Controllers e devolve resposta padronizada.

### Controllers
- Responsabilidade: orquestrar casos de uso, validacoes de negocio e transacoes.
- Interage com models/repositorios/servicos.
- Nao deve: formatar detalhes de infraestrutura de baixo nivel.

### Services (opcional, recomendado)
- Responsabilidade: integracoes externas (email, pagamento, cache, fila).
- Encapsular clientes e retries/timeouts.

## Config Centralizado
- Criar modulo de configuracao por ambiente.
- Ler segredos de variaveis de ambiente.
- Evitar constantes sensiveis no codigo-fonte.

## Error Handling Middleware
- Centralizar traducao de excecoes para respostas HTTP.
- Usar estrutura consistente:
  - error_code
  - message
  - details (opcional em dev)
  - trace_id (quando disponivel)

## Regras de Seguranca Minimas
- Hash de senha com algoritmo adequado (Argon2/bcrypt).
- Queries parametrizadas.
- Sanitizacao e validacao de entrada por schema.
- Token valido e somente autenticacao; cada rota mutavel DEVE tambem aplicar autorizacao RBAC e verificar acesso ao recurso.
- Extrair identidade e papel (`user_id`, `role`) somente de claims de token autenticado e validado no servidor; nunca confiar em valores equivalentes enviados no body, query ou parametros do cliente.
- Em atualizacao de usuario, usar allowlist de campos. Alterar `role` e permitido somente a admin; tentativa por usuario nao-admin deve retornar `403 Forbidden`, inclusive quando o campo vier misturado a outros campos permitidos.
- Em rotas mutaveis de usuario/recurso (PUT/PATCH/DELETE), permitir a acao somente se o solicitante for o proprietario persistido do recurso (`current_user.id == resource.owner_id`) ou admin (`current_user.role == 'admin'`); caso contrario, retornar `403 Forbidden`.
- Aplicar autorizacao no controller/service ou middleware com recurso carregado do repositorio, sem depender apenas de esconder IDs ou da camada de interface.
- Rotas administrativas com autenticacao e autorizacao RBAC explicita.
- Nunca retornar password/hash/secret em payload.

## Autorizacao em rotas mutaveis
- O middleware de autenticacao valida assinatura e claims do token e disponibiliza identidade/papel no contexto da requisicao; ele nao concede permissao por si so.
- Cada operacao deve verificar papel e escopo sobre o recurso alvo, antes de persistir qualquer alteracao.
- Testar pelo menos: dono permitido, admin permitido, outro usuario negado com 403, e usuario nao-admin tentando definir `role` negado com 403.

## Estrutura de Pastas (referencia)

Python (Flask):
- src/
- src/config/
- src/models/
- src/controllers/
- src/routes/
- src/services/
- src/middlewares/
- src/app.py

Node (Express):
- src/
- src/config/
- src/models/
- src/controllers/
- src/routes/
- src/services/
- src/middlewares/
- src/app.js
