from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Crew,
    Order,
)

from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    CrewSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name",)
    ordering_fields = ("name",)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ["source", "destination"]
    ordering_fields = ["distance"]

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ["airplane_type"]
    search_fields = ("name",)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        return AirplaneSerializer


class FlightViewSet(viewsets.ModelViewSet):

    queryset = Flight.objects.select_related(
        "route__source", "route__destination", "airplane__airplane_type"
    ).prefetch_related("crew", "tickets")
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        "route": ["exact"],
        "airplane": ["exact"],
        "departure_time": ["gte", "lte", "exact", "date"],
    }
    ordering_fields = ["departure_time", "arrival_time"]

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


class CrewViewSet(viewsets.ModelViewSet):

    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name"]
    ordering_fields = ["last_name", "first_name"]


class OrderViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]

    def get_queryset(self):

        return Order.objects.filter(user=self.request.user).prefetch_related(
            "tickets__flight__route__source",
            "tickets__flight__route__destination",
            "tickets__flight__airplane",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
