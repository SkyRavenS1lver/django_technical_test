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
        from django.utils import timezone

        events = _event_queryset(request.user)
        search = request.GET.get("search", "").strip()
        active_filter = request.GET.get("filter", "all")

        if search:
            events = events.filter(
                Q(title__icontains=search) | Q(venue_name__icontains=search)
            )

        now = timezone.now()
        if active_filter == "upcoming":
            events = events.filter(status=Event.Status.PUBLISHED, start_date__gt=now)
        elif active_filter == "ongoing":
            events = events.filter(status=Event.Status.PUBLISHED, start_date__lte=now, end_date__gte=now)
        elif active_filter == "finished":
            events = events.filter(status=Event.Status.PUBLISHED, end_date__lt=now)
        elif active_filter == "draft" and request.user.is_authenticated and request.user.is_organizer:
            events = events.filter(status=Event.Status.DRAFT)

        filter_pills = [
            ("all", "All", "✨"),
            ("upcoming", "Upcoming", "🟢"),
            ("ongoing", "Ongoing", "🔵"),
            ("finished", "Finished", "⚫"),
        ]
        if request.user.is_authenticated and request.user.is_organizer:
            filter_pills.append(("draft", "My Drafts", "🟡"))

        context = {
            "events": events,
            "search": search,
            "active_filter": active_filter,
            "filter_pills": filter_pills,
        }
        if request.htmx:
            return render(request, "events/partials/event_list.html", context)
        return render(request, "events/list.html", context)


class EventDetailView(View):
    def get(self, request, slug):
        from app.sessions.models import Session
        from app.registrations.models import Registration
        event = get_object_or_404(
            Event.objects.select_related("organizer").prefetch_related("tracks"),
            slug=slug,
        )
        sessions = (
            Session.objects
            .filter(track__event=event)
            .select_related("track", "speaker")
            .order_by("start_time")
        )
        registration = None
        if request.user.is_authenticated:
            registration = Registration.objects.filter(attendee=request.user, event=event).first()
        return render(request, "events/detail.html", {
            "event": event,
            "sessions": sessions,
            "registration": registration,
        })


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
