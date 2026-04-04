import django_filters

from .models import Session


class SessionFilter(django_filters.FilterSet):
    start_from = django_filters.DateTimeFilter(field_name="start_time", lookup_expr="gte")
    start_to = django_filters.DateTimeFilter(field_name="start_time", lookup_expr="lte")

    class Meta:
        model = Session
        fields = ("track", "speaker", "session_type")
