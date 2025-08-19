from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from nuagefernandez.api.auth.api_views import MyTokenObtainPairView

urlpatterns = [
    # Auth JWT
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Schema & Swagger UI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Tes endpoints métier ici :
    path("messages/", include("user_messages.api_urls")),
]
