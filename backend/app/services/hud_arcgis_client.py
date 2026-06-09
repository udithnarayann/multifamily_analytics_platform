from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.errors import ExternalDataSourceError


class HudArcgisClient:
    """Async client for HUD Multifamily Properties - Assisted ArcGIS endpoint."""

    def __init__(self, base_url: str, timeout_seconds: int = 30) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    async def fetch_page(self, *, offset: int, page_size: int) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "f": "json",
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true",
            "resultOffset": offset,
            "resultRecordCount": page_size,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalDataSourceError(f"HUD ArcGIS request failed: {exc}") from exc

        payload = response.json()
        if "error" in payload:
            raise ExternalDataSourceError(f"HUD ArcGIS error payload: {payload['error']}")

        features = payload.get("features")
        if not isinstance(features, list):
            raise ExternalDataSourceError("HUD ArcGIS response did not include a feature list")
        return features

    async def iter_features(self, *, limit: int, page_size: int) -> AsyncIterator[dict[str, Any]]:
        fetched = 0
        offset = 0

        while fetched < limit:
            current_page_size = min(page_size, limit - fetched)
            features = await self.fetch_page(offset=offset, page_size=current_page_size)
            if not features:
                break

            for feature in features:
                if fetched >= limit:
                    break
                yield feature
                fetched += 1

            if len(features) < current_page_size:
                break
            offset += len(features)
