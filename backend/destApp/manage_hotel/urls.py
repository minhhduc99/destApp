from django.urls import path, include
from manage_hotel.room_views import ListRoomView, AddRoomView, EditRoomView
from manage_hotel.booking_views import ListBookingView, AddBookingView, \
    EditBookingView, CheckInOrCheckOutView
from manage_hotel.statistics_views import BookingStatisticsView

urlpatterns = [
    path('rooms/', include([
        path('', ListRoomView.as_view(), name="list-all-rooms"),
        path('new', AddRoomView.as_view(), name="add-room"),
        path('<int:pk>', EditRoomView.as_view(), name="edit-room"),
    ])),
    path('bookings/', include([
        path('', ListBookingView.as_view(), name="list-all-bookings"),
        path('new', AddBookingView.as_view(), name="add-booking"),
        path('<int:pk>/', include([
            path('', EditBookingView.as_view(), name="edit-booking"),
            path('action', CheckInOrCheckOutView.as_view(), name="booking-action")
        ]))
    ])),
    path('statistics', BookingStatisticsView.as_view(), name="hotel-statistics")
]