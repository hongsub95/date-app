"""보호된 엔드포인트에서 "지금 요청한 사용자"를 꺼내는 FastAPI 의존성.

인증이 필요한 라우터는 인자에 `current_user: CurrentUser`만 추가하면 된다.
인증 방식 판별과 401 처리는 전부 여기서 끝난다.

이 프로젝트는 플랫폼별로 인증 방식이 다르다.

- 웹: Redis 세션 + httpOnly 쿠키 (서버가 로그인 상태를 보관 → 강제 로그아웃 가능)
- 앱: JWT Bearer 토큰 (무상태)

두 방식 모두 같은 API를 쓰므로, 여기서 쿠키를 먼저 보고 없으면 Authorization 헤더를
확인한다. 덕분에 각 라우터는 어느 쪽으로 로그인했는지 신경 쓸 필요가 없다.
"""

from typing import Annotated

import redis
from fastapi import Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth import security, service, session as session_store
from app.core.config import get_settings
from app.core.database import get_db
from app.core.errors import AppError
from app.core.redis_client import get_redis
from app.users.models import User

settings = get_settings()

# auto_error=False로 두는 이유: 기본값(True)이면 Authorization 헤더가 없을 때 FastAPI가
# 403을 반환한다. 하지만 프론트엔드의 토큰 자동 갱신 로직은 보통 401을 신호로 삼으므로,
# "인증 안 됨"은 전부 401로 통일하기 위해 직접 처리한다.
# (401 = 로그인이 필요함, 403 = 로그인했지만 권한이 없음)
bearer_scheme = HTTPBearer(auto_error=False)


class UnauthorizedError(AppError):
    """토큰이 없거나 유효하지 않은 경우.

    "토큰 만료", "위조된 서명", "탈퇴한 사용자"를 구분해서 알려주면 공격자에게 힌트가
    되므로 하나의 응답으로 합친다. 클라이언트는 이 코드를 받으면 refresh를 시도하고,
    그것도 실패하면 로그인 화면으로 보내면 된다.
    """

    def __init__(self) -> None:
        super().__init__(
            code="UNAUTHORIZED",
            message="인증 정보가 유효하지 않습니다.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


def _resolve_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
    redis_client: redis.Redis,
) -> int | None:
    """요청에서 사용자 id를 알아낸다. 웹 세션을 먼저 보고, 없으면 JWT를 본다.

    세션을 먼저 보는 이유: 웹 브라우저는 쿠키를 자동으로 붙여 보내므로 쿠키가 있으면
    웹 요청으로 보는 것이 자연스럽고, 세션은 서버에서 폐기할 수 있어 더 신뢰할 수 있다.

    :return: 확인되면 사용자 id, 아니면 None
    """
    session_id = request.cookies.get(settings.session_cookie_name)
    if session_id:
        user_id = session_store.get_session_user_id(redis_client, session_id)
        if user_id is not None:
            return user_id
        # 쿠키는 있지만 세션이 만료·폐기된 경우다. 여기서 바로 실패시키지 않고
        # 아래 JWT 검사로 넘어간다. 같은 브라우저에서 앱용 토큰을 테스트하는 상황을
        # 막지 않기 위해서다.

    if credentials is not None:
        # refresh token으로 일반 API를 호출하는 오용을 막기 위해 종류를 명시해 검증한다.
        return security.decode_token(credentials.credentials, security.TOKEN_TYPE_ACCESS)

    return None


def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
) -> User:
    """세션 쿠키 또는 access token을 검증하고 해당 User를 돌려준다.

    :param request: 세션 쿠키를 읽기 위해 필요
    :param credentials: FastAPI가 "Bearer {token}" 헤더에서 파싱해 넣어주는 값.
        헤더가 없으면 None이 들어온다.
    :param db: DB 세션
    :param redis_client: 웹 세션 조회용 Redis 클라이언트
    :raises UnauthorizedError: 인증 정보가 없거나 유효하지 않을 때 (401)
    :return: 인증된 User
    """
    user_id = _resolve_user_id(request, credentials, redis_client)
    if user_id is None:
        raise UnauthorizedError()

    # 세션/토큰이 유효해도 그 사이 탈퇴했을 수 있으므로 DB에서 실제 존재를 확인한다.
    user = service.get_user_by_id(db, user_id)
    if user is None:
        raise UnauthorizedError()

    return user


# 라우터에서 반복해서 쓰는 타입을 짧게 별칭으로 둔다.
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]
RedisClient = Annotated[redis.Redis, Depends(get_redis)]
