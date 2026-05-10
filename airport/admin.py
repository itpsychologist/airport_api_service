from django.contrib import admin
from django.db.models import Count

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Crew,
    Order,
    Ticket,
)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ["name", "city"]
    search_fields = ["name", "city"]
    ordering = ["name"]


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ["source", "destination", "distance"]
    list_filter = ["source", "destination"]
    search_fields = ["source__name", "destination__name"]


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ["name", "airplane_type", "rows", "seats_in_row", "capacity"]
    list_filter = ["airplane_type"]
    search_fields = ["name"]

    @admin.display(description="Capacity")
    def capacity(self, obj):
        return obj.capacity


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "full_name"]
    search_fields = ["first_name", "last_name"]
    ordering = ["last_name", "first_name"]

    @admin.display(description="Full Name")
    def full_name(self, obj):
        return obj.full_name


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ["id", "route", "airplane", "departure_time", "arrival_time"]
    list_filter = ["route", "airplane", "departure_time"]
    search_fields = [
        "route__source__name",
        "route__destination__name",
        "airplane__name",
    ]
    filter_horizontal = ["crew"]
    date_hierarchy = "departure_time"
    inlines = [TicketInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "created_at", "tickets_count"]
    list_filter = ["created_at", "user"]
    search_fields = ["user__email"]
    date_hierarchy = "created_at"
    inlines = [TicketInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(tickets_count=Count("tickets"))

    @admin.display(description="Tickets", ordering="tickets_count")
    def tickets_count(self, obj):
        return obj.tickets_count


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["id", "flight", "row", "seat", "order"]
    list_filter = ["flight", "order"]
    search_fields = ["flight__route__source__name"]
