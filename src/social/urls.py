from django.urls import path
from . import views

app_name = "social"

urlpatterns = [
    path("feed/", views.feed, name="feed"),
    path("following/", views.following, name="following"),
    path("search/", views.user_search, name="search"),
    path("follow/<int:user_id>/", views.follow, name="follow"),
    path("unfollow/<int:user_id>/", views.unfollow, name="unfollow"),
]