import csv
import logging
from pathlib import Path

from app.db.repositories.freddie_mac_observations import FreddieMacObservationsRepository
from app.db.repositories.ingestion_runs import IngestionRunsRepository
from app.schemas.common import utc_now
from app.schemas.freddie_mac import FreddieMacLoanQuarterObservationUpsert
from app.schemas.ingestion import (
    FreddieMacMlpdIngestionRequest,
    FreddieMacMlpdIngestionResponse,
    IngestionRunCreate,
    IngestionRunUpdate,
)
from app.services.freddie_mac_mlp_mapper import (
    FREDDIE_MAC_MLPD_SOURCE_NAME,
    map_mlp_csv_row_to_observation,
)

logger = logging.getLogger(__name__)

EXPECTED_MLPD_FILES = (
    "mlpd_y1994q1_y2021q4.csv",
    "mlpd_y2022q1_y2025q3.csv",
)


class FreddieMacMlpdIngestionService:
    def __init__(
        self,
        *,
        data_dir: Path,
        observations_repository: FreddieMacObservationsRepository,
        ingestion_runs_repository: IngestionRunsRepository,
    ) -> None:
        self.data_dir = data_dir
        self.observations_repository = observations_repository
        self.ingestion_runs_repository = ingestion_runs_repository

    def ingest(self, request: FreddieMacMlpdIngestionRequest) -> FreddieMacMlpdIngestionResponse:
        resolved_data_dir = self.data_dir.resolve()
        source_files = self._available_source_files(resolved_data_dir)
        run_id = self.ingestion_runs_repository.create(
            IngestionRunCreate(
                source_name=FREDDIE_MAC_MLPD_SOURCE_NAME,
                source_url=str(resolved_data_dir),
                records_requested=request.limit,
                metadata={
                    "batch_size": request.batch_size,
                    "source_files": [path.name for path in source_files],
                },
            )
        )

        records_read = 0
        records_mapped = 0
        records_upserted = 0
        records_failed = 0
        errors: list[str] = []
        batch: list[FreddieMacLoanQuarterObservationUpsert] = []

        try:
            for source_file in source_files:
                with source_file.open("r", newline="", encoding="utf-8-sig") as csv_file:
                    reader = csv.DictReader(csv_file)
                    for row_number, row in enumerate(reader, start=2):
                        if records_read >= request.limit:
                            break
                        records_read += 1
                        try:
                            batch.append(
                                map_mlp_csv_row_to_observation(row, source_file=source_file.name)
                            )
                            records_mapped += 1
                        except Exception as exc:  # noqa: BLE001 - row-level CSV data tolerance
                            records_failed += 1
                            message = f"{source_file.name}:{row_number}: {exc}"
                            logger.warning("Freddie Mac MLPD row mapping failed: %s", message)
                            errors.append(message)

                        if len(batch) >= request.batch_size:
                            records_upserted += self._flush_batch(batch)
                if records_read >= request.limit:
                    break

            records_upserted += self._flush_batch(batch)
            status = "completed" if records_failed == 0 else "partial"
            self.ingestion_runs_repository.update(
                run_id,
                IngestionRunUpdate(
                    completed_at=utc_now(),
                    status=status,
                    records_requested=request.limit,
                    records_upserted=records_upserted,
                    records_failed=records_failed,
                    error_summary="; ".join(errors[:5]) if errors else None,
                    metadata={"records_read": records_read, "records_mapped": records_mapped},
                ),
            )
            return FreddieMacMlpdIngestionResponse(
                ingestion_run_id=run_id,
                source_name=FREDDIE_MAC_MLPD_SOURCE_NAME,
                data_dir=str(resolved_data_dir),
                source_files=[path.name for path in source_files],
                records_requested=request.limit,
                records_read=records_read,
                records_mapped=records_mapped,
                records_upserted=records_upserted,
                records_failed=records_failed,
                status=status,
                errors=errors,
            )
        except Exception as exc:
            logger.exception("Freddie Mac MLPD ingestion failed")
            self.ingestion_runs_repository.update(
                run_id,
                IngestionRunUpdate(
                    completed_at=utc_now(),
                    status="failed",
                    records_requested=request.limit,
                    records_upserted=records_upserted,
                    records_failed=max(records_read - records_mapped, 0),
                    error_summary=str(exc),
                    metadata={"records_read": records_read, "records_mapped": records_mapped},
                ),
            )
            raise

    def _available_source_files(self, data_dir: Path) -> list[Path]:
        if not data_dir.exists():
            raise FileNotFoundError(f"Freddie Mac MLPD data directory not found: {data_dir}")
        source_files = [data_dir / file_name for file_name in EXPECTED_MLPD_FILES]
        found_files = [path for path in source_files if path.exists()]
        if not found_files:
            raise FileNotFoundError(f"No expected Freddie Mac MLPD CSV files found in {data_dir}")
        return found_files

    def _flush_batch(self, batch: list[FreddieMacLoanQuarterObservationUpsert]) -> int:
        if not batch:
            return 0
        upserted = self.observations_repository.upsert_many(batch)
        batch.clear()
        return upserted
