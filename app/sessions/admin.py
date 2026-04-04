from django.contrib import admin

from .models import Session, Speaker


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "user")
    search_fields = ("name", "company")
    list_select_related = ("user",)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("title", "track", "speaker", "start_time", "end_time", "session_type")
    list_filter = ("session_type", "track__event")
    search_fields = ("title", "room")
    list_select_related = ("track__event", "speaker")
