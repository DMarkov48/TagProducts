from django.db import models
from django.conf import settings

class ProductProposal(models.Model):
    STATUS = [
        ("pending", "На рассмотрении"),
        ("approved", "Одобрено"),
        ("rejected", "Отклонено"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор")
    name = models.CharField("Базовое название", max_length=200)            # например: Яблоко
    kind = models.CharField("Вид", max_length=120, blank=True)      # например: Фуджи
    photo = models.ImageField("Фото (опц.)", upload_to="proposals/", blank=True, null=True)
    kcal = models.DecimalField("Ккал/100г", max_digits=6, decimal_places=2, null=True, blank=True)
    proteins = models.DecimalField("Белки/100г", max_digits=6, decimal_places=2, null=True, blank=True)
    fats = models.DecimalField("Жиры/100г", max_digits=6, decimal_places=2, null=True, blank=True)
    carbs = models.DecimalField("Углеводы/100г", max_digits=6, decimal_places=2, null=True, blank=True)

    categories_text = models.CharField(
        "Категория",
        max_length=200, blank=True,
        help_text="Напр.: Фрукты, Овощи, Напитки и т.д."
    )
    comment = models.TextField("Комментарий автора", blank=True)

    status = models.CharField("Статус", max_length=16, choices=STATUS, default="pending")
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_proposals",
        verbose_name="Модератор"
    )
    reviewed_at = models.DateTimeField("Проверено", null=True, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка на продукт"
        verbose_name_plural = "Заявки на продукты"

    def __str__(self):
        return f"{self.name}" + (f" — {self.kind}" if self.kind else "")