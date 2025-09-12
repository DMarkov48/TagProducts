from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "kcal")
    list_filter = ("categories",)
    search_fields = ("name", "kind")
    filter_horizontal = ("categories",)
    prepopulated_fields = {"slug": ("name",)}