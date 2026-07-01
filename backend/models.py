from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, CheckConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default='viewer')
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'viewer')", name="check_role"),
    )

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    subsystem = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    severity = Column(String, nullable=False, default='medium')
    status = Column(String, nullable=False, default='active')
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        CheckConstraint("subsystem IN ('smart_home', 'autonomous_car', 'smart_train', 'ev_charging', 'smart_parking', 'warehouse')", name="check_subsystem"),
        CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')", name="check_severity"),
        CheckConstraint("status IN ('active', 'resolved')", name="check_status"),
        Index("idx_incidents_status", "status"),
        Index("idx_incidents_subsystem", "subsystem"),
    )

    resolver = relationship("User", foreign_keys=[resolved_by])

class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, index=True)
    subsystem = Column(String, nullable=False)
    metric_key = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    recorded_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_telemetry_subsystem_key", "subsystem", "metric_key"),
        Index("idx_telemetry_recorded_at", "recorded_at"),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False)
    details = Column(Text)
    ip_address = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_audit_user", "user_id"),
    )