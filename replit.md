# PDP-Container — Trusted User Verification Simulation

## Overview
A Django-based simulation tool for the "PDP-Container" (Trusted User Verification) system. It simulates security risk assessment for user requests, calculates risk scores based on various factors, and visualizes results with charts.

## Tech Stack
- **Framework:** Django 5.0 (Python 3.11)
- **Data Analysis:** pandas
- **Visualization:** matplotlib (Agg backend for server-side image generation)
- **Dependency Management:** Poetry (`pyproject.toml`)
- **Database:** SQLite (`db.sqlite3`)

## Project Structure
- `django_project/` — Django configuration (settings, URLs, WSGI/ASGI)
- `tasks/` — Main application logic
  - `views.py` — Simulation logic (`run_pdp_simulation`) and index view
  - `static/tasks/` — Generated chart images (risk_bar.png, decision_pie.png, risk_trend.png)
  - `templates/index.html` — Frontend dashboard
- `deploy.sh` — Deployment script (install deps, migrate, collect static, run server)
- `manage.py` — Django CLI utility

## Running the App
The workflow runs: `PORT=5000 ./deploy.sh`
This installs dependencies, runs migrations, collects static files, and starts the Django server on port 5000.

## Key Configuration
- **Port:** 5000 (webview)
- **Threshold:** Configurable via `THRESHOLD` env variable (default: 95)
- **Secret keys:** `IMP_S1_KASHIN`, `IMP_S2_KASHIN`, `IMP_S3_KASHIN` (optional, set via Replit Secrets)

## Simulation Logic
On each page load (`/`):
1. Generates 16 mock requests with randomized risk metrics
2. Calculates weighted risk scores (token/IP/device mismatch + replay detection)
3. Decides "Allowed" or "Blocked" based on threshold
4. Saves three PNG charts to `tasks/static/tasks/`
5. Renders the dashboard with a data table and charts
