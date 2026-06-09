from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, PositiveInt, model_validator

IngestionStatus = Literal["started", "completed", "failed", "partial"]


class HudIngestionRequest(BaseModel):
    limit: PositiveInt = Field(default=100, le=500)
    page_size: PositiveInt = Field(default=100, le=500)

    @model_validator(mode="after")
    def page_size_must_not_exceed_limit(self) -> "HudIngestionRequest":
        if self.page_size > self.limit:
            self.page_size = self.limit
        return self


class IngestionRunCreate(BaseModel):
    source_name: str
    source_url: str
    status: IngestionStatus = "started"
    records_requested: int = 0
    records_upserted: int = 0
    records_failed: int = 0
    metadata: dict[str, Any] | None = None


class IngestionRunUpdate(BaseModel):
    completed_at: datetime | None = None
    status: IngestionStatus
    records_requested: int | None = None
    records_upserted: int | None = None
    records_failed: int | None = None
    error_summary: str | None = None
    metadata: dict[str, Any] | None = None


class HudIngestionResponse(BaseModel):
    ingestion_run_id: UUID | str | None
    source_name: str
    records_requested: int
    records_fetched: int
    records_mapped: int
    records_upserted: int
    records_failed: int
    status: IngestionStatus
    errors: list[str] = Field(default_factory=list)


class FreddieMacMlpdIngestionRequest(BaseModel):
    limit: PositiveInt = Field(default=1000, le=5000)
    batch_size: PositiveInt = Field(default=500, le=5000)

    @model_validator(mode="after")
    def batch_size_must_not_exceed_limit(self) -> "FreddieMacMlpdIngestionRequest":
        if self.batch_size > self.limit:
            self.batch_size = self.limit
        return self


class FreddieMacMlpdIngestionResponse(BaseModel):
    ingestion_run_id: UUID | str | None
    source_name: str
    data_dir: str
    source_files: list[str]
    records_requested: int
    records_read: int
    records_mapped: int
    records_upserted: int
    records_failed: int
    status: IngestionStatus
    errors: list[str] = Field(default_factory=list)
