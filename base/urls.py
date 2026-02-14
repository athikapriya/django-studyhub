# third-party imports
from django.urls import path

# local app imports
from . import views

urlpatterns = [
    # =============== Auth urls =============== 
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerUser, name="register"),

    # =============== Homepage =============== 
    path('', views.homepage, name="homepage"),   

    # =============== Rooms =============== 
    path("room/<slug:slug>/", views.room, name="room"),

    # =============== Room CURD =============== 
    path("create-room/", views.createRoom, name="create-room"),
    path('update-room/<int:pk>/', views.updateRoom, name="update-room"),
    path("delete-room/<int:pk>/", views.deleteRoom, name="delete-room"),

    # =============== Topics ===============
    path("topics/", views.browseTopics, name="browse-topics"),

    # =============== Messages =============== 
    path('message/update/<int:pk>/', views.updateMessage, name='update-message'),
    path("message/delete/<int:pk>/", views.deleteMessage, name="delete-message"),

    # =============== User Profile =============== 
    path("<str:username>/", views.userProfile, name="user-profile"),
    path("<str:username>/activity/", views.user_activity, name="activity"),
]
