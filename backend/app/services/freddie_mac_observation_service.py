from decimal import Decimal
from typing import Any

from app.db.repositories.freddie_mac_observations import FreddieMacObservationsRepository
from app.schemas.freddie_mac import (
    FreddieMacObservationSample,
    FreddieMacObservationSampleResponse,
)
from app.services.freddie_mac_mlp_mapper import MORTGAGE_STATUS_LABELS


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _int_or_none(value: Any) -> int | None:
    return int(value) if value is not None else None


class FreddieMacObservationService:
    def __init__(self, repository: FreddieMacObservationsRepository) -> None:
        self.repository = repository

    def sample_observations(self, limit: int = 5) -> FreddieMacObservationSampleResponse:
        rows = self.repository.get_sample_observations(limit)
        observations = []
        for row in rows:
            status_code = row.get("mortgage_status_code")
            normalized_status_code = _int_or_none(status_code)
            observations.append(
                FreddieMacObservationSample(
                    id=str(row.get("id")),
                    loan_id=str(row.get("loan_id")),
                    reporting_quarter=str(row.get("reporting_quarter")),
                    mortgage_status_code=normalized_status_code,
                    mortgage_status_label=(
                        MORTGAGE_STATUS_LABELS.get(normalized_status_code, "unknown")
                        if normalized_status_code is not None
                        else None
                    ),
                    ending_balance=_float_or_none(row.get("ending_balance")),
                    original_ltv=_float_or_none(row.get("original_ltv")),
                    original_dcr=_float_or_none(row.get("original_dcr")),
                    note_rate=_float_or_none(row.get("note_rate")),
                    property_state=row.get("property_state"),
                    property_metro=row.get("property_metro"),
                    residential_units=_int_or_none(row.get("residential_units")),
                )
            )
        return FreddieMacObservationSampleResponse(observations=observations)