from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField("Название", max_length=120, unique=True)
    slug = models.SlugField("Слаг", unique=True, blank=True)
    parent = models.ForeignKey("self", verbose_name="Родитель",
                               null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("Название", max_length=200, unique=True)
    slug = models.SlugField("Слаг", unique=True, blank=True)
    photo = models.ImageField("Фото", upload_to="products/", blank=True, null=True)
    kind = models.CharField("Вид", max_length=200)
    kcal = models.DecimalField("Калории (ккал/100г)", max_digits=6, decimal_places=2, default=0)
    proteins = models.DecimalField("Белки (г/100г)", max_digits=6, decimal_places=2, default=0)
    fats = models.DecimalField("Жиры (г/100г)", max_digits=6, decimal_places=2, default=0)
    carbs = models.DecimalField("Углеводы (г/100г)", max_digits=6, decimal_places=2, default=0)
    categories = models.ManyToManyField(Category, verbose_name="Категории", blank=True, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name