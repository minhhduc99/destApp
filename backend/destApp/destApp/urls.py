from django.urls import path, include


urlpatterns = [
    path('api/', include([
        path('account/', include("account.urls")),
        path('hotel/', include("manage_hotel.urls")),
    ])),
]
