# Audit Report Template (Phase 2)

## Header
- Project: task-manager-api
- Stack: Python + Flask + SQLAlchemy + SQLite
- Date: 2026-10-08
- Files analyzed: 8 core source files

## Summary
- CRITICAL: 2
- HIGH: 3
- MEDIUM: 2
- LOW: 2
- Total findings: 9

## Architecture Snapshot
- Current architecture: parcialmente em camadas, mas com regras de negócio, validação e persistência misturadas em rotas e models.
- Persistence: SQLite via SQLAlchemy (`sqlite:///tasks.db`)
- Main domain: gestão de usuários, tarefas, categorias e relatórios de produtividade.

## Findings (ordenados por severidade)

### CRITICAL Hardcoded secret and debug mode enabled
- File: app.py:11-14, 33-34
- Category: security
- Evidence: `app.config['SECRET_KEY'] = 'super-secret-key-123'` and `app.run(debug=True, host='0.0.0.0', port=5000)`.
- Impact: secret exposed in source code and debug mode leaks internal traces in non-local environments.
- Recommendation: move secrets to environment variables and restrict debug mode to local development only.

### CRITICAL Mass assignment and missing authorization on user mutation
- File: routes/user_routes.py:92-132
- Category: security
- Evidence: the PUT route accepts arbitrary keys from `request.get_json()` and immediately applies `user.role = data['role']` without verifying whether the caller is an admin or the owner.
- Impact: an authenticated user can self-promote or change another account's role, violating RBAC and integrity.
- Recommendation: introduce an allowlist for mutable fields, reject `role` changes for non-admins with `403 Forbidden`, and enforce server-side ownership checks before updating any resource.

### HIGH Password hashing is weak and user password is exposed in responses
- File: models/user.py:16-32
- Category: security
- Evidence: `hashlib.md5` is used in `set_password()` and `check_password()`, and `to_dict()` returns `'password': self.password`.
- Impact: passwords are vulnerable to rapid brute-force and API responses leak stored credentials.
- Recommendation: replace MD5 with `werkzeug.security.generate_password_hash` / `check_password_hash`, and remove password hashes from any DTO returned to clients.

### HIGH Fake authentication token and no authorization layer
- File: routes/user_routes.py:185-210
- Category: security
- Evidence: login returns `'token': 'fake-jwt-token-' + str(user.id)`, and there is no token verification or middleware enforcing auth on mutating routes.
- Impact: the app presents a false sense of authentication while all mutation endpoints remain effectively public.
- Recommendation: implement real JWT validation or session auth, then require verified `user_id`/`role` claims on every mutable endpoint.

### HIGH Unauthenticated mutation of task and category resources
- File: routes/task_routes.py:85-154; routes/report_routes.py:121-183
- Category: security
- Evidence: task creation/update/delete and category creation/update/delete are exposed without any authentication or ownership check before persisting changes.
- Impact: any caller can alter or delete any task/category item, not only the owner or an admin.
- Recommendation: require auth on mutable routes and validate `current_user.id == resource.user_id` or `current_user.role == 'admin'` before commit.

### MEDIUM God module / business logic concentrated in route handlers
- File: routes/task_routes.py:11-211; routes/user_routes.py:10-211; routes/report_routes.py:13-183
- Category: architecture
- Evidence: endpoints contain validation, business rules, database access, and serialization all in the same modules.
- Impact: harder testing, higher regression risk, and poor separation of responsibilities.
- Recommendation: move request validation and domain logic into controllers/services and keep routes thin.

### MEDIUM Broad exception handling without centralized error mapping
- File: routes/task_routes.py:13-63, 146-154, 190-211; routes/user_routes.py:80-90, 127-132; routes/report_routes.py:14-52
- Category: code smell
- Evidence: several handlers use bare `except:` and return generic JSON errors without structured error codes or trace correlation.
- Impact: inconsistent behavior and poor observability for production incidents.
- Recommendation: define a centralized error handler and standardize domain exceptions and HTTP responses.

### LOW Production logging via print statements
- File: routes/task_routes.py:146-153; routes/user_routes.py:80-89
- Category: code smell
- Evidence: `print(f"Task criada: {task.id} - {task.title}")` and similar logs are used in request flows.
- Impact: noisy operational logs and insufficient context for debugging in production.
- Recommendation: use a configured logger with structured output and levels.

### LOW Duplicate validation blocks and ad-hoc rules
- File: routes/task_routes.py:92-144; routes/user_routes.py:54-77, 105-125
- Category: code smell
- Evidence: status, priority, email, password, and role rules are repeated across multiple route functions instead of being centralized in schemas or validators.
- Impact: maintenance is harder and request validation can drift between endpoints.
- Recommendation: centralize validation in reusable schemas or service-layer validators.

## Deprecated API Notes
- API/Pattern: MD5 password hashing and fake token generation
- Location: models/user.py:27-32; routes/user_routes.py:207-210
- Why obsolete/risky: MD5 is not a password hashing mechanism and fake tokens do not verify identity; both are insecure and misleading.
- Modern equivalent: `werkzeug.security.generate_password_hash` + real JWT or session authentication with verified claims.

## Quick Wins
- 1) Replace MD5 password hashing with a secure password-hash library and remove password data from response DTOs.
- 2) Prevent direct `role` assignment in the user update route by requiring admin-only changes and returning `403 Forbidden` otherwise.
- 3) Move all secret configuration into environment variables and disable debug mode outside local development.

## Refactoring Readiness
- Blocking issues before refactor: insecure auth model, role mass-assignment, weak password hashing, and missing ownership checks.
- Estimated complexity: high
- Suggested order: secret/config cleanup -> auth+RBAC foundation -> model/controller extraction -> validation/schema centralization -> route security hardening.

## Mandatory Checkpoint Output
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
