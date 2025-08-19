# api/auth/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Ajoute des champs custom ici
        token["username"] = user.username
        token["email"] = user.email
        token["is_staff"] = user.is_staff
        token["id"] = user.id

        return token
