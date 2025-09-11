"""
Project models for SAIA Business Management System

This module contains models related to project management.
Note: WebsiteSession and SessionHandover models have been moved to the widget app.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from company.models import Company
from django_ai_assistant.models import Thread

User = get_user_model()

# WebsiteSession and SessionHandover models have been moved to widget app
# This file now only contains project-related models (if any)

# If you need to add project-specific models in the future, add them here
