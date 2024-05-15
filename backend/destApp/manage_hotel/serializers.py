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
    def update(self, instance, validated_data):
        instance.room_number = validated_data.get('room_number',instance.room_number)
        instance.room_type = validated_data.get('room_type',instance.room_type)
        instance.room_description = validated_data.get('room_description',instance.room_description)
        instance.save()
        return instance
