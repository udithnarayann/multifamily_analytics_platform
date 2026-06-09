from postgrest.exceptions import APIError

from app.core.errors import PersistenceError
from app.schemas.risk_report import RiskReportCreate


class RiskReportsRepository:
    def __init__(self, supabase_client) -> None:
        self.supabase = supabase_client

    def insert(self, report: RiskReportCreate) -> dict:
        output = report.output
        payload = {
            "freddie_mac_observation_id": report.freddie_mac_observation_id,
            "hud_property_id": report.hud_property_id,
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
        }
        try:
            response = self.supabase.table("ai_risk_reports").insert(payload).execute()
        except APIError as exc:
            raise PersistenceError(f"ai_risk_reports insert failed: {exc}") from exc
        data = response.data or []
        if not data:
            raise PersistenceError("ai_risk_reports insert returned no data")
        return data[0]

    def get_latest_for_freddie_mac_observation(self, observation_id: str) -> dict | None:
        response = (
            self.supabase.table("ai_risk_reports")
            .select("*")
            .eq("freddie_mac_observation_id", observation_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        data = response.data or []
        return data[0] if data else None
