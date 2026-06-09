from functools import lru_cache
from pathlib import Path

from pydantic import Field, HttpUrl, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"), env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    api_title: str = Field(
        default="Real-Time Multifamily Property Analytics API", alias="API_TITLE"
    )
    api_version: str = Field(default="0.1.0", alias="API_VERSION")

    hud_arcgis_url: HttpUrl = Field(
        default=(
            "https://services.arcgis.com/VTyQ9soqVukalItT/arcgis/rest/services/"
            "Multifamily_Properties_Assisted/FeatureServer/0/query"
        ),
        alias="HUD_ARCGIS_URL",
    )
    hud_page_size: PositiveInt = Field(default=100, alias="HUD_PAGE_SIZE")
    hud_max_test_ingest_records: PositiveInt = Field(
        default=500, alias="HUD_MAX_TEST_INGEST_RECORDS"
    )
    hud_request_timeout_seconds: PositiveInt = Field(
        default=30, alias="HUD_REQUEST_TIMEOUT_SECONDS"
    )
    cors_allowed_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173", alias="CORS_ALLOWED_ORIGINS"
    )

    freddie_mac_mlpd_data_dir: Path = Field(
        default=Path("../data/raw/freddie_mac_mlp"), alias="FREDDIE_MAC_MLPD_DATA_DIR"
    )
    freddie_mac_mlpd_batch_size: PositiveInt = Field(
        default=500, alias="FREDDIE_MAC_MLPD_BATCH_SIZE"
    )
    freddie_mac_mlpd_max_test_ingest_records: PositiveInt = Field(
        default=5000, alias="FREDDIE_MAC_MLPD_MAX_TEST_INGEST_RECORDS"
    )

    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")

    gemini_model_primary: str = Field(default="gemini-3.5-flash", alias="GEMINI_MODEL_PRIMARY")
    gemini_model_fallback: str = Field(
        default="gemini-3.1-flash-lite", alias="GEMINI_MODEL_FALLBACK"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
