# serializers.py

from rest_framework import serializers
from .models import Message, Group, MessageReadStatus
from django.contrib.auth.models import User


class MessageSendSerializer(serializers.ModelSerializer):
    recipient = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    recipient_group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False, allow_null=True
    )
    captured_image = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Message
        fields = [
            "text",
            "image",
            "recipient",
            "recipient_group",
            "latitude",
            "longitude",
            "captured_image",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["sender"] = request.user
        validated_data["ip_address"] = request.META.get("REMOTE_ADDR")
        validated_data["user_agent"] = request.META.get("HTTP_USER_AGENT", "Unknown")
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)
    recipient_username = serializers.SerializerMethodField()
    recipient_group_name = serializers.SerializerMethodField()

    def get_recipient_username(self, obj):
        return obj.recipient.username if obj.recipient else None

    def get_recipient_group_name(self, obj):
        return obj.recipient_group.name if obj.recipient_group else None

    class Meta:
        model = Message
        fields = [
            "id",
            "text",
            "image",
            "timestamp",
            "latitude",
            "longitude",
            "sender_username",
            "recipient_username",
            "recipient_group_name",
        ]


class MessageReadStatusSerializer(serializers.ModelSerializer):
    """
    Utilisé pour la LISTE : on imbrique le message.
    """

    message = MessageSerializer(read_only=True)

    class Meta:
        model = MessageReadStatus
        fields = ["id", "message", "is_read", "is_deleted", "read_at"]


class MessageReadStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Utilisé pour PATCH : on ne modifie que le statut.
    """

    class Meta:
        model = MessageReadStatus
        fields = ["is_read", "is_deleted", "read_at"]
        read_only_fields = ["read_at"]

    def update(self, instance, validated_data):
        # Si on passe is_read=True et qu'aucune date n'est encore enregistrée,
        # on remplit read_at automatiquement.
        if validated_data.get("is_read") and not instance.read_at:
            from django.utils import timezone

            instance.read_at = timezone.now()
        return super().update(instance, validated_data)


class GroupSerializer(serializers.ModelSerializer):
    member_usernames = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username", source="members"
    )

    class Meta:
        model = Group
        fields = ["id", "name", "member_usernames"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]
