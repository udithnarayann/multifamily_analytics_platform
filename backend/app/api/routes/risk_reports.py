from fastapi import APIRouter, Depends, HTTPException, status

from app.core.errors import AIServiceError, ConfigurationError, NotFoundError, PersistenceError
from app.schemas.risk_report import RiskReportResponse
from app.services.risk_report_service import RiskReportService

from ..deps import get_risk_report_service

router = APIRouter(prefix="/risk-reports", tags=["risk-reports"])
RiskReportServiceDependency = Depends(get_risk_report_service)


@router.post("/freddie-mac/{observation_id}", response_model=RiskReportResponse)
def create_freddie_mac_risk_report(
    observation_id: str,
    risk_report_service: RiskReportService = RiskReportServiceDependency,
) -> RiskReportResponse:
    try:
        return risk_report_service.create_freddie_mac_report(observation_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except PersistenceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except AIServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/freddie-mac/{observation_id}", response_model=RiskReportResponse)
def get_freddie_mac_risk_report(
    observation_id: str,
    risk_report_service: RiskReportService = RiskReportServiceDependency,
) -> RiskReportResponse:
    try:
        return risk_report_service.get_latest_freddie_mac_report(observation_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
