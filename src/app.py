from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from src.routers import monitor
from src.middlewares import get_public_domin

def create_app() -> FastAPI:
    """create fastapi app"""
    app = FastAPI()

    # adding middleware
    app.middleware("http")(get_public_domin)

    # adding static html_apps
    app.mount("/HLSplayer", StaticFiles(directory="src/html_apps/HLSplayer", html=True), name="HLSplayer")

    # adding router
    app.include_router(monitor, prefix="/monitor", tags=["monitor API"])

    # adding ROOT router
    @app.get("/", tags=["ROOT"])
    async def root(request: Request):
        public_domain = getattr(request.state, "public_domain", None)
        print(public_domain)
        return {
            "message": "MyAPI for ForestPetAssistant is running",
            "public_domain": public_domain
        }

    return app
