"""비밀번호 해싱과 JWT 토큰 발급/검증을 담당하는 저수준 보안 유틸.

이 모듈은 DB나 FastAPI를 알지 못한다. 순수하게 "문자열 -> 해시", "사용자 id -> 토큰"
변환만 책임지고, 실제 회원가입/로그인 흐름은 service.py가 담당한다.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings

settings = get_settings()

# bcrypt는 72바이트를 넘는 입력을 처리하지 못한다(초과분을 조용히 버리는 대신 에러를 낸다).
# 스키마에서 미리 검증하지만, 여기서도 상수로 남겨 의도를 드러낸다.
MAX_PASSWORD_BYTES = 72

# JWT payload의 "type" 클레임 값. access token으로 refresh를 시도하는 등의
# 토큰 오용을 막기 위해 발급 시 종류를 새겨두고 검증 시 대조한다.
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# 존재하지 않는 이메일로 로그인을 시도했을 때 대조용으로 쓰는 더미 해시.
# 실제로는 절대 일치하지 않지만, 검증에 같은 시간을 쓰게 만들어 응답 속도로
# 계정 존재 여부를 알아내는 타이밍 공격을 막는다.
DUMMY_PASSWORD_HASH = bcrypt.hashpw(b"invalid-placeholder", bcrypt.gensalt()).decode("utf-8")


def hash_password(plain_password: str) -> str:
    """평문 비밀번호를 bcrypt 해시로 변환한다.

    :param plain_password: 사용자가 입력한 평문 비밀번호
    :return: DB의 users.password_hash에 저장할 해시 문자열
    """
    # gensalt()가 매번 다른 salt를 만들기 때문에, 같은 비밀번호라도 해시 결과는 매번 다르다.
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """평문 비밀번호가 저장된 해시와 일치하는지 확인한다.

    :param plain_password: 로그인 시 입력받은 평문 비밀번호
    :param password_hash: DB에 저장된 해시
    :return: 일치하면 True
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # 저장된 해시가 손상되어 bcrypt 형식이 아닌 경우. 인증 실패로 처리한다.
        return False


def _create_token(subject: int, token_type: str, expires_delta: timedelta) -> str:
    """JWT를 만드는 내부 공통 함수. access/refresh 토큰이 같은 구조를 공유한다.

    :param subject: 토큰의 주인이 되는 사용자 id
    :param token_type: TOKEN_TYPE_ACCESS 또는 TOKEN_TYPE_REFRESH
    :param expires_delta: 발급 시점부터의 유효 기간
    :return: 서명된 JWT 문자열
    """
    now = datetime.now(timezone.utc)
    payload = {
        # sub(subject)는 JWT 표준상 문자열이어야 해서 int를 str로 변환해 담는다.
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: int) -> str:
    """API 요청 인증에 사용할 짧은 수명의 access token을 발급한다."""
    return _create_token(
        subject=user_id,
        token_type=TOKEN_TYPE_ACCESS,
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )


def create_refresh_token(user_id: int) -> str:
    """access token 재발급에만 사용할 긴 수명의 refresh token을 발급한다."""
    return _create_token(
        subject=user_id,
        token_type=TOKEN_TYPE_REFRESH,
        expires_delta=timedelta(days=settings.jwt_refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str) -> int | None:
    """토큰을 검증하고 주인의 사용자 id를 돌려준다.

    :param token: 클라이언트가 보낸 JWT 문자열
    :param expected_type: 기대하는 토큰 종류(TOKEN_TYPE_ACCESS / TOKEN_TYPE_REFRESH)
    :return: 검증에 성공하면 사용자 id, 실패하면 None
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.InvalidTokenError:
        # 만료, 서명 불일치, 형식 오류를 모두 포함한다. 원인을 구분해 알려주면
        # 공격자에게 힌트가 되므로 한 번에 실패로 처리한다.
        return None

    # refresh 전용 토큰으로 일반 API를 호출하는 식의 오용을 여기서 차단한다.
    if payload.get("type") != expected_type:
        return None

    subject = payload.get("sub")
    if subject is None:
        return None

    try:
        return int(subject)
    except (TypeError, ValueError):
        return None
