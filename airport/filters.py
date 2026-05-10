import django_filters
from .models import Flight


class FlightFilter(django_filters.FilterSet):
    departure_date = django_filters.DateFilter(
        field_name="departure_time", lookup_expr="date"
    )
    min_departure = django_filters.DateTimeFilter(
        field_name="departure_time", lookup_expr="gte"
    )
    max_departure = django_filters.DateTimeFilter(
        field_name="departure_time", lookup_expr="lte"
    )

    class Meta:
        model = Flight
        fields = ["route", "airplane", "departure_date"]
