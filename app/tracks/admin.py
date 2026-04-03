from django.contrib import admin

from .models import Track


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "color")
    search_fields = ("name", "event__title")
    list_select_related = ("event",)
