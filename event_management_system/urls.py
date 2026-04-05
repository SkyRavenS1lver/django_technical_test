from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

api_urlpatterns = [
    path("", include("app.accounts.urls")),
    path("", include("app.events.urls")),
    path("", include("app.tracks.urls")),
    path("", include("app.sessions.urls")),
    path("", include("app.registrations.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    # Versioned API — e.g. /api/v1/events/
    path("api/<version>/", include(api_urlpatterns)),
    # API docs
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Frontend pages
    path("", RedirectView.as_view(url="/events/", permanent=False), name="index"),
    path("events/", include("app.events.page_urls")),
    path("", include("app.sessions.page_urls")),
    path("", include("app.tracks.page_urls")),
    path("", include("app.registrations.page_urls")),
    path("auth/", include("app.accounts.page_urls")),
    path("dashboard/", include("app.accounts.dashboard_urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
