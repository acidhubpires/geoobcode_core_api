from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from app.core.security import verify_password, hash_password

DATA_DIR = Path("data")
INDEX_DIR = DATA_DIR / "index"
MSG_DIR = DATA_DIR / "messages"

USERS_PATH = DATA_DIR / "users.json"
AGENTS_PATH = DATA_DIR / "agents.json"
CONVS_PATH = DATA_DIR / "conversations.json"

IDX_AGENTS_BY_TENANT = INDEX_DIR / "agents_by_tenant.json"
IDX_AGENTS_BY_USER = INDEX_DIR / "agents_by_user.json"
IDX_CONVS_BY_AGENT = INDEX_DIR / "conversations_by_agent.json"
IDX_CONVS_BY_USER = INDEX_DIR / "conversations_by_user.json"


def _ensure_dirs():
    for p in [DATA_DIR, INDEX_DIR, MSG_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def _load(path: Path, default: Any):
    _ensure_dirs()
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def _save(path: Path, data: Any):
    _ensure_dirs()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def _save_index(path: Path, data: Dict[str, List[str]]):
    _save(path, data)


class JsonStore:
    def upsert_user(self, tenant_id: str, email: str, password: str, role: str = "user") -> Dict[str, Any]:
        users = _load(USERS_PATH, {"users": []})
        user = next((u for u in users["users"] if u["tenant_id"] == tenant_id and u["email"] == email), None)
        if user:
            user["password_hash"] = hash_password(password)
            user["role"] = role
            user["updated_at"] = datetime.utcnow().isoformat()
        else:
            user = {
                "id": str(uuid.uuid4()),
                "tenant_id": tenant_id,
                "email": email,
                "password_hash": hash_password(password),
                "role": role,
                "created_at": datetime.utcnow().isoformat(),
            }
            users["users"].append(user)
        _save(USERS_PATH, users)
        return user

    def authenticate(self, tenant_id: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        users = _load(USERS_PATH, {"users": []})
        user = next((u for u in users["users"] if u["tenant_id"] == tenant_id and u["email"] == email), None)
        if not user:
            return None
        if not verify_password(password, user["password_hash"]):
            return None
        return user

    def list_agents(self, tenant_id: str, user_id: str, role: str) -> List[Dict[str, Any]]:
        agents = _load(AGENTS_PATH, {"agents": []})["agents"]
        if role == "admin":
            return [a for a in agents if a["tenant_id"] == tenant_id]
        return [a for a in agents if a["tenant_id"] == tenant_id and a["owner_user_id"] == user_id]

    def create_agent(self, tenant_id: str, owner_user_id: str, name: str, a_type: str, specialty: str) -> Dict[str, Any]:
        db = _load(AGENTS_PATH, {"agents": []})
        agent = {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "owner_user_id": owner_user_id,
            "name": name,
            "type": a_type,
            "specialty": specialty,
            "matrix": "",
            "matrix_version": 0,
            "created_at": datetime.utcnow().isoformat(),
        }
        db["agents"].append(agent)
        _save(AGENTS_PATH, db)
        self._reindex_agents()
        return agent

    def get_agent(self, tenant_id: str, agent_id: str) -> Optional[Dict[str, Any]]:
        agents = _load(AGENTS_PATH, {"agents": []})["agents"]
        return next((a for a in agents if a["tenant_id"] == tenant_id and a["id"] == agent_id), None)

    def update_agent_matrix(self, tenant_id: str, agent_id: str, matrix: str) -> Dict[str, Any]:
        db = _load(AGENTS_PATH, {"agents": []})
        agent = next((a for a in db["agents"] if a["tenant_id"] == tenant_id and a["id"] == agent_id), None)
        if not agent:
            raise KeyError("agent_not_found")
        agent["matrix"] = matrix
        agent["matrix_version"] = int(agent.get("matrix_version", 0)) + 1
        agent["updated_at"] = datetime.utcnow().isoformat()
        _save(AGENTS_PATH, db)
        return agent

    def _reindex_agents(self):
        db = _load(AGENTS_PATH, {"agents": []})
        by_tenant: Dict[str, List[str]] = {}
        by_user: Dict[str, List[str]] = {}
        for a in db["agents"]:
            by_tenant.setdefault(a["tenant_id"], []).append(a["id"])
            by_user.setdefault(a["owner_user_id"], []).append(a["id"])
        _save_index(IDX_AGENTS_BY_TENANT, by_tenant)
        _save_index(IDX_AGENTS_BY_USER, by_user)

    def create_conversation(self, tenant_id: str, user_id: str, agent_id: str) -> Dict[str, Any]:
        db = _load(CONVS_PATH, {"conversations": []})
        conv = {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "user_id": user_id,
            "agent_id": agent_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        db["conversations"].append(conv)
        _save(CONVS_PATH, db)
        self._reindex_conversations()
        return conv

    def _reindex_conversations(self):
        db = _load(CONVS_PATH, {"conversations": []})
        by_agent: Dict[str, List[str]] = {}
        by_user: Dict[str, List[str]] = {}
        for c in db["conversations"]:
            by_agent.setdefault(c["agent_id"], []).append(c["id"])
            by_user.setdefault(c["user_id"], []).append(c["id"])
        _save_index(IDX_CONVS_BY_AGENT, by_agent)
        _save_index(IDX_CONVS_BY_USER, by_user)

    def append_message(self, conversation_id: str, role: str, content: str) -> None:
        _ensure_dirs()
        path = MSG_DIR / f"conv_{conversation_id}.jsonl"
        record = {"role": role, "content": content, "created_at": datetime.utcnow().isoformat()}
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def load_last_messages(self, conversation_id: str, limit: int = 12) -> List[Dict[str, Any]]:
        path = MSG_DIR / f"conv_{conversation_id}.jsonl"
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
        tail = lines[-limit:]
        return [json.loads(x) for x in tail if x.strip()]
