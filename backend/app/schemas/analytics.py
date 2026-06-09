from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CountBucket(BaseModel):
    key: str
    count: int


class BalanceBucket(BaseModel):
    key: str
    total_ending_balance: float | None = None
    observation_count: int


class IngestionRunSummary(BaseModel):
    id: str
    source_name: str
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    records_requested: int | None = None
    records_fetched: int | None = None
    records_upserted: int | None = None
    records_failed: int | None = None
    metadata: dict[str, Any] | None = None


class HudPropertySummary(BaseModel):
    source_label: str = "HUD Multifamily Properties - Assisted"
    total_hud_properties: int
    total_units: int | None = None
    total_assisted_units: int | None = None
    property_count_by_state: list[CountBucket] = Field(default_factory=list)
    top_states_by_property_count: list[CountBucket] = Field(default_factory=list)
    count_by_geocode_quality: list[CountBucket] = Field(default_factory=list)
    latest_hud_ingestion_run: IngestionRunSummary | None = None


class FreddieMacMlpdSummary(BaseModel):
    source_label: str = "Freddie Mac Multifamily Loan Performance Database"
    total_loan_quarter_observations: int
    distinct_loan_count: int
    min_reporting_quarter: str | None = None
    max_reporting_quarter: str | None = None
    total_ending_balance_for_latest_quarter: float | None = None
    average_original_ltv: float | None = None
    average_original_dcr: float | None = None
    average_note_rate: float | None = None
    count_by_mortgage_status_code: list[CountBucket] = Field(default_factory=list)
    count_by_property_state: list[CountBucket] = Field(default_factory=list)
    latest_freddie_mac_ingestion_run: IngestionRunSummary | None = None


class FreddieMacStatusCode(BaseModel):
    code: int
    label: str


class FreddieMacLatestQuarterSummary(BaseModel):
    source_label: str = "Freddie Mac Multifamily Loan Performance Database"
    reporting_quarter: str | None = None
    observation_count: int
    distinct_loan_count: int
    total_ending_balance: float | None = None
    average_original_ltv: float | None = None
    average_original_dcr: float | None = None
    average_note_rate: float | None = None
    count_by_mortgage_status_code: list[CountBucket] = Field(default_factory=list)
    count_by_property_state: list[CountBucket] = Field(default_factory=list)
    top_property_metros_by_balance: list[BalanceBucket] = Field(default_factory=list)


class RecentIngestionRunsResponse(BaseModel):
    source_label: str = "Ingestion Runs"
    runs: list[IngestionRunSummary]
