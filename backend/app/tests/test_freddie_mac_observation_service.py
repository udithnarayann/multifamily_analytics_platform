from decimal import Decimal

from app.services.freddie_mac_observation_service import FreddieMacObservationService


class FakeFreddieMacObservationsRepository:
    def get_sample_observations(self, limit: int = 5):
        return [
            {
                "id": "05762b36-5beb-471b-a4b3-55506eb47a5a",
                "loan_id": "418251002",
                "reporting_quarter": "y01q2",
                "mortgage_status_code": "100",
                "ending_balance": Decimal("11132601.44"),
                "original_ltv": Decimal("0.79718"),
                "original_dcr": Decimal("1.268"),
                "note_rate": Decimal("0.0782"),
                "property_state": "GA",
                "property_metro": "ATLANTA, GA",
                "residential_units": "264",
                "raw_row_payload": {"should": "not be returned"},
            }
        ]


def test_sample_observations_adds_label_and_excludes_raw_payload() -> None:
    response = FreddieMacObservationService(
        FakeFreddieMacObservationsRepository()
    ).sample_observations()

    observation = response.observations[0]
    payload = observation.model_dump()

    assert observation.id == "05762b36-5beb-471b-a4b3-55506eb47a5a"
    assert observation.mortgage_status_code == 100
    assert observation.mortgage_status_label == "current_or_less_than_60_days_delinquent"
    assert observation.ending_balance == 11132601.44
    assert observation.original_ltv == 0.79718
    assert observation.original_dcr == 1.268
    assert observation.note_rate == 0.0782
    assert observation.residential_units == 264
    assert "raw_row_payload" not in payload
