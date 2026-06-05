from django.db import models

from backends.accounts.models import User


class Notification(models.Model):
    class Type(models.TextChoices):
        NEW_MESSAGE = "new_message", "Nouveau message"
        PROFILE_VERIFIED = "profile_verified", "Profil vérifié"
        NEW_REVIEW = "new_review", "Nouvel avis"
        PAYMENT_RECEIVED = "payment_received", "Paiement reçu"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True, default="")
    link = models.CharField(max_length=500, blank=True, default="")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "notifications"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ("-created_at",)

    def __str__(self):
        return f"[{'Lu' if self.is_read else 'Non lu'}] {self.title}"
