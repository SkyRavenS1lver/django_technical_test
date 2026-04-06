# events

Core event model with organiser ownership, capacity tracking, and status lifecycle.

## Model: `Event`

| Field | Type | Notes |
|---|---|---|
| `title` | CharField | Required |
| `slug` | SlugField | Auto-generated from title; collision resolved with `-n` suffix |
| `description` | TextField | Required |
| `start_date` / `end_date` | DateTimeField | `end > start` enforced by `CheckConstraint` + `clean()` |
| `venue_name` | CharField | Required |
| `venue_address` | TextField | Required |
| `max_attendees` | PositiveIntegerField | Used for capacity checks and session effective capacity |
| `organizer` | FK → User | Set automatically from `request.user` on create |
| `status` | CharField | `draft` · `published` · `cancelled` |
| `banner` | ImageField | Optional; uploaded to `banners/` |

## Slug Auto-generation

```python
# events/models.py – save()
base_slug = slugify(title)          # "My Event" → "my-event"
# On collision: "my-event-1", "my-event-2", …
```

Slug is set once on first save and never auto-updated (stable URLs).

## Status Visibility

| User | Sees |
|---|---|
| Unauthenticated | `published` only |
| Authenticated attendee | `published` only |
| Organiser | `published` + own `draft` / `cancelled` |
| Staff | All |

## API Actions

Standard CRUD at `/api/<version>/events/{slug}/` plus nested actions:

| Method | Path | Description |
|---|---|---|
| GET / POST | `…/tracks/` | List or add tracks |
| GET | `…/sessions/` | List all sessions for this event |
| POST | `…/register/` | Register authenticated user |
| GET | `…/registrations/` | List registrations (organiser only) |

## Serializers

| Class | Used for |
|---|---|
| `EventListSerializer` | `list` action — lightweight, includes `organizer_name` |
| `EventDetailSerializer` | `retrieve` action — full fields + nested tracks |
| `EventWriteSerializer` | `create` / `update` — validates `end_date > start_date`; injects `organizer` from context |

## Files

| File | Purpose |
|---|---|
| `models.py` | `Event` model with slug generation and date validation |
| `serializers.py` | Three serializers for list / detail / write |
| `views.py` | `EventViewSet` with nested `@action` methods |
| `urls.py` | API routes |
| `pages.py` | List, detail, create, edit template views |
| `page_urls.py` | Frontend routes under `/events/` |
| `filters.py` | `EventFilter` — filter by status, date range |
| `admin.py` | Event admin with prepopulated slug |
