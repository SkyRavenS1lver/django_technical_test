from django.urls import path

from .pages import EventCancelRegistrationView, EventRegisterView

urlpatterns = [
    path("events/<slug:slug>/register/", EventRegisterView.as_view(), name="event-register"),
    path("events/<slug:slug>/cancel-registration/", EventCancelRegistrationView.as_view(), name="event-cancel-registration"),
]
