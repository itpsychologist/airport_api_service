from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airport.views import (
    AirportViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    FlightViewSet,
    CrewViewSet,
    OrderViewSet,
)

router = DefaultRouter()
router.register("airports", AirportViewSet, basename="airport")
router.register("routes", RouteViewSet, basename="route")
router.register("airplane-types", AirplaneTypeViewSet, basename="airplane-type")
router.register("airplanes", AirplaneViewSet, basename="airplane")
router.register("flights", FlightViewSet, basename="flight")
router.register("crew", CrewViewSet, basename="crew")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
