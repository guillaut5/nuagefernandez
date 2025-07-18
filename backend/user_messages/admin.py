from django.contrib import admin
from .models import Message, Group


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
        "recipient_group__name",
    )
    readonly_fields = ("ip_address", "user_agent", "timestamp")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
