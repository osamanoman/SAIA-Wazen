from django.apps import AppConfig


class WidgetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'widget'
    verbose_name = 'Chatbot Widget'

    def ready(self):
        """Initialize the widget app."""
        # Import any signals or startup code here
        pass
