from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Airport(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Airports"
        ordering = ["name"]

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Airplane Types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplane_type"
    )

    class Meta:
        ordering = ["name"]

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name} {self.airplane_type.name}"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Crews"
        ordering = ["first_name", "last_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Route(models.Model):
    source = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="departing_routes"
    )
    destination = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="arriving_routes"
    )
    distance = models.PositiveIntegerField(help_text="Distance in kilometers")

    class Meta:
        verbose_name_plural = "Routes"
        ordering = ["source", "destination"]
        unique_together = ("source", "destination")

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination airports must be different.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.source.name + " -> " + self.destination.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    class Meta:
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights", blank=True)
    tickets = models.ManyToManyField(
        "Ticket", related_name="flight_tickets", blank=True
    )

    @property
    def tickets_available(self) -> int:
        return self.airplane.capacity - self.tickets.count()

    class Meta:
        verbose_name_plural = "Flights"
        ordering = ["departure_time"]

    def __str__(self):
        return self.route.source.name + " -> " + self.route.destination.name


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        ordering = ["flight", "row", "seat"]
        unique_together = ["flight", "row", "seat"]

    def clean(self):
        airplane = self.flight.airplane

        if self.row > airplane.rows:
            raise ValidationError(
                {
                    "row": f"Row number exceeds airplane capacity. "
                    f"Max rows: {airplane.rows}"
                }
            )

        if self.seat > airplane.seats_in_row:
            raise ValidationError(
                {
                    "seat": f"Seat number exceeds airplane capacity. "
                    f"Max seats per row: {airplane.seats_in_row}"
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Row {self.row}, Seat {self.seat} - {self.flight}"
