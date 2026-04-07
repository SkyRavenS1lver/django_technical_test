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

## Display Status (computed property)

`status` is the **organiser's intent** — a value they explicitly set. `display_status` is a **read-only property** that derives the UI state from real time, so organizers never have to manually mark events as finished.

| `display_status` | Condition |
|---|---|
| `upcoming` | published + now < start_date |
| `ongoing` | published + start_date ≤ now ≤ end_date |
| `finished` | published + now > end_date |
| `draft` | status == draft |
| `cancelled` | status == cancelled |

## Frontend Filtering (EventListView)

`pages.py` reads two GET params and applies them to the queryset before rendering:

| Param | Values | Behaviour |
|---|---|---|
| `search` | any string | `contains` on `title` and `venue_name` |
| `filter` | `all` (default) | No extra constraint |
| | `upcoming` | `status=published` + `start_date > now` |
| | `ongoing` | `status=published` + `start_date ≤ now ≤ end_date` |
| | `finished` | `status=published` + `end_date < now` |
| | `draft` | `status=draft` (organizers only) |

HTMX triggers a partial refresh of `#event-list` on search input (300ms debounce) and on filter pill change — no full page reload. The load more button preserves active search and filter params in its URL.

## Session Type Filtering (detail page)

Sessions on the event detail page can be filtered by type (Keynote / Workshop / Panel / Talk) via client-side JavaScript. No extra request is made — all sessions are already in the DOM and toggled by `data-session-type` attribute.

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
