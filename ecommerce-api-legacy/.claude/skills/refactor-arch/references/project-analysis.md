# Project Analysis Heuristics

## Objetivo
Detectar stack e arquitetura de forma agnostica, sem assumir tecnologia unica.

## 1) Deteccao de Linguagem

### Sinais de Python
- Arquivos .py predominantes
- requirements.txt, pyproject.toml, Pipfile
- Imports como flask, django, fastapi, sqlalchemy

### Sinais de Node.js
- Arquivos .js/.ts predominantes
- package.json presente
- require(...) ou import ... from em JS/TS

## 2) Deteccao de Framework

### Flask
- from flask import Flask
- app = Flask(__name__)
- decorators @app.route ou Blueprints

### Express
- const express = require('express')
- const app = express()
- app.get/post/put/delete

## 3) Deteccao de Persistencia

### SQLite
- sqlite3.connect(...) (Python)
- new sqlite3.Database(...) (Node)
- URI sqlite:///... em ORM

### ORM / SQL Builder
- SQLAlchemy Model/db.session
- Prisma/Sequelize/TypeORM em Node

### SQL bruto
- cursor.execute("SELECT ...")
- db.run/db.get/db.all em Node sqlite

## 4) Mapeamento de Entidades e Tabelas
- Procurar CREATE TABLE e migrations.
- Mapear classes de model para entidades.
- Extrair relacionamentos (FK, joins, relationships).

## 5) Inferencia de Dominio
- Ler README e descricao de endpoints.
- Extrair substantivos recorrentes em rotas e models.
- Verificar casos de uso centrais (checkout, tasks, usuarios, pedidos).

## 6) Heuristica de Arquitetura Atual

### Monolitica / Script-centric
- Muitas responsabilidades no mesmo arquivo.
- Rotas, negocio e SQL no mesmo modulo.

### Parcialmente em camadas
- Pastas de models/routes/services existentes.
- Ainda com violacoes de fronteira entre camadas.

### MVC organizado
- Controllers orquestram casos de uso.
- Models isolam persistencia.
- Routes apenas mapeiam HTTP para controllers.

## 7) Contagem de Arquivos
- Contar apenas arquivos de codigo-fonte.
- Excluir lockfiles, assets, logs e diretorios de build.
- Reportar total por extensao e por pasta principal.

## 8) Saida Recomendada da Fase 1
- Language
- Framework
- Dependency highlights
- Persistence strategy
- Domain
- Architecture profile
- Source file count
- Entities/tables list
