"""
Phase 5 Tests: Enhanced Routing with Company Config

Tests for the enhanced routing system that considers company AI configuration preferences.

NOTE: These tests are temporarily disabled as they reference legacy AI assistant classes
that have been replaced with the new company-specific assistant system.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from datetime import date
from unittest.mock import Mock

from company.models import Company
from project.views import BaseAIAssistantView
# Import company-specific AI assistants
from product.assistants import COMPANY_ASSISTANTS

User = get_user_model()


class EnhancedRoutingTests(TestCase):
    """Test enhanced routing system with company configuration"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.view = BaseAIAssistantView()
        
        # Create companies with different configurations
        self.company_configured = Company.objects.create(
            name="Configured Company",
            email="configured@company.com",
            phone=1111111111,
            activity_name="Configured Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1',
            ai_instructions_template="Custom instructions for configured company",
            ai_language='ar',
            ai_temperature=0.5,
            enabled_tools_json=["get_all_invoices", "get_contacts"],
            database_config_json={"host": "configured.db.com", "name": "configured_db"}
        )
        
        self.company_unconfigured = Company.objects.create(
            name="Unconfigured Company",
            email="unconfigured@company.com",
            phone=2222222222,
            activity_name="Unconfigured Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1'
            # No AI configuration - should use fallbacks
        )
        
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True
        )
        
        self.customer_user_configured = User.objects.create_user(
            username='customer_configured',
            email='customer_configured@test.com',
            password='testpass123',
            is_customer=True
        )
        self.customer_user_configured.company = self.company_configured
        self.customer_user_configured.save()
        
        self.customer_user_unconfigured = User.objects.create_user(
            username='customer_unconfigured',
            email='customer_unconfigured@test.com',
            password='testpass123',
            is_customer=True
        )
        self.customer_user_unconfigured.company = self.company_unconfigured
        self.customer_user_unconfigured.save()
    
    def _create_request(self, user, session_data=None):
        """Helper to create request with user and session"""
        request = self.factory.get('/')
        request.user = user
        request.session = session_data or {}
        self.view.request = request
        return request
    
    def test_admin_user_routing(self):
        """Test routing for admin users without company context"""
        self._create_request(self.admin_user)
        
        assistant_id = self.view.get_assistant_id()
        company = self.view._get_user_company_context(self.admin_user)
        
        # Admin without company should get ProductAIAssistant
        self.assertEqual(assistant_id, ProductAIAssistant.id)
        self.assertIsNotNone(company)  # Admin has a company in this test setup
    
    def test_customer_user_configured_company_routing(self):
        """Test routing for customer users with configured company"""
        self._create_request(self.customer_user_configured)
        
        assistant_id = self.view.get_assistant_id()
        company = self.view._get_user_company_context(self.customer_user_configured)
        ai_info = self.view._get_company_ai_info(company)
        
        # Customer should get CustomerDataAIAssistant
        self.assertEqual(assistant_id, CustomerDataAIAssistant.id)
        self.assertEqual(company, self.company_configured)
        
        # Should have AI configuration info
        self.assertIsNotNone(ai_info)
        self.assertEqual(ai_info['company_name'], 'Configured Company')
        self.assertEqual(ai_info['ai_language'], 'ar')
        self.assertEqual(ai_info['ai_temperature'], 0.5)
        self.assertTrue(ai_info['has_custom_instructions'])
        self.assertTrue(ai_info['has_custom_database'])
        self.assertEqual(ai_info['enabled_tools_count'], 2)
    
    def test_customer_user_unconfigured_company_routing(self):
        """Test routing for customer users with unconfigured company"""
        self._create_request(self.customer_user_unconfigured)
        
        assistant_id = self.view.get_assistant_id()
        company = self.view._get_user_company_context(self.customer_user_unconfigured)
        ai_info = self.view._get_company_ai_info(company)
        
        # Customer should get CustomerDataAIAssistant
        self.assertEqual(assistant_id, CustomerDataAIAssistant.id)
        self.assertEqual(company, self.company_unconfigured)
        
        # Should have fallback AI configuration info
        self.assertIsNotNone(ai_info)
        self.assertEqual(ai_info['company_name'], 'Unconfigured Company')
        self.assertEqual(ai_info['ai_language'], 'en')  # Default fallback
        self.assertEqual(ai_info['ai_temperature'], 0.1)  # Default fallback
        self.assertFalse(ai_info['has_custom_instructions'])
        self.assertFalse(ai_info['has_custom_database'])
        self.assertGreater(ai_info['enabled_tools_count'], 0)  # Should have default tools
    
    def test_session_company_selection_routing(self):
        """Test routing when admin selects a company via session"""
        session_data = {
            'selected_company_id': self.company_configured.id,
            'selected_company_name': self.company_configured.name
        }
        self._create_request(self.admin_user, session_data)
        
        assistant_id = self.view.get_assistant_id()
        company = self.view._get_user_company_context(self.admin_user)
        
        # Should get CustomerDataAIAssistant for selected company
        self.assertEqual(assistant_id, CustomerDataAIAssistant.id)
        self.assertEqual(company, self.company_configured)
    
    def test_invalid_session_company_fallback(self):
        """Test fallback when session contains invalid company ID"""
        session_data = {
            'selected_company_id': 99999,  # Non-existent company
            'selected_company_name': 'Non-existent Company'
        }
        self._create_request(self.admin_user, session_data)
        
        assistant_id = self.view.get_assistant_id()
        company = self.view._get_user_company_context(self.admin_user)
        
        # Should fallback and clear invalid session data
        # The exact behavior depends on whether admin has a company
        self.assertIsNotNone(assistant_id)


class CompanyAIFallbackTests(TestCase):
    """Test fallback logic for unconfigured companies"""
    
    def setUp(self):
        """Set up test data"""
        self.view = BaseAIAssistantView()
        
        self.company_minimal = Company.objects.create(
            name="Minimal Company",
            email="minimal@company.com",
            phone=3333333333,
            activity_name="Minimal Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='0'  # Inactive subscription
        )
        
        self.company_partial = Company.objects.create(
            name="Partial Company",
            email="partial@company.com",
            phone=4444444444,
            activity_name="Partial Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1',
            ai_language='ar',  # Only language configured
            ai_temperature=0.3  # Only temperature configured
        )
    
    def test_minimal_company_fallbacks(self):
        """Test fallbacks for company with minimal configuration"""
        ai_info = self.view._get_company_ai_info(self.company_minimal)
        
        self.assertIsNotNone(ai_info)
        self.assertEqual(ai_info['ai_language'], 'en')  # Default fallback
        self.assertEqual(ai_info['ai_temperature'], 0.1)  # Default fallback
        self.assertFalse(ai_info['has_custom_instructions'])
        self.assertFalse(ai_info['has_custom_database'])
        self.assertFalse(ai_info['is_configured'])
        
        # Should have multiple fallbacks applied
        fallbacks = ai_info['fallback_applied']
        self.assertIn('language', fallbacks)
        self.assertIn('temperature', fallbacks)
        self.assertIn('instructions', fallbacks)
        self.assertIn('database', fallbacks)
    
    def test_partial_company_fallbacks(self):
        """Test fallbacks for company with partial configuration"""
        ai_info = self.view._get_company_ai_info(self.company_partial)
        
        self.assertIsNotNone(ai_info)
        self.assertEqual(ai_info['ai_language'], 'ar')  # Configured value
        self.assertEqual(ai_info['ai_temperature'], 0.3)  # Configured value
        self.assertFalse(ai_info['has_custom_instructions'])
        self.assertFalse(ai_info['has_custom_database'])
        
        # Should have some fallbacks applied
        fallbacks = ai_info['fallback_applied']
        self.assertNotIn('language', fallbacks)  # Language was configured
        self.assertNotIn('temperature', fallbacks)  # Temperature was configured
        self.assertIn('instructions', fallbacks)
        self.assertIn('database', fallbacks)
    
    def test_configuration_recommendations(self):
        """Test configuration recommendations for unconfigured companies"""
        ai_info = self.view._get_company_ai_info(self.company_minimal)
        recommendations = self.view._get_configuration_recommendations(self.company_minimal, ai_info)
        
        self.assertGreater(len(recommendations), 0)
        
        # Should recommend high-priority items
        rec_types = [rec['type'] for rec in recommendations]
        self.assertIn('instructions', rec_types)
        self.assertIn('tools', rec_types)
        self.assertIn('database', rec_types)
        
        # Check recommendation structure
        for rec in recommendations:
            self.assertIn('type', rec)
            self.assertIn('title', rec)
            self.assertIn('description', rec)
            self.assertIn('priority', rec)
            self.assertIn(rec['priority'], ['high', 'medium', 'low'])
    
    def test_no_recommendations_for_configured_company(self):
        """Test that configured companies get no recommendations"""
        company_configured = Company.objects.create(
            name="Fully Configured Company",
            email="configured@company.com",
            phone=5555555555,
            activity_name="Configured Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1',
            ai_instructions_template="Custom instructions",
            ai_language='en',
            ai_temperature=0.2,
            enabled_tools_json=["get_all_invoices"],
            database_config_json={"host": "configured.db.com"}
        )
        
        ai_info = self.view._get_company_ai_info(company_configured)
        recommendations = self.view._get_configuration_recommendations(company_configured, ai_info)
        
        # Configured company should get no recommendations
        self.assertEqual(len(recommendations), 0)


class ContextDataEnhancementTests(TestCase):
    """Test enhanced context data with company AI information"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.view = BaseAIAssistantView()
        
        self.company = Company.objects.create(
            name="Context Test Company",
            email="context@company.com",
            phone=6666666666,
            activity_name="Context Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1',
            ai_instructions_template="Custom context instructions",
            ai_language='ar',
            enabled_tools_json=["get_all_invoices", "get_contacts", "test_customer_database_connection"]
        )
        
        self.user = User.objects.create_user(
            username='context_user',
            email='context@test.com',
            password='testpass123',
            is_customer=True
        )
        self.user.company = self.company
        self.user.save()
    
    def test_enhanced_context_data(self):
        """Test that context data includes enhanced company AI information"""
        request = self.factory.get('/')
        request.user = self.user
        request.session = {}
        self.view.request = request
        
        # Mock the parent get_context_data method
        self.view.get_context_data = lambda **kwargs: {}
        
        context = self.view.get_context_data()
        
        # Should include enhanced context
        self.assertIn('company_ai_info', context)
        self.assertIn('current_company', context)
        self.assertIn('config_recommendations', context)
        
        # Check company AI info
        ai_info = context['company_ai_info']
        self.assertEqual(ai_info['company_name'], 'Context Test Company')
        self.assertEqual(ai_info['ai_language'], 'ar')
        self.assertTrue(ai_info['has_custom_instructions'])
        self.assertEqual(ai_info['enabled_tools_count'], 3)
        
        # Check current company
        self.assertEqual(context['current_company'], self.company)
        
        # Check assistant description enhancement
        self.assertIn('assistant_description', context)
        description = context['assistant_description']
        self.assertIn('Context Test Company', description)
        self.assertIn('custom instructions', description)
        self.assertIn('3 AI tools', description)
        self.assertIn('language: ar', description)
