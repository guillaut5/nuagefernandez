# views.py

# Standard library
import logging
import json

# Third-party / Django
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.db.models import Max, Q, Exists, OuterRef

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import now
from django.http import StreamingHttpResponse

# DRF
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ipware import get_client_ip

# drf-spectacular (OpenAPI)
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)

# Local app
from nuagefernandez.api.auth.authentification import CookieJWTAuthentication
from .models import Group, Message, MessageReadStatus
from .pagination import FifteenPerPagePagination
from .serializers import (
    ConversationSummarySerializer,
    GroupSerializer,
    MessageReadStatusSerializer,
    MessageReadStatusUpdateSerializer,
    MessageSendSerializer,
    MessageSerializer,
    MessageThreadSerializer,
    UserSerializer,
)
from user_messages.sse_bus import subscribe, unsubscribe, publish
from user_messages.sse_renderer import EventStreamRenderer

logger = logging.getLogger(__name__)


# -- les conversations summary


@extend_schema(
    operation_id="sse_messages",
    tags=["liste"],
    summary="Flux SSE des messages",
    description=(
        "Établit une connexion SSE (Server-Sent Events) protégée par JWT en cookie. "
        "Retourne un flux `text/event-stream` contenant les messages au format SSE.\n\n"
        "Exemple de premier event :\n\n"
        "```\n"
        "event: hello\n"
        "data: {}\n"
        "\n```\n"
        "Ensuite, chaque message :\n\n"
        "```\n"
        'data: {"from": "user-12", "text": "Salut !"}\n'
        "\n```\n"
    ),
    responses={
        200: OpenApiResponse(description="Flux SSE (content-type: text/event-stream)."),
        401: OpenApiResponse(description="Authentification requise."),
    },
    examples=[
        OpenApiExample(
            "Premier event SSE",
            value="event: hello\ndata: {}\n\n",
            media_type="text/event-stream",
        ),
        OpenApiExample(
            "Message SSE",
            value='data: {"from": "user-12", "text": "Salut !"}\n\n',
            media_type="text/event-stream",
        ),
    ],
)
class SSEMessagesView(APIView):
    """
    SSE protégé par JWT en cookie (HttpOnly).
    """

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [EventStreamRenderer]  # <-- clé pour éviter le 406

    def get(self, request):
        user_id = request.user.id
        q = subscribe(user_id)

        def stream():
            try:
                yield "event: hello\ndata: {}\n\n"
                while True:
                    payload = q.get()
                    yield f"data: {json.dumps(payload)}\n\n"
            finally:
                unsubscribe(user_id, q)

        resp = StreamingHttpResponse(stream(), content_type="text/event-stream")
        resp["Cache-Control"] = "no-cache"
        resp["X-Accel-Buffering"] = "no"
        return resp


@extend_schema(
    operation_id="conversations_summary",
    tags=["liste"],
    summary="Résumé des conversations de l’utilisateur courant",
    description=(
        "Renvoie la liste des conversations (directes et groupes) avec : "
        "`id`, `label`, `type`, `last_message_at`, `unread_count`. "
        "Triée par `last_message_at` décroissant."
    ),
    # Pas de query params ici
    responses={
        200: OpenApiResponse(
            response=ConversationSummarySerializer(many=True),
            description="Liste des conversations.",
        ),
        401: OpenApiResponse(description="Authentification requise."),
    },
    examples=[
        OpenApiExample(
            "Exemple mixte (user + group)",
            value=[
                {
                    "id": "user-12",
                    "label": "renaud",
                    "type": "user",
                    "last_message_at": "2025-08-22T14:25:37Z",
                    "unread_count": 2,
                },
                {
                    "id": "group-5",
                    "label": "Classe de maths",
                    "type": "group",
                    "last_message_at": "2025-08-21T19:03:12Z",
                    "unread_count": 0,
                },
            ],
        ),
    ],
)
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
            Q(sender=user) | Q(recipient=user),
            recipient_group__isnull=True,
            deleted_for_all=False,
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
    qs = MessageReadStatus.objects.filter(
        user=user, is_read=False, is_hidden=False
    ).values("message_id")
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


@extend_schema(tags=["liste"])
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

    @extend_schema(
        operation_id="messages_thread",
        tags=["liste"],
        summary="Messages d'un conversation",
        description=(
            "Retourne les messages d'une conversation.\n"
            "- 1-to-1 : tous les messages entre l’utilisateur courant et `user`.\n"
            "- group : tous les messages du groupe `group`.\n\n"
            "Contrainte : **exactement un** des deux paramètres `user` ou `group`."
        ),
        parameters=[
            OpenApiParameter(
                name="user",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="ID d'un autre utilisateur (mutuellement exclusif avec `group`).",
            ),
            OpenApiParameter(
                name="group",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="ID d'un groupe (mutuellement exclusif avec `user`).",
            ),
            OpenApiParameter(
                name="mark_read",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Marque les messages comme lus pour l’utilisateur courant (par défaut: false).",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=MessageSerializer(many=True),
                description="Liste triée par timestamp ASC.",
            ),
            400: OpenApiResponse(description="Erreur de validation des paramètres."),
            403: OpenApiResponse(description="Accès refusé (sécurité)."),
        },
        examples=[
            OpenApiExample(
                "Exemple 1-to-1",
                value=[
                    {
                        "id": 101,
                        "text": "Salut, tu es dispo demain ?",
                        "image": "/media/image/aeax.jpg",
                        "timestamp": "2025-08-22T14:20:01Z",
                        "latitude": None,
                        "longitude": None,
                        "sender": {"id": 3, "username": "guillaume"},
                        "recipient": {"id": 12, "username": "renaud"},
                        "recipient_group": None,
                    }
                ],
            ),
            OpenApiExample(
                "Exemple groupe",
                value=[
                    {
                        "id": 201,
                        "text": "Bienvenue dans le groupe !",
                        "image": None,
                        "timestamp": "2025-08-22T09:10:30Z",
                        "latitude": None,
                        "longitude": None,
                        "sender": {"id": 5, "username": "prof"},
                        "recipient": None,
                        "recipient_group": {"id": 7, "name": "Classe de maths"},
                    }
                ],
            ),
        ],
    )
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

        # Point de départ : tous les messages non supprimés globalement
        qs = Message.objects.select_related(
            "sender", "recipient", "recipient_group"
        ).filter(deleted_for_all=False)

        # Sous-requête : "y a-t-il un MessageReadStatus pour CE message (OuterRef('pk'))
        # appartenant à l'utilisateur me ET avec is_hidden=True ?"
        hidden_for_me = MessageReadStatus.objects.filter(
            message_id=OuterRef("pk"),
            user=me,
            is_hidden=True,
        )

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

            # Annote chaque message avec un booléen _hidden:
            #   True  si la sous-requête renvoie au moins une ligne (=> le message est caché pour me)
            #   False sinon.
            # Puis on garde uniquement _hidden=False (donc non caché) et on ordonne par date.
            qs = (
                qs.annotate(_hidden=Exists(hidden_for_me))
                .filter(_hidden=False)
                .order_by("timestamp")
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
            # Annote chaque message avec un booléen _hidden:
            #   True  si la sous-requête renvoie au moins une ligne (=> le message est caché pour me)
            #   False sinon.
            # Puis on garde uniquement _hidden=False (donc non caché) et on ordonne par date.
            qs = (
                qs.annotate(_hidden=Exists(hidden_for_me))
                .filter(_hidden=False)
                .order_by("timestamp")
            )
            if mark_read:
                # Exemple : marquer comme lus les messages du groupe pour me (hors messages envoyés par me)
                ids = list(qs.exclude(sender_id=me.id).values_list("id", flat=True))
                MessageReadStatus.objects.filter(message_id__in=ids, user=me).update(
                    is_read=True
                )

        data = MessageThreadSerializer(qs, many=True, context={"request": request}).data
        return Response(data, status=200)


def _payload_for_user(msg, conv_id):
    return {
        "kind": "message",
        "message_id": msg.id,
        "conv_id": conv_id,  # "user-<id>" ou "group-<id>"
        "preview": (msg.text or "")[:120],
        "timestamp": msg.timestamp.isoformat(),
        "sender": {"id": msg.sender_id, "username": msg.sender.username},
    }


@extend_schema(tags=["actions"])
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

        ip, is_routable = get_client_ip(request)
        if ip is None:
            client_ip = "0.0.0.0"
        else:
            client_ip = ip
        msg.ip_address = client_ip
        msg.user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

        msg.save()
        # Statuts de lecture
        targets = []
        # Création des statuts
        if msg.recipient:
            MessageReadStatus.objects.create(message=msg, user=msg.recipient)
            targets = [msg.recipient_id]
            conv_id = (
                f"user-{msg.sender_id}"  # côté destinataire, la conv = user-<sender>
            )
        elif msg.recipient_group:
            users = msg.recipient_group.members.exclude(id=request.user.id)
            MessageReadStatus.objects.bulk_create(
                [MessageReadStatus(message=msg, user=u) for u in users],
                ignore_conflicts=True,
            )
            targets = list(users.values_list("id", flat=True))
            conv_id = f"group-{msg.recipient_group_id}"
        else:
            conv_id = "unknown"

        # ➜ Publier un event SSE pour chaque destinataire
        payload = _payload_for_user(msg, conv_id)
        for uid in targets:
            publish(uid, payload)

        # Logging pédagogique
        timestamp = now().strftime("%Y-%m-%d %H:%M:%S")
        recipient = msg.recipient.username if msg.recipient else ""
        group = msg.recipient_group.groupname if msg.recipient_group else ""
        target = recipient or group or "TOUS"
        has_image = "Oui" if msg.image else "Non"

        logger.info(
            f"[{timestamp}] Expéditeur: {msg.sender.username}  Destinataire: {target} | Contenu: {msg.text} | Image: {has_image}"
        )

        return Response({"success": True}, status=status.HTTP_201_CREATED)


@extend_schema(tags=["actions"])
class HideMessageAPIView(APIView):
    """
    POST /api/messages/{id}/hide/  -> masque le message pour l'utilisateur courant
    """

    permission_classes = [permissions.IsAuthenticated]

    def _is_participant(self, user, msg: Message) -> bool:
        if msg.sender_id == user.id:
            return True
        if msg.recipient_id and msg.recipient_id == user.id:
            return True
        if (
            msg.recipient_group_id
            and user.groups.filter(id=msg.recipient_group_id).exists()
        ):
            return True
        return False

    def post(self, request, pk: int):
        msg = get_object_or_404(Message, pk=pk)
        if not self._is_participant(request.user, msg):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        mrs, _ = MessageReadStatus.objects.get_or_create(message=msg, user=request.user)
        if not mrs.is_hidden:
            mrs.is_hidden = True
            mrs.save(update_fields=["is_hidden"])
        return Response({"status": "ok", "hidden": True})


@extend_schema(tags=["actions"])
class DeleteForAllMessageAPIView(APIView):
    """
    POST /api/messages/{id}/delete_for_all/  -> retire pour tout le monde
    Autorisé: expéditeur
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        msg = get_object_or_404(Message, pk=pk)
        if msg.sender_id != request.user.id:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        if not msg.deleted_for_all:
            msg.deleted_for_all = True
            # Optionnel si tu as ces champs :
            msg.deleted_at = timezone.now()
            msg.deleted_by = request.user
            msg.save(update_fields=["deleted_for_all", "deleted_at", "deleted_by"])
            # (Pédago) tu peux garder text/image intacts côté base
            # OU anonymiser: msg.text="", msg.image=None, puis save()

        return Response({"status": "ok", "deleted_for_all": True})


@extend_schema(tags=["oldstuff"])
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
                is_hidden=False,
                message__deleted_for_all=False,
            )
            .select_related(
                "message",
                "message__sender",
                "message__recipient",
                "message__recipient_group",
            )
            .order_by("-message__timestamp")
        )


# pour lister les message status
@extend_schema(tags=["oldstuff"])
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
@extend_schema(tags=["oldstuff"])
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
                deleted_for_all=False,
            )
            .select_related("sender", "recipient", "recipient_group")
            .order_by("-timestamp")
        )


# -- tous les gropues
@extend_schema(tags=["user & group"])
class AllGroupsAPIView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


# - kes gropues auxquel j'appartiens
@extend_schema(tags=["user & group"])
class UserGroupsAPIView(generics.ListAPIView):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.custom_user_groups.all()


# - Tous les user
@extend_schema(tags=["user & group"])
class UserAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()
