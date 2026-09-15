"""
ASGI config for nuagefernandez project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Non utilisé en prod (gunicorn tourne en WSGI, voir wsgi.py) : ce fichier
# reste disponible si on veut un jour lancer le serveur en ASGI (daphne/uvicorn).
# Le temps réel du chat passe par SSE (voir user_messages/sse_bus.py), pas par
# des WebSockets : l'ancien MessageConsumer (Channels) a été retiré car il
# n'était jamais réellement branché (aucun code n'appelait channel_layer.group_send).

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nuagefernandez.settings")

application = get_asgi_application()
