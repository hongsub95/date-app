from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 모든 모델을 SQLAlchemy 레지스트리에 등록한다. 직접 쓰지 않지만 relationship 문자열
# 해석에 필요하므로 지우면 안 된다. (자세한 이유는 app/models.py 참고)
# `import app.models`가 아니라 이 형태를 쓰는 이유: 전자는 `app`이라는 이름을 패키지에
# 묶어버려서 아래에서 만드는 FastAPI 인스턴스 `app`과 충돌한다.
from app import models as _models  # noqa: F401
from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import register_error_handlers

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)

# 프론트엔드(Vite 개발 서버)가 다른 포트에서 돌기 때문에 브라우저가 교차 출처 요청을
# 차단한다. 허용할 출처는 .env의 CORS_ORIGINS로 관리한다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모든 오류 응답을 {code, message, field} 형태로 통일한다. 라우터 등록 전에 걸어둔다.
register_error_handlers(app)

app.include_router(api_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "FastAPI is running",
        "env": settings.app_env,
    }
