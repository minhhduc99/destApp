from rest_framework import serializers
from manage_hotel.models import Room, Booking


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class BookingListSerializer(serializers.ModelSerializer):
    room_number = serializers.SerializerMethodField()
    def get_room_number(self, obj):
        return obj.room.room_number
    class Meta:
        model = Booking
        fields = '__all__'
