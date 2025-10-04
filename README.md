# Celeste X

Celeste X modernises the legacy Visual Basic + Access tool used to compute the
mechanical and geometric parameters of overhead power lines. This repository
contains the FastAPI backend, the SQLAdmin dashboard, the React front-end and
tooling required to run the first iteration locally.

## Project structure

```
backend/
  app/
    api/               # REST API routers
    core/              # Shared configuration helpers
    models/            # SQLAlchemy models
    main.py            # FastAPI application serving API + React build
  admin/
    main.py            # SQLAdmin dashboard (HTTP Basic Auth protected)
scripts/
  import_cables.py     # Placeholder for future XML import logic
frontend/              # Vite + React + TypeScript application
  dist/                # Production build output (created by `npm run build`)
data/
  celestex.db          # SQLite database (created on first run)
```

## Requirements

- Python 3.11
- Node.js 18+ (tested with Node 22)

Install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install front-end dependencies:

```bash
cd frontend
npm install
cd ..
```

## Running the applications

### 1. Build the React front-end

The FastAPI backend serves the static build from `frontend/dist`. Generate the
assets before starting the API service:

```bash
cd frontend
npm run build
cd ..
```

### 2. Start the main FastAPI application (port 6000)

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 6000 --reload
```

The application exposes:

- `GET /api/health` returning `{ "status": "ok" }`
- `GET /api/calc/span` placeholder endpoint
- React single-page application from the build output with SPA fallback

Visit `http://<IP_VM>:6000` to access the UI.

### 3. Start the SQLAdmin dashboard (port 8000)

Set the required environment variables and launch Uvicorn:

```bash
export ADMIN_USER=admin
export ADMIN_PASS=change-me
export ADMIN_SECRET=super-secret-key
uvicorn backend.admin.main:app --host 0.0.0.0 --port 8000 --reload
```

The dashboard is protected with HTTP Basic Auth (same credentials as above) and
provides CRUD access to the `cables` table at `http://<IP_VM>:8000`.

### Sample systemd units

Two unit file templates are available in the `deploy/` directory:

- `celestex.service` for the main FastAPI application (port 6000)
- `celestex-admin.service` for the SQLAdmin dashboard (port 8000)

Adjust the absolute paths and environment variables before deploying to the
Debian VM, then enable with `systemctl enable --now <service>`.

## Data import placeholder

The `scripts/import_cables.py` module provides the scaffold for importing cable
data from the legacy XML files located at the repository root. The parser will
be implemented in a future iteration.
