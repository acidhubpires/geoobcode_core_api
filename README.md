# ACID AgentIA Hub — PoC API (FastAPI)

Infraestrutura cognitiva (PoC avançada) para **Agentes de IA** com:
- autenticação JWT (tenant/user/role),
- ingestão de conhecimento (arquivos + URLs + notas),
- síntese em **Matriz de Conhecimento** (memória do agente),
- interação via chat autenticado,
- persistência local (JSON) apenas para testes de fluxo.

> Este projeto **não** é um chatbot genérico. É um **middleware cognitivo** orientado a governança e continuidade.

---

## Sumário

- [ACID AgentIA Hub — PoC API (FastAPI)](#acid-agentia-hub--poc-api-fastapi)
  - [Sumário](#sumário)
  - [Visão Geral](#visão-geral)
  - [Fluxo Cognitivo](#fluxo-cognitivo)
    - [Modelo mental (arquivo → conhecimento → conversa)](#modelo-mental-arquivo--conhecimento--conversa)
    - [Princípio chave](#princípio-chave)
  - [Arquitetura](#arquitetura)
  - [Endpoints](#endpoints)
    - [Auth](#auth)
    - [Agents](#agents)
    - [Chat](#chat)
    - [Admin](#admin)
    - [Ingest (genérico)](#ingest-genérico)
  - [Quickstart](#quickstart)
    - [1) Instalar dependências](#1-instalar-dependências)
    - [2) Variáveis de ambiente](#2-variáveis-de-ambiente)
    - [3) Rodar API](#3-rodar-api)
  - [Testes via Swagger / cURL](#testes-via-swagger--curl)
    - [1) Login](#1-login)
    - [2) Criar agente](#2-criar-agente)
    - [3) Ingestão de arquivo (recomendado)](#3-ingestão-de-arquivo-recomendado)
    - [4) Chat com o agente](#4-chat-com-o-agente)
  - [Decisões Importantes](#decisões-importantes)
  - [Limites da PoC](#limites-da-poc)
  - [Roadmap (PoC → MVP)](#roadmap-poc--mvp)

---

## Visão Geral

O ACID AgentIA Hub oferece uma API para:
1) criar/agregar agentes (entidades cognitivas),
2) ingerir documentos/URLs/notas,
3) sintetizar o conteúdo em uma **Matriz de Conhecimento** versionada,
4) conversar com o agente usando essa matriz como contexto autoritativo.

A PoC usa persistência local em JSON para validar interações e contratos.

---

## Fluxo Cognitivo

### Modelo mental (arquivo → conhecimento → conversa)

```text
[Upload/URLs/Notes]
     ↓
[Extração por tipo (pdf/docx/xlsx/txt)]
     ↓
[Normalização + budgets + warnings]
     ↓
[Síntese LLM → Matriz do Agente]
     ↓
[Persistência local (JSON) — PoC]
     ↓
[/chat usa matriz como contexto]
````

### Princípio chave

* O arquivo **não** é a memória.
* A memória é a **Matriz de Conhecimento** (texto consolidado, versionado).
* O chat responde sobre a matriz, **sem reler o arquivo**.

---

## Arquitetura

Estrutura típica:

* `app/main.py` — app FastAPI, routers
* `app/api/` — rotas (`auth`, `agents`, `chat`, `admin`, `ingest`)
* `app/core/` — config, segurança, governança
* `app/services/` — ingestão, loaders, cliente LLM, utilitários
* `app/infra/` — store local em JSON (PoC)
* `app/domain/` — schemas/contratos

---

## Endpoints

### Auth

* `POST /auth/login`

### Agents

* `GET /agents` (auth)

* `POST /agents` (auth)

* `POST /agents/{agent_id}/ingest` (auth)
  Ingestão via JSON (docs_text/urls) — útil para testes rápidos.

* `POST /agents/{agent_id}/ingest/upload` (auth)
  Ingestão via `multipart/form-data` (arquivos + urls + notes) — fluxo recomendado.

### Chat

* `POST /chat` (auth)
* `POST /chat/stream` (auth)

### Admin

* `GET /health`

### Ingest (genérico)

* `POST /ingest/upload` (opcional)

> Pode existir como endpoint “genérico”, porém o fluxo recomendado para a PoC é o **agent-first**:
> `/agents/{agent_id}/ingest/upload`

---

## Quickstart

### 1) Instalar dependências

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Variáveis de ambiente

Crie `.env` baseado no `.env.example`.

### 3) Rodar API

```bash
uvicorn app.main:app --reload
```

Swagger:

* `http://127.0.0.1:8000/docs`

---

## Testes via Swagger / cURL

### 1) Login

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"tenant":"electra","email":"admin@electra.local","password":"SenhaForte123"}'
```

### 2) Criar agente

```bash
curl -X POST "http://127.0.0.1:8000/agents" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Powerledger Analyst","specialty":"Blockchain / Tokenomics","description":"Agente para leitura e análise de whitepapers."}'
```

### 3) Ingestão de arquivo (recomendado)

```bash
curl -X POST "http://127.0.0.1:8000/agents/<AGENT_ID>/ingest/upload" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "files=@./docs/powerledger-lightpaper.pdf" \
  -F "urls=https://exemplo.com/pagina1
https://exemplo.com/pagina2" \
  -F "notes=Considere riscos regulatórios e tokenomics."
```

### 4) Chat com o agente

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"<AGENT_ID>","message":"Quais são os riscos principais e como mitigá-los?"}'
```

---

## Decisões Importantes

* **Agent-first**: a unidade cognitiva é o `agent_id`.
* **Matriz versionada**: ingestão gera `matrix_version` (evolução controlada).
* **PoC sem BD**: persistência local em JSON para validar contrato/fluxo.
* **Governança mínima**: limites, truncamento, warnings (evita “explodir contexto”).

---

## Limites da PoC

* Persistência local: sem lock / concorrência avançada.
* Extração PDF “digital”: OCR não incluído.
* Budget e truncamento: prioriza estabilidade do fluxo e custo previsível.
* Sem embeddings/RAG por padrão: foco em validação do middleware cognitivo.

---

## Roadmap (PoC → MVP)

* Store: JSON → DB (SQLite/Firebase/Firestore)
* Auditoria: hash + provenance + trilha de ingestão
* Ingest incremental: anexar+consolidar por seções
* Multi-LLM: roteamento por provider (Groq/Gemini/OpenAI)
* RAG opcional: ativável por caso de uso, com governança

```

Docs:
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health
