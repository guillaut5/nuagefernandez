import os
from pathlib import Path
from datetime import timedelta

# BASE_DIR pour chemins absolus
BASE_DIR = Path(__file__).resolve().parent.parent

# Clé secrète Django (tu pourras la changer plus tard pour plus de sécurité)
SECRET_KEY = "django-insecure-nuagefernandez-1234567890"

# Debug activé pour ton projet local
DEBUG = True

# Autoriser tout pour l'instant
ALLOWED_HOSTS = ["*"]

# Applications installées
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "user_messages",  # Notre app
    "widget_tweaks",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",
]
CORS_ALLOW_ALL_ORIGINS = True


# Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "nuagefernandez.api.auth.authentification.CookieJWTAuthentication",
        # "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
# Swagger setting
SPECTACULAR_SETTINGS = {
    "TITLE": "API Nuage Fernandez",
    "DESCRIPTION": "API REST pour le cloud NuageFernandez",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "TAGS": [
        {"name": "auth", "description": "Login/refresh/logout"},
        {"name": "liste", "description": "Listings pour la sidebar, etc."},
        {"name": "actions", "description": "Actions de chat (envoyer, thread, etc.)"},
        {"name": "user & group", "description": "Endpoints utilisateurs et groupes"},
        {"name": "oldstuff", "description": "Anciennes routes (deprecated)"},
    ],
}
# Middlewares
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # tout en haut !
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# JWT

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),  # ex. 2h au lieu de 5 min
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),  # ex. 7 jours
    "ROTATE_REFRESH_TOKENS": True,  # optionnel
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    # "LEEWAY": 30,  # tolérance si horloge décalée
}
# URLs
ROOT_URLCONF = "nuagefernandez.urls"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "messages", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "user_messages.context_processors.new_messages_count",
            ],
        },
    },
]

# WSGI
# WSGI_APPLICATION = "nuagefernandez.wsgi.application"
# ASGI (pour les channls)
ASGI_APPLICATION = "nuagefernandez.asgi.application"

# channels:
# Channels layers - on utilise la mémoire pour l'instant (simple pour commencer)
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}

# Base de données SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Validation mot de passe (standard Django)
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Langue et fuseau horaire
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# Dossier statiques (CSS)
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "user_messages", "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Dossier des médias (images uploadées)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "uploads")

# Redirection après login
LOGIN_REDIRECT_URL = "/messages/"
LOGIN_REDIRECT_URL = "/login/success/"

# Default auto field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Log directory
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
# --- Logging pédagogique pour user_messages ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "user_messages_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "user_messages.log",  # fichier log au même niveau que manage.py
            "formatter": "simple",
        },
    },
    "loggers": {
        "user_messages": {
            "handlers": ["user_messages_file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
