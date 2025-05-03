from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages as flash_messages
from .forms import UserRegistrationForm, MessageForm
from .models import Message
import requests
import os
from django.http import HttpResponse
from user_messages.models import Message, Group, MessageReadStatus
import base64
from django.core.files.base import ContentFile
import logging
from django.utils.timezone import now
from django.urls import reverse

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# Configurer un logger spécifique à ton appli
logger = logging.getLogger("user_messages")


def home(request):
    if request.user.is_authenticated:
        return redirect("user_messages:user_messages")
    else:
        return redirect("login")


@login_required
def login_success(request):
    if request.user.is_superuser:
        return redirect("/admin/")  # Si c'est un superutilisateur → page admin
    else:
        return redirect(
            "/"
        )  # Sinon tu peux rediriger ailleurs, genre vers la page d'accueil


# Fonction pour loguer les actions
def log_action(action_type, description):
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "actions.log")
    timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] [{action_type}] {description}\n")


# Fonction pour récupérer une géolocalisation rapide par IP
def get_geo_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        data = response.json()
        if data["status"] == "success":
            return f"{data['country']} - {data['regionName']} - {data['city']} (FAI: {data['isp']})"
        else:
            return "Géolocalisation impossible"
    except Exception:
        return "Erreur géolocalisation"


# Inscription
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_active = False  # Nécessite validation admin
            user.save()

            ip = request.META.get("REMOTE_ADDR")
            user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")
            geo = get_geo_info(ip)

            log_action(
                "INSCRIPTION",
                f"Utilisateur '{user.username}' créé depuis IP {ip} ({geo}) - User-Agent: {user_agent}",
            )

            return redirect(reverse("user_messages:registration_success"))
    else:
        form = UserRegistrationForm()
    return render(request, "registration/register.html", {"form": form})


def registration_success(request):
    return render(request, "registration/registration_success.html")


@login_required
def sent_messages(request):
    user = request.user
    messages = Message.objects.filter(sender=user, deleted=False).order_by("-timestamp")
    return render(request, "user_messages/sent.html", {"messages": messages})


# Liste des messages reçus
@login_required
def message_list(request):
    user = request.user
    user_groups = Group.objects.filter(members=user)

    statuses = MessageReadStatus.objects.filter(
        user=request.user,
        is_deleted=False,
        message__deleted=False,  # 👈 exclure les messages supprimés par l'émetteur
    ).select_related("message")
    # Marquer comme lu automatiquement
    statuses.filter(is_read=False).update(is_read=True, read_at=timezone.now())

    received_messages = (
        Message.objects.filter(deleted=False, recipient=user)
        | Message.objects.filter(
            deleted=False, recipient__isnull=True, recipient_group__in=user_groups
        )
        | Message.objects.filter(
            deleted=False, recipient__isnull=True, recipient_group__isnull=True
        )
    )

    received_messages = received_messages.order_by("-timestamp")
    return render(
        request,
        "user_messages/list.html",
        {"messages": received_messages, "statuses": statuses},
    )


@login_required
def delete_received_message(request, status_id):
    status = get_object_or_404(MessageReadStatus, id=status_id, user=request.user)
    if request.method == "POST":
        status.is_deleted = True
        status.save()
    return redirect("user_messages:user_messages")


@login_required
def send_message(request):
    recipient_username = request.GET.get("recipient")
    if request.method == "POST":
        form = MessageForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.ip_address = request.META.get("REMOTE_ADDR")
            msg.user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

            # Traitement spécial pour capture webcam
            if "captured_image" in request.POST and request.POST["captured_image"]:
                data_url = request.POST["captured_image"]
                format, imgstr = data_url.split(";base64,")
                ext = format.split("/")[-1]
                msg.image.save(
                    f"photo_capture.{ext}",
                    ContentFile(base64.b64decode(imgstr)),
                    save=True,
                )

            msg.save()
            # Créer le statut pour le destinataire direct
            if msg.recipient:
                MessageReadStatus.objects.create(message=msg, user=msg.recipient)
            # OU pour chaque utilisateur du groupe
            elif msg.recipient_group:
                group = msg.recipient_group
                for user in group.user_set.all():
                    MessageReadStatus.objects.create(message=msg, user=user)
            # envoie dans le message channel
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "messages_group",
                {
                    "type": "new_message",
                    "message": f"Message reçu de {msg.sender.username}",
                },
            )

            # --- LOGGING pédagogique ---
            timestamp = now().strftime("%Y-%m-%d %H:%M:%S")
            recipient = msg.recipient.username if msg.recipient else ""
            group = msg.recipient_group.name if msg.recipient_group else ""
            target = recipient if recipient else (group if group else "TOUS")
            has_image = "Oui" if msg.image else "Non"

            logger.info(
                f"[{timestamp}] Expéditeur: {msg.sender.username}  Destinataire: {target} | Contenu: {msg.text} | Image: {has_image}"
            )

            return redirect("user_messages:user_messages")
        else:
            print(form.errors)
    else:
        recipient_username = request.GET.get("recipient")
        initial_data = {}
        if recipient_username:
            try:
                user_obj = User.objects.get(username=recipient_username)
                initial_data[
                    "recipient"
                ] = user_obj  # 👈 ici on passe l'instance utilisateur directement
            except User.DoesNotExist:
                pass  # Ignore si l'utilisateur n'existe pas (pas bloquant)
        form = MessageForm(initial=initial_data)

    return render(request, "user_messages/send.html", {"form": form})


# Suppression douce (Soft delete)
@login_required
def delete_message(request, message_id):
    msg = Message.objects.get(id=message_id, sender=request.user)
    if msg:
        msg.deleted = True
        msg.save()
        log_action(
            "SUPPRESSION",
            f"Message ID {message_id} supprimé par {request.user.username}",
        )
    return redirect("user_messages:user_messages")
