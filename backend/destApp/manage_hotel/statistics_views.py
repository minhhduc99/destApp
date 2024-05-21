from datetime import timedelta
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.db.models.functions import Coalesce
from manage_hotel.models import Booking, Room

class BookingStatisticsView(APIView):

    def get(self, request):
        # Total number of Bookings
        total_bookings = Booking.objects.count()

        # Total revenue achieved
        total_revenue = Booking.objects.annotate(
            duration=ExpressionWrapper(
                F('end_time') - F('start_time'),
                output_field=fields.DurationField()
            ),
            room_revenue=ExpressionWrapper(
                F('room__room_price') * (ExpressionWrapper(F('end_time') - F('start_time'), output_field=fields.DurationField()) / timedelta(days=1)),
                output_field=fields.FloatField()
            )
        ).aggregate(
            total_revenue=Coalesce(Sum('room_revenue'), 0, output_field=fields.FloatField())
        )['total_revenue']

        # Revenue statistics classified by room type
        revenue_by_room_type = Room.objects.values('room_type').annotate(
            total_revenue=Coalesce(Sum(
                ExpressionWrapper(
                    F('booking__room__room_price') * (ExpressionWrapper(F('booking__end_time') - F('booking__start_time'), output_field=fields.DurationField()) / timedelta(days=1)),
                    output_field=fields.FloatField()
                )
            ), 0, output_field=fields.FloatField())
        ).order_by('-total_revenue')

        data = {
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'revenue_by_room_type': revenue_by_room_type
        }

        return Response({"data": data},
                        status=status.HTTP_200_OK)
