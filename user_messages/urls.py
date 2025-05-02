from django.urls import path
from . import views

app_name = "user_messages"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("user_messages/", views.message_list, name="user_messages"),
    path("send/", views.send_message, name="send_message"),
    path("delete/<int:message_id>/", views.delete_message, name="delete_message"),
    path("sent/", views.sent_messages, name="sent_messages"),
    path("login/success/", views.login_success, name="login_success"),
]
