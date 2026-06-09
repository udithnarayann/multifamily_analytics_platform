from app.schemas.freddie_mac import FreddieMacLoanQuarterObservationUpsert


class FreddieMacObservationsRepository:
    def __init__(self, supabase_client) -> None:
        self.supabase = supabase_client

    def upsert_many(self, observations: list[FreddieMacLoanQuarterObservationUpsert]) -> int:
        if not observations:
            return 0

        payload = [observation.model_dump(mode="json") for observation in observations]
        response = (
            self.supabase.table("freddie_mac_loan_quarter_observations")
            .upsert(payload, on_conflict="loan_id,reporting_quarter")
            .execute()
        )
        data = response.data or []
        return len(data) if isinstance(data, list) else len(observations)
