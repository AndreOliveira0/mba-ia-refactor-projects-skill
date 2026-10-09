---
name: refactor-arch
description: Analisa projetos backend de forma agnostica, audita anti-patterns com severidade e linhas exatas, pausa para confirmacao e refatora para MVC com validacao final.
---

# Refactor Arch Skill

## Objetivo
Executar uma pipeline em 3 fases para:
1. Analisar stack, framework, persistencia e arquitetura atual.
2. Auditar anti-patterns/code smells/APIs obsoletas com severidade, arquivo e linhas exatas.
3. Refatorar para MVC mantendo comportamento funcional.

## Regras Operacionais
- A skill e agnostica de tecnologia (Python/Node.js como foco principal).
- Nao modificar arquivos durante Fase 1 e Fase 2.
- Toda evidencia deve incluir caminho de arquivo e linha/intervalo.
- Classificar findings em ordem de severidade: CRITICAL, HIGH, MEDIUM, LOW.
- Se nao houver evidencia suficiente para um achado, nao reportar.

## Fase 1 - Analise

### Passos
1. Detectar linguagem principal por extensao de arquivos e manifestos (ex.: requirements.txt, package.json).
2. Detectar framework (ex.: Flask, Express) por imports/requires e bootstrap da aplicacao.
3. Detectar persistencia (SQLite/ORM/outros) por conexoes, DSN e pacotes.
4. Mapear tabelas/entidades por migrations, models e CREATE TABLE.
5. Inferir dominio de negocio por rotas, nomes de entidades e README.
6. Contar arquivos-fonte analisados e organizar por camada/pasta.

### Saida esperada
Imprimir bloco de resumo:
- Language
- Framework
- Dependencies-chave
- Domain
- Architecture atual
- Source files analisados
- DB tables/collections detectadas

## Fase 2 - Auditoria

### Passos
1. Carregar catalogo de anti-patterns em references/anti-patterns-catalog.md.
2. Cruzar codigo-fonte com sinais de deteccao do catalogo.
3. Registrar cada finding com:
   - Severidade
   - Titulo
   - Arquivo:linha(s)
   - Evidencia objetiva
   - Impacto
   - Recomendacao
4. Ordenar findings por severidade descendente (CRITICAL -> LOW).
5. Produzir relatorio usando references/report-template.md.
6. PERSISTÊNCIA AUTOMÁTICA LOCAL:
   - Salvar o relatório completo gerado diretamente na raiz do diretório de trabalho atual com o nome exato: `audit-project.md`.

## Ponto de Paragem Obrigatório
Ao finalizar a Fase 2 e após salvar o arquivo `audit-project.md` na raiz do projeto, interromper o fluxo imediatamente e imprimir no console:

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

- Se a resposta do usuário for 'y' ou 'yes': prosseguir automaticamente para a Fase 3 (Refatoração).
- Se a resposta for 'n' ou 'no': encerrar a execução imediatamente sem alterar o código.
- NUNCA realizar alterações de código antes da confirmação explícita do usuário.

## Fase 3 - Refatoracao MVC Obrigatoria + Validacao

### Passos
1. CRIAR OBRIGATORIAMENTE A ESTRUTURA DE DIRETORIOS MVC:
   - Toda refatoracao DEVE criar fisicamente os diretorios no disco:
     * `models/` (entidades, repositorios e persistencia)
     * `controllers/` (regras de negocio e orquestracao)
     * `routes/` (ou `views/`, definicao de endpoints HTTP, Blueprints/Routers)
     * `config/` (configuracoes centrais e leitura de env)
     * `middlewares/` (handlers globais de erro, auth e validacoes)
   - NUNCA manter modulos de controllers, models ou errors soltos na raiz.
   - O arquivo principal (`app.py` ou `app.js` / `server.js`) deve permanecer na raiz estritamente como entry point / composition root limpo.
2. Aplicar as transformacoes tecnicas de `references/refactoring-playbook.md`.
3. Isolar credenciais e segredos em `config/`.
4. Centralizar tratamento de erro em `middlewares/`.
5. Mitigar vulnerabilidades de seguranca (queries parametrizadas, hash forte).
6. Aplicar integralmente autorizacao RBAC e controle de proprietario nas rotas mutaveis de usuario/recursos; um token valido comprova autenticacao, mas nao autoriza acesso por si so.
   - Extrair `user_id` e `role` de claims verificadas no servidor, nunca do payload da requisicao.
   - Impedir mass assignment de campos sensiveis: somente admin pode alterar `role`; tentativa de nao-admin deve retornar `403 Forbidden`.
   - Permitir PUT/PATCH/DELETE somente ao proprietario persistido do recurso ou a um admin; negar outros usuarios com `403 Forbidden`.
7. Ajustar imports e composicao de rotas entre as pastas criadas.

### Validacao obrigatoria
- Aplicacao inicializa sem erro a partir do entry point na raiz.
- Todos os endpoints originais continuam respondendo com mesmos contratos.
- Fluxos criticos testados e validados.
- Validar autorizacao em rotas mutaveis: proprietario permitido, admin permitido, outro usuario negado (403) e tentativa de mass assignment de `role` por nao-admin negada (403).

### Saida final
- Estrutura nova gerada.
- Resumo de alteracoes por arquivo.
- Resultado da validacao (boot + endpoints).
- Riscos residuais e proximos passos recomendados.

## Referencias da Skill
- references/project-analysis.md
- references/anti-patterns-catalog.md
- references/report-template.md
- references/mvc-guidelines.md
- references/refactoring-playbook.md
