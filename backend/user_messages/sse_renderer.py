# sse_renderer.py
from rest_framework.renderers import BaseRenderer


class EventStreamRenderer(BaseRenderer):
    media_type = "text/event-stream"
    format = "sse"
    charset = None  # pas d'encodage ajouté par DRF

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # On retourne tel quel; on n'utilise pas DRF Response ici
        return data
