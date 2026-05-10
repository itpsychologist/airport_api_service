from rest_framework import serializers
from django.db import transaction
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


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = ["id", "name", "city"]


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]

    def validate(self, attrs):
        if attrs.get("source") == attrs.get("destination"):
            raise serializers.ValidationError(
                "Source and destination airports must be different."
            )
        return attrs


class RouteListSerializer(RouteSerializer):
    source = serializers.StringRelatedField()
    destination = serializers.StringRelatedField()


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = ["id", "name"]


class AirplaneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "airplane_type"]


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.StringRelatedField()
    capacity = serializers.IntegerField(required=False)

    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "airplane_type", "capacity"]


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)
    capacity = serializers.IntegerField(required=False)

    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "airplane_type", "capacity"]


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Crew
        fields = ["id", "full_name", "last_name", "first_name"]


class FlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "departure_time", "arrival_time", "crew"]

    def validate(self, attrs):
        departure = attrs.get("departure_time")
        arrival = attrs.get("arrival_time")

        if departure and arrival and arrival <= departure:
            raise serializers.ValidationError(
                "Arrival time must be after departure time."
            )
        return attrs


class FlightListSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField()
    airplane = serializers.StringRelatedField()
    tickets_available = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "tickets_available",
        ]

    def get_tickets_available(self, obj) -> int:
        """Calculate available seats on this flight."""
        sold = getattr(obj, "tickets_count", obj.tickets.count())
        return obj.airplane.capacity - sold


class TicketSeatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ["row", "seat"]


class FlightDetailSerializer(serializers.ModelSerializer):
    route = RouteDetailSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    taken_seats = TicketSeatsSerializer(source="tickets", many=True, read_only=True)

    tickets_available = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
            "taken_seats",
            "tickets_available",
        ]

    def get_tickets_available(self, obj) -> int:
        return obj.airplane.capacity - obj.tickets.count()


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight"]

    def validate(self, attrs):
        flight = attrs.get("flight")
        row = attrs.get("row")
        seat = attrs.get("seat")

        if flight:
            airplane = flight.airplane

            if row is not None and row < 1:
                raise serializers.ValidationError(
                    {"row": "Row number must be at least 1."}
                )

            if seat is not None and seat < 1:
                raise serializers.ValidationError(
                    {"seat": "Seat number must be at least 1."}
                )

            if row and row > airplane.rows:
                raise serializers.ValidationError(
                    {"row": f"Row exceeds capacity. Max: {airplane.rows}"}
                )

            if seat and seat > airplane.seats_in_row:
                raise serializers.ValidationError(
                    {"seat": f"Seat exceeds capacity. Max: {airplane.seats_in_row}"}
                )

            # Check for duplicate booking
            if Ticket.objects.filter(flight=flight, row=row, seat=seat).exists():
                raise serializers.ValidationError(
                    "This seat is already booked for this flight."
                )

        return attrs


class TicketListSerializer(serializers.ModelSerializer):
    flight = FlightDetailSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight"]


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "tickets", "created_at"]
        read_only_fields = ["created_at"]

    def validate_tickets(self, value):
        if not value:
            raise serializers.ValidationError("Order must contain at least one ticket.")
        flights = set(ticket["flight"].id for ticket in value)
        if len(flights) > 1:
            raise serializers.ValidationError(
                "All tickets in an order must be for the same flight."
            )

        return value

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")

        with transaction.atomic():

            flight = tickets_data[0]["flight"]
            Flight.objects.select_for_update().get(pk=flight.pk)
            available = flight.airplane.capacity - flight.tickets.count()

            if len(tickets_data) > available:
                raise serializers.ValidationError(
                    f"Not enough seats available. Only {available} seats left."
                )

            order = Order.objects.create(**validated_data)

            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)

        return order


class OrderListSerializer(serializers.ModelSerializer):

    tickets_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "tickets_count"]


class OrderDetailSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "tickets"]
