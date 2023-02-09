# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/frontend-stream/$', consumers.FrontendStreamConsumer.as_asgi()),
    re_path(r'ws/audio-stream/$', consumers.AudioStreamConsumer.as_asgi()),
]
