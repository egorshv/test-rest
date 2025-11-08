from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (CheckConstraint("level BETWEEN 1 AND 3", name="activity_level_range"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("activities.id", ondelete="SET NULL"), nullable=True, index=True
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    parent: Mapped["Activity | None"] = relationship(
        "Activity", remote_side="Activity.id", back_populates="children", uselist=False
    )
    children: Mapped[list["Activity"]] = relationship("Activity", back_populates="parent", cascade="all")
    organizations: Mapped[list["Organization"]] = relationship(
        "Organization", secondary="organization_activities", back_populates="activities"
    )
