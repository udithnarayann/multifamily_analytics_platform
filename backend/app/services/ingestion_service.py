import logging

from app.db.repositories.ingestion_runs import IngestionRunsRepository
from app.db.repositories.properties import PropertiesRepository
from app.schemas.common import utc_now
from app.schemas.ingestion import (
    HudIngestionRequest,
    HudIngestionResponse,
    IngestionRunCreate,
    IngestionRunUpdate,
)
from app.schemas.property import PropertyUpsert
from app.services.hud_arcgis_client import HudArcgisClient
from app.services.property_mapper import HUD_SOURCE_NAME, map_hud_feature_to_property

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(
        self,
        *,
        hud_client: HudArcgisClient,
        properties_repository: PropertiesRepository,
        ingestion_runs_repository: IngestionRunsRepository,
        source_url: str,
    ) -> None:
        self.hud_client = hud_client
        self.properties_repository = properties_repository
        self.ingestion_runs_repository = ingestion_runs_repository
        self.source_url = source_url

    async def ingest_hud_properties(self, request: HudIngestionRequest) -> HudIngestionResponse:
        started_at = utc_now()
        run_id = self.ingestion_runs_repository.create(
            IngestionRunCreate(
                source_name=HUD_SOURCE_NAME,
                source_url=self.source_url,
                records_requested=request.limit,
                metadata={"page_size": request.page_size, "started_at": started_at.isoformat()},
            )
        )

        fetched = 0
        mapped: list[PropertyUpsert] = []
        errors: list[str] = []

        try:
            async for feature in self.hud_client.iter_features(
                limit=request.limit, page_size=request.page_size
            ):
                fetched += 1
                try:
                    mapped.append(
                        map_hud_feature_to_property(
                            feature,
                            source_url=self.source_url,
                            source_last_updated=started_at,
                        )
                    )
                except Exception as exc:  # noqa: BLE001 - capture per-record mapping failure
                    logger.warning("HUD property mapping failed", exc_info=exc)
                    errors.append(str(exc))

            upserted = self.properties_repository.upsert_many(mapped)
            failed = fetched - len(mapped)
            status = "completed" if failed == 0 else "partial"

            self.ingestion_runs_repository.update(
                run_id,
                IngestionRunUpdate(
                    completed_at=utc_now(),
                    status=status,
                    records_requested=request.limit,
                    records_upserted=upserted,
                    records_failed=failed,
                    error_summary="; ".join(errors[:5]) if errors else None,
                    metadata={"records_fetched": fetched, "records_mapped": len(mapped)},
                ),
            )

            return HudIngestionResponse(
                ingestion_run_id=run_id,
                source_name=HUD_SOURCE_NAME,
                records_requested=request.limit,
                records_fetched=fetched,
                records_mapped=len(mapped),
                records_upserted=upserted,
                records_failed=failed,
                status=status,
                errors=errors,
            )
        except Exception as exc:
            logger.exception("HUD ingestion failed")
            self.ingestion_runs_repository.update(
                run_id,
                IngestionRunUpdate(
                    completed_at=utc_now(),
                    status="failed",
                    records_requested=request.limit,
                    records_upserted=0,
                    records_failed=max(request.limit - len(mapped), 0),
                    error_summary=str(exc),
                    metadata={"records_fetched": fetched, "records_mapped": len(mapped)},
                ),
            )
            raise
