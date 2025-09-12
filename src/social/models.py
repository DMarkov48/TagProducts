from django.db import models
from django.conf import settings

class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="following",
        on_delete=models.CASCADE
    )
    followee = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="followers",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["follower", "followee"], name="uniq_follower_followee")
        ]

    def __str__(self):
        return f"{self.follower} → {self.followee}"


class Event(models.Model):
    # универсальная лента: пока фиксируем только «добавил продукт в дневник»
    TYPE_CHOICES = [
        ("entry_created", "Добавил(а) запись в дневник"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events")
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    payload = models.JSONField(default=dict, blank=True)  # {product_id, product_name, kind, date}
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} {self.type} {self.created_at:%Y-%m-%d %H:%M}"