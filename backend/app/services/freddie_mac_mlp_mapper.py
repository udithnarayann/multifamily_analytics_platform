from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from app.schemas.freddie_mac import FreddieMacLoanQuarterObservationUpsert

FREDDIE_MAC_MLPD_SOURCE_NAME = "Freddie Mac Multifamily Loan Performance Database"

MORTGAGE_STATUS_LABELS: dict[int, str] = {
    100: "current_or_less_than_60_days_delinquent",
    200: "60_or_more_days_delinquent",
    250: "modification_with_loss",
    300: "foreclosure",
    450: "real_estate_owned",
    500: "closed",
}

NULL_STRINGS = {"", ".", "NA", "N/A", "NULL", "NONE", "nan", "NaN"}
DATE_FORMATS = ("%Y-%m-%d", "%d%b%Y", "%d-%b-%Y", "%d%b%y")


def parse_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text in NULL_STRINGS:
        return None
    return text


def parse_optional_decimal(value: Any) -> Decimal | None:
    text = parse_optional_text(value)
    if text is None:
        return None
    try:
        return Decimal(text.replace(",", ""))
    except (InvalidOperation, ValueError):
        return None


def parse_optional_int(value: Any) -> int | None:
    decimal_value = parse_optional_decimal(value)
    if decimal_value is None:
        return None
    return int(decimal_value)


def parse_optional_date(value: Any) -> date | None:
    text = parse_optional_text(value)
    if text is None:
        return None

    upper_text = text.upper()
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(upper_text, date_format).date()
        except ValueError:
            continue
    return None


def normalize_mortgage_status_code(value: Any) -> int | None:
    return parse_optional_int(value)


def label_mortgage_status(value: Any) -> str | None:
    status_code = normalize_mortgage_status_code(value)
    if status_code is None:
        return None
    return MORTGAGE_STATUS_LABELS.get(status_code, "unknown")


def _clean_raw_row(row: dict[str, Any]) -> dict[str, Any]:
    """Preserve source row while dropping the leading unnamed CSV index column."""

    return {key: value for key, value in row.items() if key not in (None, "")}


def map_mlp_csv_row_to_observation(
    row: dict[str, Any], *, source_file: str | Path
) -> FreddieMacLoanQuarterObservationUpsert:
    raw_row_payload = _clean_raw_row(row)

    return FreddieMacLoanQuarterObservationUpsert(
        loan_id=parse_optional_text(row.get("lnno")) or "",
        reporting_quarter=parse_optional_text(row.get("quarter")) or "",
        mortgage_status_code=normalize_mortgage_status_code(row.get("mrtg_status")),
        ending_balance=parse_optional_decimal(row.get("amt_upb_endg")),
        liquidation_date=parse_optional_date(row.get("liq_dte")),
        liquidation_balance=parse_optional_decimal(row.get("liq_upb_amt")),
        date_sold=parse_optional_date(row.get("dt_sold")),
        fixed_to_float_code=parse_optional_text(row.get("cd_fxfltr")),
        amortization_term_months=parse_optional_int(row.get("cnt_amtn_per")),
        balloon_term_months=parse_optional_int(row.get("cnt_blln_term")),
        interest_only_period_months=parse_optional_int(row.get("cnt_io_per")),
        interest_only_end_date=parse_optional_date(row.get("dt_io_end")),
        mortgage_term_months=parse_optional_int(row.get("cnt_mrtg_term")),
        yield_maintenance_months=parse_optional_int(row.get("cnt_yld_maint")),
        rate_type=parse_optional_text(row.get("code_int")),
        original_dcr=parse_optional_decimal(row.get("rate_dcr")),
        note_rate=parse_optional_decimal(row.get("rate_int")),
        original_ltv=parse_optional_decimal(row.get("rate_ltv")),
        original_balance=parse_optional_decimal(row.get("amt_upb_pch")),
        fund_date=parse_optional_date(row.get("dt_fund")),
        maturity_date=parse_optional_date(row.get("dt_mty")),
        residential_units=parse_optional_int(row.get("cnt_rsdntl_unit")),
        property_state=parse_optional_text(row.get("code_st")),
        property_metro=parse_optional_text(row.get("geographical_region")),
        link_id_indicator=parse_optional_int(row.get("id_link_grp")),
        lien_number=parse_optional_text(row.get("lien_number")),
        senior_housing_code=parse_optional_text(row.get("code_sr")),
        deal_name=parse_optional_text(row.get("dealname")),
        securitized=parse_optional_text(row.get("securitized")),
        defeasance_flag=parse_optional_text(row.get("flag_defeased")),
        reo_operating_expense_income=parse_optional_decimal(row.get("REO_Operating_ExpInc")),
        pre_foreclosure_expense_income=parse_optional_decimal(row.get("PreFcl_FCL_ExpInc")),
        selling_expense_income=parse_optional_decimal(row.get("Selling_ExpInc")),
        sales_price=parse_optional_decimal(row.get("Sales_Price")),
        credit_loss=parse_optional_decimal(row.get("credit_loss")),
        source_file=Path(source_file).name,
        raw_row_payload=raw_row_payload,
    )
