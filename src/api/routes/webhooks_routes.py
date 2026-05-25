from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.domain.webhooks.schemas import WebhookCardUpdatedInput
from src.domain.webhooks.service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/pipefy/card-updated", status_code=status.HTTP_200_OK)
def card_updated_webhook(
    payload: WebhookCardUpdatedInput,
    db: Session = Depends(get_db),
) -> dict:
    service = WebhookService(db)
    return service.process_card_updated(payload)