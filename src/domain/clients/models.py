from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cliente_nome: Mapped[str] = mapped_column(String(255), nullable=False)
    cliente_email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    tipo_solicitacao: Mapped[str] = mapped_column(String(100), nullable=False)
    valor_patrimonio: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Aguardando Análise")
    prioridade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pipefy_card_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pipefy_create_card_payload: Mapped[dict | None] = mapped_column(Text, nullable=True)
    pipefy_update_payload: Mapped[dict | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )