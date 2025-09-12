from django.contrib import admin
from .models import Challenge, DiaryEntry

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("user", "start_date", "end_date", "target_unique", "is_active")
    search_fields = ("user__email",)

@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "product", "amount_grams", "created_at")
    list_filter = ("date",)
    search_fields = ("user__email", "product__name", "product__kind")