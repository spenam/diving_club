# Diving Club Manager

A small, locally hosted inventory and equipment-loan application for a diving club.
The starter release uses Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic and
server-rendered HTML fragments with HTMX (plus small fetch helpers for forms). It is designed as a modular monolith so future
member, dive-event, site and finance modules can be added without splitting the
system into microservices.

## Included in this starter

- Equipment categories and individual equipment records
- Member records (manual member selection)
- Equipment availability states
- QR payload generation using a stable UUID
- Checkout and return API endpoints
- Loan history and basic web dashboard
- PostgreSQL persistence and Alembic migrations
- Docker Compose deployment
- pytest and Ruff checks in GitHub Actions

The first UI focuses on registering and viewing equipment and members. The loan
API is present as a starter interface; the next milestone should add the complete
camera/USB scanning workflow and incident-resolution screens.

## Requirements

- Linux host (Ubuntu/Debian recommended)
- Docker Engine and Docker Compose plugin
- Git
- A GitHub repository

## Quick start

1. Clone this repository.
2. Copy `.env.example` to `.env`.
3. Change `POSTGRES_PASSWORD` to a strong, unique value and update the password
   in `DATABASE_URL` to match it.
4. Start the stack and apply migrations:

   ```bash
   cp .env.example .env
   # Edit .env before continuing
   docker compose up -d --build
   docker compose exec backend alembic upgrade head
   ```

5. Open `http://<club-server-ip>:8080`.

The database is not published to the host or LAN. Only the web container exposes
port 8080. The backend is reachable by the web reverse proxy on the private
Docker network.

## Local development without Docker

Python 3.12+ and PostgreSQL are required.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
export DATABASE_URL='postgresql+psycopg://club:password@localhost:5432/diving_club'
alembic upgrade head
uvicorn app.main:app --reload
```

The development server serves the API at `http://localhost:8000` and interactive
API docs at `/docs`. The web frontend is served separately by nginx in Docker.
For quick backend-only development, `/` returns a small service response.

## QR codes and scanners

Each equipment item has a UUID that does not change if its name or database
primary key changes. The intended QR payload is `DCM:<uuid>`. A future frontend
scanner can decode that payload with the device camera. A USB QR scanner normally
acts as a keyboard and can enter the same payload into a focused input field.
Camera access from phones generally requires HTTPS (or localhost); plain HTTP
on a LAN may not qualify as a secure browser context.

## Network access from outside the club

This stack is local-first. Do not expose PostgreSQL or the backend directly to
the internet. For remote access, put an HTTPS reverse proxy or a VPN such as
WireGuard/Tailscale in front of the web service. Prefer VPN access for a small
club. Configure TLS, authentication, firewall rules and backups before allowing
remote use. The starter does not yet include user login/role management and
should not be treated as an internet-ready production service.

## Data and backups

PostgreSQL data lives in the named Docker volume `postgres_data`. A simple
logical backup can be made with:

```bash
docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup.sql
```

Restore only after stopping writes and reviewing the target database:

```bash
cat backup.sql | docker compose exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"
```

Keep encrypted off-host backups and test restoration. A Docker volume is not a
backup. Never commit `.env`, backups, member personal data or secrets to Git.

## GitHub Actions and releases

- `tests.yml`: runs Ruff and pytest on pushes and pull requests.
- `docker-build.yml`: builds and publishes backend/web images to GHCR on pushes
  to `main` and version tags.
- `deploy.yml`: optional deployment workflow for a self-hosted runner installed
  on the club Linux host. It runs only when manually dispatched. Protect that
  runner: use a dedicated low-privilege account, restrict repository access,
  and do not run untrusted pull-request code on it.

Set repository variables `GHCR_OWNER` (lowercase GitHub owner/org) and
`IMAGE_PREFIX` (for example `diving-club-manager`) for image publishing.
For local deployment via the optional runner, install Docker Compose and add
the repository secret `DEPLOY_ENV_FILE` only if your operational process
requires it; the safer default is to maintain `.env` directly on the host.

## Project layout

```text
backend/app/       FastAPI application, models, schemas, routes and services
backend/alembic/   Database migrations
web/               HTMX templates and nginx reverse proxy
docs/              Architecture and operational notes
.github/workflows/ CI, image publishing and optional local deployment
```

## Important next steps before real club use

1. Add authentication and roles (administrator, equipment manager, member).
2. Add incident reporting and an explicit safety hold/clearance workflow.
3. Add a proper camera scanner and keyboard-wedge USB scanner UI.
4. Add audit logging, concurrency tests and automated backups.
5. Add HTTPS/VPN for remote access.
6. Review privacy obligations applicable to your club and jurisdiction.

Equipment marked unavailable or under maintenance must never be checked out.
Safety-critical equipment must be inspected and cleared by an appropriately
qualified person before returning to service. This starter is not a substitute
for the club's equipment inspection procedures.
