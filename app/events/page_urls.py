from django.urls import path

from .pages import EventCreateView, EventDetailView, EventListView, EventUpdateView

urlpatterns = [
    path("", EventListView.as_view(), name="event-list"),
    path("create/", EventCreateView.as_view(), name="event-create"),
    path("<slug:slug>/", EventDetailView.as_view(), name="event-detail"),
    path("<slug:slug>/edit/", EventUpdateView.as_view(), name="event-edit"),
]
