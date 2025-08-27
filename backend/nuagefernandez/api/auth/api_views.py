# api/auth/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

# drf-spectacular (OpenAPI)
from drf_spectacular.utils import (
    extend_schema,
)


@extend_schema(tags=["auth"])
class MyTokenObtainPairView(TokenObtainPairView):
    """
    Renvoie toujours access/refresh dans le body,
    ET pose des cookies HttpOnly pour pouvoir utiliser SSE sans header.
    """

    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # appele l'aut de DRF qui retourne les token
        resp = super().post(request, *args, **kwargs)
        # reupere les token pour les placer dans le cookie
        # necessaire pour SSE, car l'implementation SSE par defaut ne met pas bearer dans les header
        # donc il faut passer par des cookie d'auth que l'on met ici.
        access = resp.data.get("access")
        refresh = resp.data.get("refresh")

        if access:
            resp.set_cookie(
                "access",
                access,
                httponly=True,
                samesite="Lax",  # même site grâce au proxy
                secure=request.is_secure(),  # True en prod (https), False en dev http
                path="/",
                max_age=3600,
            )
        if refresh:
            resp.set_cookie(
                "refresh",
                refresh,
                httponly=True,
                samesite="Lax",  # même site grâce au proxy
                secure=request.is_secure(),  # True en prod (https), False en dev http
                path="/api/token/refresh/",
                max_age=3600,
            )
        return resp
