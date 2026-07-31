"""보호된 엔드포인트에서 "지금 요청한 사용자"를 꺼내는 FastAPI 의존성.

인증이 필요한 라우터는 인자에 `current_user: User = Depends(get_current_user)`만
추가하면 된다. 토큰 파싱과 401 처리는 전부 여기서 끝난다.
"""

from typing import Annotated

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth import security, service
from app.core.database import get_db
from app.core.errors import AppError
from app.users.models import User

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


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Authorization 헤더의 access token을 검증하고 해당 User를 돌려준다.

    :param credentials: FastAPI가 "Bearer {token}" 헤더에서 파싱해 넣어주는 값. 헤더가
        없으면 None이 들어온다.
    :param db: DB 세션
    :raises UnauthorizedError: 토큰이 없거나, 만료됐거나, 사용자가 존재하지 않을 때 (401)
    :return: 인증된 User
    """
    if credentials is None:
        raise UnauthorizedError()

    # refresh token으로 일반 API를 호출하는 오용을 막기 위해 종류를 명시해 검증한다.
    user_id = security.decode_token(credentials.credentials, security.TOKEN_TYPE_ACCESS)
    if user_id is None:
        raise UnauthorizedError()

    # 토큰 서명이 유효해도 그 사이 탈퇴했을 수 있으므로 DB에서 실제 존재를 확인한다.
    user = service.get_user_by_id(db, user_id)
    if user is None:
        raise UnauthorizedError()

    return user


# 라우터에서 반복해서 쓰는 타입을 짧게 별칭으로 둔다.
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]
