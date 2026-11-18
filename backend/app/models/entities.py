import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow():
    return datetime.now(UTC)


class EquipmentStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"
    RETIRED = "RETIRED"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    equipment: Mapped[list["Equipment"]] = relationship(back_populates="category")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100), index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    loans: Mapped[list["Loan"]] = relationship(back_populates="member")


class Equipment(Base):
    __tablename__ = "equipment"
    __table_args__ = (UniqueConstraint("serial_number", name="uq_equipment_serial_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    name: Mapped[str] = mapped_column(String(160), index=True)
    manufacturer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    status: Mapped[EquipmentStatus] = mapped_column(
        Enum(EquipmentStatus, name="equipment_status"),
        default=EquipmentStatus.AVAILABLE,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[Category] = relationship(back_populates="equipment")
    loans: Mapped[list["Loan"]] = relationship(back_populates="equipment")
    incidents: Mapped[list["Incident"]] = relationship(back_populates="equipment")
    maintenance_records: Mapped[list["MaintenanceRecord"]] = relationship(
        back_populates="equipment"
    )


class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = (
        Index(
            "uq_active_loan_per_equipment",
            "equipment_id",
            unique=True,
            postgresql_where=(__import__("sqlalchemy").text("returned_at IS NULL")),
            sqlite_where=(__import__("sqlalchemy").text("returned_at IS NULL")),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    borrowed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    checkout_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    return_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    equipment: Mapped[Equipment] = relationship(back_populates="loans")
    member: Mapped[Member] = relationship(back_populates="loans")
    incidents: Mapped[list["Incident"]] = relationship(back_populates="loan")


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), index=True)
    loan_id: Mapped[int | None] = mapped_column(ForeignKey("loans.id"), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(30), default="UNASSESSED")
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    equipment: Mapped[Equipment] = relationship(back_populates="incidents")
    loan: Mapped[Loan | None] = relationship(back_populates="incidents")


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), index=True)
    maintenance_type: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    performed_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    next_inspection: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    equipment: Mapped[Equipment] = relationship(back_populates="maintenance_records")
