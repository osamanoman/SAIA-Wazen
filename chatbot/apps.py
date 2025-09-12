"""
Django App Configuration for SAIA Chatbot
"""

from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'
    verbose_name = 'SAIA Website Chatbot'
    
    def ready(self):
        """
        Perform initialization when Django starts.
        Import signal handlers and other startup code here.
        """
        # Import signal handlers when app is ready
        try:
            from . import signals
        except ImportError:
            pass
