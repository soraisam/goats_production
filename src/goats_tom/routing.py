from django.urls import path

from goats_tom.consumers import DRAGONSConsumer, UpdatesConsumer

websocket_urlpatterns = [
    path("ws/updates/", UpdatesConsumer.as_asgi()),
    path("ws/dragons/", DRAGONSConsumer.as_asgi()),
]
