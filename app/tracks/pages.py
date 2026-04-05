from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from app.events.models import Event

from .models import Track

_WRITE_FIELDS = ("name", "description", "color")
_REQUIRED_FIELDS = ("name", "color")


class TrackCreateView(LoginRequiredMixin, View):
    login_url = "/auth/login/"

    def get(self, request, slug):
        event = get_object_or_404(Event, slug=slug)
        if not request.user.is_organizer or event.organizer != request.user:
            return redirect(f"/events/{slug}/")
        return render(request, "tracks/form.html", {
            "action": "create",
            "event": event,
            "data": {"color": "#6366f1"},
            "errors": {},
        })

    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug)
        if not request.user.is_organizer or event.organizer != request.user:
            return redirect(f"/events/{slug}/")

        data = {f: request.POST.get(f, "").strip() for f in _WRITE_FIELDS}
        errors = {f: "This field is required." for f in _REQUIRED_FIELDS if not data[f]}

        if errors:
            return render(request, "tracks/form.html", {
                "action": "create", "event": event, "data": data, "errors": errors,
            })

        try:
            track = Track(event=event, **data)
            track.full_clean()
            track.save()
        except ValidationError as e:
            errors.update({f: msgs[0] for f, msgs in e.message_dict.items()})
            return render(request, "tracks/form.html", {
                "action": "create", "event": event, "data": data, "errors": errors,
            })

        return redirect(f"/events/{slug}/")


class TrackUpdateView(LoginRequiredMixin, View):
    login_url = "/auth/login/"

    def get(self, request, slug, pk):
        event = get_object_or_404(Event, slug=slug)
        if not request.user.is_organizer or event.organizer != request.user:
            return redirect(f"/events/{slug}/")
        track = get_object_or_404(Track, pk=pk, event=event)
        data = {
            "name": track.name,
            "description": track.description,
            "color": track.color,
        }
        return render(request, "tracks/form.html", {
            "action": "edit", "event": event, "track": track, "data": data, "errors": {},
        })

    def post(self, request, slug, pk):
        event = get_object_or_404(Event, slug=slug)
        if not request.user.is_organizer or event.organizer != request.user:
            return redirect(f"/events/{slug}/")
        track = get_object_or_404(Track, pk=pk, event=event)

        data = {f: request.POST.get(f, "").strip() for f in _WRITE_FIELDS}
        errors = {f: "This field is required." for f in _REQUIRED_FIELDS if not data[f]}

        if errors:
            return render(request, "tracks/form.html", {
                "action": "edit", "event": event, "track": track, "data": data, "errors": errors,
            })

        try:
            for field, value in data.items():
                setattr(track, field, value)
            track.full_clean()
            track.save()
        except ValidationError as e:
            errors.update({f: msgs[0] for f, msgs in e.message_dict.items()})
            return render(request, "tracks/form.html", {
                "action": "edit", "event": event, "track": track, "data": data, "errors": errors,
            })

        return redirect(f"/events/{slug}/")
