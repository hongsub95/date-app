"""Redis 연결을 관리하는 모듈.

웹 세션 저장소로 사용한다. 앱(JWT)은 Redis가 필요 없지만, 웹 로그인은 세션이
Redis에 있어야 동작하므로 서버 기동 시 연결이 되는지 확인하는 것이 좋다.
"""

import redis

from app.core.config import get_settings

settings = get_settings()

# ConnectionPool을 내부에서 재사용하므로 요청마다 새로 만들지 않고 모듈 단위로 하나만 둔다.
# decode_responses=True: 저장/조회 시 bytes가 아니라 str로 다루게 해 매번 디코딩하지 않아도 된다.
redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    # 서버가 죽었을 때 요청이 무한정 매달리지 않도록 짧은 타임아웃을 둔다.
    socket_connect_timeout=3,
    socket_timeout=3,
)


def get_redis() -> redis.Redis:
    """Redis 클라이언트를 돌려주는 FastAPI 의존성.

    테스트에서 가짜 Redis로 갈아끼울 수 있도록 의존성 형태로 노출한다.
    """
    return redis_client


def ping_redis() -> bool:
    """Redis에 연결할 수 있는지 확인한다. 헬스체크와 기동 점검에 쓴다."""
    try:
        return redis_client.ping()
    except redis.RedisError:
        return False
