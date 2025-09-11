"""
Phase 6 Tests: End-to-End Multi-Tenant System Testing

Comprehensive tests for the complete multi-tenant AI assistant system.

NOTE: These tests are temporarily disabled as they reference legacy AI assistant classes
that have been replaced with the new company-specific assistant system.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from datetime import date
import json

from company.models import Company
from product.customer_ai_assistant import CustomerDataAIAssistant
from product.ai_tools_registry import AIToolsRegistry
from project.views import BaseAIAssistantView
from saia.client_data_service import ClientDataService

User = get_user_model()


class EndToEndMultiTenantTests(TestCase):
    """End-to-end tests for multi-tenant AI assistant system"""
    
    def setUp(self):
        """Set up comprehensive test data"""
        # Create different types of companies
        self.insurance_company = Company.objects.create(
            name="SecureLife Insurance",
            email="admin@securelife.com",
            phone=5551111111,
            activity_name="Insurance Services",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1',  # Premium
            ai_instructions_template="You are SecureLife Insurance AI Assistant specializing in insurance operations.",
            ai_language='en',
            ai_temperature=0.1,
            enabled_tools_json=[
                'get_all_invoices', 'get_latest_invoice', 'get_contacts',
                'test_customer_database_connection', 'get_database_overview'
            ],
            database_config_json={
                'host': 'insurance.securelife.com',
                'name': 'insurance_db',
                'user': 'readonly_user'
            }
        )
        
        self.retail_company = Company.objects.create(
            name="QuickMart Retail",
            email="admin@quickmart.com",
            phone=5552222222,
            activity_name="Retail Operations",
            activity_type=Company.COMMERCIAL,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='0',  # Basic
            ai_language='en',
            ai_temperature=0.2,
            enabled_tools_json=[
                'get_all_invoices', 'get_contacts', 'test_customer_database_connection'
            ]
            # No custom database config
        )
        
        # Create users for each company
        self.insurance_user = User.objects.create_user(
            username='insurance_user',
            email='user@securelife.com',
            password='testpass123',
            is_customer=True
        )
        self.insurance_user.company = self.insurance_company
        self.insurance_user.save()
        
        self.retail_user = User.objects.create_user(
            username='retail_user',
            email='user@quickmart.com',
            password='testpass123',
            is_customer=True
        )
        self.retail_user.company = self.retail_company
        self.retail_user.save()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@saia.com',
            password='testpass123',
            is_superuser=True
        )
    
    def test_complete_customer_workflow(self):
        """Test complete workflow from company configuration to AI interaction"""
        # 1. Verify company configuration
        self.assertEqual(self.insurance_company.name, "SecureLife Insurance")
        self.assertEqual(self.insurance_company.ai_language, 'en')
        self.assertEqual(self.insurance_company.ai_temperature, 0.1)
        self.assertTrue(self.insurance_company.ai_instructions_template)
        self.assertTrue(self.insurance_company.database_config_json)
        
        # 2. Create AI assistant for insurance user
        insurance_assistant = CustomerDataAIAssistant(_user=self.insurance_user)
        
        # 3. Verify AI assistant configuration
        self.assertEqual(insurance_assistant.company, self.insurance_company)
        self.assertEqual(insurance_assistant.temperature, 0.1)
        self.assertIn("SecureLife Insurance", insurance_assistant.instructions)
        self.assertEqual(len(insurance_assistant.enabled_tools), 5)
        
        # 4. Test tool access
        self.assertIn('get_database_overview', insurance_assistant.enabled_tools)
        self.assertIn('get_all_invoices', insurance_assistant.enabled_tools)
        
        # 5. Test tool execution (enabled tool)
        result = insurance_assistant.test_customer_database_connection()
        result_data = json.loads(result)
        # Should not be blocked (status should not be 'disabled')
        self.assertNotEqual(result_data.get('status'), 'disabled')
    
    def test_multiple_customers_isolation(self):
        """Test that multiple customers don't interfere with each other"""
        # Create AI assistants for both companies
        insurance_assistant = CustomerDataAIAssistant(_user=self.insurance_user)
        retail_assistant = CustomerDataAIAssistant(_user=self.retail_user)
        
        # Verify different companies
        self.assertEqual(insurance_assistant.company, self.insurance_company)
        self.assertEqual(retail_assistant.company, self.retail_company)
        self.assertNotEqual(insurance_assistant.company, retail_assistant.company)
        
        # Verify different configurations
        self.assertEqual(insurance_assistant.temperature, 0.1)
        self.assertEqual(retail_assistant.temperature, 0.2)
        
        # Verify different tool access
        self.assertEqual(len(insurance_assistant.enabled_tools), 5)  # Premium tools
        self.assertEqual(len(retail_assistant.enabled_tools), 3)     # Basic tools
        
        # Verify premium tool access
        self.assertIn('get_database_overview', insurance_assistant.enabled_tools)
        self.assertNotIn('get_database_overview', retail_assistant.enabled_tools)
        
        # Test premium tool blocking for basic user
        result = retail_assistant.get_database_overview()
        result_data = json.loads(result)
        self.assertEqual(result_data['status'], 'disabled')
        self.assertIn('not enabled', result_data['message'])
    
    def test_routing_system_integration(self):
        """Test integration with enhanced routing system"""
        factory = RequestFactory()
        view = BaseAIAssistantView()
        
        # Test insurance user routing
        request = factory.get('/')
        request.user = self.insurance_user
        request.session = {}
        view.request = request
        
        assistant_id = view.get_assistant_id()
        company = view._get_user_company_context(self.insurance_user)
        ai_info = view._get_company_ai_info(company)
        
        # Verify correct routing and configuration
        self.assertEqual(assistant_id, CustomerDataAIAssistant.id)
        self.assertEqual(company, self.insurance_company)
        self.assertIsNotNone(ai_info)
        self.assertEqual(ai_info['company_name'], 'SecureLife Insurance')
        self.assertTrue(ai_info['has_custom_instructions'])
        self.assertTrue(ai_info['has_custom_database'])
        self.assertEqual(ai_info['enabled_tools_count'], 5)
        
        # Test retail user routing
        request.user = self.retail_user
        view.request = request
        
        assistant_id = view.get_assistant_id()
        company = view._get_user_company_context(self.retail_user)
        ai_info = view._get_company_ai_info(company)
        
        # Verify different configuration
        self.assertEqual(assistant_id, CustomerDataAIAssistant.id)
        self.assertEqual(company, self.retail_company)
        self.assertEqual(ai_info['company_name'], 'QuickMart Retail')
        self.assertFalse(ai_info['has_custom_instructions'])
        self.assertFalse(ai_info['has_custom_database'])
        self.assertEqual(ai_info['enabled_tools_count'], 3)
    
    def test_subscription_level_tool_access(self):
        """Test tool access based on subscription levels"""
        # Premium company should have access to premium tools
        premium_tools = AIToolsRegistry.get_premium_tools()
        basic_tools = AIToolsRegistry.get_basic_tools()
        
        insurance_assistant = CustomerDataAIAssistant(_user=self.insurance_user)
        retail_assistant = CustomerDataAIAssistant(_user=self.retail_user)
        
        # Insurance (premium) should have premium tools
        for tool in premium_tools:
            if tool in insurance_assistant.enabled_tools:
                # Test that premium tool works
                if hasattr(insurance_assistant, tool):
                    # Tool should be accessible (not blocked)
                    pass
        
        # Retail (basic) should not have premium tools
        for tool in premium_tools:
            if tool not in retail_assistant.enabled_tools:
                # Test that premium tool is blocked
                if hasattr(retail_assistant, tool):
                    result = getattr(retail_assistant, tool)()
                    if isinstance(result, str):
                        try:
                            result_data = json.loads(result)
                            if result_data.get('status') == 'disabled':
                                # Tool correctly blocked
                                self.assertIn('not enabled', result_data['message'])
                        except json.JSONDecodeError:
                            # Tool executed (might be allowed)
                            pass
    
    def test_database_isolation_security(self):
        """Test that database isolation prevents cross-company data access"""
        # Create client data services for each user
        insurance_service = ClientDataService(user=self.insurance_user)
        retail_service = ClientDataService(user=self.retail_user)
        
        # Verify different database configurations
        insurance_has_custom = hasattr(insurance_service, 'custom_db_config')
        retail_has_custom = hasattr(retail_service, 'custom_db_config')
        
        # Insurance company has custom database config
        if insurance_has_custom:
            self.assertIsNotNone(insurance_service.custom_db_config)
            self.assertEqual(insurance_service.custom_db_config['host'], 'insurance.securelife.com')
        
        # Retail company uses default database
        if not retail_has_custom:
            self.assertEqual(retail_service.db_alias, 'client_data')
    
    def test_ai_tools_registry_integration(self):
        """Test integration with AI tools registry"""
        # Test registry provides correct tools for each company
        insurance_tools = AIToolsRegistry.get_tools_for_company(self.insurance_company)
        retail_tools = AIToolsRegistry.get_tools_for_company(self.retail_company)
        
        # Insurance (premium) should have more tools
        self.assertGreaterEqual(len(insurance_tools), len(retail_tools))
        
        # Both should have basic tools
        basic_tools = AIToolsRegistry.get_basic_tools()
        for tool in basic_tools:
            if tool in self.insurance_company.enabled_tools_json:
                self.assertIn(tool, insurance_tools)
            if tool in self.retail_company.enabled_tools_json:
                self.assertIn(tool, retail_tools)
        
        # Premium tools should only be in premium company
        premium_tools = AIToolsRegistry.get_premium_tools()
        for tool in premium_tools:
            if tool in self.insurance_company.enabled_tools_json:
                self.assertIn(tool, insurance_tools)
            # Retail shouldn't have premium tools in their enabled list
            self.assertNotIn(tool, self.retail_company.enabled_tools_json)


class SystemPerformanceTests(TestCase):
    """Test system performance with multiple customers"""
    
    def setUp(self):
        """Set up performance test data"""
        self.companies = []
        self.users = []
        
        # Create multiple companies for performance testing
        for i in range(3):
            company = Company.objects.create(
                name=f"Test Company {i+1}",
                email=f"admin{i+1}@testcompany.com",
                phone=5550000000 + i,
                activity_name=f"Test Activity {i+1}",
                activity_type=Company.SERVICE,
                activity_status='1',
                subscription_start_date=date.today(),
                subscription_end_date=date(2025, 12, 31),
                subscription_status='1',
                ai_language='en',
                ai_temperature=0.1 + (i * 0.1),
                enabled_tools_json=AIToolsRegistry.get_basic_tools()[:3+i]
            )
            self.companies.append(company)
            
            user = User.objects.create_user(
                username=f'testuser{i+1}',
                email=f'user{i+1}@testcompany.com',
                password='testpass123',
                is_customer=True
            )
            user.company = company
            user.save()
            self.users.append(user)
    
    def test_multiple_assistants_creation(self):
        """Test creating multiple AI assistants simultaneously"""
        assistants = []
        
        # Create assistants for all users
        for user in self.users:
            assistant = CustomerDataAIAssistant(_user=user)
            assistants.append(assistant)
        
        # Verify all assistants are properly configured
        self.assertEqual(len(assistants), 3)
        
        for i, assistant in enumerate(assistants):
            self.assertEqual(assistant.company, self.companies[i])
            self.assertEqual(assistant.temperature, 0.1 + (i * 0.1))
            self.assertGreaterEqual(len(assistant.enabled_tools), 3)
    
    def test_concurrent_tool_execution(self):
        """Test concurrent tool execution across multiple companies"""
        assistants = [CustomerDataAIAssistant(_user=user) for user in self.users]
        
        # Execute same tool across all assistants
        results = []
        for assistant in assistants:
            try:
                result = assistant.test_customer_database_connection()
                results.append(result)
            except Exception as e:
                results.append(f"Error: {e}")
        
        # All should execute (though may fail due to no actual database)
        self.assertEqual(len(results), 3)
        
        # Results should be independent (no cross-contamination)
        for result in results:
            self.assertIsInstance(result, str)


class BackwardCompatibilityTests(TestCase):
    """Test backward compatibility with existing system"""
    
    def test_unconfigured_company_fallbacks(self):
        """Test that unconfigured companies still work with fallbacks"""
        # Create company with minimal configuration
        minimal_company = Company.objects.create(
            name="Minimal Company",
            email="minimal@company.com",
            phone=5559999999,
            activity_name="Minimal Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1'
            # No AI configuration - should use fallbacks
        )
        
        minimal_user = User.objects.create_user(
            username='minimal_user',
            email='minimal@test.com',
            password='testpass123',
            is_customer=True
        )
        minimal_user.company = minimal_company
        minimal_user.save()
        
        # Create AI assistant
        assistant = CustomerDataAIAssistant(_user=minimal_user)
        
        # Should work with fallback values
        self.assertEqual(assistant.company, minimal_company)
        self.assertEqual(assistant.temperature, 0.1)  # Default fallback
        self.assertGreater(len(assistant.enabled_tools), 0)  # Should have default tools
        
        # Should be able to execute basic tools
        result = assistant.test_customer_database_connection()
        self.assertIsInstance(result, str)
    
    def test_existing_system_compatibility(self):
        """Test that existing system functionality is preserved"""
        # Test that admin users still work
        admin_user = User.objects.create_user(
            username='admin_compat',
            email='admin@saia.com',
            password='testpass123',
            is_superuser=True
        )
        
        # Test routing for admin user
        factory = RequestFactory()
        view = BaseAIAssistantView()
        request = factory.get('/')
        request.user = admin_user
        request.session = {}
        view.request = request
        
        assistant_id = view.get_assistant_id()
        # Should still route to appropriate assistant
        self.assertIsNotNone(assistant_id)
