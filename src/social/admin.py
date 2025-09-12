from django.contrib import admin
from .models import Follow, Event

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "followee", "created_at")
    search_fields = ("follower__email", "followee__email")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "created_at")
    search_fields = ("user__email",)
    list_filter = ("type",)