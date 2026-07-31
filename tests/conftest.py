"""pytest 공용 설정.

테스트는 개발용 DB(nailgi)가 아니라 별도의 테스트 DB(nailgi_test)를 사용한다.
테스트가 개발 중인 데이터를 지우거나 더럽히지 않게 하기 위해서다.

SQLite를 쓰지 않는 이유: 스키마가 PostgreSQL 전용 기능(UUID 타입, gen_random_uuid())을
쓰기 때문에 SQLite에서는 테이블 생성 자체가 실패한다. 운영과 같은 DB로 테스트해야
방언 차이로 인한 버그도 잡을 수 있다.
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app import models as _models  # noqa: F401  (모든 모델을 메타데이터에 등록)
from app.core.config import get_settings
from app.core.database import Base, get_db
from app.main import app

TEST_DB_NAME = "nailgi_test"


def _build_test_database_url() -> str:
    """개발용 DATABASE_URL에서 DB 이름만 테스트용으로 바꾼 접속 문자열을 만든다.

    호스트/계정/비밀번호는 .env 값을 그대로 재사용하므로 설정을 이중으로 관리하지 않아도 된다.
    """
    base_url = get_settings().database_url
    prefix, _, _ = base_url.rpartition("/")
    return f"{prefix}/{TEST_DB_NAME}"


@pytest.fixture(scope="session")
def test_engine():
    """테스트 세션 전체에서 쓸 엔진. 테스트 DB와 테이블을 만들어 둔다."""
    settings = get_settings()

    # CREATE DATABASE는 트랜잭션 안에서 실행할 수 없어 AUTOCOMMIT이 필요하다.
    # 또한 자기 자신에 접속한 채로는 만들 수 없으므로 기본 postgres DB에 붙어서 만든다.
    admin_url = settings.database_url.rpartition("/")[0] + "/postgres"
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": TEST_DB_NAME}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin_engine.dispose()

    engine = create_engine(_build_test_database_url())
    # 테스트는 alembic을 거치지 않고 모델 메타데이터에서 바로 만든다. 마이그레이션 순서와
    # 무관하게 "현재 모델이 의도한 스키마"를 검증하기 위해서다.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(test_engine) -> Generator[Session, None, None]:
    """테스트 하나마다 깨끗한 DB 상태를 보장하는 세션.

    각 테스트가 끝나면 모든 테이블을 비운다. 앞 테스트가 만든 사용자가 남아 있으면
    "중복 이메일" 같은 검사가 엉뚱하게 실패하기 때문이다.
    """
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = session_factory()

    yield session

    session.close()
    with test_engine.begin() as conn:
        # RESTART IDENTITY로 id 시퀀스도 1부터 다시 시작시켜 테스트 간 id를 예측 가능하게 만든다.
        table_names = ", ".join(f'"{table}"' for table in reversed(Base.metadata.sorted_tables))
        conn.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """테스트 DB를 바라보는 API 클라이언트.

    앱이 쓰는 get_db 의존성을 테스트 세션으로 갈아끼워, 라우터가 개발용 DB 대신
    테스트 DB를 쓰게 만든다.
    """

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
