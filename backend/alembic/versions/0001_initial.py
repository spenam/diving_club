"""Initial inventory schema."""

import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    status = postgresql.ENUM(
        "AVAILABLE",
        "BORROWED",
        "MAINTENANCE",
        "OUT_OF_SERVICE",
        "RETIRED",
        name="equipment_status",
        create_type=False,
    )
    status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=False)
    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_members_last_name", "members", ["last_name"], unique=False)
    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("uuid", sa.String(36), nullable=False, unique=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("manufacturer", sa.String(120), nullable=True),
        sa.Column("model", sa.String(120), nullable=True),
        sa.Column("serial_number", sa.String(120), nullable=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("status", status, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.UniqueConstraint("serial_number", name="uq_equipment_serial_number"),
    )
    op.create_index("ix_equipment_uuid", "equipment", ["uuid"], unique=True)
    op.create_index("ix_equipment_name", "equipment", ["name"], unique=False)
    op.create_table(
        "loans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("equipment_id", sa.Integer(), sa.ForeignKey("equipment.id"), nullable=False),
        sa.Column("member_id", sa.Integer(), sa.ForeignKey("members.id"), nullable=False),
        sa.Column("borrowed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("checkout_note", sa.Text(), nullable=True),
        sa.Column("return_note", sa.Text(), nullable=True),
    )
    op.create_index("ix_loans_equipment_id", "loans", ["equipment_id"])
    op.create_index("ix_loans_member_id", "loans", ["member_id"])
    op.create_index(
        "uq_active_loan_per_equipment",
        "loans",
        ["equipment_id"],
        unique=True,
        postgresql_where=sa.text("returned_at IS NULL"),
        sqlite_where=sa.text("returned_at IS NULL"),
    )
    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("equipment_id", sa.Integer(), sa.ForeignKey("equipment.id"), nullable=False),
        sa.Column("loan_id", sa.Integer(), sa.ForeignKey("loans.id"), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(30), nullable=False),
        sa.Column("reported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution", sa.Text(), nullable=True),
    )
    op.create_index("ix_incidents_equipment_id", "incidents", ["equipment_id"])
    op.create_table(
        "maintenance_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("equipment_id", sa.Integer(), sa.ForeignKey("equipment.id"), nullable=False),
        sa.Column("maintenance_type", sa.String(80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("performed_by", sa.String(160), nullable=True),
        sa.Column("next_inspection", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_maintenance_records_equipment_id", "maintenance_records", ["equipment_id"])


def downgrade():
    op.drop_table("maintenance_records")
    op.drop_table("incidents")
    op.drop_index("uq_active_loan_per_equipment", table_name="loans")
    op.drop_table("loans")
    op.drop_index("ix_equipment_name", table_name="equipment")
    op.drop_index("ix_equipment_uuid", table_name="equipment")
    op.drop_table("equipment")
    op.drop_index("ix_members_last_name", table_name="members")
    op.drop_table("members")
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")
    sa.Enum(name="equipment_status").drop(op.get_bind(), checkfirst=True)
