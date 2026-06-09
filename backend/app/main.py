from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analytics import router as analytics_router
from app.api.routes.freddie_mac_ingestion import router as freddie_mac_ingestion_router
from app.api.routes.health import router as health_router
from app.api.routes.ingestion import router as ingestion_router
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(title=settings.api_title, version=settings.api_version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(ingestion_router)
    app.include_router(freddie_mac_ingestion_router)
    app.include_router(analytics_router)
    return app


app = create_app()
