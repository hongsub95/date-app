from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.auth.router import router as auth_router
from app.auth.web_router import router as auth_web_router
from app.menus.router import router as menus_router
from app.spaces.router import router as spaces_router
from app.users.router import router as users_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
# 앱용(JWT) 라우터가 /auth, 웹용(세션) 라우터가 /auth/web을 담당한다.
api_router.include_router(auth_router)
api_router.include_router(auth_web_router)
api_router.include_router(menus_router)
api_router.include_router(spaces_router)
api_router.include_router(users_router)
