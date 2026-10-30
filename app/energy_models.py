from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# 1. DATA SOURCE
# Tracks whether information is measured, simulated, estimated, or assumed.

class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    source_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    # MEASURED, SIMULATED, ESTIMATED, ASSUMPTION

    description: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )


# 2. ENERGY READINGS
# Stores electricity consumption and power information.

class EnergyReading(Base):
    __tablename__ = "energy_readings"

    __table_args__ = (
        Index("ix_energy_equipment_timestamp", "equipment_id", "timestamp"),
        Index("ix_energy_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    equipment_id: Mapped[int | None] = mapped_column(
        ForeignKey("equipment.id"), nullable=True
    )

    building_id: Mapped[int] = mapped_column(
        ForeignKey("buildings.id"), nullable=False
    )

    data_source_id: Mapped[int] = mapped_column(
        ForeignKey("data_sources.id"), nullable=False
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )

    interval_minutes: Mapped[int] = mapped_column(
        Integer, default=15, nullable=False
    )

    power_kw: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4)
    )

    energy_kwh: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False
    )

    reading_status: Mapped[str] = mapped_column(
        String(30), default="VALID", nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )


# 3. OCCUPANCY READINGS
# Stores the number of people present in a building.

class OccupancyReading(Base):
    __tablename__ = "occupancy_readings"

    __table_args__ = (
        Index("ix_occupancy_building_timestamp", "building_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    building_id: Mapped[int] = mapped_column(
        ForeignKey("buildings.id"), nullable=False
    )

    data_source_id: Mapped[int] = mapped_column(
        ForeignKey("data_sources.id"), nullable=False
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )

    occupancy_count: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )


# 4. WEATHER READINGS
# Stores environmental information for energy analysis.

class WeatherReading(Base):
    __tablename__ = "weather_readings"

    __table_args__ = (
        Index("ix_weather_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    data_source_id: Mapped[int] = mapped_column(
        ForeignKey("data_sources.id"), nullable=False
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )

    temperature_c: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2)
    )

    humidity_percent: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2)
    )

    weather_location: Mapped[str | None] = mapped_column(
        String(150)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )