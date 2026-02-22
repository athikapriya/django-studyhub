# third-party imports
from django.urls import path
from django.contrib.auth import views as auth_views

# local app imports
from . import views
from .forms import CustomSetPasswordForm

urlpatterns = [
    # =============== Auth urls =============== 
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerUser, name="register"),

    # =============== Password reset urls ===============
    path("registration/password_reset/", 
         auth_views.PasswordResetView.as_view(template_name="base/authentication/password_reset.html"), 
         name="password_reset"),
         
    path("registration/password_reset/done/", 
         auth_views.PasswordResetDoneView.as_view(template_name="base/authentication/password_reset_done.html"), 
         name="password_reset_done"),

    path("registration/reset/<uidb64>/<token>/", 
         auth_views.PasswordResetConfirmView.as_view(template_name="base/authentication/password_reset_confirm.html", 
                                                     form_class=CustomSetPasswordForm), 
         name="password_reset_confirm"),

    path("registration/reset/done/", 
         auth_views.PasswordResetCompleteView.as_view(template_name="base/authentication/password_reset_complete.html"), 
         name="password_reset_complete"),

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

    # =============== Profile edit =============== 
    path("<str:username>/settings/update-profile/", views.user_edit, name="user-edit"),

    # =============== Activities + Notifications =============== 
    path("<str:username>/activity/", views.user_activity, name="activity"),
    path("<str:username>/notification/", views.user_notifications, name="notification"),

    # =============== Change password =============== 
    path("settings/change-password/", views.change_password, name="change-password"),
]
