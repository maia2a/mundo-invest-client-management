from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from src.config import get_settings
from src.shared.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

# CRUCIAL: StaticPool garante que todas as conexões usem o MESMO banco em memória
poolclass = StaticPool if (settings.is_sqlite and ":memory:" in settings.database_url) else None

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    poolclass=poolclass,
    pool_pre_ping=True if not poolclass else False,
)

# Ensure foreign keys are enforced on SQLite (apenas para arquivos, não memory)
if settings.is_sqlite and not poolclass:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):  # pragma: no cover
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()