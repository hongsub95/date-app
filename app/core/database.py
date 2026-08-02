"""DB 엔진과 세션 설정.

커넥션 풀은 연결을 만들어두고 재사용한다. 요청이 올 때마다 새 연결을 여는 것이 아니라
풀에서 빌려 쓰고(checkout) 돌려준다(checkin). 그래서 "커넥션이 생겼다"는 두 가지
의미가 될 수 있고, 로그도 구분해서 남긴다.

- connect  : 실제 물리적 연결이 새로 만들어짐. 드물게 일어나므로 INFO로 남긴다.
- checkout : 풀에서 빌려 씀. 요청마다 일어나므로 DEBUG로만 남긴다.
"""

import logging
from datetime import datetime

from sqlalchemy import DateTime, create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger("app.db")

# 풀 크기. pool_size는 평상시 유지할 연결 수, max_overflow는 몰릴 때 추가로 열 수 있는 수다.
# 즉 최대 동시 연결은 10 + 20 = 30개다.
POOL_SIZE = 10
MAX_OVERFLOW = 20

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 끊긴 커넥션 자동 재연결
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    echo=settings.db_echo,
)


def _pool_status() -> str:
    """현재 커넥션 풀 상태를 사람이 읽기 쉬운 한 줄로 요약한다.

    SQLAlchemy의 pool.overflow()는 -pool_size에서 시작해 올라가는 내부 카운터라
    그대로 찍으면 음수가 나와 헷갈린다. 여기서 실제 초과 개수로 환산한다.
    """
    pool = engine.pool
    in_use = pool.checkedout()
    idle = pool.checkedin()
    # 음수면 아직 기본 풀 안이라는 뜻이므로 0으로 보정한다.
    overflow = max(pool.overflow(), 0)

    status = f"사용중={in_use} 대기={idle} 최대={POOL_SIZE}+{MAX_OVERFLOW}"
    if overflow:
        status += f" 초과={overflow}"
    return status


def _register_connection_logging() -> None:
    """커넥션 생명주기를 로그로 남기는 이벤트 리스너를 등록한다.

    설정(db_log_connections)이 꺼져 있으면 아무것도 등록하지 않아 오버헤드가 없다.
    """
    if not settings.db_log_connections:
        return

    @event.listens_for(engine, "connect")
    def on_connect(dbapi_connection, connection_record) -> None:
        """DB에 물리적 연결이 새로 열렸을 때. 서버 기동 직후와 부하가 늘 때만 발생한다."""
        logger.info("DB 커넥션 생성 | %s", _pool_status())

    @event.listens_for(engine, "close")
    def on_close(dbapi_connection, connection_record) -> None:
        """물리적 연결이 닫혔을 때."""
        logger.info("DB 커넥션 종료 | %s", _pool_status())

    @event.listens_for(engine, "checkout")
    def on_checkout(dbapi_connection, connection_record, connection_proxy) -> None:
        """풀에서 커넥션을 빌려갈 때. 요청마다 발생하므로 DEBUG로만 남긴다."""
        logger.debug("DB 커넥션 대여 | %s", _pool_status())

    @event.listens_for(engine, "checkin")
    def on_checkin(dbapi_connection, connection_record) -> None:
        """빌려간 커넥션을 풀에 반납할 때."""
        logger.debug("DB 커넥션 반납 | %s", _pool_status())


_register_connection_logging()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """모든 SQLAlchemy 모델의 공통 베이스. datetime 타입 힌트를 자동으로 TIMESTAMPTZ로
    매핑해서, 각 모델에서 매번 timezone=True를 명시하지 않아도 되게 한다."""

    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }


def get_db():
    """요청 하나당 SQLAlchemy 세션을 열고, 응답이 끝나면 반드시 닫아주는 FastAPI 의존성(Depends)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
