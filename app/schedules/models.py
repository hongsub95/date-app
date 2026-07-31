from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Schedule(Base):
    """약속/일정 하나. 캘린더·리스트·지도 화면의 중심 엔티티이며, 장소(SchedulePlace)와
    일기(DiaryEntry)가 여기에 매달린다."""

    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    start_at: Mapped[datetime] = mapped_column(nullable=False)
    end_at: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="planned")
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, server_default="private")
    created_at: Mapped[datetime] = mapped_column(server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(server_default="now()", onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("status IN ('planned', 'completed', 'canceled')", name="ck_schedules_status"),
        CheckConstraint("visibility IN ('private', 'shared', 'public')", name="ck_schedules_visibility"),
        # 종료 시각이 시작 시각보다 앞설 수 없다는 불변식을 DB 레벨에서도 강제.
        CheckConstraint("end_at >= start_at", name="ck_schedules_time_range"),
    )

    owner: Mapped["User"] = relationship(back_populates="schedules")
    places: Mapped[list["SchedulePlace"]] = relationship(back_populates="schedule", order_by="SchedulePlace.sort_order")
    participants: Mapped[list["ScheduleParticipant"]] = relationship(back_populates="schedule")
    diary_entry: Mapped["DiaryEntry | None"] = relationship(back_populates="schedule", uselist=False)
    share_links: Mapped[list["ShareLink"]] = relationship(back_populates="schedule")


class ScheduleParticipant(Base):
    """일정을 함께 보는 사용자(초대받은 참여자). owner_id로 소유자를 표시하는 Schedule과 별개로,
    "함께 쓰는 흐름"에서 누가 어떤 권한(owner/editor/viewer)으로 참여 중인지 기록한다."""

    __tablename__ = "schedule_participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, server_default="viewer")
    invited_at: Mapped[datetime] = mapped_column(server_default="now()")
    accepted_at: Mapped[datetime | None] = mapped_column()

    __table_args__ = (
        CheckConstraint("role IN ('owner', 'editor', 'viewer')", name="ck_participants_role"),
        UniqueConstraint("schedule_id", "user_id", name="uq_participants_schedule_user"),
    )

    schedule: Mapped["Schedule"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship()


class ShareLink(Base):
    """일정을 초대 없이 링크만으로 공유하기 위한 토큰. permission으로 열람/편집 권한을 구분하고,
    expires_at으로 만료 시점을 둘 수 있다."""

    __tablename__ = "share_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    permission: Mapped[str] = mapped_column(String(10), nullable=False, server_default="view")
    expires_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default="now()")

    __table_args__ = (
        CheckConstraint("permission IN ('view', 'edit')", name="ck_share_links_permission"),
    )

    schedule: Mapped["Schedule"] = relationship(back_populates="share_links")
