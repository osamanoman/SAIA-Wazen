from django.apps import AppConfig


class CompanyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'company'

    def ready(self):
        """Import signals when the app is ready"""
        import company.signals
