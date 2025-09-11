from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product'

    def ready(self):
        """
        Called when Django starts up.
        Import all company assistants to ensure they are registered with django-ai-assistant.
        """
        try:
            # Import the assistants module to trigger discovery and registration
            from product.assistants import COMPANY_ASSISTANTS
            print(f"✅ Registered {len(COMPANY_ASSISTANTS)} company assistants: {list(COMPANY_ASSISTANTS.keys())}")
        except Exception as e:
            print(f"❌ Error registering company assistants: {e}")
            import traceback
            traceback.print_exc()
