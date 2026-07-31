from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DiaryEntry(Base):
    """일정 하나에 대한 일기. schedule_id가 UNIQUE라서 일정당 일기는 항상 1개다."""

    __tablename__ = "diary_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    mood: Mapped[str | None] = mapped_column(String(20))
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, server_default="private")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("visibility IN ('private', 'shared', 'public')", name="ck_diary_visibility"),
        # 일정 하나당 일기 하나만 허용 (API가 /schedules/{id}/diary 단수 리소스로 설계됨).
        UniqueConstraint("schedule_id", name="uq_diary_schedule"),
    )

    schedule: Mapped["Schedule"] = relationship(back_populates="diary_entry")
    author: Mapped["User"] = relationship()
    photos: Mapped[list["DiaryPhoto"]] = relationship(back_populates="diary_entry", order_by="DiaryPhoto.sort_order")


class DiaryPhoto(Base):
    """일기에 첨부된 사진 한 장. file_url/thumbnail_url은 S3에 업로드된 후의 접근 경로를 저장한다."""

    __tablename__ = "diary_photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    diary_entry_id: Mapped[int] = mapped_column(ForeignKey("diary_entries.id", ondelete="CASCADE"), nullable=False)
    uploader_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    diary_entry: Mapped["DiaryEntry"] = relationship(back_populates="photos")
    uploader: Mapped["User"] = relationship()
