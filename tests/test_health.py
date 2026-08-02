from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


client = TestClient(app)


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    # env 값을 하드코딩하지 않는다. 실행 환경(local/test/production)에 따라 달라지므로
    # 설정에서 읽은 값과 비교해야 어느 환경에서 돌려도 통과한다.
    assert response.json() == {"message": "FastAPI is running", "env": get_settings().app_env}


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
