from src.config import get_settings
from src.domain.clients.schemas import ClientCreateInput
from src.integrations.pipefy.mutations import (
    CREATE_CARD_MUTATION,
    UPDATE_CARD_FIELD_MUTATION,
    UPDATE_FIELDS_VALUES_MUTATION,
)
from src.shared.logging import get_logger

logger = get_logger(__name__)


class PipefyClient:
    """
    Simulated Pipefy GraphQL client.
    The application NEVER makes HTTP requests to Pipefy.
    Instead, it builds the GraphQL payloads that WOULD be sent,
    following the official schema, and persists them locally.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.pipe_id = settings.pipefy_pipe_id
        self.field_cliente_nome = settings.field_cliente_nome
        self.field_cliente_email = settings.field_cliente_email
        self.field_tipo_solicitacao = settings.field_tipo_solicitacao
        self.field_valor_patrimonio = settings.field_valor_patrimonio
        self.field_status = settings.field_status
        self.field_prioridade = settings.field_prioridade
        self.auth_token = settings.pipefy_auth_token

    # --- Mutations available for reference -----------------------------------
    @staticmethod
    def create_card_query() -> str:
        return CREATE_CARD_MUTATION.strip()

    @staticmethod
    def update_card_field_query() -> str:
        return UPDATE_CARD_FIELD_MUTATION.strip()

    @staticmethod
    def update_fields_values_query() -> str:
        """
        Alternative for batch updates - documented as an evolution path
        in the README.
        """
        return UPDATE_FIELDS_VALUES_MUTATION.strip()

    # --- Payload builders ------------------------------------------------------
    def build_create_card_payload(self, client: ClientCreateInput) -> dict:
        return {
            "input": {
                "pipe_id": self.pipe_id,
                "title": client.cliente_nome,
                "fields_attributes": [
                    {"field_id": self.field_cliente_nome, "field_value": client.cliente_nome},
                    {"field_id": self.field_cliente_email, "field_value": client.cliente_email},
                    {"field_id": self.field_tipo_solicitacao, "field_value": client.tipo_solicitacao},
                    {"field_id": self.field_valor_patrimonio, "field_value": str(client.valor_patrimonio)},
                ],
            }
        }

    def build_update_card_field_payload(
        self,
        card_id: str,
        field_id: str,
        new_value: str,
        field_name: str = "unknown",
    ) -> dict:
        return {
            "operation": "updateCardField",
            "field": field_name,
            "query": self.update_card_field_query(),
            "variables": {
                "input": {
                    "card_id": card_id,
                    "field_id": field_id,
                    "new_value": new_value,
                }
            },
        }

    def build_update_fields_values_payload(self, card_id: str, fields: list[dict]) -> dict:
        """
        Alternative batch mutation. Not used by the current flow but kept
        as an evolution path for future refactors.
        """
        return {
            "operation": "updateFieldsValues",
            "query": self.update_fields_values_query(),
            "variables": {
                "input": {
                    "card_id": card_id,
                    "fields": fields,
                }
            },
        }