import httpx
import respx

from app.services.hud_arcgis_client import HudArcgisClient


@respx.mock
async def test_fetch_page_uses_arcgis_pagination_params() -> None:
    route = respx.get("https://example.test/query").mock(
        return_value=httpx.Response(200, json={"features": [{"attributes": {"PROPERTY_ID": "1"}}]})
    )
    client = HudArcgisClient("https://example.test/query")

    features = await client.fetch_page(offset=25, page_size=50)

    assert len(features) == 1
    request = route.calls.last.request
    assert request.url.params["f"] == "json"
    assert request.url.params["resultOffset"] == "25"
    assert request.url.params["resultRecordCount"] == "50"
    assert request.url.params["returnGeometry"] == "true"


@respx.mock
async def test_iter_features_stops_at_limit() -> None:
    respx.get("https://example.test/query").mock(
        return_value=httpx.Response(
            200,
            json={
                "features": [
                    {"attributes": {"PROPERTY_ID": "1"}},
                    {"attributes": {"PROPERTY_ID": "2"}},
                ]
            },
        )
    )
    client = HudArcgisClient("https://example.test/query")

    features = [feature async for feature in client.iter_features(limit=2, page_size=2)]

    assert len(features) == 2
