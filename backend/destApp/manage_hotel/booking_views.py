from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from manage_hotel.models import Booking, Room
from manage_hotel.serializers import BookingSerializer


class ListBookingView(APIView):
    def get(self, request):
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response({"data": serializer.data},
                        status=status.HTTP_200_OK)


class AddBookingView(APIView):
    def post(self, request):
        guest = request.data.get('guest')
        room = request.data.get('room')
        booking_time = request.data.get('booking_time')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        check_in = request.data.get('check_in')
        check_out = request.data.get('check_out')
        booking_status = "NotYet"

        data = {
            'guest': guest,
            'room': room,
            'booking_time': booking_time,
            'start_time': start_time,
            'end_time': end_time,
            'check_in': check_in,
            'check_out': check_out,
            'booking_status': booking_status
        }
        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            room_obj = Room.objects.get(id=room)
            room_obj.is_valid = False
            room_obj.save()
            return Response({"data":serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response({"message": "Cannot add booking"},
                        status=status.HTTP_400_BAD_REQUEST)


class EditBookingView(APIView):
    def get(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"message": "Cannot find this booking"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = BookingSerializer(booking)
        return Response({"data": serializer.data},
                        status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"message": "Cannot find this booking"},
                            status=status.HTTP_404_NOT_FOUND)
        previous_status = booking.booking_status
        if previous_status != "NotYet":
            return Response({"message":"Cannot edit booking"},
                            status=status.HTTP_400_BAD_REQUEST)

        guest = request.data.get('guest')
        room = request.data.get('room')
        booking_time = request.data.get('booking_time')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        check_in = request.data.get('check_in')
        check_out = request.data.get('check_out')
        booking_status = previous_status

        data = {
            'guest': guest,
            'room': room,
            'booking_time': booking_time,
            'start_time': start_time,
            'end_time': end_time,
            'check_in': check_in,
            'check_out': check_out,
            'booking_status': booking_status
        }

        serializer = BookingSerializer(instance=booking, data=data)
        if serializer.is_valid():
            serializer.save()
            if room != booking.room.pk:
                booking.room.is_valid = True
                booking.room.save()
                new_room = Room.objects.get(id=room)
                new_room.is_valid = False
                new_room.save()
            return Response({"data":serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"message":"Cannot edit booking"},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"message": "Cannot find this booking"},
                            status=status.HTTP_404_NOT_FOUND)
        booking.room.is_valid = True
        booking.room.save()
        booking.delete()
        return Response({"message": "Delete Successfully"},
                        status=status.HTTP_204_NO_CONTENT)


class CheckInOrCheckOutView(APIView):
    def put(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"message": "Cannot find this booking"},
                            status=status.HTTP_404_NOT_FOUND)
        previous_status = booking.booking_status

        booking_status = request.data.get('booking_status')
        if booking_status == 'CheckIn' and previous_status != 'NotYet':
            return Response({"message":"Cannot edit booking"},
                    status=status.HTTP_400_BAD_REQUEST)
        if booking_status == 'CheckOut' and previous_status != 'CheckIn':
            return Response({"message":"Cannot edit booking"},
                    status=status.HTTP_400_BAD_REQUEST)

        booking.booking_status = booking_status
        booking.save()

        if booking_status == "CheckOut":
            booking.room.is_valid = True
            booking.room.save()
            booking.check_out = datetime.now()
            booking.save()
        else:
            booking.check_in = datetime.now()
            booking.save()

        serializer = BookingSerializer(booking)
        return Response({"data":serializer.data},
                            status=status.HTTP_200_OK)
