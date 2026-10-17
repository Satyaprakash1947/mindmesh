from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai.service import TutorService
from app.api.router import router
from app.graph.repository import GraphRepository
from app.runtime import Runtime
from app.settings import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        try:
            yield
        finally:
            application.state.runtime.close()

    application = FastAPI(
        title="MindMesh API",
        description="Adaptive learning with a prerequisite graph and mastery-aware next steps.",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    application.state.runtime = Runtime(
        settings=config,
        graph=GraphRepository(config),
        tutor=TutorService(config),
    )
    application.include_router(router)

    @application.get("/", tags=["system"])
    def root() -> dict[str, str]:
        """Give browser visitors a useful landing response instead of a 404."""
        return {
            "name": "MindMesh API",
            "status": "ready",
            "docs": "/docs",
            "health": "/api/health",
        }

    return application


app = create_app()
