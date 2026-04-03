from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    # API v1
    path("api/v1/", include("app.accounts.urls")),
    path("api/v1/", include("app.events.urls")),
    path("api/v1/", include("app.tracks.urls")),
    # API docs
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Frontend pages
    path("", RedirectView.as_view(url="/events/", permanent=False), name="index"),
    path("events/", include("app.events.page_urls")),
    path("auth/", include("app.accounts.page_urls")),
    path("dashboard/", include("app.accounts.dashboard_urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
