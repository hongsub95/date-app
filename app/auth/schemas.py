"""인증 API의 요청/응답 형태를 정의하는 Pydantic 스키마.

여기서 정의한 제약(길이, 이메일 형식 등)은 FastAPI가 라우터 진입 전에 검증해서
잘못된 입력은 422로 자동 거절한다. 따라서 service.py는 형식이 아니라
"이미 가입된 이메일인가" 같은 비즈니스 규칙에만 집중하면 된다.
"""

from datetime import datetime
from string import ascii_letters, digits, punctuation

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.auth.security import MAX_PASSWORD_BYTES

MIN_PASSWORD_LENGTH = 9

# 비밀번호에서 '특수문자'로 인정하는 문자 집합. string.punctuation과 같은 ASCII 구두점
# 32자이며 공백은 포함하지 않는다. API_SPEC 3.2절에 이 목록을 그대로 명시해 두었으니
# 여기를 바꾸면 명세와 프론트엔드 검증도 함께 고쳐야 한다.
SPECIAL_CHARACTERS = punctuation


class RegisterRequest(BaseModel):
    """회원가입 요청 본문."""

    email: EmailStr
    nickname: str = Field(min_length=2, max_length=50)
    # min_length를 Field에 두면 pydantic이 "String should have at least 9 characters"
    # 라는 영어 문구를 그대로 응답에 실어 보낸다. API_SPEC 2.5절이 message를 '사용자에게
    # 그대로 노출 가능한 한국어'로 못박았기 때문에 길이 검사도 아래 validator로 옮겼다.
    password: str = Field(
        description=f"{MIN_PASSWORD_LENGTH}자 이상이며 영문, 숫자, 특수문자를 각각 1개 이상 포함",
    )

    @field_validator("password")
    @classmethod
    def validate_password_policy(cls, value: str) -> str:
        """비밀번호의 길이·구성 규칙과 bcrypt의 내부 길이 제한을 검사한다.

        Args:
            value: 사용자가 입력한 평문 비밀번호.

        Returns:
            검증을 통과한 비밀번호 원본.

        Raises:
            ValueError: 규칙을 어겼을 때. 문구는 화면에 그대로 노출된다.
        """
        # 바이트 검사를 가장 먼저 한다. Field(max_length=...)는 '글자 수'를 세지만
        # bcrypt의 한계는 '바이트 수'다. 한글은 UTF-8에서 한 글자가 3바이트라,
        # 글자 수만 검사하면 통과한 값이 해싱 단계에서 터진다.
        if len(value.encode("utf-8")) > MAX_PASSWORD_BYTES:
            raise ValueError("비밀번호가 너무 깁니다. 조금 짧게 입력해 주세요.")
        if len(value) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"비밀번호는 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다.")
        if not (
            any(character in ascii_letters for character in value)
            and any(character in digits for character in value)
            and any(character in SPECIAL_CHARACTERS for character in value)
        ):
            raise ValueError("비밀번호는 영문, 숫자, 특수문자를 각각 1개 이상 포함해야 합니다.")
        return value

    @field_validator("nickname")
    @classmethod
    def validate_nickname_not_blank(cls, value: str) -> str:
        """공백만 입력한 닉네임을 거르고 앞뒤 공백을 제거한다."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("닉네임은 공백일 수 없습니다.")
        return stripped


class LoginRequest(BaseModel):
    """로그인 요청 본문."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """access token 재발급 요청 본문."""

    refresh_token: str


class TokenResponse(BaseModel):
    """로그인/재발급 성공 시 돌려주는 토큰 묶음."""

    access_token: str
    refresh_token: str
    # OAuth2 관례상 토큰 종류를 함께 알려준다. 클라이언트는 Authorization 헤더를
    # "Bearer {access_token}" 형태로 구성한다.
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """사용자 정보 응답. password_hash는 절대 포함하지 않는다."""

    # SQLAlchemy 모델 객체를 그대로 넣어도 속성을 읽어 변환하도록 허용한다.
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nickname: str
    # 앱 실행 시 열어야 할 스페이스. 클라이언트는 로그인 후 이 값으로 첫 화면을 구성한다.
    default_space_id: int | None
    created_at: datetime


class RegisterResponse(BaseModel):
    """회원가입 성공 응답. 가입 직후 바로 로그인 상태가 되도록 토큰을 함께 준다."""

    user: UserResponse
    tokens: TokenResponse
