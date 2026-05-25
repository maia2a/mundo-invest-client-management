from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.domain.clients.schemas import ClientCreateInput, ClientOutput
from src.domain.clients.service import ClientService

router = APIRouter(prefix="/clientes", tags=["Clients"])


@router.post("", response_model=ClientOutput, status_code=status.HTTP_201_CREATED)
def create_cliente(payload: ClientCreateInput, db: Session = Depends(get_db)) -> ClientOutput:
    service = ClientService(db)
    client, simulation = service.create_client(payload)
    return ClientOutput(
        id=client.id,
        cliente_nome=client.cliente_nome,
        cliente_email=client.cliente_email,
        status=client.status,
        pipefy_simulation=simulation,
    )