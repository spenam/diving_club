# Architecture

The system is a modular monolith.

- `web`: nginx serves the HTMX-oriented browser UI and reverse-proxies `/api/`.
- `backend`: FastAPI owns validation, business rules and persistence.
- `db`: PostgreSQL stores durable club data.
- SQLAlchemy models live in `backend/app/models`.
- Alembic migrations are versioned in `backend/alembic/versions`.

The browser must never connect directly to PostgreSQL. Keep the database port
unpublished. Future modules should follow the same pattern: model/schema, API
router, service/business rules and tests.

Equipment UUIDs are permanent public identifiers for QR labels. Internal integer
primary keys remain database implementation details.
