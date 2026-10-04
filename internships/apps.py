# internships/apps.py

from django.apps import AppConfig


class InternshipConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"

    name = "internships"

    def ready(self):
        import internships.signals
