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


class HelloView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Salut {request.user.username} !"})


urlpatterns = [
    path("hello/", HelloView.as_view()),
    # Mise à jour d'un statut (read / deleted)
    path(
        "message-status/<int:pk>/",
        MessageReadStatusUpdateAPIView.as_view(),
        name="message-status-update",
    ),
    # Messages envoyés
    path(
        "sent/",
        UserSentMessagesListAPIView.as_view(),
        name="user-sent-messages",
    ),
    path("groups/", AllGroupsAPIView.as_view(), name="all-groups"),
    path("my-groups/", UserGroupsAPIView.as_view(), name="user-groups"),
    path("users/", UserAPIView.as_view(), name="all-users"),
    path("thread/", MessageThreadView.as_view(), name="messages-thread"),
    path("send/", SendMessageAPIView.as_view(), name="send-message"),
    path("conversations-summary/", conversations_summary, name="converstation-summary"),
    path("messages/", UserMessagesListAPIView.as_view(), name="user-messages"),
    path(
        "api/messages/<int:pk>/hide/", HideMessageAPIView.as_view(), name="message-hide"
    ),
    path(
        "api/messages/<int:pk>/delete_for_all/",
        DeleteForAllMessageAPIView.as_view(),
        name="message-delete-for-all",
    ),
]
