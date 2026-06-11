import logging

from fastapi import APIRouter, HTTPException

from app.models.request_models import (
    GroceryRequest
)

from app.services.llm_service import (
    NonGroceryItemError,
)

from app.services.rule_engine import (
    process_item
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/classify")
async def classify_item(
    request: GroceryRequest
):
    logger.info(
        "Classifying grocery item",
    )

    try:
        return await process_item(
            request.item
        )
    except NonGroceryItemError as exc:
        raise HTTPException(
            status_code=400,
            detail="This item does not belong to a grocery category.",
        ) from exc
