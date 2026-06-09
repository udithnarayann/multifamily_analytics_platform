from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import get_settings
from app.schemas.ingestion import (
    FreddieMacMlpdIngestionRequest,
    FreddieMacMlpdIngestionResponse,
)
from app.services.freddie_mac_mlp_ingestion_service import FreddieMacMlpdIngestionService

from ..deps import get_freddie_mac_mlpd_ingestion_service

router = APIRouter(prefix="/ingestion/freddie-mac", tags=["freddie-mac-ingestion"])
FreddieMacMlpdIngestionServiceDependency = Depends(get_freddie_mac_mlpd_ingestion_service)


@router.post("/mlpd", response_model=FreddieMacMlpdIngestionResponse)
def ingest_freddie_mac_mlpd(
    request: FreddieMacMlpdIngestionRequest,
    ingestion_service: FreddieMacMlpdIngestionService = FreddieMacMlpdIngestionServiceDependency,
) -> FreddieMacMlpdIngestionResponse:
    settings = get_settings()
    if request.limit > settings.freddie_mac_mlpd_max_test_ingest_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "limit cannot exceed "
                f"{settings.freddie_mac_mlpd_max_test_ingest_records} for test ingestion"
            ),
        )
    try:
        return ingestion_service.ingest(request)
    except Exception as exc:  # noqa: BLE001 - route returns clean API error
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Freddie Mac MLPD ingestion failed: {exc}",
        ) from exc
