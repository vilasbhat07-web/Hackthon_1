
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Importing this module retains the original facility models.  Application
# feature tables live in app.platform_models to keep the legacy schema clear.


class Campus(Base):
    __tablename__ = "campuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    location: Mapped[str | None] = mapped_column(String(200))
    timezone: Mapped[str] = mapped_column(
        String(50), default="Asia/Kolkata", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    buildings: Mapped[list["Building"]] = relationship(
        back_populates="campus"
    )


class Building(Base):
    __tablename__ = "buildings"
    __table_args__ = (
        UniqueConstraint("campus_id", "name", name="uq_building_campus_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campus_id: Mapped[int] = mapped_column(
        ForeignKey("campuses.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    building_code: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    campus: Mapped["Campus"] = relationship(back_populates="buildings")
    floors: Mapped[list["Floor"]] = relationship(back_populates="building")


class Floor(Base):
    __tablename__ = "floors"
    __table_args__ = (
        UniqueConstraint("building_id", "floor_number", name="uq_building_floor"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    building_id: Mapped[int] = mapped_column(
        ForeignKey("buildings.id"), nullable=False
    )
    floor_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String(100))

    building: Mapped["Building"] = relationship(back_populates="floors")
    rooms: Mapped[list["Room"]] = relationship(back_populates="floor")


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (
        UniqueConstraint("floor_id", "room_code", name="uq_floor_room_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    floor_id: Mapped[int] = mapped_column(
        ForeignKey("floors.id"), nullable=False
    )
    room_code: Mapped[str] = mapped_column(String(50), nullable=False)
    room_type: Mapped[str | None] = mapped_column(String(100))
    area_sq_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    floor: Mapped["Floor"] = relationship(back_populates="rooms")
    equipment: Mapped[list["Equipment"]] = relationship(
        back_populates="room"
    )


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"), nullable=False
    )
    asset_tag: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    equipment_type: Mapped[str] = mapped_column(String(80), nullable=False)
    rated_power_kw: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    room: Mapped["Room"] = relationship(back_populates="equipment")
