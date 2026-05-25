from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ClientCreateInput(BaseModel):
    cliente_nome: str = Field(..., min_length=2, max_length=255)
    cliente_email: EmailStr
    tipo_solicitacao: str = Field(..., min_length=2, max_length=100)
    valor_patrimonio: float = Field(..., gt=0)


class PipefySimulation(BaseModel):
    operation: str
    query: str
    variables: dict


class ClientOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_nome: str
    cliente_email: str
    status: str
    pipefy_simulation: PipefySimulation