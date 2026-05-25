from tests.conftest import sample_client_payload, sample_webhook_payload


def _create_client(client, valor_patrimonio: float) -> None:
    payload = sample_client_payload(
        cliente_email="test@example.com",
        valor_patrimonio=valor_patrimonio,
    )
    response = client.post("/clientes", json=payload)
    assert response.status_code == 201


def test_webhook_prioridade_alta(client):
    _create_client(client, valor_patrimonio=250_000)
    webhook = sample_webhook_payload(client_email="test@example.com")

    response = client.post("/webhooks/pipefy/card-updated", json=webhook)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Processado"
    assert data["prioridade"] == "prioridade_alta"

    simulation = data["pipefy_simulation"]
    assert simulation["operation"] == "updateCardField"
    assert len(simulation["mutations"]) == 2
    assert any(m["field"] == "status" for m in simulation["mutations"])
    assert any(m["field"] == "prioridade" for m in simulation["mutations"])
    assert all("updateCardField" in m["query"] for m in simulation["mutations"])


def test_webhook_prioridade_normal(client):
    _create_client(client, valor_patrimonio=50_000)
    webhook = sample_webhook_payload(client_email="test@example.com")

    response = client.post("/webhooks/pipefy/card-updated", json=webhook)

    assert response.status_code == 200
    assert response.json()["prioridade"] == "prioridade_normal"


def test_webhook_threshold_boundary(client):
    _create_client(client, valor_patrimonio=200_000)
    webhook = sample_webhook_payload(client_email="test@example.com")
    response = client.post("/webhooks/pipefy/card-updated", json=webhook)
    assert response.status_code == 200
    assert response.json()["prioridade"] == "prioridade_alta"


def test_webhook_client_not_found(client):
    webhook = sample_webhook_payload(client_email="not.found@example.com")
    response = client.post("/webhooks/pipefy/card-updated", json=webhook)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_webhook_invalid_payload(client):
    response = client.post("/webhooks/pipefy/card-updated", json={"bad": "payload"})
    assert response.status_code == 422