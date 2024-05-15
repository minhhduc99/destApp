from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from manage_hotel.models import Booking
from manage_hotel.serializers import BookingSerializer
from account.permissions import IsManager


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

        data = {
            'guest': guest,
            'room': room,
            'booking_time': booking_time,
            'start_time': start_time,
            'end_time': end_time,
            'check_in': check_in,
            'check_out': check_out
        }

        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
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
        guest = request.data.get('guest')
        room = request.data.get('room')
        booking_time = request.data.get('booking_time')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        check_in = request.data.get('check_in')
        check_out = request.data.get('check_out')

        data = {
            'guest': guest,
            'room': room,
            'booking_time': booking_time,
            'start_time': start_time,
            'end_time': end_time,
            'check_in': check_in,
            'check_out': check_out
        }

        serializer = BookingSerializer(instance=booking, data=data)
        if serializer.is_valid():
            serializer.save()
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
        booking.delete()
        return Response({"message": "Delete Successfully"},
                        status=status.HTTP_200_OK)
