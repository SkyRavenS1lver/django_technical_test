from django.urls import path

from .pages import TrackCreateView, TrackUpdateView

urlpatterns = [
    path("events/<slug:slug>/tracks/create/", TrackCreateView.as_view(), name="track-create"),
    path("events/<slug:slug>/tracks/<int:pk>/edit/", TrackUpdateView.as_view(), name="track-edit"),
]
