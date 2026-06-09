from app.core.config import Settings, get_settings
from app.db.repositories.analytics import AnalyticsRepository
from app.db.repositories.freddie_mac_observations import FreddieMacObservationsRepository
from app.db.repositories.ingestion_runs import IngestionRunsRepository
from app.db.repositories.properties import PropertiesRepository
from app.db.supabase import get_supabase_client
from app.services.analytics_service import AnalyticsService
from app.services.freddie_mac_mlp_ingestion_service import FreddieMacMlpdIngestionService
from app.services.hud_arcgis_client import HudArcgisClient
from app.services.ingestion_service import IngestionService


def get_ingestion_service() -> IngestionService:
    settings: Settings = get_settings()
    supabase = get_supabase_client()
    return IngestionService(
        hud_client=HudArcgisClient(
            base_url=str(settings.hud_arcgis_url),
            timeout_seconds=settings.hud_request_timeout_seconds,
        ),
        properties_repository=PropertiesRepository(supabase),
        ingestion_runs_repository=IngestionRunsRepository(supabase),
        source_url=str(settings.hud_arcgis_url),
    )


def get_freddie_mac_mlpd_ingestion_service() -> FreddieMacMlpdIngestionService:
    settings: Settings = get_settings()
    supabase = get_supabase_client()
    return FreddieMacMlpdIngestionService(
        data_dir=settings.freddie_mac_mlpd_data_dir,
        observations_repository=FreddieMacObservationsRepository(supabase),
        ingestion_runs_repository=IngestionRunsRepository(supabase),
    )


def get_analytics_service() -> AnalyticsService:
    return AnalyticsService(AnalyticsRepository(get_supabase_client()))
