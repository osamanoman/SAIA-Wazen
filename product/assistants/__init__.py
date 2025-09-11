"""
Company-Specific AI Assistants

This module automatically imports all company-specific AI assistants.
Each company can have its own dedicated assistant with isolated tools and configurations.

IMPORTANT: This module ensures all company assistants are registered with django-ai-assistant
by importing them during Django startup.
"""

import importlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Get the directory path of this module
ASSISTANTS_DIR = Path(__file__).parent

def discover_and_register_company_assistants():
    """
    Automatically discover, import, and register all company-specific AI assistants.

    This function ensures that all company assistants are:
    1. Imported (which triggers their registration with django-ai-assistant)
    2. Added to our custom COMPANY_ASSISTANTS registry

    Returns:
        dict: Mapping of assistant_id to assistant class
    """
    assistants = {}

    # Scan for all *_ai_assistant.py files in this directory
    for file_path in ASSISTANTS_DIR.glob("*_ai_assistant.py"):
        if file_path.name == "__init__.py":
            continue

        module_name = file_path.stem  # filename without extension

        try:
            # Import the module (this registers the assistant with django-ai-assistant)
            full_module_name = f"product.assistants.{module_name}"
            module = importlib.import_module(full_module_name)

            # Look for classes ending with 'AIAssistant'
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    attr_name.endswith('AIAssistant') and
                    hasattr(attr, 'id') and
                    hasattr(attr, 'name')):

                    assistants[attr.id] = attr
                    logger.info(f"Discovered and registered company assistant: {attr.id} ({attr.name})")

        except Exception as e:
            logger.warning(f"Failed to import assistant module {module_name}: {e}")

    return assistants

# Automatically discover and register all company assistants
COMPANY_ASSISTANTS = discover_and_register_company_assistants()

# Export discovered assistants
__all__ = list(COMPANY_ASSISTANTS.keys()) + ['COMPANY_ASSISTANTS', 'discover_and_register_company_assistants']
