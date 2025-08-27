# api/auth/authentication.py
# -- pour permettre un authorisation par cookie de DRF
# necessaire pour utiliser les SSE (Server Side Event) qui ne permettte pas de mettre de HEADER
# et donc de Bearer d'authentification.
# Les SSE vont donc utiliser des cookie pour s'tuahtnetifier a DRF

# settings.py
# REST_FRAMEWORK = {
#    "DEFAULT_AUTHENTICATION_CLASSES": [
#        "nuagefernandez.api.auth.authentication.CookieJWTAuthentication",
#    ],
# }
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """
    Essaie d'abord l'en-tête Authorization.
    Sinon, lit le JWT 'access' depuis les cookies.
    """

    def authenticate(self, request):
        # 1) Header normal ?
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        # 2) Sinon cookie 'access'
        raw_token = request.COOKIES.get("access")
        if not raw_token:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
