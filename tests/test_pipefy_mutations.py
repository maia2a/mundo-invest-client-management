from src.integrations.pipefy.pipefy_client import PipefyClient
from src.domain.clients.schemas import ClientCreateInput


def test_create_card_query_structure():
    query = PipefyClient.create_card_query()
    assert "createCard" in query
    assert "CreateCardInput" in query
    assert "card {" in query


def test_update_card_field_query_structure():
    query = PipefyClient.update_card_field_query()
    assert "updateCardField" in query
    assert "UpdateCardFieldInput" in query
    assert "success" in query


def test_update_fields_values_query_available():
    query = PipefyClient.update_fields_values_query()
    assert "updateFieldsValues" in query
    assert "UpdateFieldsValuesInput" in query


def test_build_create_card_payload_fields():
    pipefy = PipefyClient()
    client_input = ClientCreateInput(
        cliente_nome="Maria",
        cliente_email="maria@example.com",
        tipo_solicitacao="Abertura",
        valor_patrimonio=500_000,
    )
    payload = pipefy.build_create_card_payload(client_input)

    assert "input" in payload
    input_ = payload["input"]
    assert "pipe_id" in input_
    assert input_["title"] == "Maria"
    fields = input_["fields_attributes"]
    field_ids = {f["field_id"] for f in fields}
    assert pipefy.field_cliente_nome in field_ids
    assert pipefy.field_cliente_email in field_ids
    assert pipefy.field_tipo_solicitacao in field_ids
    assert pipefy.field_valor_patrimonio in field_ids


def test_build_update_card_field_payload():
    pipefy = PipefyClient()
    payload = pipefy.build_update_card_field_payload(
        card_id="card_abc",
        field_id=pipefy.field_status,
        new_value="Processado",
        field_name="status",
    )

    assert payload["operation"] == "updateCardField"
    assert payload["field"] == "status"
    assert "updateCardField" in payload["query"]
    variables = payload["variables"]["input"]
    assert variables["card_id"] == "card_abc"
    assert variables["new_value"] == "Processado"