# api/auth/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

# drf-spectacular (OpenAPI)
from drf_spectacular.utils import (
    extend_schema,
)


@extend_schema(tags=["auth"])
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
