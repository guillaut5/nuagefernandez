from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from nuagefernandez.api.auth.api_views import MyTokenObtainPairView
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


@extend_schema(
    tags=["auth"],
    summary="Refresh JWT",
    description="Rafraîchit le token d’accès à partir d’un refresh token.",
    request=TokenRefreshSerializer,
    responses=TokenRefreshSerializer,  # contient 'access' et éventuellement 'refresh' si rotation activée
)
class TokenRefreshViewAuth(TokenRefreshView):
    pass


urlpatterns = [
    # Auth JWT
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshViewAuth.as_view(), name="token_refresh"),
    # Schema & Swagger UI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Tes endpoints métier ici :
    path("messages/", include("user_messages.api_urls")),
]
