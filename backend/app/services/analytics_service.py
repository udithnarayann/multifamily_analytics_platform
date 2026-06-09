from typing import Any

from app.db.repositories.analytics import AnalyticsRepository
from app.schemas.analytics import (
    FreddieMacLatestQuarterSummary,
    FreddieMacMlpdSummary,
    FreddieMacStatusCode,
    HudPropertySummary,
    IngestionRunSummary,
    RecentIngestionRunsResponse,
)
from app.services.freddie_mac_mlp_mapper import (
    MORTGAGE_STATUS_LABELS,
)


def _run_summary(row: dict[str, Any] | None) -> IngestionRunSummary | None:
    if not row:
        return None
    return IngestionRunSummary(
        id=str(row.get("id")),
        source_name=row.get("source_name") or "unknown",
        status=row.get("status") or "unknown",
        started_at=row.get("started_at"),
        completed_at=row.get("completed_at"),
        records_requested=row.get("records_requested"),
        records_fetched=row.get("records_fetched"),
        records_upserted=row.get("records_upserted"),
        records_failed=row.get("records_failed"),
        metadata=row.get("metadata"),
    )


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository) -> None:
        self.repository = repository

    def hud_summary(self) -> HudPropertySummary:
        payload = self.repository.get_hud_property_summary()
        payload.setdefault("total_hud_properties", 0)
        payload.setdefault("property_count_by_state", [])
        payload.setdefault("top_states_by_property_count", [])
        payload.setdefault("count_by_geocode_quality", [])
        return HudPropertySummary(**payload)

    def freddie_mac_summary(self) -> FreddieMacMlpdSummary:
        payload = self.repository.get_freddie_mac_mlpd_summary()
        payload.setdefault("total_loan_quarter_observations", 0)
        payload.setdefault("distinct_loan_count", 0)
        payload.setdefault("count_by_mortgage_status_code", [])
        payload.setdefault("count_by_property_state", [])
        return FreddieMacMlpdSummary(**payload)

    def freddie_mac_status_codes(self) -> list[FreddieMacStatusCode]:
        return [
            FreddieMacStatusCode(code=code, label=label)
            for code, label in sorted(MORTGAGE_STATUS_LABELS.items())
        ]

    def freddie_mac_latest_quarter(self) -> FreddieMacLatestQuarterSummary:
        payload = self.repository.get_freddie_mac_latest_quarter_summary()
        payload.setdefault("observation_count", 0)
        payload.setdefault("distinct_loan_count", 0)
        payload.setdefault("count_by_mortgage_status_code", [])
        payload.setdefault("count_by_property_state", [])
        payload.setdefault("top_property_metros_by_balance", [])
        return FreddieMacLatestQuarterSummary(**payload)

    def recent_ingestion_runs(self, limit: int = 10) -> RecentIngestionRunsResponse:
        return RecentIngestionRunsResponse(
            runs=[_run_summary(row) for row in self.repository.get_recent_ingestion_runs(limit)]
        )
