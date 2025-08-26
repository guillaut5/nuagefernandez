from django.contrib import admin
from .models import Message, Group, MessageReadStatus


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sender",
        "recipient",
        "recipient_group",
        "timestamp",
        "deleted_for_all",
        "deleted_at",
        "deleted_by",
        "ip_address",
    )
    list_filter = (
        "deleted_for_all",
        "timestamp",
        "sender",
        "recipient",
        "recipient_group",
    )
    search_fields = (
        "text",
        "sender__username",
        "recipient__username",
        "recipient_group__groupname",
    )
    readonly_fields = ("ip_address", "user_agent", "timestamp")


from django.contrib import admin


@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message",
        "user",
        "sender",
        "is_read",
        "is_hidden",
        "read_at",
    )

    # Pour éviter les N+1
    list_select_related = ("message", "message__sender", "user")

    # Filtres (dont l’expéditeur)
    list_filter = (
        ("message__sender", admin.RelatedOnlyFieldListFilter),
        ("user", admin.RelatedOnlyFieldListFilter),
        "is_read",
        "is_hidden",
        "read_at",
    )

    # Recherche par sender + contenu du message, etc.
    search_fields = (
        "message__sender__username",
        "message__sender__first_name",
        "message__sender__last_name",
        "message__sender__email",
        "message__text",
        "message__id",
        "user__username",
        "user__email",
    )

    # Colonne personnalisée "sender" triable
    @admin.display(ordering="message__sender__username", description="Expéditeur")
    def sender(self, obj):
        # Retourne l'objet User : s'affichera via son __str__ (souvent username)
        return obj.message.sender

    # (Optionnel) navigation par date
    date_hierarchy = "read_at"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("groupname",)
    search_fields = ("groupname",)
