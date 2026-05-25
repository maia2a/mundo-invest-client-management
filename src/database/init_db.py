from src.database.base import Base
from src.database.session import engine
from src.shared.logging import get_logger

# Import all models so Base.metadata.create_all sees them
from src.domain.clients.models import Client  # noqa: F401
from src.domain.webhooks.models import WebhookEvent  # noqa: F401

logger = get_logger(__name__)


def init_db() -> None:
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")