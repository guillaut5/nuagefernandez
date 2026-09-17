import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# BASE_DIR pour chemins absolus
BASE_DIR = Path(__file__).resolve().parent.parent

# En local, pas de .env : les valeurs par défaut ci-dessous (dev) s'appliquent.
# En prod, on crée backend/.env (voir backend/.env.example) pour verrouiller
# SECRET_KEY / DEBUG / ALLOWED_HOSTS / CORS sans toucher au code.
load_dotenv(BASE_DIR / ".env")


def _env_bool(name, default):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes")


def _env_list(name, default):
    raw = os.environ.get(name)
    if raw is None:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


# Clé secrète Django. La valeur par défaut ne convient QUE pour du dev local :
# en prod, définir DJANGO_SECRET_KEY dans backend/.env.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-nuagefernandez-1234567890")

# Choix de la commande de speaker
SPEAKER = {
    # "engine": "espeak",
    # "voice": "fr+f3",
    "engine": "pico2wave",
    "voice": "fr-FR",
    "speed": "150",
    "pitch": "70",
    "fifo_path": "/tmp/speak.fifo",
}

# Debug activé par défaut (confort dev local) ; mettre DJANGO_DEBUG=False en prod.
DEBUG = _env_bool("DJANGO_DEBUG", True)

# Autoriser tout par défaut (dev local) ; restreindre via DJANGO_ALLOWED_HOSTS
# en prod (ex: "monprojet.duckdns.org").
ALLOWED_HOSTS = _env_list("DJANGO_ALLOWED_HOSTS", ["*"])

# Applications installées
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "user_messages",  # Notre app
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",
]

# Autorise toutes les origines par défaut (dev local). En prod, mettre
# DJANGO_CORS_ALLOW_ALL=False et lister DJANGO_CORS_ALLOWED_ORIGINS
# (ex: "https://monprojet.duckdns.org").
CORS_ALLOW_ALL_ORIGINS = _env_bool("DJANGO_CORS_ALLOW_ALL", True)
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = _env_list("DJANGO_CORS_ALLOWED_ORIGINS", [])


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

# Templates (utilisés par l'admin Django et la doc Swagger — plus d'UI HTML côté app)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI
# WSGI_APPLICATION = "nuagefernandez.wsgi.application"
#
# Le temps réel du chat (nouveaux messages, sidebar) passe par SSE
# (voir user_messages/sse_bus.py + SSEMessagesView), pas par des WebSockets/
# Channels. Le bus SSE est une simple queue en mémoire Python : il ne
# fonctionne QUE si gunicorn tourne avec un seul worker (voir
# deploy/roles/application/defaults/main.yml -> gunicorn_workers). Avec
# plusieurs workers, chaque process aurait sa propre queue et les
# notifications se perdraient silencieusement pour la moitié des clients.

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

# Default auto field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Log directory
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "django.log"),
            "formatter": "verbose",
        },
        "console": {  # facultatif, pour aussi voir les logs en console
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {  # tous les logs par défaut
        "handlers": ["file", "console"],
        "level": "INFO",
    },
}
