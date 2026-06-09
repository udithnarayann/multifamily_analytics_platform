from fastapi import APIRouter, Depends, Query

from app.schemas.freddie_mac import FreddieMacObservationSampleResponse
from app.services.freddie_mac_observation_service import FreddieMacObservationService

from ..deps import get_freddie_mac_observation_service

router = APIRouter(prefix="/freddie-mac/observations", tags=["freddie-mac-observations"])
FreddieMacObservationServiceDependency = Depends(get_freddie_mac_observation_service)


@router.get("/sample", response_model=FreddieMacObservationSampleResponse)
def sample_freddie_mac_observations(
    limit: int = Query(default=5, ge=1, le=25),
    observation_service: FreddieMacObservationService = FreddieMacObservationServiceDependency,
) -> FreddieMacObservationSampleResponse:
    return observation_service.sample_observations(limit)