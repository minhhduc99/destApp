from django.urls import path, include


urlpatterns = [
    path('account/api/', include("account.urls")),
    path('manage-hotel/api/', include("manage_hotel.api.urls")),
]
