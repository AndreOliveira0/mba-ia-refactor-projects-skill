# Refactoring Playbook

Este playbook define transformacoes concretas para migrar codigo legado para MVC.

## 1) SQL concatenado -> query parametrizada

### Antes (Python)
```python
cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
```

### Depois (Python)
```python
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```

### Antes (Node.js)
```js
db.get(`SELECT * FROM users WHERE email = '${email}'`, cb)
```

### Depois (Node.js)
```js
db.get('SELECT * FROM users WHERE email = ?', [email], cb)
```

## 2) Segredo hardcoded -> variavel de ambiente

### Antes (Python)
```python
app.config['SECRET_KEY'] = 'super-secret'
```

### Depois (Python)
```python
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
```

### Antes (Node.js)
```js
const paymentGatewayKey = 'pk_live_123'
```

### Depois (Node.js)
```js
const paymentGatewayKey = process.env.PAYMENT_GATEWAY_KEY
```

## 3) MD5/Base64 fraco -> hash de senha forte

### Antes (Python)
```python
import hashlib
pwd_hash = hashlib.md5(password.encode()).hexdigest()
```

### Depois (Python)
```python
from werkzeug.security import generate_password_hash
pwd_hash = generate_password_hash(password)
```

### Antes (Node.js)
```js
function badCrypto(pwd) { return Buffer.from(pwd).toString('base64') }
```

### Depois (Node.js)
```js
const bcrypt = require('bcryptjs')
const pwdHash = await bcrypt.hash(password, 12)
```

## 4) Rota com regra de negocio pesada -> Controller + Service

### Antes (Node.js)
```js
app.post('/checkout', (req, res) => {
  // valida, consulta db, processa pagamento, grava auditoria
})
```

### Depois (Node.js)
```js
router.post('/checkout', checkoutController.execute)
// controller chama checkoutService.run(input)
```

### Antes (Python)
```python
@app.route('/orders', methods=['POST'])
def create_order():
    # valida, calcula total, baixa estoque, envia notificacao
```

### Depois (Python)
```python
@order_bp.route('/orders', methods=['POST'])
def create_order_route():
    return order_controller.create_order()
```

## 5) Endpoint admin perigoso -> remover ou proteger com RBAC

### Antes (Python)
```python
@app.route('/admin/query', methods=['POST'])
def run_query():
    cursor.execute(request.json['sql'])
```

### Depois (Python)
```python
@admin_bp.route('/admin/reindex', methods=['POST'])
@require_role('admin')
def reindex_safe_job():
    return run_whitelisted_job('reindex')
```

## 6) Exposicao de dados sensiveis -> DTO de resposta

### Antes (Python)
```python
return jsonify({'email': user.email, 'password': user.password})
```

### Depois (Python)
```python
return jsonify({'id': user.id, 'email': user.email, 'role': user.role})
```

### Antes (Node.js)
```js
res.json(user)
```

### Depois (Node.js)
```js
res.json({ id: user.id, name: user.name, email: user.email })
```

## 7) Callback hell -> async/await e funcoes pequenas

### Antes (Node.js)
```js
db.get(sqlA, [], (e, a) => db.get(sqlB, [], (e2, b) => db.run(sqlC, [], cb)))
```

### Depois (Node.js)
```js
const a = await repo.getA()
const b = await repo.getB(a.id)
await repo.saveC(a, b)
```

## 8) Erro inconsistente -> middleware global de erros

### Antes (Express)
```js
if (err) return res.status(500).send('Erro DB')
```

### Depois (Express)
```js
next(new AppError('DATABASE_ERROR', 500, 'Erro de persistencia'))
// app.use(errorMiddleware)
```

### Antes (Flask)
```python
except Exception as e:
    return jsonify({'erro': str(e)}), 500
```

### Depois (Flask)
```python
raise DomainError('DATABASE_ERROR', 'Erro de persistencia')
# @app.errorhandler(DomainError)
```

## 9) Estado global mutavel -> encapsulamento por servico

### Antes (Node.js)
```js
let globalCache = {}
function logAndCache(k, v) { globalCache[k] = v }
```

### Depois (Node.js)
```js
class CacheService {
  constructor(client) { this.client = client }
  async set(k, v) { await this.client.set(k, JSON.stringify(v)) }
}
```

## 10) Validacao ad-hoc repetida -> schema centralizado

### Antes (Python)
```python
if not email or '@' not in email: return {'error': 'email invalido'}, 400
if len(password) < 4: return {'error': 'senha curta'}, 400
```

### Depois (Python)
```python
errors = user_schema.validate(payload)
if errors:
    return {'errors': errors}, 400
```

### Antes (Node.js)
```js
if (!email) return res.status(400).send('Bad Request')
```

### Depois (Node.js)
```js
const { error, value } = schema.validate(req.body)
if (error) return next(new AppError('VALIDATION_ERROR', 400, error.message))
```

## 11) Padrao: Autorizacao por Papel (RBAC) e Protecao de Proprietario do Recurso

Um token JWT valido comprova apenas a identidade/autenticacao. Em toda rota mutavel, valide tambem a permissao para a acao e para o recurso solicitado. Extraia `user_id` e `role` das claims de um token ja verificado pela aplicacao; nunca aceite esses valores do body, query string ou parametros controlados pelo cliente. Use allowlist de campos para atualizacao. Solicitacoes autenticadas sem permissao recebem `403 Forbidden`.

### Antes (Python/Flask)
```python
@app.put('/users/<int:user_id>')
@jwt_required()
def update_user(user_id):
        user = User.query.get_or_404(user_id)
        user.update(request.get_json())  # aceita role e nao verifica proprietario
        db.session.commit()
        return jsonify(user.to_dict())

@app.delete('/tasks/<int:task_id>')
@jwt_required()
def delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)  # qualquer usuario autenticado pode excluir
        db.session.commit()
        return '', 204
```

### Depois (Python/Flask)
```python
from functools import wraps
from flask import abort, g, request

def require_auth(handler):
        @wraps(handler)
        @jwt_required()
        def wrapped(*args, **kwargs):
                claims = get_jwt()  # somente apos validacao do JWT
                g.user_id = int(claims['user_id'])
                g.user_role = claims['role']
                return handler(*args, **kwargs)
        return wrapped

def require_owner_or_admin(resource):
        if g.user_role != 'admin' and g.user_id != resource.owner_id:
                abort(403)

@app.put('/users/<int:user_id>')
@require_auth
def update_user(user_id):
        user = User.query.get_or_404(user_id)
    if g.user_role != 'admin' and g.user_id != user.id:
        abort(403)
        payload = request.get_json(silent=True) or {}
        if 'role' in payload and g.user_role != 'admin':
                abort(403)
        allowed_fields = {'name', 'email'}
        if g.user_role == 'admin':
                allowed_fields.add('role')
        for field in allowed_fields.intersection(payload):
                setattr(user, field, payload[field])
        db.session.commit()
        return jsonify(user.to_dict())

@app.delete('/tasks/<int:task_id>')
@require_auth
def delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        require_owner_or_admin(task)
        db.session.delete(task)
        db.session.commit()
        return '', 204
```

`get_jwt()` representa a API de claims da biblioteca JWT adotada; configure a autenticacao para validar assinatura, emissor, audiencia e expiracao antes de ler claims. Aplique `require_owner_or_admin` em cada rota mutavel, sempre usando o proprietario persistido do recurso.

### Antes (Node.js/Express)
```js
router.put('/users/:userId', verifyJwt, async (req, res) => {
    const user = await users.findById(req.params.userId)
    await users.update(user.id, req.body) // aceita role e nao verifica proprietario
    res.json(await users.findById(user.id))
})

router.delete('/tasks/:taskId', verifyJwt, async (req, res) => {
    await tasks.remove(req.params.taskId) // qualquer usuario autenticado pode excluir
    res.sendStatus(204)
})
```

### Depois (Node.js/Express)
```js
function verifyJwt(req, res, next) {
    // verifyTokenFromRequest valida assinatura, emissor, audiencia e expiracao.
    const claims = verifyTokenFromRequest(req)
    req.auth = { userId: String(claims.user_id), role: claims.role }
    next()
}

async function loadUserTarget(req, res, next) {
    try {
        req.targetUser = await users.findById(req.params.userId)
        if (!req.targetUser) return res.sendStatus(404)
        next()
    } catch (error) {
        next(error)
    }
}

async function loadTask(req, res, next) {
    try {
        req.task = await tasks.findById(req.params.taskId)
        if (!req.task) return res.sendStatus(404)
        next()
    } catch (error) {
        next(error)
    }
}

function requireOwnerOrAdmin(req, res, next) {
    const ownerId = req.targetUser ? req.targetUser.id : req.task.ownerId
    if (req.auth.role !== 'admin' && req.auth.userId !== String(ownerId)) {
        return res.sendStatus(403)
    }
    next()
}

router.put('/users/:userId', verifyJwt, loadUserTarget, requireOwnerOrAdmin, async (req, res, next) => {
    try {
        const payload = req.body || {}
        if (Object.prototype.hasOwnProperty.call(payload, 'role') && req.auth.role !== 'admin') {
            return res.sendStatus(403)
        }
        const fields = req.auth.role === 'admin' ? ['name', 'email', 'role'] : ['name', 'email']
        const changes = Object.fromEntries(fields
            .filter((field) => Object.prototype.hasOwnProperty.call(payload, field))
            .map((field) => [field, payload[field]]))
        await users.update(req.targetUser.id, changes)
        res.json(await users.findById(req.targetUser.id))
    } catch (error) {
        next(error)
    }
})

router.delete('/tasks/:taskId', verifyJwt, loadTask, requireOwnerOrAdmin, async (req, res, next) => {
    try {
        await tasks.remove(req.task.id)
        res.sendStatus(204)
    } catch (error) {
        next(error)
    }
})
```

`verifyTokenFromRequest` representa a funcao da biblioteca JWT adotada e deve validar o token antes de definir `req.auth`. `requireOwnerOrAdmin` recebe apenas recursos previamente carregados do repositorio; nunca determine ownership com um ID de proprietario enviado pelo cliente.

## Sequencia sugerida de execucao
1. Corrigir segredos e credenciais.
2. Remover vetores de injecao e endpoints administrativos inseguros.
3. Migrar hash/autenticacao e aplicar RBAC + verificacao de proprietario em rotas mutaveis.
4. Separar em MVC (routes -> controllers -> models/services).
5. Padronizar validacao e tratamento de erros.
6. Validar boot, contratos dos endpoints e testes de autorizacao (owner, admin, outro usuario e tentativa de alterar role).
