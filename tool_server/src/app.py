from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import os
from loguru import logger
from tasks_se import POSPALGETDATA

from src.routers import monitor, sale
from src.middlewares import get_public_domin
from config import CONFIG


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pospal_scheduled_task = POSPALGETDATA(
        CONFIG.POSPAL_URL, CONFIG.POSPAL_USER_DATA
    )
    yield
    app.state.pospal_scheduled_task.close()


def create_app() -> FastAPI:
    """create fastapi app"""
    app = FastAPI(lifespan=lifespan)

    # adding middleware
    app.middleware("http")(get_public_domin)

    # adding static files
    app.mount("/statics", StaticFiles(directory="src/statics"), name="statics")
    os.makedirs("src/tmp", exist_ok=True)
    app.mount("/tmp", StaticFiles(directory="src/tmp"), name="tmp")

    # adding static html_apps
    app.mount("/HLSplayer", StaticFiles(directory="src/html_apps/HLSplayer", html=True), name="HLSplayer")

    # adding router
    os.makedirs("logs/router", exist_ok=True)
    app.include_router(monitor, prefix="/monitor", tags=["monitor API"])
    logger.add("logs/router/monitor.log", rotation="1 MB",
               filter=lambda record: record["extra"].get("module") == "monitor")
    app.include_router(sale, prefix="/sale", tags=["sale API"])
    logger.add("logs/router/sale.log", rotation="1 MB",
               filter=lambda record: record["extra"].get("module") == "sale")

    # adding ROOT router
    @app.get("/", tags=["ROOT"])
    async def root(request: Request):
        public_domain = getattr(request.state, "public_domain", None)
        return {
            "message": "MyAPI for ForestPetAssistant is running",
            "public_domain": public_domain
        }

    return app
