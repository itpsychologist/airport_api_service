from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Airport(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.city})"


class AirplaneType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
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
        verbose_name_plural = "Crew members"
        ordering = ["first_name", "last_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departing_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="arriving_routes"
    )
    distance = models.PositiveIntegerField(help_text="Distance in kilometers")

    class Meta:
        ordering = ["source__name", "destination__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination"],
                name="unique_route_source_destination"
            )
        ]

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination airports must be different.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source.name} -> {self.destination.name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights", blank=True)

    @property
    def tickets_available(self) -> int:
        return self.airplane.capacity - self.tickets.count()

    class Meta:
        ordering = ["departure_time"]

    def clean(self):
        if self.departure_time and self.arrival_time:
            if self.arrival_time <= self.departure_time:
                raise ValidationError("Arrival time must be after departure time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.route} - " f'{self.departure_time.strftime("%Y-%m-%d %H:%M")}'


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        ordering = ["flight", "row", "seat"]
        constraints = [
            models.UniqueConstraint(
                fields=["row", "seat", "flight"],
                name="unique_ticket_flight_row_seat",
            )
        ]

    def clean(self):
        airplane = self.flight.airplane

        if self.row < 1:
            raise ValidationError({"row": "Row number must be at least 1."})

        if self.seat < 1:
            raise ValidationError({"seat": "Seat number must be at least 1."})

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
