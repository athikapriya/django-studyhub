from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path("room/<slug:slug>/", views.room, name="room"),
]
