from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

RiskRating = Literal["low", "moderate", "elevated", "high", "critical"]


class GeminiRiskReportOutput(BaseModel):
    risk_rating: RiskRating
    risk_score: float = Field(ge=0, le=100)
    summary: str
    key_risk_factors: list[str] = Field(default_factory=list)
    loan_performance_analysis: str
    credit_metric_analysis: str
    delinquency_analysis: str
    analyst_follow_up_questions: list[str] = Field(default_factory=list)

    @field_validator(
        "summary",
        "loan_performance_analysis",
        "credit_metric_analysis",
        "delinquency_analysis",
    )
    @classmethod
    def required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("risk report text fields cannot be blank")
        return value


class RiskReportCreate(BaseModel):
    freddie_mac_observation_id: str
    hud_property_id: str | None = None
    model_name: str
    model_version: str | None = None
    prompt_version: str
    input_snapshot: dict
    output_snapshot: dict
    data_source_labels: list[str]
    created_by: str | None = None
    property_analysis: str | None = None
    output: GeminiRiskReportOutput


class RiskReportResponse(BaseModel):
    id: str
    freddie_mac_observation_id: str | None = None
    hud_property_id: str | None = None
    risk_rating: RiskRating
    risk_score: float
    summary: str
    key_risk_factors: list[str] = Field(default_factory=list)
    loan_performance_analysis: str
    credit_metric_analysis: str
    property_analysis: str | None = None
    delinquency_analysis: str
    analyst_follow_up_questions: list[str] = Field(default_factory=list)
    model_name: str
    model_version: str | None = None
    prompt_version: str
    input_snapshot: dict
    output_snapshot: dict
    data_source_labels: list[str] = Field(default_factory=list)
    created_by: str | None = None
    created_at: datetime | None = None
