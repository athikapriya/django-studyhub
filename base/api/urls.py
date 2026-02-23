# third party import
from django.urls import path

# local app import
from . import views

urlpatterns = [
    path("", views.getRoute),
    path("rooms/", views.getRooms),
    path("room/<str:pk>/", views.getRoom),
]
