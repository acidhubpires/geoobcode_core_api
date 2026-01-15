from __future__ import annotations

import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user, get_store
from app.domain.schemas import ChatRequest, ChatResponse
from app.infra.json_store import JsonStore
from app.services.groq_client import make_client
from app.services.chat_service import answer

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, user=Depends(get_current_user), store: JsonStore = Depends(get_store)):
    agent = store.get_agent(user["tenant_id"], body.agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado.")
    if user.get("role") != "admin" and agent["owner_user_id"] != user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso ao agente.")

    if body.conversation_id:
        conv_id = body.conversation_id
    else:
        conv_id = store.create_conversation(user["tenant_id"], user["user_id"], body.agent_id)["id"]

    store.append_message(conv_id, "user", body.message)
    history = store.load_last_messages(conv_id, limit=20)

    client = make_client()
    reply = answer(client, agent, history=history, prompt=body.message, profile=user.get("role", "ADMIN").upper())

    store.append_message(conv_id, "assistant", reply)
    return ChatResponse(conversation_id=conv_id, agent_id=body.agent_id, answer=reply)


@router.post("/chat/stream")
def chat_stream(body: ChatRequest, user=Depends(get_current_user), store: JsonStore = Depends(get_store)):
    agent = store.get_agent(user["tenant_id"], body.agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente não encontrado.")
    if user.get("role") != "admin" and agent["owner_user_id"] != user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem acesso ao agente.")

    if body.conversation_id:
        conv_id = body.conversation_id
    else:
        conv_id = store.create_conversation(user["tenant_id"], user["user_id"], body.agent_id)["id"]

    store.append_message(conv_id, "user", body.message)
    history = store.load_last_messages(conv_id, limit=20)

    client = make_client()
    reply = answer(client, agent, history=history, prompt=body.message, profile=user.get("role", "ADMIN").upper())
    store.append_message(conv_id, "assistant", reply)

    def gen():
        payload = {"conversation_id": conv_id, "agent_id": body.agent_id, "answer": reply}
        yield f"event: message\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
