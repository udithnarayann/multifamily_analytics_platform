from app.core.errors import NotFoundError
from app.db.repositories.freddie_mac_observations import FreddieMacObservationsRepository
from app.db.repositories.risk_reports import RiskReportsRepository
from app.schemas.risk_report import RiskReportCreate, RiskReportResponse
from app.services.freddie_mac_mlp_mapper import FREDDIE_MAC_MLPD_SOURCE_NAME
from app.services.gemini_client import GeminiClient
from app.services.risk_prompt_builder import (
    PROMPT_VERSION_FREDDIE_MAC_RISK,
    build_freddie_mac_risk_prompt,
)
from app.services.risk_response_validator import validate_gemini_risk_response


class RiskReportService:
    def __init__(
        self,
        *,
        observations_repository: FreddieMacObservationsRepository,
        risk_reports_repository: RiskReportsRepository,
        gemini_client: GeminiClient,
    ) -> None:
        self.observations_repository = observations_repository
        self.risk_reports_repository = risk_reports_repository
        self.gemini_client = gemini_client

    def create_freddie_mac_report(self, observation_id: str) -> RiskReportResponse:
        observation = self.observations_repository.get_by_id(observation_id)
        if not observation:
            raise NotFoundError("Freddie Mac MLPD observation was not found")

        prompt, input_snapshot = build_freddie_mac_risk_prompt(observation)
        gemini_response = self.gemini_client.generate_json(prompt)
        output = validate_gemini_risk_response(gemini_response.text, input_snapshot=input_snapshot)

        report = RiskReportCreate(
            freddie_mac_observation_id=observation_id,
            hud_property_id=None,
            model_name=gemini_response.model_name,
            model_version=gemini_response.model_version,
            prompt_version=PROMPT_VERSION_FREDDIE_MAC_RISK,
            input_snapshot=input_snapshot,
            output_snapshot=output.model_dump(mode="json"),
            data_source_labels=[FREDDIE_MAC_MLPD_SOURCE_NAME],
            created_by=None,
            property_analysis=None,
            output=output,
        )
        saved = self.risk_reports_repository.insert(report)
        return RiskReportResponse.model_validate(saved)

    def get_latest_freddie_mac_report(self, observation_id: str) -> RiskReportResponse:
        report = self.risk_reports_repository.get_latest_for_freddie_mac_observation(observation_id)
        if not report:
            raise NotFoundError("No AI risk report exists for this Freddie Mac MLPD observation")
        return RiskReportResponse.model_validate(report)
