from typing import Any


class AnalyticsRepository:
    def __init__(self, supabase_client) -> None:
        self.supabase = supabase_client

    def _rpc_json(self, function_name: str, params: dict[str, Any] | None = None) -> Any:
        response = self.supabase.rpc(function_name, params or {}).execute()
        return response.data

    def get_hud_property_summary(self) -> dict[str, Any]:
        return self._rpc_json("get_hud_property_summary") or {}

    def get_freddie_mac_mlpd_summary(self) -> dict[str, Any]:
        return self._rpc_json("get_freddie_mac_mlpd_summary") or {}

    def get_freddie_mac_latest_quarter_summary(self) -> dict[str, Any]:
        return self._rpc_json("get_freddie_mac_latest_quarter_summary") or {}

    def get_recent_ingestion_runs(self, limit: int = 10) -> list[dict[str, Any]]:
        data = self._rpc_json("get_recent_ingestion_runs", {"p_limit": limit})
        return data or []
