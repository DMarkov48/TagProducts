from django.urls import path
from . import views

app_name = "moderation"

urlpatterns = [
    path("submit/", views.proposal_submit, name="submit"),           # пользовательская форма
    path("", views.moderation_list, name="list"),                    # список модератору
    path("<int:pk>/", views.moderation_detail, name="detail"),       # карточка модерации
    path("<int:pk>/approve/", views.moderation_approve, name="approve"),
    path("<int:pk>/reject/", views.moderation_reject, name="reject"),
]
