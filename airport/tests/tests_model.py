from django.test import TestCase
from django.core.exceptions import ValidationError
from airport.models import Airport, Route


class RouteModelTest(TestCase):
    def setUp(self):
        self.airport1 = Airport.objects.create(name="JFK", city="New York")
        self.airport2 = Airport.objects.create(name="LAX", city="Los Angeles")

    def test_route_cannot_have_same_source_and_destination(self):
        route = Route(source=self.airport1, destination=self.airport1, distance=100)
        with self.assertRaises(ValidationError):
            route.save()

    def test_valid_route_creation(self):
        route = Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=3983
        )
        self.assertEqual(route.source, self.airport1)
        self.assertEqual(route.destination, self.airport2)
