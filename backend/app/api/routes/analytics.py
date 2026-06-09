from fastapi import APIRouter, Depends

from app.schemas.analytics import (
    FreddieMacLatestQuarterSummary,
    FreddieMacMlpdSummary,
    FreddieMacStatusCode,
    HudPropertySummary,
    RecentIngestionRunsResponse,
)
from app.services.analytics_service import AnalyticsService

from ..deps import get_analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])
AnalyticsServiceDependency = Depends(get_analytics_service)


@router.get("/hud/summary", response_model=HudPropertySummary)
def hud_summary(
    analytics_service: AnalyticsService = AnalyticsServiceDependency,
) -> HudPropertySummary:
    return analytics_service.hud_summary()


@router.get("/freddie-mac/summary", response_model=FreddieMacMlpdSummary)
def freddie_mac_summary(
    analytics_service: AnalyticsService = AnalyticsServiceDependency,
) -> FreddieMacMlpdSummary:
    return analytics_service.freddie_mac_summary()


@router.get("/freddie-mac/status-codes", response_model=list[FreddieMacStatusCode])
def freddie_mac_status_codes(
    analytics_service: AnalyticsService = AnalyticsServiceDependency,
) -> list[FreddieMacStatusCode]:
    return analytics_service.freddie_mac_status_codes()


@router.get("/freddie-mac/latest-quarter", response_model=FreddieMacLatestQuarterSummary)
def freddie_mac_latest_quarter(
    analytics_service: AnalyticsService = AnalyticsServiceDependency,
) -> FreddieMacLatestQuarterSummary:
    return analytics_service.freddie_mac_latest_quarter()


@router.get("/ingestion-runs/recent", response_model=RecentIngestionRunsResponse)
def recent_ingestion_runs(
    analytics_service: AnalyticsService = AnalyticsServiceDependency,
) -> RecentIngestionRunsResponse:
    return analytics_service.recent_ingestion_runs()
