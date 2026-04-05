from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View

from app.events.models import Event

from .models import Registration


class EventRegisterView(LoginRequiredMixin, View):
    login_url = "/auth/login/"

    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug)
        user = request.user

        registration, created = Registration.objects.get_or_create(
            attendee=user,
            event=event,
            defaults={"status": Registration.Status.CONFIRMED},
        )

        if created:
            confirmed_count = event.registrations.filter(status=Registration.Status.CONFIRMED).count()
            if confirmed_count > event.max_attendees:
                registration.status = Registration.Status.WAITLISTED
                registration.save(update_fields=["status"])

        return render(request, "events/partials/registration_btn.html", {
            "event": event,
            "registration": registration,
        })


class EventCancelRegistrationView(LoginRequiredMixin, View):
    login_url = "/auth/login/"

    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug)
        registration = get_object_or_404(Registration, attendee=request.user, event=event)
        registration.status = Registration.Status.CANCELLED
        registration.save(update_fields=["status"])

        return render(request, "events/partials/registration_btn.html", {
            "event": event,
            "registration": registration,
        })
