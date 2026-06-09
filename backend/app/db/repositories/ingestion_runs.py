from uuid import UUID

from app.schemas.ingestion import IngestionRunCreate, IngestionRunUpdate


class IngestionRunsRepository:
    def __init__(self, supabase_client) -> None:
        self.supabase = supabase_client

    def create(self, run: IngestionRunCreate) -> UUID | str | None:
        response = (
            self.supabase.table("ingestion_runs")
            .insert(run.model_dump(mode="json"))
            .execute()
        )
        data = response.data or []
        if not data:
            return None
        return data[0].get("id")

    def update(self, run_id: UUID | str | None, update: IngestionRunUpdate) -> None:
        if run_id is None:
            return
        payload = update.model_dump(mode="json", exclude_none=True)
        self.supabase.table("ingestion_runs").update(payload).eq("id", str(run_id)).execute()
