"""인증 비즈니스 로직.

라우터(HTTP)와 DB 사이의 계층이다. 라우터는 요청을 받아 이 함수들을 호출하기만 하고,
"이메일이 중복인가", "개인 스페이스를 같이 만들어야 하는가" 같은 규칙은 전부 여기 모은다.
"""

from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import security
from app.core.errors import AppError
from app.spaces.models import (
    PERSONAL_SPACE_DEFAULT_NAME,
    SPACE_MEMBER_STATUS_ACTIVE,
    SPACE_ROLE_OWNER,
    SPACE_TYPE_PERSONAL,
    Space,
    SpaceMember,
)
from app.users.models import User


class EmailAlreadyExistsError(AppError):
    """이미 가입된 이메일로 회원가입을 시도한 경우."""

    def __init__(self) -> None:
        super().__init__(
            code="EMAIL_ALREADY_EXISTS",
            message="이미 가입된 이메일입니다.",
            status_code=status.HTTP_409_CONFLICT,
            field="email",
        )


class NicknameAlreadyExistsError(AppError):
    """이미 사용 중인 닉네임으로 회원가입을 시도한 경우."""

    def __init__(self) -> None:
        super().__init__(
            code="NICKNAME_ALREADY_EXISTS",
            message="이미 사용 중인 닉네임입니다.",
            status_code=status.HTTP_409_CONFLICT,
            field="nickname",
        )


class InvalidCredentialsError(AppError):
    """이메일이 없거나 비밀번호가 틀린 경우.

    두 경우를 구분해서 알려주면 "이 이메일은 가입되어 있다"는 정보가 새어나가므로
    (계정 열거 공격) 하나의 예외로 합치고, field도 특정하지 않는다.
    """

    def __init__(self) -> None:
        super().__init__(
            code="INVALID_CREDENTIALS",
            message="이메일 또는 비밀번호가 올바르지 않습니다.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidRefreshTokenError(AppError):
    """refresh token이 만료됐거나 위조된 경우. 클라이언트는 재로그인을 유도해야 한다."""

    def __init__(self) -> None:
        super().__init__(
            code="INVALID_REFRESH_TOKEN",
            message="세션이 만료되었습니다. 다시 로그인해 주세요.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            field="refresh_token",
        )


def get_user_by_email(db: Session, email: str) -> User | None:
    """이메일로 사용자를 찾는다. 없으면 None."""
    return db.scalar(select(User).where(User.email == email))


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """id로 사용자를 찾는다. 없으면 None."""
    return db.get(User, user_id)


def register_user(db: Session, email: str, nickname: str, password: str) -> User:
    """새 사용자를 만들고 개인 스페이스까지 한 트랜잭션 안에서 생성한다.

    개인 스페이스를 같은 트랜잭션에 묶는 이유: 사용자는 있는데 스페이스가 없는 상태가
    되면 일정을 하나도 만들 수 없는 반쪽짜리 계정이 된다. 둘 다 성공하거나 둘 다
    실패해야 한다 (docs/SPACE_MODEL_SPEC.md 7.1).

    :param db: DB 세션
    :param email: 가입 이메일 (스키마에서 형식 검증 완료)
    :param nickname: 표시 이름
    :param password: 평문 비밀번호 (여기서 해싱한다)
    :raises EmailAlreadyExistsError: 이메일이 이미 존재할 때
    :raises NicknameAlreadyExistsError: 닉네임이 이미 존재할 때
    :return: 생성된 User (개인 스페이스가 default_space_id로 설정된 상태)
    """
    if get_user_by_email(db, email) is not None:
        raise EmailAlreadyExistsError()

    if db.scalar(select(User).where(User.nickname == nickname)) is not None:
        raise NicknameAlreadyExistsError()

    user = User(
        email=email,
        nickname=nickname,
        password_hash=security.hash_password(password),
    )
    db.add(user)
    # commit이 아니라 flush다. 아래에서 space.owner_id에 넣을 user.id를 DB에서
    # 받아와야 하는데, 트랜잭션은 아직 열어둔 채로 id만 확보하기 위함이다.
    db.flush()

    personal_space = Space(
        type=SPACE_TYPE_PERSONAL,
        name=PERSONAL_SPACE_DEFAULT_NAME,
        owner_id=user.id,
    )
    db.add(personal_space)
    db.flush()

    # 스페이스를 만든 것만으로는 접근 권한이 생기지 않는다. 모든 권한 검사는
    # SpaceMember를 보기 때문에 본인을 owner 멤버로 명시적으로 등록한다.
    db.add(
        SpaceMember(
            space_id=personal_space.id,
            user_id=user.id,
            role=SPACE_ROLE_OWNER,
            status=SPACE_MEMBER_STATUS_ACTIVE,
        )
    )

    # 사용자가 따로 지정하기 전까지는 개인 스페이스가 앱 실행 시 열리는 기본 스페이스다.
    user.default_space_id = personal_space.id

    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """이메일과 비밀번호로 사용자를 인증한다.

    :raises InvalidCredentialsError: 이메일이 없거나 비밀번호가 틀린 경우
    :return: 인증된 User
    """
    user = get_user_by_email(db, email)
    if user is None:
        # 존재하지 않는 이메일이어도 비밀번호를 실제로 검증한 것과 비슷한 시간을 쓰게 한다.
        # 응답 속도 차이로 "이 이메일은 가입되어 있다"를 알아내는 타이밍 공격을 막기 위함이다.
        security.verify_password(password, security.DUMMY_PASSWORD_HASH)
        raise InvalidCredentialsError()

    if not security.verify_password(password, user.password_hash):
        raise InvalidCredentialsError()

    return user


def issue_tokens(user_id: int) -> tuple[str, str]:
    """로그인/재발급 시 돌려줄 (access token, refresh token) 쌍을 만든다."""
    return security.create_access_token(user_id), security.create_refresh_token(user_id)


def refresh_access_token(db: Session, refresh_token: str) -> tuple[str, str]:
    """refresh token을 검증하고 새 토큰 쌍을 발급한다.

    무상태 방식이라 토큰을 DB에 저장하지 않는다. 대신 토큰이 가리키는 사용자가
    아직 존재하는지는 반드시 확인한다. 탈퇴한 사용자의 토큰이 만료 전까지
    계속 통과하는 것을 막기 위해서다.

    :raises InvalidRefreshTokenError: 토큰이 유효하지 않거나 사용자가 없는 경우
    :return: 새로 발급한 (access token, refresh token)
    """
    user_id = security.decode_token(refresh_token, security.TOKEN_TYPE_REFRESH)
    if user_id is None:
        raise InvalidRefreshTokenError()

    if get_user_by_id(db, user_id) is None:
        raise InvalidRefreshTokenError()

    return issue_tokens(user_id)
