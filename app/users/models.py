from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """회원 계정 테이블. 이메일/비밀번호 로그인과 닉네임 표시를 위한 기본 프로필을 담는다."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    # 평문 비밀번호는 저장하지 않고 bcrypt 해시만 저장한다 (app/auth/security.py에서 생성).
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(server_default="now()", onupdate=datetime.utcnow)

    schedules: Mapped[list["Schedule"]] = relationship(back_populates="owner")
