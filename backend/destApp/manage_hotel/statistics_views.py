from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import Coalesce
from manage_hotel.models import Booking, Room

class BookingStatisticsView(APIView):

    def get(self, request):
        # Total number of Bookings
        total_bookings = Booking.objects.count()

        # Total revenue achieved
        total_revenue = Booking.objects.aggregate(
            total_revenue=Coalesce(Sum('room__room_price'), 0))['total_revenue']

        # Revenue statistics classified by room type
        revenue_by_room_type = Room.objects.values('room_type').annotate(
            total_revenue=Coalesce(Sum('booking__room__room_price'), 0)
            ).order_by('-total_revenue')

        data = {
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'revenue_by_room_type': revenue_by_room_type
        }

        return Response({"data": data},
                        status=status.HTTP_200_OK)
