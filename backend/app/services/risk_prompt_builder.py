import json
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from app.services.freddie_mac_mlp_mapper import (
    FREDDIE_MAC_MLPD_SOURCE_NAME,
)

PROMPT_VERSION_FREDDIE_MAC_RISK = "freddie_mac_risk_v1"

AUTHORITATIVE_MORTGAGE_STATUS_LABELS: dict[int, str] = {
    100: "current or less than 60 days delinquent",
    200: "60 or more days delinquent",
    250: "modification with loss",
    300: "foreclosure",
    450: "real estate owned",
    500: "closed",
}

QUARTER_END_MONTH_DAY: dict[int, tuple[int, int]] = {
    1: (3, 31),
    2: (6, 30),
    3: (9, 30),
    4: (12, 31),
}

WHITELISTED_FREDDIE_MAC_FIELDS = (
    "loan_id",
    "reporting_quarter",
    "mortgage_status_code",
    "mortgage_status_label",
    "ending_balance",
    "original_balance",
    "original_ltv",
    "original_dcr",
    "note_rate",
    "fund_date",
    "maturity_date",
    "reporting_year",
    "reporting_quarter_number",
    "reporting_quarter_end_date",
    "months_to_maturity",
    "maturity_risk_label",
    "property_state",
    "property_metro",
    "residential_units",
    "deal_name",
    "securitized",
    "lien_number",
    "senior_housing_code",
    "credit_loss",
    "reo_operating_expense_income",
    "pre_foreclosure_expense_income",
    "selling_expense_income",
)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, date | datetime):
        return value.isoformat()
    return value


def _normalize_status_code(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def authoritative_mortgage_status_label(status_code: Any) -> str | None:
    normalized_code = _normalize_status_code(status_code)
    if normalized_code is None:
        return None
    return AUTHORITATIVE_MORTGAGE_STATUS_LABELS.get(normalized_code)


def reporting_quarter_end_date(reporting_quarter: Any) -> date | None:
    if reporting_quarter is None:
        return None
    match = re.fullmatch(r"y(\d{2})q([1-4])", str(reporting_quarter).strip(), flags=re.IGNORECASE)
    if not match:
        return None

    two_digit_year = int(match.group(1))
    full_year = 2000 + two_digit_year if two_digit_year <= 49 else 1900 + two_digit_year
    quarter = int(match.group(2))
    month, day = QUARTER_END_MONTH_DAY[quarter]
    return date(full_year, month, day)


def parse_iso_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def months_between_dates(start_date: date, end_date: date) -> int:
    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    if end_date.day < start_date.day:
        months -= 1
    return months


def maturity_risk_label(months_to_maturity: int | None) -> str:
    if months_to_maturity is None:
        return "unknown"
    if months_to_maturity < 0:
        return "matured_or_past_due"
    if months_to_maturity <= 24:
        return "near_maturity"
    return "not_near_maturity"


def build_maturity_timing_snapshot(observation: dict[str, Any]) -> dict[str, Any]:
    quarter_end = reporting_quarter_end_date(observation.get("reporting_quarter"))
    maturity = parse_iso_date(observation.get("maturity_date"))
    months_to_maturity = (
        months_between_dates(quarter_end, maturity) if quarter_end and maturity else None
    )
    quarter_number = None
    if quarter_end:
        quarter_number = next(
            quarter
            for quarter, (month, _) in QUARTER_END_MONTH_DAY.items()
            if month == quarter_end.month
        )

    return {
        "reporting_year": quarter_end.year if quarter_end else None,
        "reporting_quarter_number": quarter_number,
        "reporting_quarter_end_date": quarter_end.isoformat() if quarter_end else None,
        "months_to_maturity": months_to_maturity,
        "maturity_risk_label": maturity_risk_label(months_to_maturity),
    }


def build_freddie_mac_input_snapshot(observation: dict[str, Any]) -> dict[str, Any]:
    snapshot: dict[str, Any] = {}
    maturity_timing = build_maturity_timing_snapshot(observation)
    for field in WHITELISTED_FREDDIE_MAC_FIELDS:
        if field in maturity_timing:
            snapshot[field] = maturity_timing[field]
            continue
        if field == "mortgage_status_code":
            snapshot[field] = _normalize_status_code(observation.get(field))
            continue
        if field == "mortgage_status_label":
            snapshot[field] = authoritative_mortgage_status_label(
                observation.get("mortgage_status_code")
            )
            continue
        snapshot[field] = _json_safe(observation.get(field))
    return snapshot


def build_freddie_mac_risk_prompt(observation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    input_snapshot = build_freddie_mac_input_snapshot(observation)
    input_json = json.dumps(input_snapshot, indent=2, sort_keys=True)
    status_code = input_snapshot.get("mortgage_status_code")
    status_label = input_snapshot.get("mortgage_status_label")
    quarter_end_date = input_snapshot.get("reporting_quarter_end_date")
    maturity_date = input_snapshot.get("maturity_date")
    months_to_maturity = input_snapshot.get("months_to_maturity")
    maturity_label = input_snapshot.get("maturity_risk_label")
    months_to_maturity_text = (
        f"approximately {months_to_maturity}" if months_to_maturity is not None else "unknown"
    )
    status_section = (
        f"Mortgage status:\n- code: {status_code}\n- authoritative label: {status_label}\n\n"
        "You must use the authoritative label above. Do not contradict or weaken this known "
        "mortgage status."
        if status_code is not None and status_label
        else "Mortgage status:\n- code: not provided\n- authoritative label: not available"
    )
    maturity_section = f"""
Maturity timing:
- reporting quarter end date: {quarter_end_date or "not available"}
- maturity date: {maturity_date or "not available"}
- months to maturity: {months_to_maturity_text}
- maturity risk label: {maturity_label or "unknown"}

You must use the maturity timing above. Do not describe the loan as near maturity unless
maturity_risk_label is near_maturity or matured_or_past_due.
""".strip()

    prompt = f"""
You are a cautious commercial real estate credit analyst. Analyze only the real Freddie Mac
Multifamily Loan Performance Database loan-quarter observation provided below.

Important limitations and provenance:
- Data source: {FREDDIE_MAC_MLPD_SOURCE_NAME}.
- This is one loan-quarter observation, not a complete loan history.
- This is not a property appraisal.
- No join to HUD property data is assumed or available in this prompt.
- Do not invent missing facts, values, borrower details, property details, or market context.
- If a field is null or missing, explicitly account for that limitation instead of guessing.
- Do not describe any data as synthetic, simulated, fabricated, or assumed.
- Do not describe maturity as near unless it is within 24 months of the reporting quarter.

{status_section}

{maturity_section}

Whitelisted observation fields:
{input_json}

Return only valid JSON with exactly these keys:
{{
  "risk_rating": "low | moderate | elevated | high | critical",
  "risk_score": 0,
  "summary": "...",
  "key_risk_factors": ["..."],
  "loan_performance_analysis": "...",
  "credit_metric_analysis": "...",
  "delinquency_analysis": "...",
  "analyst_follow_up_questions": ["..."]
}}
""".strip()
    return prompt, input_snapshot
