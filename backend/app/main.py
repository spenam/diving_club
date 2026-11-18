from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.entities import Category, Equipment, EquipmentStatus, Loan, Member
from app.schemas import (
    CategoryCreate, CategoryRead, CheckoutRequest, EquipmentCreate, EquipmentRead,
    LoanRead, MemberCreate, MemberRead, ReturnRequest,
)
from app.services import checkout, return_equipment

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "diving-club-manager"}


@app.get("/api/v1/categories", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return list(db.scalars(select(Category).order_by(Category.name)))


@app.post("/api/v1/categories", response_model=CategoryRead, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(**payload.model_dump())
    db.add(category)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category name already exists")
    db.refresh(category)
    return category


@app.get("/api/v1/members", response_model=list[MemberRead])
def list_members(db: Session = Depends(get_db)):
    return list(db.scalars(select(Member).order_by(Member.last_name, Member.first_name)))


@app.post("/api/v1/members", response_model=MemberRead, status_code=201)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    member = Member(**payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@app.get("/api/v1/equipment", response_model=list[EquipmentRead])
def list_equipment(db: Session = Depends(get_db)):
    return list(db.scalars(select(Equipment).order_by(Equipment.name)))


@app.post("/api/v1/equipment", response_model=EquipmentRead, status_code=201)
def create_equipment(payload: EquipmentCreate, db: Session = Depends(get_db)):
    if db.get(Category, payload.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    item = Equipment(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/v1/equipment/qr/{equipment_uuid}", response_model=EquipmentRead)
def get_equipment_by_qr(equipment_uuid: str, db: Session = Depends(get_db)):
    item = db.scalar(select(Equipment).where(Equipment.uuid == equipment_uuid))
    if item is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return item


@app.post("/api/v1/loans/checkout", response_model=LoanRead, status_code=201)
def checkout_equipment(payload: CheckoutRequest, db: Session = Depends(get_db)):
    return checkout(db, payload.equipment_uuid, payload.member_id, payload.note)


@app.post("/api/v1/loans/return", response_model=LoanRead)
def return_loan(payload: ReturnRequest, db: Session = Depends(get_db)):
    return return_equipment(db, payload.equipment_uuid, payload.note)


@app.get("/api/v1/loans/active", response_model=list[LoanRead])
def active_loans(db: Session = Depends(get_db)):
    return list(db.scalars(select(Loan).where(Loan.returned_at.is_(None))))


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(
        "<html><body><h1>Diving Club Manager API</h1>"
        "<p>Backend is running. Open <a href='/docs'>API documentation</a>.</p></body></html>"
    )


@app.get("/ui/inventory", response_class=HTMLResponse)
def inventory_fragment(db: Session = Depends(get_db)):
    items = list(db.scalars(select(Equipment).order_by(Equipment.name)))
    rows = "".join(
        f"<tr><td>{item.name}</td><td>{item.status.value}</td><td><code>DCM:{item.uuid}</code></td></tr>"
        for item in items
    )
    return HTMLResponse(
        "<table><thead><tr><th>Equipment</th><th>Status</th><th>QR payload</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>" if items else "<p>No equipment registered yet.</p>"
    )


@app.get("/ui/members", response_class=HTMLResponse)
def members_fragment(db: Session = Depends(get_db)):
    members = list(db.scalars(select(Member).order_by(Member.last_name, Member.first_name)))
    rows = "".join(f"<li>{member.first_name} {member.last_name}</li>" for member in members)
    return HTMLResponse(f"<ul>{rows}</ul>" if members else "<p>No members registered yet.</p>")
