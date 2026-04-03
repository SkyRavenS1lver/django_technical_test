from django_filters import rest_framework as filters

from .models import Event


class EventFilter(filters.FilterSet):
    status = filters.CharFilter(field_name="status", lookup_expr="exact")
    start_from = filters.DateTimeFilter(field_name="start_date", lookup_expr="gte")
    start_to = filters.DateTimeFilter(field_name="start_date", lookup_expr="lte")

    class Meta:
        model = Event
        fields = ["status", "start_from", "start_to"]
