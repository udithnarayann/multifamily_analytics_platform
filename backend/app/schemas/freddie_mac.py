from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator


class FreddieMacLoanQuarterObservationUpsert(BaseModel):
    """Real Freddie Mac MLPD loan-quarter observation payload."""

    loan_id: str
    reporting_quarter: str
    mortgage_status_code: int | None = None
    ending_balance: Decimal | None = None
    liquidation_date: date | None = None
    liquidation_balance: Decimal | None = None
    date_sold: date | None = None
    fixed_to_float_code: str | None = None
    amortization_term_months: int | None = None
    balloon_term_months: int | None = None
    interest_only_period_months: int | None = None
    interest_only_end_date: date | None = None
    mortgage_term_months: int | None = None
    yield_maintenance_months: int | None = None
    rate_type: str | None = None
    original_dcr: Decimal | None = None
    note_rate: Decimal | None = None
    original_ltv: Decimal | None = None
    original_balance: Decimal | None = None
    fund_date: date | None = None
    maturity_date: date | None = None
    residential_units: int | None = None
    property_state: str | None = Field(default=None, max_length=2)
    property_metro: str | None = None
    link_id_indicator: int | None = None
    lien_number: str | None = None
    senior_housing_code: str | None = None
    deal_name: str | None = None
    securitized: str | None = None
    defeasance_flag: str | None = None
    reo_operating_expense_income: Decimal | None = None
    pre_foreclosure_expense_income: Decimal | None = None
    selling_expense_income: Decimal | None = None
    sales_price: Decimal | None = None
    credit_loss: Decimal | None = None
    source_file: str
    raw_row_payload: dict[str, Any]

    @field_validator("loan_id", "reporting_quarter")
    @classmethod
    def required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("required Freddie Mac observation identifier is blank")
        return value

    @field_validator("property_state")
    @classmethod
    def normalize_state(cls, value: str | None) -> str | None:
        return value.strip().upper()[:2] if value else None


class FreddieMacObservationSample(BaseModel):
    id: str
    loan_id: str
    reporting_quarter: str
    mortgage_status_code: int | None = None
    mortgage_status_label: str | None = None
    ending_balance: float | None = None
    original_ltv: float | None = None
    original_dcr: float | None = None
    note_rate: float | None = None
    property_state: str | None = None
    property_metro: str | None = None
    residential_units: int | None = None


class FreddieMacObservationSampleResponse(BaseModel):
    source_label: str = "Freddie Mac Multifamily Loan Performance Database"
    observations: list[FreddieMacObservationSample]
