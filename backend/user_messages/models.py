from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    groupname = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(User, related_name="custom_user_groups")

    def __str__(self):
        return self.groupname


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    recipient = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    recipient_group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="group_messages",
    )
    text = models.TextField()
    image = models.ImageField(upload_to="uploads/", null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    deleted_for_all = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="globally_deleted_messages",
    )

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"


class MessageReadStatus(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("message", "user")
        indexes = [
            models.Index(fields=["user", "is_hidden"]),
            models.Index(fields=["message", "user"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.message.id} - Lu: {self.is_read} / Supprimé: {self.is_hidden}"
