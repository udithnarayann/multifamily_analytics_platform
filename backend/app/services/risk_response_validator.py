import json
import re

from pydantic import ValidationError

from app.core.errors import AIServiceError
from app.schemas.risk_report import GeminiRiskReportOutput
from app.services.risk_prompt_builder import authoritative_mortgage_status_label

CONTRADICTORY_UNKNOWN_STATUS_PHRASES = (
    "status unknown",
    "label is unknown",
    "unknown status",
    "provided label is unknown",
)

FALSE_NEAR_MATURITY_PHRASES = (
    "near maturity",
    "nearing maturity",
    "approaching maturity",
    "shortly before maturity",
    "within 24 months",
    "imminent refinancing risk",
    "proximity to maturity",
)


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else stripped


def _output_text(output: GeminiRiskReportOutput) -> str:
    return "\n".join(
        [
            output.summary,
            *output.key_risk_factors,
            output.loan_performance_analysis,
            output.credit_metric_analysis,
            output.delinquency_analysis,
            *output.analyst_follow_up_questions,
        ]
    ).lower()


def _reject_contradictory_known_status_output(
    output: GeminiRiskReportOutput, input_snapshot: dict | None
) -> None:
    if not input_snapshot:
        return
    status_code = input_snapshot.get("mortgage_status_code")
    if authoritative_mortgage_status_label(status_code) is None:
        return
    text = _output_text(output)
    matched_phrase = next(
        (phrase for phrase in CONTRADICTORY_UNKNOWN_STATUS_PHRASES if phrase in text), None
    )
    if matched_phrase:
        raise AIServiceError(
            "Gemini risk response contradicted a known mortgage status label "
            f"with phrase: {matched_phrase}"
        )


def _reject_false_near_maturity_output(
    output: GeminiRiskReportOutput, input_snapshot: dict | None
) -> None:
    if not input_snapshot or input_snapshot.get("maturity_risk_label") != "not_near_maturity":
        return
    text = _output_text(output)
    matched_phrase = next(
        (phrase for phrase in FALSE_NEAR_MATURITY_PHRASES if phrase in text), None
    )
    if matched_phrase:
        raise AIServiceError(
            "Gemini risk response contradicted deterministic maturity timing "
            f"with phrase: {matched_phrase}"
        )


def validate_gemini_risk_response(
    response_text: str, input_snapshot: dict | None = None
) -> GeminiRiskReportOutput:
    try:
        payload = json.loads(_strip_code_fences(response_text))
    except json.JSONDecodeError as exc:
        raise AIServiceError("Gemini risk response was not valid JSON") from exc

    try:
        output = GeminiRiskReportOutput.model_validate(payload)
    except ValidationError as exc:
        raise AIServiceError("Gemini risk response did not match required schema") from exc

    _reject_contradictory_known_status_output(output, input_snapshot)
    _reject_false_near_maturity_output(output, input_snapshot)
    return output
