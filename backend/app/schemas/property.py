from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PropertyUpsert(BaseModel):
    """Normalized property payload ready for the `properties` table."""

    hud_property_id: str
    property_name: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = Field(default=None, max_length=2)
    zip_code: str | None = None
    total_units: int | None = None
    total_assisted_units: int | None = None
    property_type: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    geocode_quality: str | None = None
    source_name: str
    source_url: str
    source_last_updated: datetime
    raw_hud_payload: dict[str, Any]

    @field_validator("hud_property_id")
    @classmethod
    def hud_property_id_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("hud_property_id is required")
        return value

    @field_validator("state")
    @classmethod
    def normalize_state(cls, value: str | None) -> str | None:
        return value.strip().upper()[:2] if value else None


class PropertyRead(PropertyUpsert):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
