# ACID AgentIA Hub — FastAPI PoC (Groq + Local JSON Store)

Projeto **funcional** para PoC:
- FastAPI + JWT (login)
- Multi-tenant (tenant_id no token)
- Agentes (Células Neurais) com **Matriz de Conhecimento**
- Ingestão (TXT + URLs) com **síntese MAP→REDUCE** (evita explosão de tokens/TPM)
- Chat (HTTP) + opção de SSE (streaming simples)
- Persistência local em `./data/` (JSON + JSONL) — depois migra para Firebase/Firestore com baixo atrito.

## 1) Setup (Windows / PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# edite .env e coloque GROQ_API_KEY
```

## 2) Criar usuário (PoC)

Cria (ou atualiza) um usuário com senha hash (bcrypt):

```powershell
python scripts/create_user.py --tenant electra --email admin@electra.local --password "SUA_SENHA" --role admin
```

## 3) Rodar API

```powershell
uvicorn app.main:app --reload --port 8000
```

Docs:
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health
