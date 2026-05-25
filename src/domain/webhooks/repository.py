from sqlalchemy.orm import Session
from src.domain.webhooks.models import WebhookEvent


class WebhookEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def exists_by_event_id(self, event_id: str) -> bool:
        return self.db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first() is not None

    def create(self, event: WebhookEvent) -> WebhookEvent:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event