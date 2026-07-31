from datetime import datetime

from sqlalchemy import DateTime, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 끊긴 커넥션 자동 재연결
    pool_size=10,
    max_overflow=20,
)

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
