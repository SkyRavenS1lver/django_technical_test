# accounts

Custom user model with email-based authentication and JWT.

## Model: `User`

Extends `AbstractUser`. Username field replaced by `email`.

| Field | Type | Notes |
|---|---|---|
| `email` | EmailField | Unique, used as login field |
| `name` | CharField | Full name |
| `bio` | TextField | Optional profile bio |
| `avatar` | ImageField | Optional profile photo |
| `is_organizer` | BooleanField | Gates event creation; default `False` |

`REQUIRED_FIELDS = ["name"]` — required when using `createsuperuser`.

## Auth Flow

```
POST /api/v1/auth/register/  →  201 + { access, refresh }
POST /api/v1/auth/login/     →  200 + { access, refresh }
POST /api/v1/auth/refresh/   →  200 + { access, refresh }   # rotates refresh token
POST /api/v1/auth/logout/    →  204                         # blacklists refresh token
GET  /api/v1/auth/me/        →  200 user profile
```

JWT config (see `settings/base.py`):
- Access token lifetime: **60 minutes**
- Refresh token lifetime: **7 days**
- Refresh token rotation + blacklist enabled

## Permissions

| Action | Permission |
|---|---|
| Register / login | `AllowAny` |
| Me (read/update) | `IsAuthenticated` |
| Create event | `IsAuthenticated` + `is_organizer=True` |

Custom permission classes live in `app/accounts/permissions.py`:
- `IsOrganizer` — checks `request.user.is_organizer`
- `IsEventOrganizer` — object-level check: `obj.organizer == request.user`

## Files

| File | Purpose |
|---|---|
| `models.py` | `User` model + `UserManager` |
| `serializers.py` | `RegisterSerializer`, `UserSerializer` |
| `views.py` | `RegisterView`, `MeView`, `LogoutView` |
| `urls.py` | API routes under `/api/<version>/auth/` |
| `pages.py` | Login, register, logout, dashboard template views |
| `page_urls.py` | Frontend routes under `/auth/` |
| `dashboard_urls.py` | `/dashboard/` route |
| `permissions.py` | `IsOrganizer`, `IsEventOrganizer` |
| `admin.py` | User admin with `is_organizer` display |
