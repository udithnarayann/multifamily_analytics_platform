import json
from decimal import Decimal

from app.services.analytics_service import AnalyticsService
from app.services.freddie_mac_mlp_mapper import FREDDIE_MAC_MLPD_SOURCE_NAME


class FakeAnalyticsRepository:
    def get_hud_property_summary(self):
        return {
            "total_hud_properties": 2,
            "total_units": 300,
            "total_assisted_units": 150,
            "property_count_by_state": [{"key": "VA", "count": 2}],
            "top_states_by_property_count": [{"key": "VA", "count": 2}],
            "count_by_geocode_quality": [
                {"key": "A", "count": 1},
                {"key": "B", "count": 1},
            ],
            "latest_hud_ingestion_run": {
                "id": "run-1",
                "source_name": "HUD Multifamily Properties - Assisted",
                "status": "completed",
            },
        }

    def get_freddie_mac_latest_quarter_summary(self):
        return {
            "reporting_quarter": "y25q1",
            "observation_count": 2,
            "distinct_loan_count": 1,
            "total_ending_balance": Decimal("700"),
            "average_original_ltv": Decimal("0.8"),
            "average_original_dcr": Decimal("1.4"),
            "average_note_rate": Decimal("0.06"),
            "count_by_mortgage_status_code": [{"key": "200", "count": 2}],
            "count_by_property_state": [{"key": "MD", "count": 2}],
            "top_property_metros_by_balance": [
                {"key": "DC", "total_ending_balance": Decimal("700"), "observation_count": 2}
            ],
        }

    def get_freddie_mac_mlpd_summary(self):
        return {
            "total_loan_quarter_observations": 3,
            "distinct_loan_count": 2,
            "min_reporting_quarter": "y24q4",
            "max_reporting_quarter": "y25q1",
            "total_ending_balance_for_latest_quarter": Decimal("700"),
            "average_original_ltv": Decimal("0.8"),
            "average_original_dcr": Decimal("1.4"),
            "average_note_rate": Decimal("0.06"),
            "count_by_mortgage_status_code": [{"key": "200", "count": 2}],
            "count_by_property_state": [{"key": "MD", "count": 2}],
            "latest_freddie_mac_ingestion_run": {
                "id": "run-1",
                "source_name": FREDDIE_MAC_MLPD_SOURCE_NAME,
                "status": "completed",
            },
        }

    def get_recent_ingestion_runs(self, limit: int = 10):
        return [{"id": "run-1", "source_name": FREDDIE_MAC_MLPD_SOURCE_NAME, "status": "completed"}]


def test_hud_summary_aggregates_counts_and_units() -> None:
    summary = AnalyticsService(FakeAnalyticsRepository()).hud_summary()

    assert summary.total_hud_properties == 2
    assert summary.total_units == 300
    assert summary.total_assisted_units == 150
    assert summary.property_count_by_state[0].key == "VA"
    assert summary.property_count_by_state[0].count == 2


def test_freddie_mac_latest_quarter_uses_latest_available_quarter() -> None:
    summary = AnalyticsService(FakeAnalyticsRepository()).freddie_mac_latest_quarter()

    assert summary.reporting_quarter == "y25q1"
    assert summary.observation_count == 2
    assert summary.distinct_loan_count == 1
    assert summary.total_ending_balance == 700.0


def test_status_code_lookup_contains_real_data_dictionary_values() -> None:
    statuses = AnalyticsService(FakeAnalyticsRepository()).freddie_mac_status_codes()

    assert {status.code for status in statuses} == {100, 200, 250, 300, 450, 500}


def test_freddie_mac_summary_serializes_numeric_fields_as_json_numbers() -> None:
    summary = AnalyticsService(FakeAnalyticsRepository()).freddie_mac_summary()
    payload = json.loads(summary.model_dump_json())

    assert isinstance(payload["total_ending_balance_for_latest_quarter"], float | int)
    assert isinstance(payload["average_original_ltv"], float | int)
    assert isinstance(payload["average_original_dcr"], float | int)
    assert isinstance(payload["average_note_rate"], float | int)
    assert payload["average_original_ltv"] == 0.8


def test_latest_quarter_serializes_numeric_fields_as_json_numbers() -> None:
    summary = AnalyticsService(FakeAnalyticsRepository()).freddie_mac_latest_quarter()
    payload = json.loads(summary.model_dump_json())

    assert isinstance(payload["total_ending_balance"], float | int)
    assert isinstance(payload["average_original_ltv"], float | int)
    assert isinstance(payload["average_original_dcr"], float | int)
    assert isinstance(payload["average_note_rate"], float | int)
    assert isinstance(
        payload["top_property_metros_by_balance"][0]["total_ending_balance"], float | int
    )
