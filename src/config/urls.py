from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def landing(request):
    return render(request, "landing.html")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", landing, name="landing"),
    path("accounts/", include("accounts.urls")),
    path("products/", include("products.urls")),
    path("diary/", include("diary.urls")),
    path("social/", include("social.urls")),
    path("moderation/", include("moderation.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)