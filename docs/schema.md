# API Schema Reference

Base URL: `http://localhost:8000/api/v1`

Interactive Swagger UI: [`/api/v1/docs/`](http://localhost:8000/api/v1/docs/)
OpenAPI schema (JSON/YAML): [`/api/v1/schema/`](http://localhost:8000/api/v1/schema/)

---

## Authentication

All protected endpoints require:
```http
Authorization: Bearer <access_token>
```

---

## Auth Endpoints

### `POST /auth/register/`
Register a new user and receive tokens immediately.

**Request**
```json
{
  "email": "alice@example.com",
  "name": "Alice",
  "password": "securepassword",
  "is_organizer": true
}
```

**Response `201`**
```json
{
  "user": {
    "id": 1,
    "email": "alice@example.com",
    "name": "Alice",
    "is_organizer": true
  },
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>"
}
```

---

### `POST /auth/login/`
**Request**
```json
{ "email": "alice@example.com", "password": "securepassword" }
```

**Response `200`**
```json
{ "access": "<jwt_access_token>", "refresh": "<jwt_refresh_token>" }
```

**Response `401`** — invalid credentials.

---

### `POST /auth/refresh/`
**Request**
```json
{ "refresh": "<jwt_refresh_token>" }
```

**Response `200`**
```json
{ "access": "<new_access_token>", "refresh": "<new_refresh_token>" }
```

---

### `POST /auth/logout/`
Blacklists the refresh token. Requires `Authorization` header.

**Request**
```json
{ "refresh": "<jwt_refresh_token>" }
```

**Response `204`** — no content.

---

### `GET /auth/me/`
Returns the authenticated user's profile.

**Response `200`**
```json
{
  "id": 1,
  "email": "alice@example.com",
  "name": "Alice",
  "bio": "",
  "is_organizer": true
}
```

### `PATCH /auth/me/`
Update name or bio (email is read-only).

**Request**
```json
{ "name": "Alice Smith", "bio": "Django developer" }
```

---

## Event Endpoints

### `GET /events/`
List published events. Organiser also sees their own drafts.

**Query parameters**

| Param | Example | Description |
|---|---|---|
| `status` | `published` | Filter by status |
| `search` | `django` | Search title, description, venue |
| `ordering` | `-start_date` | Sort field (prefix `-` for desc) |
| `page` | `2` | Pagination (20 per page) |

**Response `200`**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "DjangoCon 2025",
      "slug": "djangocon-2025",
      "start_date": "2025-09-15T09:00:00Z",
      "end_date": "2025-09-17T18:00:00Z",
      "venue_name": "Convention Centre",
      "max_attendees": 500,
      "status": "published",
      "banner": null,
      "organizer_name": "Alice"
    }
  ]
}
```

---

### `POST /events/`
Create an event. Requires `is_organizer=true`.

**Request**
```json
{
  "title": "DjangoCon 2025",
  "description": "The annual Django conference.",
  "start_date": "2025-09-15T09:00:00Z",
  "end_date": "2025-09-17T18:00:00Z",
  "venue_name": "Convention Centre",
  "venue_address": "123 Main St, City",
  "max_attendees": 500,
  "status": "draft"
}
```

**Response `201`** — same fields as request (slug auto-generated from title).

**Response `403`** — user is not an organiser.

---

### `GET /events/{slug}/`
Full event detail including nested tracks.

**Response `200`**
```json
{
  "id": 1,
  "title": "DjangoCon 2025",
  "slug": "djangocon-2025",
  "description": "...",
  "start_date": "2025-09-15T09:00:00Z",
  "end_date": "2025-09-17T18:00:00Z",
  "venue_name": "Convention Centre",
  "venue_address": "123 Main St",
  "max_attendees": 500,
  "status": "published",
  "banner": null,
  "organizer_name": "Alice",
  "tracks": [
    { "id": 1, "name": "Backend", "color": "#6366f1", "description": "" }
  ],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

---

### `GET /events/{slug}/tracks/`
List tracks for an event.

### `POST /events/{slug}/tracks/`
Add a track to an event. Only the event organiser can do this.

**Request**
```json
{ "name": "Backend", "color": "#6366f1", "description": "Server-side topics" }
```

**Response `201`** — track object.
**Response `400`** — duplicate track name for this event.
**Response `403`** — not the event organiser.

---

### `GET /events/{slug}/sessions/`
List all sessions for an event ordered by start time.

---

### `POST /events/{slug}/register/`
Register the authenticated user for this event.

**Response `201`**
```json
{
  "id": 5,
  "event": "djangocon-2025",
  "attendee": "bob@example.com",
  "registered_at": "2025-01-10T10:00:00Z",
  "status": "confirmed"
}
```

**Response `201`** with `"status": "waitlisted"` — event is at capacity.
**Response `400`** — already registered.

---

### `GET /events/{slug}/registrations/`
List all registrations for this event. Only the event organiser.

---

## Track Endpoints

### `GET /tracks/`
List all tracks across all events.

### `GET /tracks/{id}/`
Track detail.

### `PATCH /tracks/{id}/`
Update track. Only the event organiser.

**Request**
```json
{ "name": "Frontend", "color": "#f59e0b" }
```

### `DELETE /tracks/{id}/`
Delete a track and all its sessions. Only the event organiser.

---

## Session Endpoints

### `GET /sessions/`
List sessions.

**Query parameters**

| Param | Example | Description |
|---|---|---|
| `track` | `1` | Filter by track ID |
| `speaker` | `3` | Filter by speaker ID |
| `session_type` | `keynote` | Filter by type |
| `start_from` | `2025-09-15T09:00:00Z` | Sessions starting at or after |
| `start_to` | `2025-09-15T18:00:00Z` | Sessions starting at or before |

---

### `POST /sessions/`
Create a session. Must be the organiser of the session's track's event.

**Request**
```json
{
  "title": "Scaling Django with async",
  "description": "Deep dive into async views and ORM.",
  "track": 1,
  "speaker": 2,
  "start_time": "2025-09-15T10:00:00Z",
  "end_time": "2025-09-15T11:00:00Z",
  "room": "Hall A",
  "session_type": "talk",
  "capacity": null
}
```

**Response `201`** includes `effective_capacity` (session capacity if set, else event `max_attendees`).

**Response `400`** — overlapping session in the same track.

**Session types:** `talk` · `workshop` · `panel` · `keynote`

---

### `PATCH /sessions/{id}/`
Update a session. Re-validates overlap excluding the session itself.

### `DELETE /sessions/{id}/`
Delete a session.

---

## Speaker Endpoints

### `GET /speakers/`
List all speakers.

### `POST /speakers/`
Create a speaker profile.

**Request**
```json
{
  "name": "Bob Smith",
  "bio": "Senior engineer at Acme.",
  "company": "Acme",
  "website": "https://bobsmith.dev",
  "user": null
}
```

### `GET /speakers/{id}/`
Speaker detail.

### `PATCH /speakers/{id}/` / `DELETE /speakers/{id}/`
Update or delete a speaker.

---

## Registration Endpoints

### `GET /registrations/`
List the authenticated user's own registrations. Staff sees all.

**Response `200`**
```json
{
  "results": [
    {
      "id": 1,
      "event": "djangocon-2025",
      "attendee": "bob@example.com",
      "registered_at": "2025-01-10T10:00:00Z",
      "status": "confirmed"
    }
  ]
}
```

### `POST /registrations/`
Register for an event by slug.

**Request**
```json
{ "event": "djangocon-2025" }
```

**Statuses:**
- `confirmed` — capacity available
- `waitlisted` — event full; user is on the waiting list
- `400` — already registered for this event

### `PATCH /registrations/{id}/`
Cancel a registration (sets `status` to `cancelled`). Only the registration owner.

---

## Error Format

All errors follow DRF's standard format:

```json
{ "field_name": ["Error message."] }
```

or for non-field errors:

```json
{ "detail": "Error message." }
```

---

## Versioning

The API uses URL path versioning. The current version is `v1`.

```
/api/v1/events/    ← current
/api/v2/events/    ← future
```

Passing an unlisted version returns `404 Not Found`.
