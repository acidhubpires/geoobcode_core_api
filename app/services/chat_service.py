from __future__ import annotations

from typing import Dict, Any, List

from app.core.config import settings
from app.core.governor import get_budgets, enforce_max_chars
from app.services.groq_client import chat_completion


def build_system(agent: Dict[str, Any], profile: str) -> str:
    return f"""Você é {agent.get('name')}.
Core/Especialidade: {agent.get('specialty')}

Perfil ativo: {profile}

Regras:
- Use a Matriz de Conhecimento como base.
- Se algo não estiver suportado pela Matriz, declare a lacuna.
- Evite extrapolações. Seja operacional e claro.
""".strip()


def build_user_payload(agent: Dict[str, Any], history: List[Dict[str, Any]], prompt: str) -> str:
    history_txt = "\n".join([f"{m.get('role','').upper()}: {m.get('content','')}" for m in history])
    return f"""
[MATRIZ_DE_CONHECIMENTO]
{agent.get('matrix','')}

[HISTÓRICO]
{history_txt}

[PERGUNTA_ATUAL]
{prompt}
""".strip()


def answer(client, agent: Dict[str, Any], history: List[Dict[str, Any]], prompt: str, profile: str = "ADMIN") -> str:
    budgets = get_budgets()
    prompt = enforce_max_chars(prompt, 8000, "prompt")
    history = history[-budgets.max_history_msgs:]

    system = build_system(agent, profile)
    user_payload = build_user_payload(agent, history, prompt)

    temperature = 0.2 if agent.get("type") == "Corporativo" else 0.4

    return chat_completion(
        client=client,
        model=settings.chat_model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user_payload}],
        temperature=temperature,
        max_tokens=1800,
    )
