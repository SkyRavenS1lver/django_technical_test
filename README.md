# Event Management System

A RESTful API and frontend for managing technical events and conferences, built with Django 5, Django REST Framework, PostgreSQL, JWT authentication, and an HTMX + Tailwind CSS frontend.

---

## Table of Contents

- [Stack](#stack)
- [Features](#features)
- [Setup — Local Development](#setup--local-development)
- [Setup — Docker](#setup--docker)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Architecture & Decisions](#architecture--decisions)
- [Third-party Libraries](#third-party-libraries)

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2, Django REST Framework 3.15 |
| Auth | JWT via `djangorestframework-simplejwt` |
| Database | PostgreSQL 16 |
| Frontend | Django Templates + HTMX + Tailwind CSS v4 |
| API Docs | drf-spectacular (OpenAPI 3.0 / Swagger UI) |
| Container | Docker + Docker Compose |

---

## Features

- **Event Management** — CRUD with status (`draft` / `published` / `cancelled`), capacity, venue, and banner image
- **Track Management** — Organise sessions into colour-coded tracks per event
- **Session Scheduling** — Schedule sessions with speaker, room, and type; **overlap detection** prevents double-booking within a track
- **Attendee Registration** — Register for events; automatic **waitlist** when at capacity; duplicate prevention
- **Role-based permissions** — Organiser vs. attendee; JWT-secured API; rate limiting (100/hr anon, 1000/hr authenticated)
- **API Versioning** — URL path versioning (`/api/v1/`, `/api/v2/`, …)
- **Interactive Docs** — Swagger UI at `/api/v1/docs/`
- **HTMX Frontend** — Full template-driven UI with live registration button swaps

---

## Setup — Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Node.js 20+ (for Tailwind CSS)

### Steps

```bash
# 1. Clone
git clone https://github.com/SkyRavenS1lver/django_technical_test.git
cd django_technical_test

# 2. Create and activate virtualenv
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt   # debug toolbar, extensions

# 4. Configure environment
cp .env.example .env
# Edit .env — set SECRET_KEY, DB_* credentials, DJANGO_SETTINGS_MODULE=event_management_system.settings.development

# 5. Create the database
createdb event_management_system   # or use psql

# 6. Run migrations
python manage.py migrate

# 7. Create a superuser (optional)
python manage.py createsuperuser

# 8. Build Tailwind CSS (keep this running in a separate terminal)
python manage.py tailwind start

# 9. Start the development server
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000)

---

## Setup — Docker

### Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose v2)

### Steps

```bash
# 1. Clone
git clone https://github.com/SkyRavenS1lver/django_technical_test.git
cd django_technical_test

# 2. Configure environment
cp .env.example .env
# Edit .env — set a strong SECRET_KEY, DB_NAME, DB_USER, DB_PASSWORD
# Leave DB_HOST as "db" (set automatically by docker-compose.yml)

# 3. Build and start
docker compose up --build

# 4. (Optional) Create a superuser
docker compose exec app python manage.py createsuperuser
```

Visit [http://localhost:8000](http://localhost:8000)

The entrypoint automatically runs `migrate` and `collectstatic` before starting Gunicorn.

---

## API Reference

Full interactive documentation is available at **`/api/v1/docs/`** once the server is running.

### Base URL

```
http://localhost:8000/api/v1/
```

### Authentication

All write endpoints require a JWT Bearer token:

```http
Authorization: Bearer <access_token>
```

Obtain tokens via `POST /api/v1/auth/login/`.

### Endpoints

#### Auth

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/auth/register/` | Register a new user | Public |
| POST | `/api/v1/auth/login/` | Obtain JWT tokens | Public |
| POST | `/api/v1/auth/refresh/` | Refresh access token | Public |
| POST | `/api/v1/auth/logout/` | Blacklist refresh token | Required |
| GET / PATCH | `/api/v1/auth/me/` | Get / update own profile | Required |

#### Events

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/v1/events/` | List published events | Public |
| POST | `/api/v1/events/` | Create an event | Organiser |
| GET | `/api/v1/events/{slug}/` | Event detail | Public |
| PATCH | `/api/v1/events/{slug}/` | Update event | Organiser (owner) |
| DELETE | `/api/v1/events/{slug}/` | Delete event | Organiser (owner) |
| GET / POST | `/api/v1/events/{slug}/tracks/` | List / add tracks | GET: Public, POST: Organiser |
| GET | `/api/v1/events/{slug}/sessions/` | List sessions for event | Public |
| POST | `/api/v1/events/{slug}/register/` | Register for event | Authenticated |
| GET | `/api/v1/events/{slug}/registrations/` | List event registrations | Organiser (owner) |

#### Tracks

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/v1/tracks/` | List tracks | Public |
| GET / PATCH / DELETE | `/api/v1/tracks/{id}/` | Track detail / update / delete | PATCH/DELETE: Organiser |

#### Sessions & Speakers

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/v1/sessions/` | List sessions | Public |
| POST | `/api/v1/sessions/` | Create session | Organiser (event owner) |
| GET / PATCH / DELETE | `/api/v1/sessions/{id}/` | Session detail / update / delete | PATCH/DELETE: Organiser |
| GET / POST | `/api/v1/speakers/` | List / create speakers | POST: Authenticated |
| GET / PATCH / DELETE | `/api/v1/speakers/{id}/` | Speaker detail / update / delete | Authenticated |

#### Registrations

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/v1/registrations/` | List own registrations | Authenticated |
| POST | `/api/v1/registrations/` | Register for an event | Authenticated |
| GET / PATCH | `/api/v1/registrations/{id}/` | Detail / cancel registration | Authenticated (own) |

### Filtering & Search

Events support filtering via query parameters:

```
GET /api/v1/events/?status=published
GET /api/v1/events/?search=django
GET /api/v1/events/?ordering=-start_date
```

Sessions support:
```
GET /api/v1/sessions/?track=1&session_type=keynote
GET /api/v1/sessions/?start_from=2025-01-01T09:00:00Z
```

---

## Testing

### Run Tests

```bash
# Activate virtualenv first
source venv/bin/activate

python manage.py test app.accounts app.events app.tracks app.sessions app.registrations
```

### Run with Coverage

```bash
pip install coverage
coverage run manage.py test app.accounts app.events app.tracks app.sessions app.registrations
coverage report --include="app/*/models.py,app/*/serializers.py,app/*/views.py"
```

**Current coverage (API layer):**

| Layer | Coverage |
|---|---|
| Models | 80–100% |
| Serializers | 88–100% |
| API Views | 61–88% |

### Test Suite Covers

- User model creation and email-based auth
- JWT register / login / logout / me endpoints
- Event CRUD with slug auto-generation and date validation
- Organiser-only permission enforcement (403 for non-owners)
- Track creation and unique-name constraint per event
- Session overlap detection (same track → 400, different tracks → 201)
- Back-to-back sessions (allowed)
- Registration confirmed → waitlisted at capacity → duplicate rejected

---

## Architecture & Decisions

### App Structure

Each Django app follows a strict separation:

```
app/<name>/
├── models.py        # Data layer — constraints in Meta + clean()
├── serializers.py   # Validation layer — business rules in validate()
├── views.py         # API ViewSets (JSON only)
├── pages.py         # Template views (HTML/HTMX only)
├── urls.py          # /api/v1/ routes
├── page_urls.py     # Frontend routes
├── filters.py       # django-filters FilterSet
├── permissions.py   # Custom DRF permissions
└── admin.py
```

### Key Decisions

| Decision | Rationale |
|---|---|
| Overlap detection at both model (`clean()`) and serializer (`validate()`) | `clean()` guards the admin and direct ORM saves; serializer catches API requests with a proper 400 instead of a 500 |
| Auto-waitlist on capacity | Better UX than hard rejection; attendees can gain a spot if others cancel |
| Slug auto-generated from title with collision suffix | Human-readable URLs without requiring user input |
| Template views separate from API views | Keeps API pure JSON; pages.py handles all HTML rendering |
| `select_related` / `prefetch_related` on all list queries | Prevents N+1 queries on event lists with organiser and track data |
| URL path versioning (`/api/<version>/`) | Allows future `/api/v2/` without breaking existing clients |
| Tailwind pre-built in Docker Stage 1 | Eliminates Node.js from the production runtime image |

### Caching

The public event list (`GET /api/v1/events/`) is cached using a **cache-aside pattern** with **version-based invalidation**:

- **What is cached**: Unauthenticated event list responses only. Authenticated responses are never cached because organizers see their own draft events.
- **Cache key**: `events:list:{version}:{full_path}` — includes query parameters (filters, page, ordering) so each unique query has its own entry.
- **Invalidation**: Any event create, update, or delete atomically increments a version counter in cache. All existing list keys — across all pages and filter combinations — become stale instantly without needing `delete_pattern`.
- **TTL**: 5 minutes (`CACHE_TTL = 300`).
- **Backends**:
  - Development: `LocMemCache` (built-in, no Redis required)
  - Production: `django-redis` — set `REDIS_URL` in `.env`

```
docker-compose.yml includes a redis:7-alpine service wired to the app automatically.
```

### Logging

Structured logging is configured in `settings/base.py` with three named loggers:

| Logger | Level | Purpose |
|---|---|---|
| `django` | INFO | Framework-level request/response and errors |
| `django.security` | WARNING | Auth failures, CSRF violations, permission denials |
| `app` | INFO | All `app.*` module loggers (views, serializers, etc.) |

Key business events are logged in each app's `views.py`:

- `app.accounts` — user registered, user logged out
- `app.events` — event created
- `app.sessions` — session created
- `app.registrations` — registration confirmed / waitlisted / cancelled

Logs are written to both the console and `logs/app.log` via a `RotatingFileHandler` (10 MB max, 5 backups). In development, the log level is lowered to `DEBUG` for all `app.*` loggers.

---

## Third-party Libraries

| Library | Version | Purpose |
|---|---|---|
| `djangorestframework` | 3.15 | RESTful API framework |
| `djangorestframework-simplejwt` | 5.3 | JWT authentication + token blacklist |
| `drf-spectacular` | 0.27 | OpenAPI 3.0 schema + Swagger UI |
| `django-filter` | 24.3 | Declarative queryset filtering |
| `django-htmx` | 1.19 | HTMX request detection middleware |
| `django-tailwind` | 4.4 | Tailwind CSS integration for Django |
| `python-decouple` | 3.8 | Environment variable management |
| `psycopg` | 3.2 | PostgreSQL async-capable driver |
| `pillow` | 10.4 | Image upload handling (banner, avatar, speaker photo) |
| `whitenoise` | 6.7 | Serve static files from Django in production |
| `gunicorn` | 22.0 | Production WSGI server |
