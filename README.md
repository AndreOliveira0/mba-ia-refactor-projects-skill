# Documentação da Entrega: Skill de Refatoração Arquitetural Automatizada (MVC + AI)

Este repositório contém a entrega final do desafio técnico do **MBA em Engenharia de Software com IA**. O objetivo principal foi desenvolver e validar uma **Skill agnóstica de tecnologia** (`refactor-arch`), capaz de realizar análise estática, auditoria de código/segurança e refatoração arquitetural automatizada em três codebases legadas distintas para o padrão **MVC (Model-View-Controller)**.

---

## 1. Análise Manual dos Projetos

Antes do desenvolvimento da Skill automatizada, realizou-se a inspeção manual das três codebases legadas para mapeamento de vulnerabilidades, *code smells* e violações arquiteturais.

### 1.1 `code-smells-project` (Python / Flask — E-commerce API)
* **Stack Detectada:** Python + Flask (Persistência via `sqlite3` com queries brutas)
* **Domínio:** E-commerce (Produtos, Usuários, Pedidos, Relatório de Vendas)
* **Arquitetura Inicial:** Monolítica / Script-centric dividida em 4 arquivos (`app.py`, `models.py`, `database.py`, `controllers.py`), com fortes violações de fronteira.

| Severidade | Problema / Vulnerabilidade | Arquivo / Linha | Justificativa / Impacto Relevante |
| :--- | :--- | :--- | :--- |
| **CRITICAL** | Execução de SQL arbitrário | `app.py:59-76` | O endpoint `/admin/query` recebe comandos SQL arbitrários via payload HTTP e os executa diretamente no banco de dados. Permite leitura, exclusão e destruição total do banco. |
| **CRITICAL** | SQL Injection por concatenação de strings | `models.py:47-50, 109-111` | Interpolação direta de entradas de usuário em queries SQL sem parametrização. Risco grave de sequestro e vazamento de dados. |
| **CRITICAL** | Segredos hardcoded no código | `app.py:7` | A `SECRET_KEY` ("minha-chave-super-secreta-123") está exposta no código-fonte e é retornada em endpoints públicos de health check. |
| **CRITICAL** | Senhas armazenadas em texto puro | `database.py:75-78` | Credenciais inseridas nos seeds e cadastradas no banco sem qualquer algoritmo de criptografia ou hash. |
| **HIGH** | Endpoints administrativos sem autenticação | `app.py:47-76` | Rotas de destruição/reset de banco (`/admin/reset-db`) e execução de queries expostas sem verificação de token ou perfil. |
| **HIGH** | Exposição de dados sensíveis em payloads | `controllers.py:264-290` | Serialização de usuário incluindo a senha em texto puro no JSON de resposta. |
| **HIGH** | Modo Debug ativado em produção | `app.py:8, 88` | `DEBUG = True` habilitado por padrão em ambiente configurado como produção. |
| **MEDIUM** | God Module com responsabilidades misturadas | `controllers.py:1-292` | Arquivo centraliza parsing HTTP, validação, regras de negócio, persistência e logs de múltiplos domínios. |
| **MEDIUM** | Ausência de tratamento centralizado de erros | `app.py:77-78` | Blocos `try/except` genéricos espalhados com respostas HTTP inconsistentes. |
| **LOW** | Uso de `print` para logging | `app.py:56, 83-86`; `controllers.py:8, 11, 57, 106, 161, 179, 182, 208-210, 219, 248-250` | Logs sem níveis ou contexto dificultam o troubleshooting em ambiente real. |
| **LOW** | Duplicação de validação ad-hoc | `controllers.py:28-55, 72-90` | Validações de produto repetidas em `criar_produto` e `atualizar_produto` aumentam o custo de manutenção e podem divergir. |
| **LOW** | Imports mortos / não utilizados | `database.py:2`; `models.py:2` | Imports sem uso geram ruído cognitivo e manutenção desnecessária. |

---

### 1.2 `ecommerce-api-legacy` (Node.js / Express — LMS / Checkout API)
* **Stack Detectada:** Node.js + Express (Persistência via `sqlite3` in-memory)
* **Domínio:** E-commerce / LMS (Checkout de cursos, Matrículas e Relatório Financeiro)
* **Arquitetura Inicial:** Script-centric acoplada em 3 arquivos (`src/app.js`, `src/AppManager.js`, `src/utils.js`).

| Severidade | Problema / Vulnerabilidade | Arquivo / Linha | Justificativa / Impacto Relevante |
| :--- | :--- | :--- | :--- |
| **CRITICAL** | Segredos e credenciais hardcoded | `src/utils.js:1-6` | `dbUser`, `dbPass`, `paymentGatewayKey` e `smtpUser` definidos diretamente no objeto de configuração no código. |
| **CRITICAL** | Senhas em texto puro nos seeds de banco | `src/AppManager.js:18` | Seed inicial cadastra o usuário admin com a senha literal `'123'`. |
| **HIGH** | Pseudo-hash de senha inseguro (Base64) | `src/utils.js:17-22` | Função `badCrypto` utiliza encodamento Base64 iterativo para "proteger" senhas. Inseguro e trivialmente reversível. |
| **HIGH** | Endpoint financeiro administrativo sem proteção | `src/AppManager.js:80-129` | Rota `/api/admin/financial-report` expõe faturamento e dados de alunos sem qualquer middleware de autenticação. |
| **MEDIUM** | God Module (`AppManager.js`) | `src/AppManager.js:10-141` | Arquivo único cria tabelas, popula seeds, gerencia estado e declara rotas com acessos diretos ao banco. |
| **MEDIUM** | Callbacks assíncronos aninhados ("Callback Hell") | `src/AppManager.js:28-137` | Fluxo de checkout utiliza callbacks profundos com contadores manuais, dificultando manutenção e controle de erros. |
| **LOW** | `console.log` em produção vazando dados | `src/AppManager.js:45` | Impressão da chave privada do gateway de pagamento nos logs do sistema. |
| **LOW** | Estado global compartilhado sem dono | `src/utils.js:10, 25` | Variável `totalRevenue` mantida globalmente sem encapsulamento adequado. |

---

### 1.3 `task-manager-api` (Python / Flask + SQLAlchemy — Task Manager API)
* **Stack Detectada:** Python + Flask + Flask-SQLAlchemy
* **Domínio:** Gestão de Tarefas (Tasks, Usuários e Categorias)
* **Arquitetura Inicial:** Parcialmente em camadas (`app.py`, `models/`, `routes/`, `services/`), mas com violações de responsabilidade e falhas críticas de segurança.

| Severidade | Problema / Vulnerabilidade | Arquivo / Linha | Justificativa / Impacto Relevante |
| :--- | :--- | :--- | :--- |
| **CRITICAL** | Segredo da aplicação hardcoded | `app.py:11-13` | `SECRET_KEY = 'super-secret-key-123'` definida diretamente no arquivo de entrada. |
| **CRITICAL** | Credenciais SMTP de e-mail hardcoded | `services/notification_service.py:7-10` | Host, usuário e senha do servidor SMTP expostos no código (`email_password = 'senha123'`). |
| **HIGH** | Hashing de senhas fraco/obsoleto (MD5) | `models/user.py:27-32` | Uso de `hashlib.md5()` para armazenamento e validação de credenciais de usuários. vulnerável a brute-force e rainbow tables. |
| **HIGH** | Campo `password` exposto na serialização | `models/user.py:16-24` | Método `to_dict()` inclui o hash da senha nos payloads JSON de resposta pública. |
| **HIGH** | Rotas de alteração de estado sem autenticação | `routes/user_routes.py:92-151` | Rotas de atualização/exclusão de usuários sem verificação de token real (login retorna `fake-jwt-token-...`). |
| **HIGH** | Modo Debug ativo no entrypoint | `app.py:33-34` | Inicialização com `debug=True` expõe depurador interativo e stack traces. |
| **MEDIUM** | Handlers de rota acumulando regras de negócio | `routes/task_routes.py:1-299` | Rotas realizam validações complexas, cálculo de status atrasado (*overdue*) e acesso direto ao ORM. |
| **MEDIUM** | Tratamento de erro genérico e inconsistente | `routes/task_routes.py:62-63, 137-138, 236-238; routes/user_routes.py:130-132, 149-151` | Uso de `except` genérico e respostas HTTP 500 ad-hoc escondem causa raiz, dificultam observabilidade e mantêm comportamento inconsistente entre endpoints. |
| **LOW** | Logging direto com `print` em rotas e serviços | `routes/task_routes.py:149, 219, 234; routes/user_routes.py:83, 89, 147; services/notification_service.py:21-24` | Saídas manuais em stdout misturam auditoria com fluxo de aplicação, sem níveis, contexto estruturado ou integração adequada com monitoração. |
| **LOW** | Imports mortos e utilitário ruidoso sem uso efetivo | `routes/task_routes.py:7; routes/user_routes.py:6; utils/helpers.py:2-7` | Imports não utilizados e helpers genéricos aumentam ruído cognitivo, dificultam manutenção e sinalizam ausência de limpeza sistemática do código legado. |

---

## 2. Construção da Skill (`refactor-arch`)

### 2.1 Decisões de Design e Estrutura Arquitetural
A Skill foi implementada no padrão `SKILL.md` + arquivos de referência em Markdown, garantindo portabilidade entre diferentes ferramentas agênticas (Claude Code, Gemini CLI, etc.).

* **Fases de Execução:**
  1. **Fase 1 — Análise:** Inspeção não destrutiva da codebase, identificação da linguagem, framework, gerenciador de dependências, tabelas/entidades e arquitetura atual.
  2. **Fase 2 — Auditoria:** Mapeamento de problemas contra o catálogo de anti-patterns, atribuição rigorosa de severidade (CRITICAL, HIGH, MEDIUM, LOW) com arquivo/linhas exatos, e parada obrigatória via **Checkpoint Humano** (`Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`).
  3. **Fase 3 — Refatoração:** Reestruturação física e lógica para o padrão MVC canônico, aplicação do playbook de correções (segurança e clean code) e validação de integridade sintática e funcional.

* **Arquivos de Referência Criados:**
  * `project-analysis.md`: Regras para detecção de stack (Python, Node.js, Go, etc.) e estrutura de diretórios.
  * `anti-patterns-catalog.md`: Catálogo com mais de 8 anti-patterns cobertos, incluindo detecção de APIs obsoletas/deprecated (ex: `hashlib.md5`, Base64 hashing).
  * `report-template.md`: Estrutura padronizada para geração dos relatórios `audit-project-X.md`.
  * `mvc-guidelines.md`: Definição estrita das camadas MVC (Models, Controllers, Routes/Views, Config, Middlewares).
  * `refactoring-playbook.md`: Guia de transformação com exemplos do tipo "Antes vs. Depois" para cada vulnerabilidade.

### 2.2 Garantia de Agnosticidade Tecnológica
A agnosticidade foi obtida desacoplando a lógica de análise de sintaxes específicas:
1. **Detecção Baseada em Manifestos:** Identificação da stack via arquivos como `requirements.txt`, `package.json`, `go.mod`, etc.
2. **Padrão MVC Universal:** A Skill aplica a separação conceitual e física de responsabilidades (Entrypoint -> Routes -> Controllers -> Models/Repositories -> Config/Middlewares) independentemente de o projeto ser Python/Flask ou Node.js/Express.
3. **Validação Específica por Runtimes:** A Skill utiliza os comandos nativos de checagem sintática do ecossistema detectado (`python3 -m py_compile` para Python; `node --check` para Node.js).

---

## 3. Resultados e Métricas

### 3.1 Resumo dos Relatórios de Auditoria (Fase 2)

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total Findings |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`code-smells-project`** | Python / Flask | 4 | 3 | 2 | 3 | **12** |
| **`ecommerce-api-legacy`** | Node.js / Express | 2 | 2 | 2 | 2 | **8** |
| **`task-manager-api`** | Python / Flask + SQLAlchemy | 2 | 4 | 2 | 2 | **10** |

---

### 3.2 Comparação de Estrutura Física (Antes vs. Depois)

#### `code-smells-project`
```text
# ANTES (Script-centric)
code-smells-project/
├── app.py
├── controllers.py
├── database.py
└── models.py

# DEPOIS (Estrutura Canônica MVC)
code-smells-project/
├── app.py                   # Composition Root / Bootstrap
├── config/
│   └── settings.py          # Configurações centralizadas via os.environ
├── controllers/
│   └── api_controller.py    # Adaptação HTTP e orquestração de chamadas
├── middlewares/
│   └── errors.py            # Handler global de exceções
├── models/
│   ├── database.py          # Inicialização e pool de conexões
│   └── repositories.py      # Persistência isolada com queries parametrizadas
└── routes/
    └── api_routes.py        # Mapeamento limpo de endpoints e guardas de admin
```

#### `ecommerce-api-legacy`
```text
# ANTES (God Module Monolítico)
ecommerce-api-legacy/
└── src/
    ├── app.js
    ├── AppManager.js
    └── utils.js

# DEPOIS (Estrutura Canônica MVC)
ecommerce-api-legacy/
└── src/
    ├── app.js               # Entrypoint & Express Middleware Assembly
    ├── config/
    │   └── index.js         # Variáveis de ambiente (PORT, ADMIN_TOKEN)
    ├── controllers/
    │   ├── checkoutController.js
    │   ├── reportController.js
    │   └── userController.js
    ├── middlewares/
    │   ├── adminAuth.js     # Middleware de autorização x-admin-token
    │   └── errorHandler.js  # Handler global de erros HTTP
    ├── models/
    │   ├── database.js      # Conexão e inicialização SQLite
    │   └── repositories.js  # Operações de banco 100% parametrizadas
    ├── routes/
    │   └── index.js         # Definição modular de rotas
    └── services/
        └── passwordHasher.js# Hashing seguro com scrypt + salt aleatório
```

#### `task-manager-api`
```text
# ANTES (Organização Parcial com Mistura de Responsabilidades)
task-manager-api/
├── app.py
├── models/
├── routes/
├── services/
└── utils/

# DEPOIS (MVC Reestruturado com Separação Estrita de Camadas)
task-manager-api/
├── app.py                   # Application Factory (create_app)
├── config/
│   └── settings.py          # Configuração centralizada via dotenv/environ
├── controllers/
│   ├── report_controller.py
│   ├── task_controller.py
│   └── user_controller.py
├── middlewares/
│   └── error_handler.py    # Interceptador central de exceções
├── models/                  # Entidades SQLAlchemy (User, Task, Category)
├── routes/                  # Blueprints Flask com rotas desacopladas
├── services/
│   └── notification_service.py # Serviço de e-mail com credenciais via env
└── database.py              # Instância do SQLAlchemy db
```

---

### 3.3 Checklist de Validação Preenchido

#### Projeto 1: `code-smells-project`
- [x] **Fase 1 — Análise:** Linguagem (Python), Framework (Flask) e Domínio (E-commerce) detectados corretamente.
- [x] **Fase 2 — Auditoria:** 12 findings reportados (com linha e arquivo exatos), ordenados por severidade.
- [x] **Fase 2 — Checkpoint:** Pausa com pedido de confirmação do usuário antes de alterações.
- [x] **Fase 3 — Refatoração:** Reorganização em diretórios MVC (`config`, `controllers`, `middlewares`, `models`, `routes`).
- [x] **Fase 3 — Validação:** Aplicação compila sem erros sintáticos (`python3 -m py_compile`) e responde mantendo todos os contratos de API originais.

#### Projeto 2: `ecommerce-api-legacy`
- [x] **Fase 1 — Análise:** Linguagem (Node.js), Framework (Express) e Domínio (LMS/Checkout) detectados corretamente.
- [x] **Fase 2 — Auditoria:** 8 findings reportados (incluindo substituição de Base64 por `scrypt`).
- [x] **Fase 2 — Checkpoint:** Pausa e confirmação prévia atendidos.
- [x] **Fase 3 — Refatoração:** Estrutura MVC modular criada em `src/`.
- [x] **Fase 3 — Validação:** Código verificado sem erros (`node --check`) e rotas respondendo normalmente.

#### Projeto 3: `task-manager-api`
- [x] **Fase 1 — Análise:** Stack (Python/Flask/SQLAlchemy) e Domínio (Task Manager) detectados com precisão.
- [x] **Fase 2 — Auditoria:** 10 findings identificados (incluindo tratamento de erro genérico, logging direto com `print` e imports mortos além da substituição de MD5 e eliminação de segredos SMTP).
- [x] **Fase 2 — Checkpoint:** Pausa com checkpoint humano verificada.
- [x] **Fase 3 — Refatoração:** Módulo `controllers/` introduzido e `app.py` transformado em Application Factory.
- [x] **Fase 3 — Validação:** Aplicação inicializa sem falhas e endpoints preservados.

---

## 4. Como Executar

### 4.1 Pré-requisitos
* Ferramenta de agente de IA com suporte a Custom Skills (ex: **Claude Code**, **Gemini CLI** ou **OpenAI Codex**).
* Ambientes de execução de linguagem instalados:
  * **Python 3.10+** (com pacotes `flask`, `flask-sqlalchemy`, `flask-cors`, `python-dotenv`).
  * **Node.js 18+** (com `express`, `sqlite3`).

### 4.2 Execução da Skill por Projeto

Navegue até a pasta de cada projeto e invoque o comando correspondente à sua ferramenta CLI (exemplo usando o Claude Code):

```bash
# 1. Executar no Projeto 1 (code-smells-project)
cd code-smells-project
claude "/refactor-arch"

# 2. Executar no Projeto 2 (ecommerce-api-legacy)
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# 3. Executar no Projeto 3 (task-manager-api)
cd ../task-manager-api
claude "/refactor-arch"
```

### 4.3 Validação dos Projetos Refatorados

Para testar a inicialização e os contratos de API de cada aplicação refatorada:

```bash
# Teste de Inicialização - Projeto 1
cd code-smells-project
python3 -m py_compile app.py
python3 app.py

# Teste de Inicialização - Projeto 2
cd ../ecommerce-api-legacy
node --check src/app.js
npm start

# Teste de Inicialização - Projeto 3
cd ../task-manager-api
python3 -m py_compile app.py
python3 app.py
```
