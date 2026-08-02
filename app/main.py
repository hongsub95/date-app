import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# 모든 모델을 SQLAlchemy 레지스트리에 등록한다. 직접 쓰지 않지만 relationship 문자열
# 해석에 필요하므로 지우면 안 된다. (자세한 이유는 app/models.py 참고)
# `import app.models`가 아니라 이 형태를 쓰는 이유: 전자는 `app`이라는 이름을 패키지에
# 묶어버려서 아래에서 만드는 FastAPI 인스턴스 `app`과 충돌한다.
from app import models as _models  # noqa: F401
from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import engine
from app.core.errors import register_error_handlers
from app.core.logging_config import setup_logging
from app.core.redis_client import ping_redis

settings = get_settings()

# 라우터를 만들기 전에 로깅부터 초기화해야 기동 과정의 로그도 형식이 맞는다.
setup_logging()
logger = logging.getLogger("app.startup")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """서버 기동·종료 시 한 번씩 실행되는 구간.

    기동 직후 DB와 Redis에 실제로 붙어보고 결과를 로그로 남긴다. 이렇게 해두면
    "서버는 떴는데 첫 요청에서야 연결 실패를 발견하는" 상황을 막을 수 있다.
    """
    logger.info("서버 시작 | env=%s", settings.app_env)

    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar()
        # 접속 문자열에는 비밀번호가 들어 있으므로 로그에 그대로 남기지 않고
        # 호스트와 DB 이름만 잘라서 남긴다.
        host_and_db = settings.database_url.rsplit("@", 1)[-1]
        logger.info("DB 연결 성공 | %s | %s", host_and_db, str(version).split(",")[0])
    except Exception as exc:
        # 여기서 예외를 다시 던지지 않는 이유: DB가 잠깐 늦게 뜨는 상황(docker compose)에서
        # 서버까지 죽으면 재시작 루프에 빠진다. 로그로 알리고 서버는 살려둔다.
        logger.error("DB 연결 실패 | %s", exc)

    if ping_redis():
        logger.info("Redis 연결 성공 | %s", settings.redis_url)
    else:
        logger.error("Redis 연결 실패 | %s (웹 세션 로그인이 동작하지 않습니다)", settings.redis_url)

    yield

    logger.info("서버 종료 | DB 커넥션 풀 정리")
    engine.dispose()


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

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
