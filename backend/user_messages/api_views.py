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
    MessageThreadSerializer,
)
from django.contrib.auth.models import User

# views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from .models import Message, MessageReadStatus, Group
from .serializers import MessageSerializer, MessageSendSerializer
import base64
import logging
from django.utils.timezone import now
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Max, Count, Q
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


# -- les conversations summary
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def conversations_summary(request):
    """
    Endpoint REST : renvoie le résumé des conversations de l'utilisateur courant.

    Ce résumé permet d'afficher la "sidebar" (liste des conversations) sans que
    le front ait à reconstruire toutes les conversations à partir des messages.

    Pour chaque conversation (directe ou groupe), on renvoie :
      - id : identifiant logique de la conversation (ex: "user-12" ou "group-7")
      - label : nom affiché (username ou nom du groupe)
      - type : "user" ou "group"
      - last_message_at : date/heure du dernier message (ISO 8601)
      - unread_count : nombre de messages non lus pour l'utilisateur courant

    Logique interne :
      1. Messages directs :
         - On regroupe les messages par couple (sender, recipient).
         - On détermine "l'autre" utilisateur et on crée une conversation "user-<id>".
      2. Messages de groupe :
         - On regroupe par group_id pour construire "group-<id>".
      3. On calcule pour chaque conversation :
         - la date du dernier message (via annotate/Max).
         - le compteur de non-lus (MessageReadStatus ou équivalent).
      4. On hydrate les labels (username / nom de groupe) pour affichage.
      5. On trie les conversations par date du dernier message décroissante.

    Exemple de sortie JSON :
    [
      {
        "id": "user-12",
        "label": "renaud",
        "type": "user",
        "last_message_at": "2025-08-22T14:25:37Z",
        "unread_count": 2
      },
      {
        "id": "group-5",
        "label": "Classe de maths",
        "type": "group",
        "last_message_at": "2025-08-21T19:03:12Z",
        "unread_count": 0
      }
    ]

    Avantages :
      - Le front n'a pas besoin de recoder toute la logique de regroupement.
      - Facile d'ajouter unread badges et tri dans la sidebar.
      - On conserve un schéma de base simple (pas de table Conversation explicite).

    Limites :
      - L'agrégation est recalculée à chaque appel (ok pour démo / petit volume).
      - Pour un chat à grande échelle, il faudrait matérialiser les conversations
        et maintenir last_message/unread_count côté base.
    """
    user = request.user

    # Direct: dernières dates par (autre utilisateur)
    direct = (
        Message.objects.filter(
            Q(sender=user) | Q(recipient=user), recipient_group__isnull=True
        )
        .values("sender_id", "recipient_id")
        .annotate(last_ts=Max("timestamp"))
    )

    # Transforme en convs “user-<id>” avec last_ts
    convs = {}
    for row in direct:
        s, r, ts = row["sender_id"], row["recipient_id"], row["last_ts"]
        other_id = r if s == user.id else s
        key = f"user-{other_id}"
        convs[key] = max(convs.get(key, ts), ts)

    # Groupes: dernières dates par group_id
    groups = (
        Message.objects.filter(recipient_group__isnull=False)
        .values("recipient_group_id")
        .annotate(last_ts=Max("timestamp"))
    )
    for row in groups:
        key = f'group-{row["recipient_group_id"]}'
        convs[key] = max(convs.get(key, row["last_ts"]), row["last_ts"])

    # Unread counts (si tu as MessageReadStatus(message, user, is_read))
    # Exemple simple: compter les non-lus par conv_id
    unread = {}
    qs = MessageReadStatus.objects.filter(user=user, is_read=False).values("message_id")
    # Récupère les messages non lus pour mapper vers conv_id
    unread_msgs = (
        Message.objects.filter(
            id__in=qs,  # prend seulement les ids de qs
        )
        .exclude(sender_id=request.user.id)  # enlève ceux envoyés par l'utilisateur
        .values("id", "sender_id", "recipient_id", "recipient_group_id")
    )
    for m in unread_msgs:
        if m["recipient_group_id"]:
            key = f'group-{m["recipient_group_id"]}'
        else:
            other = m["sender_id"]  # pour le destinataire, l'autre = sender
            key = f"user-{other}"
        unread[key] = unread.get(key, 0) + 1

    # Hydrate label/type (selon le prefixe)
    # (à optimiser avec des prefetchs si besoin)
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user_map = {
        u.id: u.username
        for u in User.objects.filter(
            id__in=[
                int(k[5:])
                for k in convs.keys()
                if k.startswith("user-") and "None" not in k
            ]
        )
    }
    group_map = {
        g.id: g.groupname
        for g in Group.objects.filter(
            id__in=[
                int(k[6:])
                for k in convs.keys()
                if k.startswith("group-") and "None" not in k
            ]
        )
    }

    data = []
    for key, last_ts in convs.items():
        if key.startswith("user-") and "None" not in key:
            oid = int(key[5:])
            data.append(
                {
                    "id": key,
                    "label": user_map.get(oid, f"user-{oid}"),
                    "type": "user",
                    "last_message_at": last_ts,
                    "unread_count": unread.get(key, 0),
                }
            )
        else:
            if "None" in key:
                continue
            gid = int(key[6:])
            data.append(
                {
                    "id": key,
                    "label": group_map.get(gid, f"group-{gid}"),
                    "type": "group",
                    "last_message_at": last_ts,
                    "unread_count": unread.get(key, 0),
                }
            )
    # tri desc
    data.sort(key=lambda x: x["last_message_at"] or "", reverse=True)
    return Response(data)


## -- Les Thread de conversation


class MessageThreadView(APIView):
    """
    GET /api/messages/thread/?user=<id>  ou  /api/messages/thread/?group=<id>

    Retourne la liste des messages d'une conversation :
      - 1-to-1: tous les messages entre l'utilisateur courant et <user>
      - group : tous les messages du groupe <group>

    Sécurité :
      - 1-to-1 : l'utilisateur courant doit être l'un des deux participants
      - group  : l'utilisateur courant doit être membre du groupe

    Query params:
      - user: int  (mutuellement exclusif avec group)
      - group: int (mutuellement exclusif avec user)
      - mark_read: "true" | "false" (optionnel) → marque les messages comme lus
                   pour l'utilisateur courant (selon ta logique de MessageReadStatus)

    Réponse: liste JSON triée par timestamp ASC (premier message → dernier).

    Exemple de réponse JSON :
    [
      {
        "id": 101,
        "text": "Salut, tu es dispo demain ?",
        "image": "/media/image/aeax.jpg",
        "timestamp": "2025-08-22T14:20:01Z",
        "latitude": null,
        "longitude": null,
        "sender": {
          "id": 3,
          "username": "guillaume"
        },
        "recipient": {
          "id": 12,
          "username": "renaud"
        },
        "recipient_group": null
      },
      {
        "id": 102,
        "text": "Oui parfait, on se voit à 10h.",
        "image": null,
        "timestamp": "2025-08-22T14:22:45Z",
        "latitude": null,
        "longitude": null,
        "sender": {
          "id": 12,
          "username": "renaud"
        },
        "recipient": {
          "id": 3,
          "username": "guillaume"
        },
        "recipient_group": null
      }
    ]

    Exemple pour un groupe :
    [
      {
        "id": 201,
        "text": "Bienvenue dans le groupe !",
        "image": null,
        "timestamp": "2025-08-22T09:10:30Z",
        "latitude": null,
        "longitude": null,
        "sender": {
          "id": 5,
          "username": "prof"
        },
        "recipient": null,
        "recipient_group": {
          "id": 7,
          "name": "Classe de maths"
        }
      }
    ]
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        me = request.user
        user_id = request.query_params.get("user")
        group_id = request.query_params.get("group")
        mark_read = request.query_params.get("mark_read") == "true"

        # Validation "un seul des deux"
        if bool(user_id) == bool(group_id):
            return Response(
                {
                    "detail": "Spécifiez exactement l'un des deux paramètres : user ou group."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = Message.objects.select_related("sender", "recipient", "recipient_group")

        if user_id:
            try:
                other_id = int(user_id)
            except ValueError:
                return Response({"detail": "Paramètre user invalide."}, status=400)

            # Sécurité minimale : on autorise seulement si me parle à other (dans un sens ou l'autre)
            # (Pas besoin d'existence explicite d'une 'Conversation')
            thread_filter = Q(sender_id=me.id, recipient_id=other_id) | Q(
                sender_id=other_id, recipient_id=me.id
            )
            qs = qs.filter(thread_filter, recipient_group__isnull=True).order_by(
                "timestamp"
            )

            # Il n'y a pas de groupe ici, donc pas de vérif d'appartenance

            # Option: mark_read (si tu utilises MessageReadStatus)
            if mark_read:
                # Exemple : marquer comme lus les messages reçus par me depuis other
                ids = list(qs.filter(recipient_id=me.id).values_list("id", flat=True))
                MessageReadStatus.objects.filter(message_id__in=ids, user=me).update(
                    is_read=True
                )

        else:
            try:
                gid = int(group_id)
            except ValueError:
                return Response({"detail": "Paramètre group invalide."}, status=400)

            group = get_object_or_404(Group, id=gid)

            # Sécurité: me doit être membre du groupe
            if not group.members.filter(id=me.id).exists():
                return Response({"detail": "Accès refusé à ce groupe."}, status=403)

            qs = qs.filter(recipient_group_id=gid).order_by("timestamp")

            if mark_read:
                # Exemple : marquer comme lus les messages du groupe pour me (hors messages envoyés par me)
                ids = list(qs.exclude(sender_id=me.id).values_list("id", flat=True))
                MessageReadStatus.objects.filter(message_id__in=ids, user=me).update(
                    is_read=True
                )

        data = MessageThreadSerializer(qs, many=True, context={"request": request}).data
        return Response(data, status=200)


class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MessageSendSerializer(
            data=request.data, context={"request": request}
        )
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            # exc.detail contient la structure d’erreurs DRF (dict/list)
            logger.warning(
                "Validation error in SendMessage: %s | data=%s",
                exc.detail,
                request.data,
            )
            return Response(exc.detail, status=400)

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
            users = msg.recipient_group.members.exclude(id=request.user.id)
            for user in users:
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
