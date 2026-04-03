from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "organizer", "status", "start_date", "end_date", "max_attendees")
    list_filter = ("status",)
    search_fields = ("title", "venue_name", "organizer__email")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-start_date",)
    raw_id_fields = ("organizer",)
