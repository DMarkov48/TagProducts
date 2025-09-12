from django.db import models
from django.conf import settings
from django.utils import timezone
from products.models import Product

class Challenge(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="challenge")
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField()  # установим при создании (start_date + 365)
    target_unique = models.PositiveIntegerField(default=400)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Челлендж {self.user.email} {self.start_date}–{self.end_date}"

class DiaryEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="diary_entries")
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="diary_entries")
    amount_grams = models.PositiveIntegerField(null=True, blank=True)
    note = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # запретим повтор самой пары (user, date, product)
            models.UniqueConstraint(fields=["user", "date", "product"], name="uniq_user_date_product")
        ]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "product"]),
        ]

    def __str__(self):
        return f"{self.user.email} — {self.product} — {self.date}"