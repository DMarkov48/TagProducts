from django.contrib import admin
from .models import ProductProposal

@admin.register(ProductProposal)
class ProductProposalAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "status", "user", "reviewer", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "kind", "categories_text", "user__email")