from datetime import UTC, datetime

from app.services.property_mapper import map_hud_feature_to_property


def test_maps_hud_feature_to_property_schema() -> None:
    feature = {
        "attributes": {
            "PROPERTY_ID": "HUD123",
            "PROPERTY_NAME_TEXT": "Sample Apartments",
            "ADDRESS_LINE1_TEXT": "100 Main St",
            "ADDRESS_LINE2_TEXT": "Apt 2",
            "PLACED_BASE_CITY_NAME_TEXT": "McLean",
            "STATE_CODE": "va",
            "ZIP_CODE": "22102",
            "TOTAL_UNIT_COUNT": "120",
            "TOTAL_ASSISTED_UNIT_COUNT": 80,
            "PROPERTY_CATEGORY_NAME": "Multifamily",
            "LVL2KX": "Rooftop",
        },
        "geometry": {"x": -77.2, "y": 38.9},
    }

    mapped = map_hud_feature_to_property(
        feature,
        source_url="https://example.test/query",
        source_last_updated=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert mapped.hud_property_id == "HUD123"
    assert mapped.property_name == "Sample Apartments"
    assert mapped.state == "VA"
    assert mapped.total_units == 120
    assert mapped.total_assisted_units == 80
    assert mapped.geocode_quality == "Rooftop"
    assert str(mapped.longitude) == "-77.2"
    assert str(mapped.latitude) == "38.9"
    assert mapped.raw_hud_payload == feature


def test_mapper_tolerates_missing_optional_fields() -> None:
    feature = {"attributes": {"PROPERTY_ID": "HUD456"}}

    mapped = map_hud_feature_to_property(
        feature,
        source_url="https://example.test/query",
        source_last_updated=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert mapped.hud_property_id == "HUD456"
    assert mapped.property_name is None
    assert mapped.latitude is None
    assert mapped.longitude is None
    assert mapped.raw_hud_payload == feature
