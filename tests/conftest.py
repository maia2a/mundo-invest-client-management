import os
import pytest
from fastapi.testclient import TestClient

# Force SQLite in-memory for tests BEFORE importing the app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["PIPEFY_PIPE_ID"] = "test_pipe_id"
os.environ["FIELD_CLIENTE_NOME"] = "test_field_nome"
os.environ["FIELD_CLIENTE_EMAIL"] = "test_field_email"
os.environ["FIELD_TIPO_SOLICITACAO"] = "test_field_tipo"
os.environ["FIELD_VALOR_PATRIMONIO"] = "test_field_patrimonio"
os.environ["FIELD_STATUS"] = "test_field_status"
os.environ["FIELD_PRIORIDADE"] = "test_field_prioridade"

# Import app and database components AFTER setting env vars
from src.database.base import Base
from src.database.session import engine, SessionLocal, get_db
from src.main import app  # noqa: E402


@pytest.fixture(scope="function")
def db_session():
    # Create tables in the global in-memory engine
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop tables after each test to ensure isolation
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def sample_client_payload(**overrides) -> dict:
    base = {
        "cliente_nome": "João Silva",
        "cliente_email": "joao.silva@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 250000,
    }
    base.update(overrides)
    return base


def sample_webhook_payload(client_email: str = "joao.silva@example.com", **overrides) -> dict:
    base = {
        "event_id": "evt_123",
        "card_id": "card_456",
        "cliente_email": client_email,
        "timestamp": "2026-05-18T12:00:00Z",
    }
    base.update(overrides)
    return base