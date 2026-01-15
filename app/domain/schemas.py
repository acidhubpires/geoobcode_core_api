from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, Field

AgentType = Literal["Pessoal", "Corporativo"]


class LoginRequest(BaseModel):
    tenant_id: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AgentCreate(BaseModel):
    name: str
    type: AgentType
    specialty: str


class AgentOut(BaseModel):
    id: str
    tenant_id: str
    owner_user_id: str
    name: str
    type: AgentType
    specialty: str
    matrix_version: int = 0
    created_at: datetime


class IngestRequest(BaseModel):
    docs_text: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)


class IngestResponse(BaseModel):
    agent_id: str
    matrix_version: int
    matrix_preview: str


class ChatRequest(BaseModel):
    agent_id: str
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    agent_id: str
    answer: str


class HealthResponse(BaseModel):
    status: str = "ok"
    time_utc: datetime = Field(default_factory=datetime.utcnow)
