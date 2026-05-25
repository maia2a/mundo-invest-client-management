from tests.conftest import sample_client_payload


def test_create_client_success(client):
    payload = sample_client_payload()
    response = client.post("/clientes", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["cliente_nome"] == "João Silva"
    assert data["cliente_email"] == "joao.silva@example.com"
    assert data["status"] == "Aguardando Análise"

    simulation = data["pipefy_simulation"]
    assert simulation["operation"] == "createCard"
    assert "createCard" in simulation["query"]
    assert simulation["variables"]["input"]["pipe_id"] == "test_pipe_id"
    assert simulation["variables"]["input"]["title"] == "João Silva"
    assert len(simulation["variables"]["input"]["fields_attributes"]) == 4


def test_create_client_invalid_email(client):
    payload = sample_client_payload(cliente_email="invalid-email")
    response = client.post("/clientes", json=payload)
    assert response.status_code == 422


def test_create_client_missing_field(client):
    payload = {"cliente_nome": "João"}  # missing required fields
    response = client.post("/clientes", json=payload)
    assert response.status_code == 422


def test_create_client_negative_patrimonio(client):
    payload = sample_client_payload(valor_patrimonio=-100)
    response = client.post("/clientes", json=payload)
    assert response.status_code == 422


def test_create_client_duplicate_email(client):
    payload = sample_client_payload()
    response1 = client.post("/clientes", json=payload)
    assert response1.status_code == 201

    response2 = client.post("/clientes", json=payload)
    assert response2.status_code == 409