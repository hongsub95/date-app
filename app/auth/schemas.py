"""인증 API의 요청/응답 형태를 정의하는 Pydantic 스키마.

여기서 정의한 제약(길이, 이메일 형식 등)은 FastAPI가 라우터 진입 전에 검증해서
잘못된 입력은 422로 자동 거절한다. 따라서 service.py는 형식이 아니라
"이미 가입된 이메일인가" 같은 비즈니스 규칙에만 집중하면 된다.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.auth.security import MAX_PASSWORD_BYTES

MIN_PASSWORD_LENGTH = 8


class RegisterRequest(BaseModel):
    """회원가입 요청 본문."""

    email: EmailStr
    nickname: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)

    @field_validator("password")
    @classmethod
    def validate_password_byte_length(cls, value: str) -> str:
        """bcrypt가 처리할 수 있는 길이인지 바이트 단위로 검사한다.

        Field(max_length=...)는 '글자 수'를 세지만 bcrypt의 한계는 '바이트 수'다.
        한글은 UTF-8에서 한 글자가 3바이트라, 글자 수만 검사하면 통과한 값이
        해싱 단계에서 터진다. 그래서 여기서 인코딩 후 길이를 직접 확인한다.
        """
        if len(value.encode("utf-8")) > MAX_PASSWORD_BYTES:
            raise ValueError(f"비밀번호는 UTF-8 기준 {MAX_PASSWORD_BYTES}바이트를 넘을 수 없습니다.")
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
