# tracks

Organises sessions into named, colour-coded tracks within an event.

## Model: `Track`

| Field | Type | Notes |
|---|---|---|
| `event` | FK → Event | CASCADE delete |
| `name` | CharField | Unique per event (enforced by `UniqueConstraint`) |
| `description` | TextField | Optional |
| `color` | CharField | Hex colour, default `#6366f1`; displayed in UI and session badges |

**Constraint:** `unique_track_per_event` — same name cannot exist twice in the same event. Duplicate attempts via the API return `400`.

## Permissions

Track write operations are restricted to the event organiser via `IsEventOrganizer` (object-level permission). `get_object()` attaches `obj.organizer = obj.event.organizer` so the permission class can compare it with `request.user`.

Track **creation** goes through the `EventViewSet.tracks` action (`POST /api/v1/events/{slug}/tracks/`) rather than directly via `POST /api/v1/tracks/` — the `TrackViewSet` intentionally omits `CreateModelMixin`.

## Files

| File | Purpose |
|---|---|
| `models.py` | `Track` model with unique constraint |
| `serializers.py` | `TrackSerializer` — `event` is read-only (set by the view) |
| `views.py` | `TrackViewSet` — list, retrieve, update, delete only |
| `urls.py` | API routes |
| `pages.py` | `TrackCreateView`, `TrackUpdateView` — organiser-only template views |
| `page_urls.py` | `/events/{slug}/tracks/create/` and `…/tracks/{pk}/edit/` |
| `filters.py` | `TrackFilter` |
| `admin.py` | Track admin |
