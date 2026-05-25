import json
from datetime import datetime
from sqlalchemy.orm import Session
from src.domain.webhooks.models import WebhookEvent
from src.domain.webhooks.repository import WebhookEventRepository
from src.domain.webhooks.schemas import WebhookCardUpdatedInput
from src.domain.clients.repository import ClientRepository
from src.integrations.pipefy.pipefy_client import PipefyClient
from src.shared.errors import NotFoundException, ConflictException
from src.shared.logging import get_logger

logger = get_logger(__name__)

PRIORIDADE_ALTA = "prioridade_alta"
PRIORIDADE_NORMAL = "prioridade_normal"
THRESHOLD_PATRIMONIO = 200_000.0


class WebhookService:
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = WebhookEventRepository(db)
        self.client_repo = ClientRepository(db)
        self.pipefy = PipefyClient()

    @staticmethod
    def _compute_prioridade(valor_patrimonio: float) -> str:
        return PRIORIDADE_ALTA if valor_patrimonio >= THRESHOLD_PATRIMONIO else PRIORIDADE_NORMAL

    def process_card_updated(self, payload: WebhookCardUpdatedInput) -> dict:
        logger.info(f"Processing webhook event_id={payload.event_id}")

        # Idempotency check
        if self.event_repo.exists_by_event_id(payload.event_id):
            raise ConflictException("Webhook event already processed")

        # Find client
        client = self.client_repo.get_by_email(payload.cliente_email)
        if not client:
            raise NotFoundException("Client not found for the provided email")

        prioridade = self._compute_prioridade(client.valor_patrimonio)
        new_status = "Processado"

        # Build simulated mutations
        mutations = [
            self.pipefy.build_update_card_field_payload(
                card_id=payload.card_id,
                field_id=self.pipefy.field_status,
                new_value=new_status,
                field_name="status",
            ),
            self.pipefy.build_update_card_field_payload(
                card_id=payload.card_id,
                field_id=self.pipefy.field_prioridade,
                new_value=prioridade,
                field_name="prioridade",
            ),
        ]

        # Update client
        client.status = new_status
        client.prioridade = prioridade
        client.pipefy_card_id = payload.card_id
        client.pipefy_update_payload = str(mutations)
        self.client_repo.update(client)

        # Persist webhook event
        event = WebhookEvent(
            event_id=payload.event_id,
            card_id=payload.card_id,
            cliente_email=payload.cliente_email,
            processed_at=datetime.utcnow(),
            raw_payload=json.dumps(payload.model_dump(mode="json")),
            status="processed",
        )
        self.event_repo.create(event)

        simulation = {
            "operation": "updateCardField",
            "mutations": mutations,
        }

        return {
            "event_id": payload.event_id,
            "cliente_email": payload.cliente_email,
            "status": new_status,
            "prioridade": prioridade,
            "pipefy_simulation": simulation,
        }