from django.urls import path

from .pages import SessionCreateView, SessionUpdateView

urlpatterns = [
    path("events/<slug:slug>/sessions/create/", SessionCreateView.as_view(), name="session-create"),
    path("sessions/<int:pk>/edit/", SessionUpdateView.as_view(), name="session-edit"),
]
