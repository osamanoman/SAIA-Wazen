"""
Django signals for Company model automation.

Handles automatic generation of company-specific AI assistant files
when new companies are created.
"""

import logging
from pathlib import Path
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Company

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Company)
def create_company_assistant(sender, instance, created, **kwargs):
    """
    Automatically create a company-specific AI assistant file when a new company is created.
    
    Args:
        sender: The Company model class
        instance: The Company instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if not created:
        # Only create assistant for new companies
        return
    
    try:
        # Import here to avoid circular imports
        from product.assistants.assistant_template import generate_company_assistant
        
        # Generate the assistant file content
        company_name = instance.name
        activity_name = getattr(instance, 'activity_name', 'business operations') or 'business operations'
        
        assistant_content = generate_company_assistant(company_name, activity_name)
        
        # Create the file path
        company_slug = company_name.lower().replace(' ', '_').replace('-', '_')
        assistants_dir = Path(settings.BASE_DIR) / 'product' / 'assistants'
        assistant_file = assistants_dir / f"{company_slug}_ai_assistant.py"
        
        # Create assistants directory if it doesn't exist
        assistants_dir.mkdir(exist_ok=True)
        
        # Write the assistant file (only if it doesn't already exist)
        if not assistant_file.exists():
            with open(assistant_file, 'w', encoding='utf-8') as f:
                f.write(assistant_content)
            
            logger.info(f"Created AI assistant file for company '{company_name}': {assistant_file}")
            
            # Update the __init__.py to refresh the assistant registry
            _refresh_assistants_init()
            
        else:
            logger.info(f"AI assistant file already exists for company '{company_name}': {assistant_file}")
            
    except Exception as e:
        logger.error(f"Failed to create AI assistant for company '{instance.name}': {e}")


def _refresh_assistants_init():
    """
    Refresh the assistants __init__.py file to include newly created assistants.
    This ensures the new assistant is automatically discovered.
    """
    try:
        # Import the discovery function
        from product.assistants import discover_company_assistants
        
        # Re-discover assistants (this will update the registry)
        discover_company_assistants()
        
        logger.info("Refreshed company assistants registry")
        
    except Exception as e:
        logger.warning(f"Failed to refresh assistants registry: {e}")


def generate_assistant_for_existing_company(company_id):
    """
    Manually generate an AI assistant for an existing company.
    
    This function can be called from Django admin or management commands
    to create assistants for companies that were created before this system was implemented.
    
    Args:
        company_id (int): ID of the company to create assistant for
        
    Returns:
        bool: True if assistant was created successfully, False otherwise
    """
    try:
        company = Company.objects.get(id=company_id)
        
        # Trigger the signal manually
        create_company_assistant(Company, company, created=True)
        
        return True
        
    except Company.DoesNotExist:
        logger.error(f"Company with ID {company_id} does not exist")
        return False
    except Exception as e:
        logger.error(f"Failed to generate assistant for company ID {company_id}: {e}")
        return False
