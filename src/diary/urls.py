from django.urls import path
from . import views

app_name = "diary"

urlpatterns = [
    path("", views.diary_view, name="index"),
    path("add/", views.add_entry, name="add"),
    path("delete/<int:entry_id>/", views.delete_entry, name="delete"),
    path("join/", views.join_challenge, name="join"),
    path("month/", views.month_view, name="month"),
]