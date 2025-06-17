from django.apps import AppConfig


class GOATSTomConfig(AppConfig):
    name = "goats_tom"

    def ready(self):
        from django.conf import settings  # noqa: PLC0415
        from dramatiq import get_broker  # noqa: PLC0415
        from dramatiq_abort import Abortable, backends  # noqa: PLC0415

        event_backend = backends.RedisBackend.from_url(settings.DRAMATIQ_REDIS_URL)
        abortable = Abortable(backend=event_backend)
        get_broker().add_middleware(abortable)
