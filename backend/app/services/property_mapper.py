from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from app.schemas.property import PropertyUpsert

HUD_SOURCE_NAME = "HUD Multifamily Properties - Assisted"


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _clean_decimal(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _first_present(attributes: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        if name in attributes and attributes[name] not in (None, ""):
            return attributes[name]
    return None


def map_hud_feature_to_property(
    feature: dict[str, Any], *, source_url: str, source_last_updated: datetime
) -> PropertyUpsert:
    """Map one ArcGIS feature into the normalized properties schema.

    This function is intentionally pure and defensive so it can be tested without
    FastAPI, Supabase, or network access.
    """

    attributes = feature.get("attributes") or {}
    geometry = feature.get("geometry") or {}

    hud_property_id = _clean_text(attributes.get("PROPERTY_ID"))
    if not hud_property_id:
        object_id = _first_present(attributes, ("OBJECTID", "FID"))
        hud_property_id = _clean_text(object_id)

    longitude = _clean_decimal(
        _first_present(attributes, ("LON", "LONGITUDE", "Longitude", "X", "x"))
        if _first_present(attributes, ("LON", "LONGITUDE", "Longitude", "X", "x")) is not None
        else geometry.get("x")
    )
    latitude = _clean_decimal(
        _first_present(attributes, ("LAT", "LATITUDE", "Latitude", "Y", "y"))
        if _first_present(attributes, ("LAT", "LATITUDE", "Latitude", "Y", "y")) is not None
        else geometry.get("y")
    )

    return PropertyUpsert(
        hud_property_id=hud_property_id or "",
        property_name=_clean_text(attributes.get("PROPERTY_NAME_TEXT")),
        address_line1=_clean_text(attributes.get("ADDRESS_LINE1_TEXT")),
        address_line2=_clean_text(attributes.get("ADDRESS_LINE2_TEXT")),
        city=_clean_text(attributes.get("PLACED_BASE_CITY_NAME_TEXT")),
        state=_clean_text(_first_present(attributes, ("STATE_CODE", "STD_ST"))),
        zip_code=_clean_text(_first_present(attributes, ("ZIP_CODE", "STD_ZIP5"))),
        total_units=_clean_int(attributes.get("TOTAL_UNIT_COUNT")),
        total_assisted_units=_clean_int(attributes.get("TOTAL_ASSISTED_UNIT_COUNT")),
        property_type=_clean_text(attributes.get("PROPERTY_CATEGORY_NAME")),
        latitude=latitude,
        longitude=longitude,
        geocode_quality=_clean_text(attributes.get("LVL2KX")),
        source_name=HUD_SOURCE_NAME,
        source_url=source_url,
        source_last_updated=source_last_updated,
        raw_hud_payload=feature,
    )
