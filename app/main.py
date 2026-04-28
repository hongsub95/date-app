from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(api_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "FastAPI is running",
        "env": settings.app_env,
    }
