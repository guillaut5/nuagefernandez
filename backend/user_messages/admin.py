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
        "deleted",
        "ip_address",
    )
    list_filter = ("deleted", "timestamp", "sender", "recipient", "recipient_group")
    search_fields = (
        "text",
        "sender__username",
        "recipient__username",
        "recipient_group__groupname",
    )
    readonly_fields = ("ip_address", "user_agent", "timestamp")


@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = (
        "message",
        "user",
        "is_read",
        "is_deleted",
        "read_at",
    )
    search_fields = ("user", "is_read", "is_deleted")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("groupname",)
    search_fields = ("groupname",)
