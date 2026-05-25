from tests.conftest import sample_client_payload, sample_webhook_payload


def _seed_client(client) -> None:
    payload = sample_client_payload(
        cliente_email="idempotency@example.com",
        valor_patrimonio=300_000,
    )
    response = client.post("/clientes", json=payload)
    assert response.status_code == 201


def test_webhook_idempotency_blocks_duplicate(client):
    _seed_client(client)
    webhook = sample_webhook_payload(client_email="idempotency@example.com")

    first = client.post("/webhooks/pipefy/card-updated", json=webhook)
    assert first.status_code == 200

    second = client.post("/webhooks/pipefy/card-updated", json=webhook)
    assert second.status_code == 409
    assert second.json()["detail"] == "Webhook event already processed"


def test_webhook_different_event_ids_are_independent(client):
    _seed_client(client)
    w1 = sample_webhook_payload(client_email="idempotency@example.com", event_id="evt_1")
    w2 = sample_webhook_payload(client_email="idempotency@example.com", event_id="evt_2")

    r1 = client.post("/webhooks/pipefy/card-updated", json=w1)
    assert r1.status_code == 200

    # Second event still processed (different event_id)
    r2 = client.post("/webhooks/pipefy/card-updated", json=w2)
    assert r2.status_code == 200