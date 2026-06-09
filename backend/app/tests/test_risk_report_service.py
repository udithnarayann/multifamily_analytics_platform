import json
from datetime import datetime
from decimal import Decimal

from app.services.gemini_client import GeminiTextResponse
from app.services.risk_prompt_builder import PROMPT_VERSION_FREDDIE_MAC_RISK
from app.services.risk_report_service import RiskReportService


class FakeObservationsRepository:
    def get_by_id(self, observation_id: str):
        return {
            "id": observation_id,
            "loan_id": "loan-123",
            "reporting_quarter": "y25q1",
            "mortgage_status_code": 100,
            "ending_balance": Decimal("900000"),
            "original_balance": Decimal("1000000"),
            "original_ltv": Decimal("0.7"),
            "original_dcr": Decimal("1.3"),
            "note_rate": Decimal("0.05"),
            "property_state": "VA",
            "property_metro": "Richmond, VA",
            "residential_units": 80,
        }


class FakeGeminiClient:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate_json(self, prompt: str) -> GeminiTextResponse:
        self.prompts.append(prompt)
        return GeminiTextResponse(
            text=json.dumps(
                {
                    "risk_rating": "low",
                    "risk_score": 20,
                    "summary": "Current status and moderate leverage indicate lower observed risk.",
                    "key_risk_factors": ["Single quarter view limits trend analysis"],
                    "loan_performance_analysis": (
                        "The loan is current or less than 60 days delinquent."
                    ),
                    "credit_metric_analysis": (
                        "Original LTV and DCR appear within a reasonable range."
                    ),
                    "delinquency_analysis": (
                        "No severe delinquency is indicated by this status code."
                    ),
                    "analyst_follow_up_questions": ["Review later quarters for trend changes."],
                }
            ),
            model_name="gemini-3.5-flash",
        )


class FakeRiskReportsRepository:
    def __init__(self) -> None:
        self.saved = None

    def insert(self, report):
        self.saved = report
        output = report.output
        return {
            "id": "report-1",
            "freddie_mac_observation_id": report.freddie_mac_observation_id,
            "hud_property_id": None,
            "risk_rating": output.risk_rating,
            "risk_score": output.risk_score,
            "summary": output.summary,
            "key_risk_factors": output.key_risk_factors,
            "loan_performance_analysis": output.loan_performance_analysis,
            "credit_metric_analysis": output.credit_metric_analysis,
            "property_analysis": report.property_analysis,
            "delinquency_analysis": output.delinquency_analysis,
            "analyst_follow_up_questions": output.analyst_follow_up_questions,
            "model_name": report.model_name,
            "model_version": report.model_version,
            "prompt_version": report.prompt_version,
            "input_snapshot": report.input_snapshot,
            "output_snapshot": report.output_snapshot,
            "data_source_labels": report.data_source_labels,
            "created_by": report.created_by,
            "created_at": datetime.now().isoformat(),
        }

    def get_latest_for_freddie_mac_observation(self, observation_id: str):
        return None


def test_service_persists_mocked_gemini_response() -> None:
    risk_reports_repository = FakeRiskReportsRepository()
    gemini_client = FakeGeminiClient()
    service = RiskReportService(
        observations_repository=FakeObservationsRepository(),
        risk_reports_repository=risk_reports_repository,
        gemini_client=gemini_client,
    )

    response = service.create_freddie_mac_report("00000000-0000-0000-0000-000000000001")

    assert response.id == "report-1"
    assert response.risk_rating == "low"
    assert response.model_name == "gemini-3.5-flash"
    assert response.prompt_version == PROMPT_VERSION_FREDDIE_MAC_RISK
    assert response.freddie_mac_observation_id == "00000000-0000-0000-0000-000000000001"
    assert response.hud_property_id is None
    assert response.created_by is None
    assert response.data_source_labels == ["Freddie Mac Multifamily Loan Performance Database"]
    assert risk_reports_repository.saved is not None
    assert risk_reports_repository.saved.property_analysis is None
    assert gemini_client.prompts
