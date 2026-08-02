"""웹 로그인에 쓰는 Redis 세션 관리.

앱(JWT)과 달리 웹은 서버가 로그인 상태를 들고 있다. 그래서 다음이 가능하다.

- 로그아웃 시 즉시 무효화 (JWT는 만료 전까지 막을 수 없다)
- 한 계정의 접속 기기 목록 조회
- 비밀번호 변경 시 전체 세션 종료

Redis에 저장하는 구조는 두 가지다.

    session:{session_id}      -> 세션 정보 (해시). TTL이 걸려 있어 자동 만료된다.
    user_sessions:{user_id}   -> 그 사용자의 session_id 목록 (셋). "전체 로그아웃"과
                                 "기기 목록"을 위해 역방향 색인을 따로 둔다.

session:{...}만 있으면 특정 사용자의 세션을 모두 찾으려 할 때 Redis 전체를 훑어야
하므로(KEYS 명령은 운영에서 쓰면 안 된다) 역방향 색인이 필요하다.
"""

import secrets
from datetime import datetime, timezone

import redis

from app.core.config import get_settings

settings = get_settings()

# 세션 ID 길이(바이트). 32바이트면 추측이 사실상 불가능하다.
SESSION_ID_BYTES = 32

_SESSION_KEY_PREFIX = "session:"
_USER_SESSIONS_KEY_PREFIX = "user_sessions:"


def _session_key(session_id: str) -> str:
    """세션 정보를 저장하는 Redis 키."""
    return f"{_SESSION_KEY_PREFIX}{session_id}"


def _user_sessions_key(user_id: int) -> str:
    """한 사용자의 session_id 목록을 저장하는 Redis 키."""
    return f"{_USER_SESSIONS_KEY_PREFIX}{user_id}"


def _ttl_seconds() -> int:
    """세션 유효기간을 초 단위로 환산한다."""
    return settings.session_expire_days * 24 * 60 * 60


def create_session(
    client: redis.Redis,
    user_id: int,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> str:
    """새 세션을 만들고 세션 ID를 돌려준다.

    :param client: Redis 클라이언트
    :param user_id: 로그인한 사용자 id
    :param user_agent: 접속 기기 식별용 User-Agent 헤더 (기기 목록 표시에 사용)
    :param ip_address: 접속 IP (이상 접속 확인용)
    :return: 브라우저 쿠키에 심을 세션 ID
    """
    # token_urlsafe는 암호학적 난수를 쓴다. random 모듈은 예측 가능하므로 쓰지 않는다.
    session_id = secrets.token_urlsafe(SESSION_ID_BYTES)
    now = datetime.now(timezone.utc).isoformat()

    # 여러 명령을 한 번에 보내 왕복 횟수를 줄인다. 중간에 실패해도
    # TTL 덕분에 고아 데이터가 알아서 사라진다.
    pipe = client.pipeline()
    pipe.hset(
        _session_key(session_id),
        mapping={
            "user_id": str(user_id),
            "created_at": now,
            "last_seen_at": now,
            "user_agent": user_agent or "",
            "ip_address": ip_address or "",
        },
    )
    pipe.expire(_session_key(session_id), _ttl_seconds())
    pipe.sadd(_user_sessions_key(user_id), session_id)
    # 역방향 색인에도 TTL을 건다. 없으면 사용자가 다시는 로그인하지 않아도
    # 이 셋이 영원히 남는다. 세션이 갱신될 때마다 같이 연장된다.
    pipe.expire(_user_sessions_key(user_id), _ttl_seconds())
    pipe.execute()

    return session_id


def get_session_user_id(client: redis.Redis, session_id: str) -> int | None:
    """세션 ID로 사용자 id를 찾고, 동시에 유효기간을 연장한다.

    요청이 올 때마다 TTL을 다시 채우기 때문에 "마지막 사용 후 N일"로 동작한다.
    사용 중인 사용자가 갑자기 로그아웃되지 않게 하기 위함이다.

    :return: 유효한 세션이면 사용자 id, 아니면 None
    """
    key = _session_key(session_id)
    user_id_raw = client.hget(key, "user_id")
    if user_id_raw is None:
        # 만료됐거나 로그아웃으로 삭제됐거나, 애초에 없는 세션.
        return None

    try:
        user_id = int(user_id_raw)
    except ValueError:
        # 값이 손상된 경우. 인증 실패로 처리하고 지운다.
        client.delete(key)
        return None

    pipe = client.pipeline()
    pipe.hset(key, "last_seen_at", datetime.now(timezone.utc).isoformat())
    pipe.expire(key, _ttl_seconds())
    pipe.expire(_user_sessions_key(user_id), _ttl_seconds())
    pipe.execute()

    return user_id


def delete_session(client: redis.Redis, session_id: str) -> None:
    """세션 하나를 삭제한다(로그아웃). 없는 세션이어도 오류를 내지 않는다."""
    key = _session_key(session_id)
    user_id_raw = client.hget(key, "user_id")

    pipe = client.pipeline()
    pipe.delete(key)
    if user_id_raw is not None:
        # 역방향 색인에서도 빼야 "기기 목록"에 유령 세션이 남지 않는다.
        pipe.srem(_user_sessions_key(int(user_id_raw)), session_id)
    pipe.execute()


def delete_all_user_sessions(client: redis.Redis, user_id: int) -> int:
    """한 사용자의 모든 세션을 삭제한다.

    비밀번호 변경이나 "모든 기기에서 로그아웃"에 사용한다.

    :return: 삭제된 세션 개수
    """
    index_key = _user_sessions_key(user_id)
    session_ids = client.smembers(index_key)

    if not session_ids:
        return 0

    pipe = client.pipeline()
    for session_id in session_ids:
        pipe.delete(_session_key(session_id))
    pipe.delete(index_key)
    pipe.execute()

    return len(session_ids)


def list_user_sessions(client: redis.Redis, user_id: int) -> list[dict[str, str]]:
    """한 사용자의 활성 세션 목록을 돌려준다(접속 기기 목록 화면용).

    색인에는 있지만 이미 만료된 session_id가 섞여 있을 수 있으므로,
    실제 조회에 실패한 항목은 색인에서 정리하며 건너뛴다.
    """
    index_key = _user_sessions_key(user_id)
    sessions: list[dict[str, str]] = []
    stale_ids: list[str] = []

    for session_id in client.smembers(index_key):
        data = client.hgetall(_session_key(session_id))
        if not data:
            stale_ids.append(session_id)
            continue
        sessions.append({"session_id": session_id, **data})

    if stale_ids:
        client.srem(index_key, *stale_ids)

    return sessions
