from app.schemas.property import PropertyUpsert


class PropertiesRepository:
    def __init__(self, supabase_client) -> None:
        self.supabase = supabase_client

    def upsert_many(self, properties: list[PropertyUpsert]) -> int:
        if not properties:
            return 0

        payload = [property_.model_dump(mode="json") for property_ in properties]
        response = (
            self.supabase.table("properties")
            .upsert(payload, on_conflict="hud_property_id")
            .execute()
        )
        data = response.data or []
        return len(data) if isinstance(data, list) else len(properties)
