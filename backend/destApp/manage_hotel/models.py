from django.db import models


class Room(models.Model):
    TYPE_CHOICES = (
        ('Standard', 'Standard'),
        ('Single', 'Single'),
        ('Double', 'Double'),
        ('Deluxe', 'Deluxe')
    )
    room_number = models.IntegerField(blank=True, null=True)
    room_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    room_price = models.IntegerField()
    room_description = models.TextField(null=True)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room_number}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('CheckIn', 'CheckIn'),
        ('CheckOut', 'CheckOut'),
        ('NotYet', 'NotYet')
    )
    guest = models.CharField(max_length=50)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateField()
    end_time = models.DateField()
    check_in = models.DateTimeField(blank=True, null=True)
    check_out = models.DateTimeField(blank=True, null=True)
    booking_status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.guest}-{self.room}"
