from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Equipment, EquipmentStatus, Loan, Member, utcnow


def checkout(db: Session, equipment_uuid: str, member_id: int, note: str | None = None) -> Loan:
    equipment = db.scalar(
        select(Equipment).where(Equipment.uuid == equipment_uuid).with_for_update()
    )
    member = db.get(Member, member_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if member is None or not member.active:
        raise HTTPException(status_code=404, detail="Active member not found")
    if equipment.status != EquipmentStatus.AVAILABLE:
        raise HTTPException(status_code=409, detail="Equipment is not available")
    loan = Loan(equipment=equipment, member=member, checkout_note=note)
    equipment.status = EquipmentStatus.BORROWED
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_equipment(db: Session, equipment_uuid: str, note: str | None = None) -> Loan:
    equipment = db.scalar(
        select(Equipment).where(Equipment.uuid == equipment_uuid).with_for_update()
    )
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    loan = db.scalar(
        select(Loan).where(Loan.equipment_id == equipment.id, Loan.returned_at.is_(None))
    )
    if loan is None:
        raise HTTPException(status_code=409, detail="No active loan for this equipment")
    loan.returned_at = utcnow()
    loan.return_note = note
    equipment.status = EquipmentStatus.AVAILABLE
    db.commit()
    db.refresh(loan)
    return loan
