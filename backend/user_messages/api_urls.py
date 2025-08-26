from django.urls import path
from rest_framework.views import APIView
from user_messages.api_views import (
    SendMessageAPIView,
    UserMessagesListAPIView,
    MessageReadStatusUpdateAPIView,
    AllGroupsAPIView,
    UserGroupsAPIView,
    UserSentMessagesListAPIView,
    UserAPIView,
    conversations_summary,
    MessageThreadView,
    HideMessageAPIView,
    DeleteForAllMessageAPIView,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


urlpatterns = [
    # === liste ===============================================================
    # Canonique
    path("conversations-summary/", conversations_summary, name="conversations-summary"),
    # Alias rétro-compat (conserver quelques semaines puis supprimer)
    path(
        "conversations-summary/", conversations_summary, name="converstation-summary"
    ),  # deprecated
    path("thread/", MessageThreadView.as_view(), name="messages-thread"),
    # === actions =============================================================
    path(
        "messages/<int:pk>/delete_for_all/",
        DeleteForAllMessageAPIView.as_view(),
        name="message-delete-for-all",
    ),
    path(
        "messages/<int:pk>/hide/",
        HideMessageAPIView.as_view(),
        name="message-hide",
    ),
    path("send/", SendMessageAPIView.as_view(), name="send-message"),
    # === user & group ========================================================
    path("groups/", AllGroupsAPIView.as_view(), name="all-groups"),
    path("my-groups/", UserGroupsAPIView.as_view(), name="user-groups"),
    path("users/", UserAPIView.as_view(), name="all-users"),
    # === oldstuff ============================================================
    path(
        "message-status/<int:pk>/",
        MessageReadStatusUpdateAPIView.as_view(),
        name="message-status-update",
    ),
    path("messages/", UserMessagesListAPIView.as_view(), name="user-messages"),
    path("sent/", UserSentMessagesListAPIView.as_view(), name="user-sent-messages"),
]
