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

    def get_by_id(self, observation_id: str) -> dict | None:
        response = (
            self.supabase.table("freddie_mac_loan_quarter_observations")
            .select("*")
            .eq("id", observation_id)
            .limit(1)
            .execute()
        )
        data = response.data or []
        return data[0] if data else None

    def get_sample_observations(self, limit: int = 5) -> list[dict]:
        safe_columns = ",".join(
            [
                "id",
                "loan_id",
                "reporting_quarter",
                "mortgage_status_code",
                "ending_balance",
                "original_ltv",
                "original_dcr",
                "note_rate",
                "property_state",
                "property_metro",
                "residential_units",
            ]
        )
        response = (
            self.supabase.table("freddie_mac_loan_quarter_observations")
            .select(safe_columns)
            .not_.is_("original_ltv", "null")
            .not_.is_("original_dcr", "null")
            .not_.is_("note_rate", "null")
            .not_.is_("mortgage_status_code", "null")
            .not_.is_("property_state", "null")
            .not_.is_("property_metro", "null")
            .limit(limit)
            .execute()
        )
        return response.data or []
