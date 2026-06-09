import json

import pytest

from app.core.errors import AIServiceError
from app.services.risk_response_validator import validate_gemini_risk_response


def valid_payload() -> dict:
    return {
        "risk_rating": "elevated",
        "risk_score": 72,
        "summary": "The record shows elevated risk based on delinquency status.",
        "key_risk_factors": ["60 or more days delinquent"],
        "loan_performance_analysis": "The status code indicates payment stress.",
        "credit_metric_analysis": "Original LTV and DCR require follow-up context.",
        "delinquency_analysis": "The delinquency code is a key limitation and risk signal.",
        "analyst_follow_up_questions": ["Has the loan cured in later quarters?"],
    }


def test_validator_accepts_valid_json() -> None:
    output = validate_gemini_risk_response(json.dumps(valid_payload()))

    assert output.risk_rating == "elevated"
    assert output.risk_score == 72


def test_validator_rejects_malformed_json() -> None:
    with pytest.raises(AIServiceError, match="not valid JSON"):
        validate_gemini_risk_response("not json")


def test_validator_rejects_invalid_risk_rating() -> None:
    payload = valid_payload()
    payload["risk_rating"] = "severe"

    with pytest.raises(AIServiceError, match="required schema"):
        validate_gemini_risk_response(json.dumps(payload))


def test_validator_rejects_risk_score_outside_range() -> None:
    payload = valid_payload()
    payload["risk_score"] = 101

    with pytest.raises(AIServiceError, match="required schema"):
        validate_gemini_risk_response(json.dumps(payload))


def test_validator_accepts_json_inside_code_fence() -> None:
    output = validate_gemini_risk_response(f"```json\n{json.dumps(valid_payload())}\n```")

    assert output.risk_rating == "elevated"


def test_validator_rejects_unknown_status_contradiction_for_known_status_code() -> None:
    payload = valid_payload()
    payload["delinquency_analysis"] = (
        "Per instructions, this is evaluated as current, though the provided label is unknown."
    )

    with pytest.raises(AIServiceError, match="contradicted a known mortgage status label"):
        validate_gemini_risk_response(
            json.dumps(payload),
            input_snapshot={
                "mortgage_status_code": 100,
                "mortgage_status_label": "current or less than 60 days delinquent",
            },
        )


def test_validator_allows_unknown_status_language_when_status_code_is_unknown() -> None:
    payload = valid_payload()
    payload["delinquency_analysis"] = "The unknown status requires follow-up."

    output = validate_gemini_risk_response(
        json.dumps(payload),
        input_snapshot={"mortgage_status_code": 999, "mortgage_status_label": None},
    )

    assert output.delinquency_analysis == "The unknown status requires follow-up."


def test_validator_rejects_near_maturity_language_when_not_near_maturity() -> None:
    payload = valid_payload()
    payload["key_risk_factors"] = ["Loan maturity is within 24 months of the reporting quarter"]
    payload["loan_performance_analysis"] = (
        "The proximity to maturity presents a refinancing risk."
    )

    with pytest.raises(AIServiceError, match="contradicted deterministic maturity timing"):
        validate_gemini_risk_response(
            json.dumps(payload),
            input_snapshot={
                "reporting_quarter_end_date": "2001-06-30",
                "maturity_date": "2009-10-01",
                "months_to_maturity": 99,
                "maturity_risk_label": "not_near_maturity",
            },
        )


def test_validator_allows_near_maturity_language_when_near_maturity() -> None:
    payload = valid_payload()
    payload["key_risk_factors"] = ["Loan maturity is within 24 months of the reporting quarter"]

    output = validate_gemini_risk_response(
        json.dumps(payload),
        input_snapshot={
            "reporting_quarter_end_date": "2008-12-31",
            "maturity_date": "2009-10-01",
            "months_to_maturity": 9,
            "maturity_risk_label": "near_maturity",
        },
    )

    assert output.key_risk_factors == ["Loan maturity is within 24 months of the reporting quarter"]
