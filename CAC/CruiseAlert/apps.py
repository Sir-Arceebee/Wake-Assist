from django.apps import AppConfig


class CruisealertConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CruiseAlert'

    def ready(self):
        import CruiseAlert.models  # Ensures signals are registered
