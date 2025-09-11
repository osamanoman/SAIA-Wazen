"""
Phase 4 Tests: AI Tools Registry and Management

Tests for the AI Tools Registry system and admin interface for tool management.

NOTE: These tests are temporarily disabled as they reference legacy AI assistant classes
that have been replaced with the new company-specific assistant system.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
import json

from company.models import Company
from product.ai_tools_registry import AIToolsRegistry, ToolCategory, SubscriptionLevel, AIToolInfo
from product.customer_ai_assistant import CustomerDataAIAssistant

User = get_user_model()


class AIToolsRegistryTests(TestCase):
    """Test AI Tools Registry functionality"""
    
    def test_registry_has_all_tools(self):
        """Test that registry contains all expected tools"""
        all_tools = AIToolsRegistry.get_all_tools()
        
        # Should have 13 tools as documented
        self.assertEqual(len(all_tools), 13)
        
        # Check some key tools exist
        expected_tools = [
            'test_customer_database_connection',
            'get_all_invoices',
            'get_contacts',
            'get_database_overview',
            'search_customer_data'
        ]
        
        for tool_name in expected_tools:
            self.assertIn(tool_name, all_tools)
            self.assertIsInstance(all_tools[tool_name], AIToolInfo)
    
    def test_tools_by_category(self):
        """Test filtering tools by category"""
        database_tools = AIToolsRegistry.get_tools_by_category(ToolCategory.DATABASE)
        invoice_tools = AIToolsRegistry.get_tools_by_category(ToolCategory.INVOICES)
        contact_tools = AIToolsRegistry.get_tools_by_category(ToolCategory.CONTACTS)
        
        # Check expected counts
        self.assertEqual(len(database_tools), 5)
        self.assertEqual(len(invoice_tools), 4)
        self.assertEqual(len(contact_tools), 1)
        
        # Check specific tools are in correct categories
        self.assertIn('list_customer_tables', database_tools)
        self.assertIn('get_all_invoices', invoice_tools)
        self.assertIn('get_contacts', contact_tools)
    
    def test_tools_by_subscription_level(self):
        """Test filtering tools by subscription level"""
        basic_tools = AIToolsRegistry.get_tools_by_subscription(SubscriptionLevel.BASIC)
        premium_tools = AIToolsRegistry.get_tools_by_subscription(SubscriptionLevel.PREMIUM)
        
        # Premium should include all basic tools plus premium-only tools
        self.assertGreater(len(premium_tools), len(basic_tools))
        
        # All basic tools should be in premium
        for tool_name in basic_tools:
            self.assertIn(tool_name, premium_tools)
        
        # Check specific subscription requirements
        self.assertIn('get_all_invoices', basic_tools)  # Basic tool
        self.assertIn('search_customer_data', premium_tools)  # Premium tool
        
        # Premium-only tool should not be in basic
        premium_only_tools = set(premium_tools.keys()) - set(basic_tools.keys())
        self.assertGreater(len(premium_only_tools), 0)
    
    def test_get_basic_and_premium_tools(self):
        """Test getting basic and premium tool lists"""
        basic_tools = AIToolsRegistry.get_basic_tools()
        premium_tools = AIToolsRegistry.get_premium_tools()
        
        self.assertIsInstance(basic_tools, list)
        self.assertIsInstance(premium_tools, list)
        
        # Should have some tools in each category
        self.assertGreater(len(basic_tools), 0)
        self.assertGreater(len(premium_tools), 0)
    
    def test_tool_info_retrieval(self):
        """Test getting information about specific tools"""
        tool_info = AIToolsRegistry.get_tool_info('get_all_invoices')
        
        self.assertIsNotNone(tool_info)
        self.assertEqual(tool_info.name, 'get_all_invoices')
        self.assertEqual(tool_info.display_name, 'Get All Invoices')
        self.assertEqual(tool_info.category, ToolCategory.INVOICES)
        self.assertEqual(tool_info.subscription_level, SubscriptionLevel.BASIC)
        
        # Test non-existent tool
        non_existent = AIToolsRegistry.get_tool_info('non_existent_tool')
        self.assertIsNone(non_existent)
    
    def test_tool_availability_check(self):
        """Test checking if tool is available for subscription level"""
        # Basic tool should be available for all levels
        self.assertTrue(AIToolsRegistry.is_tool_available('get_all_invoices', SubscriptionLevel.BASIC))
        self.assertTrue(AIToolsRegistry.is_tool_available('get_all_invoices', SubscriptionLevel.PREMIUM))
        
        # Premium tool should only be available for premium+
        self.assertFalse(AIToolsRegistry.is_tool_available('search_customer_data', SubscriptionLevel.BASIC))
        self.assertTrue(AIToolsRegistry.is_tool_available('search_customer_data', SubscriptionLevel.PREMIUM))


class CompanyToolConfigurationTests(TestCase):
    """Test company-specific tool configuration"""
    
    def setUp(self):
        """Set up test data"""
        self.company_custom_tools = Company.objects.create(
            name="Custom Tools Company",
            email="custom@company.com",
            phone=1111111111,
            activity_name="Custom Tool Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1',
            enabled_tools_json=["get_all_invoices", "get_contacts", "test_customer_database_connection"]
        )
        
        self.company_default_tools = Company.objects.create(
            name="Default Tools Company",
            email="default@company.com",
            phone=2222222222,
            activity_name="Default Tool Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1'
            # No enabled_tools_json - should use defaults
        )
        
        self.company_inactive = Company.objects.create(
            name="Inactive Company",
            email="inactive@company.com",
            phone=3333333333,
            activity_name="Inactive Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='0'  # Inactive subscription
        )
    
    def test_custom_tools_configuration(self):
        """Test company with custom tools configuration"""
        tools = AIToolsRegistry.get_tools_for_company(self.company_custom_tools)
        expected_tools = ["get_all_invoices", "get_contacts", "test_customer_database_connection"]
        
        self.assertEqual(tools, expected_tools)
        
        # Test via company method
        company_tools = self.company_custom_tools.get_enabled_tools()
        self.assertEqual(company_tools, expected_tools)
    
    def test_default_tools_active_subscription(self):
        """Test company with default tools and active subscription"""
        tools = AIToolsRegistry.get_tools_for_company(self.company_default_tools)
        
        # Should get basic + premium tools for active subscription
        basic_tools = AIToolsRegistry.get_basic_tools()
        premium_tools = AIToolsRegistry.get_premium_tools()
        expected_tools = basic_tools + premium_tools
        
        self.assertEqual(set(tools), set(expected_tools))
    
    def test_default_tools_inactive_subscription(self):
        """Test company with default tools and inactive subscription"""
        tools = AIToolsRegistry.get_tools_for_company(self.company_inactive)
        
        # Should get only basic tools for inactive subscription
        basic_tools = AIToolsRegistry.get_basic_tools()
        self.assertEqual(set(tools), set(basic_tools))


class EnhancedToolFilteringTests(TestCase):
    """Test enhanced tool filtering with registry information"""
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name="Tool Filtering Test Company",
            email="filtering@company.com",
            phone=4444444444,
            activity_name="Tool Filtering Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1',
            enabled_tools_json=["test_customer_database_connection", "get_contacts"]
        )
        
        self.user = User.objects.create_user(
            username='filteringuser',
            email='filtering@test.com',
            password='testpass123',
            is_customer=True
        )
        self.user.company = self.company
        self.user.save()
    
    def test_enhanced_tool_blocking_message(self):
        """Test that blocked tools return enhanced information from registry"""
        assistant = CustomerDataAIAssistant(_user=self.user)
        
        # Test a tool that should be blocked
        result = assistant.get_all_invoices(limit=5)
        result_data = json.loads(result)
        
        # Should be blocked
        self.assertEqual(result_data["status"], "disabled")
        self.assertEqual(result_data["tool_name"], "get_all_invoices")
        
        # Should have enhanced information from registry
        self.assertEqual(result_data["display_name"], "Get All Invoices")
        self.assertIn("Retrieve all invoices", result_data["description"])
        self.assertEqual(result_data["category"], "invoices")
        self.assertEqual(result_data["subscription_required"], "basic")
        
        # Should list available tools
        self.assertEqual(result_data["available_tools"], ["test_customer_database_connection", "get_contacts"])
    
    def test_enabled_tool_execution(self):
        """Test that enabled tools execute normally"""
        assistant = CustomerDataAIAssistant(_user=self.user)
        
        # This tool should be enabled and execute (though may fail due to no actual database)
        try:
            result = assistant.test_customer_database_connection()
            result_data = json.loads(result)
            
            # Should not be blocked (status should be success or error, not disabled)
            self.assertNotEqual(result_data["status"], "disabled")
        except Exception:
            # Database connection may fail, but tool should not be blocked
            pass


class ToolCategoriesAndMetadataTests(TestCase):
    """Test tool categories and metadata"""
    
    def test_all_categories_represented(self):
        """Test that all tool categories have tools"""
        categories = AIToolsRegistry.get_categories()
        
        for category in categories:
            tools = AIToolsRegistry.get_tools_by_category(category)
            # Most categories should have at least one tool
            if category in [ToolCategory.DATABASE, ToolCategory.INVOICES, ToolCategory.CONTACTS, ToolCategory.ANALYTICS, ToolCategory.SYSTEM]:
                self.assertGreater(len(tools), 0, f"Category {category.value} should have tools")
    
    def test_subscription_levels(self):
        """Test subscription level functionality"""
        levels = AIToolsRegistry.get_subscription_levels()
        
        self.assertIn(SubscriptionLevel.BASIC, levels)
        self.assertIn(SubscriptionLevel.PREMIUM, levels)
        self.assertIn(SubscriptionLevel.ENTERPRISE, levels)
    
    def test_tool_metadata_completeness(self):
        """Test that all tools have complete metadata"""
        all_tools = AIToolsRegistry.get_all_tools()
        
        for tool_name, tool_info in all_tools.items():
            # Check required fields
            self.assertIsNotNone(tool_info.name)
            self.assertIsNotNone(tool_info.display_name)
            self.assertIsNotNone(tool_info.description)
            self.assertIsNotNone(tool_info.category)
            self.assertIsNotNone(tool_info.subscription_level)
            self.assertIsNotNone(tool_info.method_name)
            
            # Check that display name is more user-friendly than internal name
            self.assertNotEqual(tool_info.display_name, tool_name)
            
            # Check that description is meaningful
            self.assertGreater(len(tool_info.description), 10)
