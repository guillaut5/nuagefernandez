from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "user_messages"

urlpatterns = [
    path("", views.home, name="home"),
    path("user_messages/", views.message_list, name="user_messages"),
    path("send/", views.send_message, name="send_message"),
    path("delete/<int:message_id>/", views.delete_message, name="delete_message"),
    path(
        "delete_received/<int:status_id>/",
        views.delete_received_message,
        name="delete_received_message",
    ),
    path("sent/", views.sent_messages, name="sent_messages"),
    path("login/success/", views.login_success, name="login_success"),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="/accounts/login/"),
        name="logout",
    ),
    path("register/", views.register, name="register"),
    path(
        "registration_success/", views.registration_success, name="registration_success"
    ),
]
