# third-party imports
from django.urls import path

# local app imports
from . import views

urlpatterns = [
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerUser, name="register"),

    path('', views.homepage, name="homepage"),
    path("room/<slug:slug>/", views.room, name="room"),
    path("topics/", views.browseTopics, name="browse-topics"),

    path("<str:username>/", views.userProfile, name="user-profile"),

    # =============== CURD urls =============== 
    path("create-room/", views.createRoom, name="create-room"),
    path('update-room/<int:pk>/', views.updateRoom, name="update-room"),
    path("delete-room/<int:pk>/", views.deleteRoom, name="delete-room"),

    path('message/update/<int:pk>/', views.updateMessage, name='update-message'),
    path("message/delete/<int:pk>/", views.deleteMessage, name="delete-message"),
]
