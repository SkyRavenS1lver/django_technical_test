from django.contrib import admin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("attendee", "event", "status", "registered_at")
    list_filter = ("status",)
    list_select_related = ("attendee", "event")
    readonly_fields = ("registered_at",)
