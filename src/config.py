from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "mundo-invest-client-management"
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./mundo_invest.db"

    # Pipefy
    pipefy_pipe_id: str = "mock_pipe_id_12345"
    pipefy_auth_token: str = "mock_token"

    # Field IDs
    field_cliente_nome: str = "cliente_nome_field"
    field_cliente_email: str = "cliente_email_field"
    field_tipo_solicitacao: str = "tipo_solicitacao_field"
    field_valor_patrimonio: str = "valor_patrimonio_field"
    field_status: str = "status_field"
    field_prioridade: str = "prioridade_field"

    # Logging
    log_level: str = "INFO"

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()