# views.py

from rest_framework import generics, permissions
from django.db.models import Q
from .models import Message, Group, MessageReadStatus
from .pagination import FifteenPerPagePagination
from .serializers import (
    GroupSerializer,
    UserSerializer,
    MessageReadStatusUpdateSerializer,
    MessageReadStatusSerializer,
    MessageSerializer,
)
from django.contrib.auth.models import User

# views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from .models import Message, MessageReadStatus
from .serializers import MessageSerializer, MessageSendSerializer
import base64
import logging
from django.utils.timezone import now
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MessageSendSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        msg = serializer.save()

        # On sauve sans commit si nécessaire (DRF ne gère pas commit=False de base !)

        msg.sender = request.user
        msg.ip_address = request.META.get("REMOTE_ADDR")
        msg.user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

        msg.save()

        # Création des statuts
        if msg.recipient:
            MessageReadStatus.objects.create(message=msg, user=msg.recipient)
        elif msg.recipient_group:
            for user in msg.recipient_group.members.all():
                MessageReadStatus.objects.create(message=msg, user=user)

        # Message WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "messages_group",
            {
                "type": "new_message",
                "message": f"Message reçu de {msg.sender.username}",
            },
        )

        # Logging pédagogique
        timestamp = now().strftime("%Y-%m-%d %H:%M:%S")
        recipient = msg.recipient.username if msg.recipient else ""
        group = msg.recipient_group.name if msg.recipient_group else ""
        target = recipient or group or "TOUS"
        has_image = "Oui" if msg.image else "Non"

        logger.info(
            f"[{timestamp}] Expéditeur: {msg.sender.username}  Destinataire: {target} | Contenu: {msg.text} | Image: {has_image}"
        )

        return Response({"success": True}, status=status.HTTP_201_CREATED)


class UserMessagesListAPIView(generics.ListAPIView):
    """
    GET /api/messages/  ->  Liste paginée des messages destinés à l'utilisateur
    avec leur statut de lecture / suppression.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageReadStatusSerializer
    pagination_class = FifteenPerPagePagination

    def get_queryset(self):
        user = self.request.user
        return (
            MessageReadStatus.objects.filter(
                user=user,
                is_deleted=False,
                message__deleted=False,
            )
            .select_related(
                "message",
                "message__sender",
                "message__recipient",
                "message__recipient_group",
            )
            .order_by("-message__timestamp")
        )


class MessageReadStatusUpdateAPIView(generics.UpdateAPIView):
    """
    PATCH /api/message-status/<pk>/  ->  Marquer un message comme lu / supprimé
    (uniquement si le statut appartient à l'utilisateur connecté).
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageReadStatusUpdateSerializer
    http_method_names = ["patch"]

    def get_queryset(self):
        return MessageReadStatus.objects.filter(user=self.request.user)


# - messages envoyés
class UserSentMessagesListAPIView(generics.ListAPIView):
    """
    GET /api/messages/sent/  ->  Liste paginée des messages que l'utilisateur a envoyés.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer  # pas besoin du statut
    pagination_class = FifteenPerPagePagination

    def get_queryset(self):
        return (
            Message.objects.filter(
                sender=self.request.user,
                deleted=False,
            )
            .select_related("sender", "recipient", "recipient_group")
            .order_by("-timestamp")
        )


# -- tous les gropues
class AllGroupsAPIView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


# - kes gropues auxquel j'appartiens
class UserGroupsAPIView(generics.ListAPIView):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.custom_user_groups.all()


# - kes gropues auxquel j'appartiens
class UserAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()
