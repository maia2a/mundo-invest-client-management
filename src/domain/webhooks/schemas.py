from datetime import datetime
from pydantic import BaseModel, EmailStr


class WebhookCardUpdatedInput(BaseModel):
    event_id: str
    card_id: str
    cliente_email: EmailStr
    timestamp: datetime


class WebhookPipefySimulation(BaseModel):
    operation: str
    mutations: list[dict]


class WebhookOutput(BaseModel):
    event_id: str
    cliente_email: str
    status: str
    prioridade: str | None
    pipefy_simulation: WebhookPipefySimulation