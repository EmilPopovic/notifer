# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**NotiFER** is a web service that monitors FER (Faculty of Electrical Engineering and Computing, Zagreb) student timetable calendars via ICS feeds and sends email notifications when schedule changes are detected.

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start development environment (API + PostgreSQL + Worker)
docker compose -f compose.dev.yaml up --build -d

# Initialize database tables
make initdb COMPOSE_FILE=compose.dev.yaml
```

## Database Management

```bash
make initdb COMPOSE_FILE=compose.dev.yaml    # Create tables
make resetdb COMPOSE_FILE=compose.dev.yaml   # Drop and recreate all tables
make dropdb COMPOSE_FILE=compose.dev.yaml    # Drop all tables
make checkdb COMPOSE_FILE=compose.dev.yaml   # Check table status
make encryptdb COMPOSE_FILE=compose.dev.yaml # Encrypt plaintext calendar_auth values (idempotent)
```

These commands run `db_manager.py` inside the running container.

## Architecture

The app runs two concurrent threads from `src/run.py`:

- **API thread**: FastAPI server on port 8026 handling HTTP requests
- **Worker thread**: Background polling loop that checks calendars for changes and queues notification emails

### Source layout

```
src/
├── run.py                    # Entry point — starts API + Worker threads
├── config.py                 # Pydantic settings loaded from env vars
├── db_manager.py             # CLI for DB init/reset/drop/check/encrypt
├── api/
│   ├── main.py               # FastAPI app + route registration
│   ├── routers/
│   │   ├── subscriptions.py  # Student self-service endpoints
│   │   ├── admin.py          # Admin endpoints (token-protected)
│   │   ├── health.py         # Health + metrics
│   │   └── frontend.py       # Static HTML serving
│   └── services/
│       ├── subscription_service.py
│       ├── email_service.py
│       └── template_service.py  # Jinja2 + i18n rendering
├── worker/
│   ├── main.py               # Standalone worker entry point
│   └── services/
│       ├── worker_service.py     # Main polling loop
│       └── calendar_service.py  # Change detection + email queuing
└── shared/
    ├── models.py             # SQLAlchemy ORM — single `user_calendars` table
    ├── crud.py               # All DB queries
    ├── database.py           # Engine + session factory
    ├── encryption.py         # Fernet TypeDecorator for calendar_auth at-rest encryption
    ├── email_client.py       # Thread-safe email queue
    ├── email_sender.py       # SMTP sending
    ├── email_templates.py    # HTML email templates (Croatian/English)
    ├── calendar_utils.py     # ICS parsing + diff/change detection
    ├── token_utils.py        # JWT generation/validation
    └── storage_manager.py    # Local ICS file caching
```

### Key data flow

1. Student subscribes → pending `user_calendars` row created, activation email sent (JWT link)
2. Student clicks activation link → row marked active
3. Worker polls at `WORKER_INTERVAL` seconds → downloads ICS, hashes content, compares to stored hash
4. On change detected → notification email queued via `email_client.py`, hash updated in DB
5. Email sender drains queue at `EMAIL_RATE_LIMIT_PER_SECOND`

### Database

Single table `user_calendars` with composite primary key `(username, domain)`. Stores calendar auth token, activation state, language preference, ICS hash, and change history timestamps.

### Feature flags (env vars)

Features can be toggled independently:
- `STUDENT_SIGNUP`, `STUDENT_PAUSE`, `STUDENT_RESUME`, `STUDENT_DELETE` — self-service operations
- `ADMIN_API`, `FRONTEND` — module toggles
- `WORKER` — enable/disable background polling

## Environment Variables

Copy `.env.example` and fill in values. Key vars:

| Variable | Purpose |
|---|---|
| `POSTGRES_*` | Database connection |
| `SMTP_*` | Email sending |
| `JWT_KEY` | Token signing |
| `ENCRYPTION_KEY` | Fernet key for `calendar_auth` at-rest encryption — generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`, then run `make encryptdb` on existing deployments |
| `NOTIFER_API_TOKEN_HASH` | SHA256 hash of admin API token |
| `API_URL` | Base URL used in email links |
| `BASE_CALENDAR_URL` | FER ICS calendar URL template |
| `WORKER_INTERVAL` | Seconds between calendar checks (default 3600) |
| `RECIPIENT_DOMAIN` | Allowed email domain (default `fer.hr`) |

## Deployment

```bash
# Production
docker compose -f compose.yaml up -d
make initdb

# CI/CD builds and pushes to GHCR on pushes to master
# Image: ghcr.io/emilpopovic/notifer:latest
```

## Internationalization

Email templates and UI support Croatian (`hr`) and English (`en`). Templates live in `templates/` and are rendered via `api/services/template_service.py` using Jinja2. Email-specific templates are in `shared/email_templates.py`.
