from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """회원 계정 테이블. 이메일/비밀번호 로그인과 닉네임 표시를 위한 기본 프로필을 담는다."""

    __tablename__ = "nl_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    # 평문 비밀번호는 저장하지 않고 bcrypt 해시만 저장한다 (app/auth/security.py에서 생성).
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    # 앱 실행 시 열리는 스페이스. 회원가입 때 개인 스페이스로 설정되고, 이후 사용자가
    # 직접 바꿀 수 있다. 현재 기본값으로 지정된 스페이스는 삭제할 수 없다 (명세 0절).
    # spaces.owner_id -> users.id 순환 참조가 생기므로 FK 제약은 마이그레이션에서 use_alter로 처리한다.
    default_space_id: Mapped[int | None] = mapped_column(
        ForeignKey("nl_spaces.id", ondelete="SET NULL", use_alter=True, name="fk_users_default_space")
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # 앱을 열 때마다 기본 스페이스를 찾고, 스페이스 삭제 시 이를 기본값으로
        # 지정한 사용자가 있는지 확인해야 하므로 인덱스를 둔다.
        Index("ix_nl_users_default_space_id", "default_space_id"),
    )

    # created_schedules: 내가 만든 일정. 접근 권한은 이걸로 판단하지 않고 SpaceMember로 판단한다.
    created_schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="created_by_user", foreign_keys="Schedule.created_by", passive_deletes=True
    )
    space_memberships: Mapped[list["SpaceMember"]] = relationship(back_populates="user", passive_deletes=True)
