from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import get_settings
from app.schemas.ingestion import HudIngestionRequest, HudIngestionResponse
from app.services.ingestion_service import IngestionService

from ..deps import get_ingestion_service

router = APIRouter(prefix="/ingestion", tags=["ingestion"])
IngestionServiceDependency = Depends(get_ingestion_service)


@router.post("/hud/properties", response_model=HudIngestionResponse)
async def ingest_hud_properties(
    request: HudIngestionRequest,
    ingestion_service: IngestionService = IngestionServiceDependency,
) -> HudIngestionResponse:
    settings = get_settings()
    if request.limit > settings.hud_max_test_ingest_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"limit cannot exceed {settings.hud_max_test_ingest_records} for test ingestion",
        )

    try:
        return await ingestion_service.ingest_hud_properties(request)
    except Exception as exc:  # noqa: BLE001 - route returns clean API error
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"HUD ingestion failed: {exc}",
        ) from exc
