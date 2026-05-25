from sqlalchemy.orm import Session
from src.domain.clients.models import Client
from src.domain.clients.repository import ClientRepository
from src.domain.clients.schemas import ClientCreateInput
from src.integrations.pipefy.pipefy_client import PipefyClient
from src.shared.logging import get_logger

logger = get_logger(__name__)

INITIAL_STATUS = "Aguardando Análise"


class ClientService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ClientRepository(db)
        self.pipefy = PipefyClient()

    def create_client(self, payload: ClientCreateInput) -> tuple[Client, dict]:
        logger.info(f"Creating client {payload.cliente_email}")

        if self.repo.get_by_email(payload.cliente_email):
            from src.shared.errors import ConflictException
            raise ConflictException("Client with this email already exists")

        # Build the simulated createCard payload
        pipefy_payload = self.pipefy.build_create_card_payload(payload)
        pipefy_query = self.pipefy.create_card_query()

        client = Client(
            cliente_nome=payload.cliente_nome,
            cliente_email=payload.cliente_email,
            tipo_solicitacao=payload.tipo_solicitacao,
            valor_patrimonio=payload.valor_patrimonio,
            status=INITIAL_STATUS,
            pipefy_create_card_payload=str(pipefy_payload),
        )
        client = self.repo.create(client)

        simulation = {
            "operation": "createCard",
            "query": pipefy_query,
            "variables": pipefy_payload,
        }

        logger.info(f"Client {client.id} created successfully")
        return client, simulation