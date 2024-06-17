from django.apps import AppConfig


class GOATSTomConfig(AppConfig):
    name = "goats_tom"

    def ready(self):
        from dramatiq import get_broker
        from dramatiq_abort import Abortable, backends
        from django.conf import settings

        event_backend = backends.RedisBackend.from_url(settings.DRAMATIQ_REDIS_URL)
        abortable = Abortable(backend=event_backend)
        get_broker().add_middleware(abortable)
