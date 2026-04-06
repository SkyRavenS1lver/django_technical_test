# registrations

Handles attendee registration for events with capacity enforcement and automatic waitlisting.

## Model: `Registration`

| Field | Type | Notes |
|---|---|---|
| `attendee` | FK → User | CASCADE delete |
| `event` | FK → Event | CASCADE delete |
| `registered_at` | DateTimeField | Auto-set on creation |
| `status` | CharField | `confirmed` · `waitlisted` · `cancelled` |

**Constraint:** `unique_registration` — `(attendee, event)` is unique; a user cannot register for the same event twice.

## Business Rules

All enforced in `RegistrationSerializer.validate()`:

### 1. Duplicate check
```python
if Registration.objects.filter(attendee=user, event=event).exists():
    raise ValidationError({"event": "You are already registered for this event."})
```

### 2. Capacity check & auto-waitlist
```python
confirmed_count = event.registrations.filter(status=Registration.Status.CONFIRMED).count()
attrs["status"] = (
    Registration.Status.WAITLISTED
    if confirmed_count >= event.max_attendees
    else Registration.Status.CONFIRMED
)
```

Registrations are never hard-rejected due to capacity — users are placed on the waitlist instead.

## Registration Flow

```
POST /api/v1/registrations/
  → duplicate?        → 400
  → confirmed < max?  → status = "confirmed"  → 201
  → confirmed >= max? → status = "waitlisted" → 201

PATCH /api/v1/registrations/{id}/
  → sets status = "cancelled"
  → only the registration owner can cancel
```

## Visibility

| User | Sees |
|---|---|
| Authenticated attendee | Own registrations only |
| Staff | All registrations |
| Event organiser | All registrations for their event via `GET /events/{slug}/registrations/` |

## HTMX Registration Button

The frontend registration button (`templates/events/partials/registration_btn.html`) is an HTMX partial that swaps itself after a POST/cancel action. States:

- **Unauthenticated** → "Register" link → redirects to login
- **Not registered / cancelled** → "Register" button → `hx-post` → swaps partial
- **Confirmed** → "Registered ✓" badge + "Cancel" button
- **Waitlisted** → "On Waitlist" badge + "Cancel" button
- **Organiser** → button hidden

## Files

| File | Purpose |
|---|---|
| `models.py` | `Registration` model with unique constraint |
| `serializers.py` | `RegistrationSerializer` — duplicate check, capacity check, attendee injection |
| `views.py` | `RegistrationViewSet` — own-records queryset, PATCH-only cancel |
| `urls.py` | API routes |
| `pages.py` | `EventRegisterView`, `EventCancelRegistrationView` — HTMX POST handlers |
| `page_urls.py` | `/events/{slug}/register/` and `/events/{slug}/cancel-registration/` |
| `admin.py` | Registration admin with status filter |
