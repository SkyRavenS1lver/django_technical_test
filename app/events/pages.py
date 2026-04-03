from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .models import Event

_WRITE_FIELDS = ("title", "description", "start_date", "end_date", "venue_name", "venue_address", "max_attendees", "status")
_REQUIRED_FIELDS = ("title", "description", "start_date", "end_date", "venue_name", "venue_address", "max_attendees")


def _event_queryset(user):
    qs = Event.objects.select_related("organizer")
    if not user.is_authenticated:
        return qs.filter(status=Event.Status.PUBLISHED)
    if user.is_organizer:
        return qs.filter(Q(status=Event.Status.PUBLISHED) | Q(organizer=user))
    return qs.filter(status=Event.Status.PUBLISHED)


class EventListView(View):
    def get(self, request):
        events = _event_queryset(request.user)
        if request.htmx:
            return render(request, "events/partials/event_list.html", {"events": events})
        return render(request, "events/list.html", {"events": events})


class EventDetailView(View):
    def get(self, request, slug):
        event = get_object_or_404(
            Event.objects.select_related("organizer").prefetch_related("tracks"),
            slug=slug,
        )
        return render(request, "events/detail.html", {"event": event})


class EventCreateView(LoginRequiredMixin, View):
    login_url = "/auth/login/"

    def get(self, request):
        if not request.user.is_organizer:
            return redirect("/events/")
        return render(request, "events/form.html", {"action": "create", "event": None, "data": {"status": "draft"}})

    def post(self, request):
        if not request.user.is_organizer:
            return redirect("/events/")

        data = {f: request.POST.get(f, "").strip() for f in _WRITE_FIELDS}
        errors = {f: "This field is required." for f in _REQUIRED_FIELDS if not data[f]}

        if errors:
            return render(request, "events/form.html", {"action": "create", "data": data, "errors": errors, "event": None})

        try:
            event = Event(organizer=request.user, **data)
            event.full_clean()
            event.save()
        except ValidationError as e:
            errors.update({f: msgs[0] for f, msgs in e.message_dict.items()})
            return render(request, "events/form.html", {"action": "create", "data": data, "errors": errors, "event": None})

        return redirect(f"/events/{event.slug}/")


class EventUpdateView(LoginRequiredMixin, View):
    login_url = "/auth/login/"

    def get(self, request, slug):
        event = get_object_or_404(Event, slug=slug)
        if event.organizer != request.user:
            return redirect(f"/events/{slug}/")
        data = {
            "title": event.title,
            "description": event.description,
            "start_date": event.start_date.strftime("%Y-%m-%dT%H:%M") if event.start_date else "",
            "end_date": event.end_date.strftime("%Y-%m-%dT%H:%M") if event.end_date else "",
            "venue_name": event.venue_name,
            "venue_address": event.venue_address or "",
            "max_attendees": str(event.max_attendees) if event.max_attendees is not None else "",
            "status": event.status,
        }
        return render(request, "events/form.html", {"action": "edit", "event": event, "data": data})

    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug)
        if event.organizer != request.user:
            return redirect(f"/events/{slug}/")

        data = {f: request.POST.get(f, "").strip() for f in _WRITE_FIELDS}
        errors = {f: "This field is required." for f in _REQUIRED_FIELDS if not data[f]}

        if errors:
            return render(request, "events/form.html", {"action": "edit", "event": event, "data": data, "errors": errors})

        try:
            for field, value in data.items():
                setattr(event, field, value)
            event.full_clean()
            event.save()
        except ValidationError as e:
            errors.update({f: msgs[0] for f, msgs in e.message_dict.items()})
            return render(request, "events/form.html", {"action": "edit", "event": event, "data": data, "errors": errors})

        return redirect(f"/events/{event.slug}/")
