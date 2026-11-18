from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import EquipmentStatus


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class CategoryRead(CategoryCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class MemberCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str | None = None


class MemberRead(MemberCreate):
    id: int
    active: bool
    model_config = ConfigDict(from_attributes=True)


class EquipmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    category_id: int
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    notes: str | None = None


class EquipmentRead(BaseModel):
    id: int
    uuid: str
    name: str
    category_id: int
    manufacturer: str | None
    model: str | None
    serial_number: str | None
    status: EquipmentStatus
    notes: str | None
    model_config = ConfigDict(from_attributes=True)


class CheckoutRequest(BaseModel):
    equipment_uuid: str
    member_id: int
    note: str | None = None


class ReturnRequest(BaseModel):
    equipment_uuid: str
    note: str | None = None


class LoanRead(BaseModel):
    id: int
    equipment_id: int
    member_id: int
    borrowed_at: datetime
    returned_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
