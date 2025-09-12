from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def landing(request):
    return HttpResponse("<h1>400 продуктов в год</h1><p>Добро пожаловать!</p>")

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