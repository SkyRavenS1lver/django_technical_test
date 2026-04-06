# sessions

Manages speakers and scheduled sessions within event tracks. Enforces overlap-free scheduling.

## Models

### `Speaker`

| Field | Type | Notes |
|---|---|---|
| `name` | CharField | Required |
| `bio` | TextField | Required |
| `photo` | ImageField | Optional; uploaded to `speakers/` |
| `company` | CharField | Optional |
| `website` | URLField | Optional |
| `user` | FK → User | Optional; links speaker to a registered user account |

### `Session`

| Field | Type | Notes |
|---|---|---|
| `title` | CharField | Required |
| `description` | TextField | Required |
| `track` | FK → Track | CASCADE delete |
| `speaker` | FK → Speaker | Nullable |
| `start_time` / `end_time` | DateTimeField | `end > start` enforced by constraint + `clean()` |
| `room` | CharField | Optional room label |
| `session_type` | CharField | `talk` · `workshop` · `panel` · `keynote` |
| `capacity` | PositiveIntegerField | Nullable; `null` = inherit `event.max_attendees` |

## Overlap Detection

Enforced at **two layers** to cover both API requests and direct ORM/admin saves:

### Model layer (`Session.clean()`)
```python
overlapping = Session.objects.filter(
    track_id=self.track_id,
    start_time__lt=self.end_time,
    end_time__gt=self.start_time,
).exclude(pk=self.pk)
if overlapping.exists():
    raise ValidationError("This session overlaps …")
```

### Serializer layer (`SessionSerializer.validate()`)
Same query runs before the DB is touched; raises `serializers.ValidationError` → HTTP `400`.

**Rules:**
- Overlap detected: `new.start < existing.end AND new.end > existing.start`
- Back-to-back sessions (B starts exactly when A ends) → **allowed**
- Same time in **different tracks** → **allowed**

## Effective Capacity

`effective_capacity` is a read-only computed field on `SessionSerializer`:

```python
def get_effective_capacity(self, obj) -> int | None:
    return obj.capacity if obj.capacity is not None else obj.track.event.max_attendees
```

## App Label

The app uses `label = "event_sessions"` in `apps.py` to avoid a naming collision with Django's built-in `django.contrib.sessions` app (both would default to label `sessions`).

## Permissions

- `SpeakerViewSet` — `AllowAny` for read; `IsAuthenticated` for write
- `SessionViewSet` — `AllowAny` for read; `IsAuthenticated` + organiser check in `perform_create` for write

`perform_create` validates that the request user is the organiser of the session's track's event before saving:
```python
def perform_create(self, serializer):
    track = serializer.validated_data["track"]
    if track.event.organizer != self.request.user:
        raise PermissionDenied(…)
```

## Files

| File | Purpose |
|---|---|
| `models.py` | `Speaker` + `Session` models with overlap logic in `clean()` |
| `serializers.py` | `SpeakerSerializer`, `SessionSerializer` with overlap validation + `effective_capacity` |
| `views.py` | `SpeakerViewSet`, `SessionViewSet` with organiser check in `perform_create` |
| `urls.py` | API routes for `/sessions/` and `/speakers/` |
| `pages.py` | `SessionCreateView`, `SessionUpdateView` — organiser-only template views |
| `page_urls.py` | `/events/{slug}/sessions/create/` and `/sessions/{pk}/edit/` |
| `filters.py` | `SessionFilter` — filter by track, speaker, type, date range |
| `admin.py` | `SpeakerAdmin`, `SessionAdmin` |
