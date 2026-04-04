from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from app.events.models import Event
from app.tracks.models import Track

from .models import Session, Speaker

_WRITE_FIELDS = ("title", "description", "track", "speaker", "start_time", "end_time", "room", "session_type", "capacity")
_REQUIRED_FIELDS = ("title", "description", "track", "start_time", "end_time")


def _get_event_or_403(slug, user):
    event = get_object_or_404(Event, slug=slug)
    if event.organizer != user:
        return None, event
    return event, event


class SessionCreateView(LoginRequiredMixin, View):
    login_url = "/auth/login/"

    def get(self, request, slug):
        event = get_object_or_404(Event, slug=slug)
        if event.organizer != request.user:
            return redirect(f"/events/{slug}/")
        tracks = Track.objects.filter(event=event)
        speakers = Speaker.objects.all()
        return render(request, "sessions/form.html", {
            "action": "create",
            "event": event,
            "tracks": tracks,
            "speakers": speakers,
            "data": {"session_type": "talk"},
            "session": None,
        })

    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug)
        if event.organizer != request.user:
            return redirect(f"/events/{slug}/")

        data = {f: request.POST.get(f, "").strip() for f in _WRITE_FIELDS}
        errors = {f: "This field is required." for f in _REQUIRED_FIELDS if not data[f]}

        tracks = Track.objects.filter(event=event)
        speakers = Speaker.objects.all()

        if errors:
            return render(request, "sessions/form.html", {
                "action": "create", "event": event,
                "tracks": tracks, "speakers": speakers,
                "data": data, "errors": errors, "session": None,
            })

        try:
            track = get_object_or_404(Track, pk=data["track"], event=event)
            speaker = Speaker.objects.filter(pk=data["speaker"]).first() if data["speaker"] else None
            session = Session(
                title=data["title"],
                description=data["description"],
                track=track,
                speaker=speaker,
                start_time=data["start_time"],
                end_time=data["end_time"],
                room=data["room"],
                session_type=data["session_type"],
                capacity=data["capacity"] or None,
            )
            session.full_clean()
            session.save()
        except ValidationError as e:
            errors.update({f: msgs[0] for f, msgs in e.message_dict.items()})
            return render(request, "sessions/form.html", {
                "action": "create", "event": event,
                "tracks": tracks, "speakers": speakers,
                "data": data, "errors": errors, "session": None,
            })

        return redirect(f"/events/{slug}/")


class SessionUpdateView(LoginRequiredMixin, View):
    login_url = "/auth/login/"

    def get(self, request, pk):
        session = get_object_or_404(Session.objects.select_related("track__event"), pk=pk)
        event = session.track.event
        if event.organizer != request.user:
            return redirect(f"/events/{event.slug}/")
        tracks = Track.objects.filter(event=event)
        speakers = Speaker.objects.all()
        data = {
            "title": session.title,
            "description": session.description,
            "track": str(session.track_id),
            "speaker": str(session.speaker_id) if session.speaker_id else "",
            "start_time": session.start_time.strftime("%Y-%m-%dT%H:%M") if session.start_time else "",
            "end_time": session.end_time.strftime("%Y-%m-%dT%H:%M") if session.end_time else "",
            "room": session.room,
            "session_type": session.session_type,
            "capacity": str(session.capacity) if session.capacity is not None else "",
        }
        return render(request, "sessions/form.html", {
            "action": "edit", "event": event, "session": session,
            "tracks": tracks, "speakers": speakers, "data": data,
        })

    def post(self, request, pk):
        session = get_object_or_404(Session.objects.select_related("track__event"), pk=pk)
        event = session.track.event
        if event.organizer != request.user:
            return redirect(f"/events/{event.slug}/")

        data = {f: request.POST.get(f, "").strip() for f in _WRITE_FIELDS}
        errors = {f: "This field is required." for f in _REQUIRED_FIELDS if not data[f]}

        tracks = Track.objects.filter(event=event)
        speakers = Speaker.objects.all()

        if errors:
            return render(request, "sessions/form.html", {
                "action": "edit", "event": event, "session": session,
                "tracks": tracks, "speakers": speakers,
                "data": data, "errors": errors,
            })

        try:
            track = get_object_or_404(Track, pk=data["track"], event=event)
            speaker = Speaker.objects.filter(pk=data["speaker"]).first() if data["speaker"] else None
            session.title = data["title"]
            session.description = data["description"]
            session.track = track
            session.speaker = speaker
            session.start_time = data["start_time"]
            session.end_time = data["end_time"]
            session.room = data["room"]
            session.session_type = data["session_type"]
            session.capacity = data["capacity"] or None
            session.full_clean()
            session.save()
        except ValidationError as e:
            errors.update({f: msgs[0] for f, msgs in e.message_dict.items()})
            return render(request, "sessions/form.html", {
                "action": "edit", "event": event, "session": session,
                "tracks": tracks, "speakers": speakers,
                "data": data, "errors": errors,
            })

        return redirect(f"/events/{event.slug}/")
