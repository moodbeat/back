from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "events"
    verbose_name = 'События'

    def ready(self):
        from .signals import handlers  # noqa
