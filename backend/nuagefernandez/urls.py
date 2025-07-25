from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("user_messages.urls")),  # Toutes les URLs de ton app "messages"
    path(
        "accounts/", include("django.contrib.auth.urls")
    ),  # Login, Logout de Django natif
    path("api/", include("nuagefernandez.api_urls")),  # <- tout passe par /api/
]

# Pour servir les fichiers uploadés (images) en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
