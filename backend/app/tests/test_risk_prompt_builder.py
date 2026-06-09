from datetime import date
from decimal import Decimal

from app.services.freddie_mac_mlp_mapper import FREDDIE_MAC_MLPD_SOURCE_NAME
from app.services.risk_prompt_builder import (
    WHITELISTED_FREDDIE_MAC_FIELDS,
    authoritative_mortgage_status_label,
    build_freddie_mac_risk_prompt,
    months_between_dates,
    reporting_quarter_end_date,
)


def sample_observation() -> dict:
    return {
        "id": "obs-1",
        "loan_id": "loan-123",
        "reporting_quarter": "y25q1",
        "mortgage_status_code": 200,
        "ending_balance": Decimal("1000000.50"),
        "original_balance": Decimal("1200000"),
        "original_ltv": Decimal("0.72"),
        "original_dcr": Decimal("1.25"),
        "note_rate": Decimal("0.055"),
        "fund_date": "2020-01-15",
        "maturity_date": "2030-01-15",
        "property_state": "VA",
        "property_metro": "Washington-Arlington-Alexandria",
        "residential_units": 100,
        "deal_name": "REAL-DEAL",
        "securitized": "Y",
        "lien_number": "First Mortgage",
        "senior_housing_code": None,
        "credit_loss": None,
        "raw_row_payload": {"SUPABASE_SERVICE_ROLE_KEY": "should-not-appear"},
        "SUPABASE_SERVICE_ROLE_KEY": "should-not-appear",
        "GEMINI_API_KEY": "should-not-appear",
    }


def test_prompt_includes_real_data_provenance_and_limitations() -> None:
    prompt, snapshot = build_freddie_mac_risk_prompt(sample_observation())

    assert FREDDIE_MAC_MLPD_SOURCE_NAME in prompt
    assert "one loan-quarter observation" in prompt
    assert "not a complete loan history" in prompt
    assert "not a property appraisal" in prompt
    assert "No join to HUD property data is assumed" in prompt
    assert "Do not invent missing facts" in prompt
    assert snapshot["mortgage_status_label"] == "60 or more days delinquent"


def test_prompt_makes_mortgage_status_label_authoritative() -> None:
    observation = sample_observation()
    observation["mortgage_status_code"] = 100

    prompt, snapshot = build_freddie_mac_risk_prompt(observation)

    assert snapshot["mortgage_status_code"] == 100
    assert snapshot["mortgage_status_label"] == "current or less than 60 days delinquent"
    assert '"mortgage_status_code": 100' in prompt
    assert '"mortgage_status_label": "current or less than 60 days delinquent"' in prompt
    assert "Mortgage status:" in prompt
    assert "- code: 100" in prompt
    assert "- authoritative label: current or less than 60 days delinquent" in prompt
    assert "You must use the authoritative label above" in prompt
    assert "Do not contradict or weaken this known mortgage status" in prompt
    assert "unknown" not in prompt.lower()


def test_reporting_quarter_end_date_uses_sql_century_logic() -> None:
    assert reporting_quarter_end_date("y01q2") == date(2001, 6, 30)
    assert reporting_quarter_end_date("y19q3") == date(2019, 9, 30)
    assert reporting_quarter_end_date("y50q1") == date(1950, 3, 31)


def test_prompt_includes_deterministic_maturity_timing_for_not_near_maturity() -> None:
    observation = sample_observation()
    observation["reporting_quarter"] = "y01q2"
    observation["maturity_date"] = "2009-10-01"

    prompt, snapshot = build_freddie_mac_risk_prompt(observation)

    assert months_between_dates(date(2001, 6, 30), date(2009, 10, 1)) == 99
    assert snapshot["reporting_year"] == 2001
    assert snapshot["reporting_quarter_number"] == 2
    assert snapshot["reporting_quarter_end_date"] == "2001-06-30"
    assert snapshot["months_to_maturity"] == 99
    assert snapshot["maturity_risk_label"] == "not_near_maturity"
    assert "Maturity timing:" in prompt
    assert "- reporting quarter end date: 2001-06-30" in prompt
    assert "- maturity date: 2009-10-01" in prompt
    assert "- months to maturity: approximately 99" in prompt
    assert "- maturity risk label: not_near_maturity" in prompt
    assert "Do not describe the loan as near maturity unless" in prompt


def test_authoritative_mortgage_status_label_mapping_is_human_readable() -> None:
    assert authoritative_mortgage_status_label(100) == "current or less than 60 days delinquent"
    assert authoritative_mortgage_status_label("200") == "60 or more days delinquent"
    assert authoritative_mortgage_status_label(250) == "modification with loss"
    assert authoritative_mortgage_status_label(300) == "foreclosure"
    assert authoritative_mortgage_status_label(450) == "real estate owned"
    assert authoritative_mortgage_status_label(500) == "closed"
    assert authoritative_mortgage_status_label(999) is None


def test_prompt_excludes_secrets_env_vars_and_raw_payload() -> None:
    prompt, snapshot = build_freddie_mac_risk_prompt(sample_observation())

    forbidden_terms = [
        "SUPABASE_SERVICE_ROLE_KEY",
        "GEMINI_API_KEY",
        "should-not-appear",
        "raw_row_payload",
        "JWT",
    ]
    for term in forbidden_terms:
        assert term not in prompt
        assert term not in str(snapshot)


def test_prompt_snapshot_uses_only_whitelisted_fields() -> None:
    _, snapshot = build_freddie_mac_risk_prompt(sample_observation())

    assert set(snapshot) == set(WHITELISTED_FREDDIE_MAC_FIELDS)
    assert "id" not in snapshot
    assert "raw_row_payload" not in snapshot


def test_prompt_does_not_use_synthetic_data_language() -> None:
    prompt, _ = build_freddie_mac_risk_prompt(sample_observation())
    disallowed = ["synthetic data", "simulated data", "fake data", "fabricated data"]

    for phrase in disallowed:
        assert phrase not in prompt.lower()
