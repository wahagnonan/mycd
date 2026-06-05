from django.db import models

from backends.accounts.models import User


class Conversation(models.Model):
    parent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversations_as_parent"
    )
    encadreur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversations_as_encadreur"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "messagerie"
        unique_together = ("parent", "encadreur")
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ("-updated_at",)

    def __str__(self):
        return f"Conversation {self.parent.email} ↔ {self.encadreur.email}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        app_label = "messagerie"
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ("created_at",)

    def __str__(self):
        return f"Message de {self.sender.email} à {self.created_at:%d/%m %H:%M}"
