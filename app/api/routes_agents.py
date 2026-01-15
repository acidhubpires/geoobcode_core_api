from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_store
from app.domain.schemas import AgentCreate, AgentOut, IngestRequest, IngestResponse
from app.infra.json_store import JsonStore
from app.services.groq_client import make_client
from app.services.ingestion_service import synthesize_matrix

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentOut])
def list_agents(user=Depends(get_current_user), store: JsonStore = Depends(get_store)):
    agents = store.list_agents(user["tenant_id"], user["user_id"], user.get("role", "user"))
    return [AgentOut(**a) for a in agents]


@router.post("", response_model=AgentOut)
def create_agent(body: AgentCreate, user=Depends(get_current_user), store: JsonStore = Depends(get_store)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas admin pode criar agentes no PoC.")
    agent = store.create_agent(user["tenant_id"], user["user_id"], body.name, body.type, body.specialty)
    return AgentOut(**agent)


@router.post("/{agent_id}/ingest", response_model=IngestResponse)
def ingest(agent_id: str, body: IngestRequest, user=Depends(get_current_user), store: JsonStore = Depends(get_store)):
    agent = store.get_agent(user["tenant_id"], agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado.")
    if user.get("role") != "admin" and agent["owner_user_id"] != user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso ao agente.")

    client = make_client()
    matrix = synthesize_matrix(client, specialty=agent["specialty"], docs_text=body.docs_text, urls=body.urls)

    updated = store.update_agent_matrix(user["tenant_id"], agent_id, matrix)
    preview = (matrix[:800] + "…") if len(matrix) > 800 else matrix
    return IngestResponse(agent_id=agent_id, matrix_version=int(updated["matrix_version"]), matrix_preview=preview)
