"""Additive application tables.  All analytical outputs are estimates."""
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(150))
    password_hash: Mapped[str] = mapped_column(String(512))
    role: Mapped[str] = mapped_column(String(30), default="VIEWER", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

class ForecastHistory(Base):
    __tablename__ = "forecast_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int | None] = mapped_column(ForeignKey("buildings.id"), index=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    method: Mapped[str] = mapped_column(String(100))
    horizon_hours: Mapped[int] = mapped_column(Integer)
    result_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int | None] = mapped_column(ForeignKey("buildings.id"), index=True)
    severity: Mapped[str] = mapped_column(String(20))
    kind: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(Text)
    details_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

class OptimizationRun(Base):
    __tablename__ = "optimization_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), index=True)
    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    baseline_kwh: Mapped[float] = mapped_column(Numeric(12,4))
    optimized_kwh: Mapped[float] = mapped_column(Numeric(12,4))
    savings_kwh: Mapped[float] = mapped_column(Numeric(12,4))
    result_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[int] = mapped_column(primary_key=True)
    optimization_run_id: Mapped[int] = mapped_column(ForeignKey("optimization_runs.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    detail: Mapped[str] = mapped_column(Text)
    estimated_savings_kwh: Mapped[float] = mapped_column(Numeric(12,4))

class ElectricityTariff(Base):
    __tablename__ = "electricity_tariffs"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    rate_per_kwh: Mapped[float] = mapped_column(Numeric(10,4))
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class CarbonEmissionFactor(Base):
    __tablename__ = "carbon_emission_factors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    kg_co2e_per_kwh: Mapped[float] = mapped_column(Numeric(10,4))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    report_type: Mapped[str] = mapped_column(String(50))
    content_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(100))
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

class AIExplanationHistory(Base):
    __tablename__ = "ai_explanation_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    subject: Mapped[str] = mapped_column(String(50))
    explanation: Mapped[str] = mapped_column(Text)
    input_json: Mapped[str] = mapped_column(Text)
