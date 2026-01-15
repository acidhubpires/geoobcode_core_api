from __future__ import annotations

from typing import List
import requests

from app.core.config import settings
from app.core.governor import get_budgets, enforce_max_chars, guard_payload_size
from app.services.groq_client import chat_completion


def build_matrix_prompt(specialty: str) -> str:
    return f"""
Você vai atuar como um sintetizador técnico e fiel.
Especialidade (Core da Célula Neural): {specialty}

Tarefa:
1) Extraia terminologia essencial e definições (glossário).
2) Extraia regras de negócio e constraints (separar por categorias).
3) Identifique processos (passo a passo) quando existirem.
4) Identifique exceções, riscos e zonas de ambiguidade.
5) Gere uma Matriz de Conhecimento em formato estruturado (YAML ou JSON legível).

Regras:
- Não invente fatos.
- Se algo não estiver nos documentos, marque como "lacuna".
- Priorize fidelidade e concisão.
""".strip()


def fetch_url_text(url: str, timeout: int = 10, max_chars: int = 200000) -> str:
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    ct = (r.headers.get("content-type") or "").lower()
    if "text" not in ct and "json" not in ct and "xml" not in ct and "html" not in ct:
        return f"[conteúdo não-textual: {ct}]"
    return r.text[:max_chars]


def _chunk_text(text: str, max_chars: int) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]


def _map_summarize(client, specialty: str, chunk: str, temperature: float) -> str:
    sys = "Você é um motor de síntese fiel e metódico. Produza uma síntese curta e estruturada."
    user = f"""
Core/Especialidade: {specialty}

Trecho de entrada:
{chunk}

Produza:
- glossário essencial
- regras/constraints encontradas
- processos (se houver)
- exceções/ambiguidade
Formato: YAML curto
""".strip()

    return chat_completion(
        client=client,
        model=settings.synth_model,
        messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}],
        temperature=temperature,
        max_tokens=900,
    )


def _reduce(client, specialty: str, partials: List[str], temperature: float) -> str:
    sys = "Você é um consolidado neuro-simbólico. Una sínteses sem duplicar e sem inventar."
    joined = "\n\n---\n\n".join(partials)

    user = f"""
Core/Especialidade: {specialty}

Consolide as sínteses parciais em UMA Matriz final.
Requisitos:
- Deduplicar termos e regras
- Conflitos: marcar como 'conflito' (não resolver inventando)
- Lacunas: manter como 'lacuna'
- Estrutura final em YAML (ou JSON legível)

Sínteses parciais:
{joined}
""".strip()

    return chat_completion(
        client=client,
        model=settings.synth_model,
        messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}],
        temperature=temperature,
        max_tokens=1800,
    )


def synthesize_matrix(client, specialty: str, docs_text: List[str], urls: List[str], temperature: float = 0.2) -> str:
    budgets = get_budgets()

    urls_text: List[str] = []
    for u in (urls or [])[:10]:
        try:
            urls_text.append(fetch_url_text(u))
        except Exception as e:
            urls_text.append(f"[falha ao baixar {u}] {e}")

    parts: List[str] = [build_matrix_prompt(specialty)]

    for t in docs_text or []:
        t = enforce_max_chars(t, 120000, "doc_txt")
        if t.strip():
            parts.append("[DOC_TXT]\n" + t.strip())

    for t in urls_text:
        t = enforce_max_chars(t, 120000, "url_txt")
        if t.strip():
            parts.append("[URL_TXT]\n" + t.strip())

    merged = "\n\n---\n\n".join(parts)
    guard_payload_size(len(merged))

    merged = merged[:budgets.max_total_chars]
    chunks = _chunk_text(merged, budgets.chunk_chars)[:budgets.max_partials]

    if not chunks:
        return "lacuna: nenhum texto válido para sintetizar."

    partials = [_map_summarize(client, specialty, c, temperature) for c in chunks]
    return _reduce(client, specialty, partials, temperature)
