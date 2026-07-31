from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Place(Base):
    """지도상의 장소 하나. 여러 일정(Schedule)이 같은 Place를 재사용할 수 있다."""

    __tablename__ = "places"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500))
    latitude: Mapped[Decimal | None] = mapped_column()
    longitude: Mapped[Decimal | None] = mapped_column()
    # 장소 출처: 사용자가 직접 입력했는지(manual) 외부 지도 API로 검색했는지 구분.
    provider: Mapped[str] = mapped_column(String(20), nullable=False, server_default="manual")
    provider_place_id: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(server_default="now()")

    __table_args__ = (
        CheckConstraint("provider IN ('manual', 'kakao', 'naver', 'google')", name="ck_places_provider"),
    )


class SchedulePlace(Base):
    """일정(Schedule)에 담긴 장소 하나. Schedule과 Place의 다대다 관계를 풀어주는 연결 테이블이며,
    방문 순서(sort_order)와 방문 여부(visited) 같은 일정별 상태를 함께 갖는다."""

    __tablename__ = "schedule_places"

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    # 같은 일정 안에서 장소를 방문할 순서. 값이 작을수록 먼저 방문.
    sort_order: Mapped[int] = mapped_column(nullable=False, server_default="0")
    planned_time: Mapped[time | None] = mapped_column()
    memo: Mapped[str | None] = mapped_column(Text)
    visited: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(server_default="now()", onupdate=datetime.utcnow)

    schedule: Mapped["Schedule"] = relationship(back_populates="places")
    place: Mapped["Place"] = relationship()
