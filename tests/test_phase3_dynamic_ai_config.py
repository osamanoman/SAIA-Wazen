"""
Phase 3 Tests: Dynamic AI Configuration

Tests for CustomerDataAIAssistant with company-specific configuration loading.

NOTE: These tests are temporarily disabled as they reference legacy AI assistant classes
that have been replaced with the new company-specific assistant system.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch
from datetime import date
import json

from company.models import Company
from product.customer_ai_assistant import CustomerDataAIAssistant, tool_enabled
from saia.client_data_service import ClientDataService

User = get_user_model()


class CustomerAIDynamicConfigTests(TestCase):
    """Test CustomerDataAIAssistant with dynamic company configuration"""
    
    def setUp(self):
        """Set up test data"""
        # Create company with AI configuration
        self.company = Company.objects.create(
            name="Test AI Company",
            email="test@ai.com",
            phone=1234567890,
            activity_name="AI Testing Services",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1',
            # AI Configuration
            ai_instructions_template="Custom AI instructions for Test AI Company",
            ai_language='ar',
            ai_temperature=0.5,
            enabled_tools_json=["get_all_invoices", "get_contacts", "test_customer_database_connection"],
            database_config_json={
                "host": "test.db.com",
                "name": "test_company_db",
                "user": "readonly_user",
                "password": "secure_password",
                "port": 3306
            }
        )
        
        # Create user with company
        self.user = User.objects.create_user(
            username='testcustomer',
            email='customer@test.com',
            password='testpass123',
            is_customer=True
        )
        self.user.company = self.company
        self.user.save()
        
        # Create company without AI configuration for fallback testing
        self.company_no_config = Company.objects.create(
            name="No Config Company",
            email="noconfig@company.com",
            phone=9876543210,
            activity_name="Standard Services",
            activity_type=Company.COMMERCIAL,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1'
        )
        
        self.user_no_config = User.objects.create_user(
            username='noconfiguser',
            email='noconfig@test.com',
            password='testpass123',
            is_customer=True
        )
        self.user_no_config.company = self.company_no_config
        self.user_no_config.save()
    
    def test_dynamic_instructions_loading_custom(self):
        """Test that AI assistant loads company-specific custom instructions"""
        assistant = CustomerDataAIAssistant(_user=self.user)
        
        self.assertEqual(assistant.instructions, "Custom AI instructions for Test AI Company")
        self.assertEqual(assistant.company, self.company)
    
    def test_dynamic_instructions_loading_default(self):
        """Test that AI assistant loads default instructions when no custom instructions"""
        assistant = CustomerDataAIAssistant(_user=self.user_no_config)
        
        # Should use company's get_ai_instructions() method
        expected_instructions = self.company_no_config.get_ai_instructions()
        self.assertEqual(assistant.instructions, expected_instructions)
        self.assertIn("No Config Company", assistant.instructions)
        self.assertIn("Business Intelligence Assistant", assistant.instructions)
    
    def test_dynamic_temperature_setting(self):
        """Test that AI assistant uses company-specific temperature"""
        assistant = CustomerDataAIAssistant(_user=self.user)
        
        self.assertEqual(assistant.temperature, 0.5)
    
    def test_dynamic_temperature_default(self):
        """Test that AI assistant uses default temperature when not configured"""
        assistant = CustomerDataAIAssistant(_user=self.user_no_config)
        
        # Should use default temperature from Company model (0.1)
        self.assertEqual(assistant.temperature, 0.1)
    
    def test_enabled_tools_loading(self):
        """Test that enabled tools are loaded from company configuration"""
        assistant = CustomerDataAIAssistant(_user=self.user)
        
        expected_tools = ["get_all_invoices", "get_contacts", "test_customer_database_connection"]
        self.assertEqual(assistant.enabled_tools, expected_tools)
    
    def test_enabled_tools_default(self):
        """Test that default tools are loaded when no custom configuration"""
        assistant = CustomerDataAIAssistant(_user=self.user_no_config)
        
        # Should use company's get_enabled_tools() method
        expected_tools = self.company_no_config.get_enabled_tools()
        self.assertEqual(assistant.enabled_tools, expected_tools)
        self.assertGreater(len(assistant.enabled_tools), 4)  # Should have basic + premium tools
    
    def test_user_without_company(self):
        """Test behavior when user has no company"""
        user_no_company = User.objects.create_user(
            username='nocompanyuser',
            email='nocompany@test.com',
            password='testpass123',
            is_customer=True
        )
        
        assistant = CustomerDataAIAssistant(_user=user_no_company)
        
        # Should not crash and use default settings
        self.assertIsNotNone(assistant.instructions)
        self.assertEqual(assistant.temperature, 0.3)  # Default from SAIAAIAssistantMixin


class ToolFilteringTests(TestCase):
    """Test tool filtering decorator functionality"""
    
    def setUp(self):
        """Set up test data for tool filtering"""
        self.company = Company.objects.create(
            name="Tool Filter Test Company",
            email="tooltest@company.com",
            phone=1111111111,
            activity_name="Tool Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1',
            enabled_tools_json=["get_all_invoices", "get_contacts"]  # Limited tools
        )
        
        self.user = User.objects.create_user(
            username='tooltestuser',
            email='tooltest@test.com',
            password='testpass123',
            is_customer=True
        )
        self.user.company = self.company
        self.user.save()
    
    @patch('product.customer_ai_assistant.ClientDataService')
    def test_enabled_tool_execution(self, mock_client_service):
        """Test that enabled tools execute normally"""
        # Mock the client service
        mock_service_instance = Mock()
        mock_service_instance.execute_safe_query.return_value = [{"count": 5}]
        mock_client_service.return_value = mock_service_instance
        
        assistant = CustomerDataAIAssistant(_user=self.user)
        
        # Test enabled tool - should execute normally
        result = assistant.get_all_invoices(limit=10)
        result_data = json.loads(result)
        
        self.assertEqual(result_data["status"], "success")
        mock_service_instance.execute_safe_query.assert_called()
    
    @patch('product.customer_ai_assistant.ClientDataService')
    def test_disabled_tool_blocking(self, mock_client_service):
        """Test that disabled tools are blocked"""
        assistant = CustomerDataAIAssistant(_user=self.user)
        
        # Test disabled tool - should return disabled message
        result = assistant.get_database_overview()
        result_data = json.loads(result)
        
        self.assertEqual(result_data["status"], "disabled")
        self.assertEqual(result_data["tool_name"], "get_database_overview")
        self.assertIn("not enabled for your company", result_data["message"])
        self.assertEqual(result_data["available_tools"], ["get_all_invoices", "get_contacts"])
    
    def test_tool_enabled_decorator_function(self):
        """Test the tool_enabled decorator function directly"""
        # Create a mock function
        @tool_enabled("test_tool")
        def mock_tool_function(self):
            return "Tool executed successfully"
        
        # Create mock assistant with enabled tools
        mock_assistant = Mock()
        mock_assistant.enabled_tools = ["test_tool", "other_tool"]
        
        # Test enabled tool
        result = mock_tool_function(mock_assistant)
        self.assertEqual(result, "Tool executed successfully")
        
        # Test disabled tool
        mock_assistant.enabled_tools = ["other_tool"]  # test_tool not in list
        result = mock_tool_function(mock_assistant)
        result_data = json.loads(result)
        self.assertEqual(result_data["status"], "disabled")
        self.assertEqual(result_data["tool_name"], "test_tool")


class ClientDataServiceCustomConnectionTests(TestCase):
    """Test ClientDataService with custom database connections"""
    
    def setUp(self):
        """Set up test data for database connection testing"""
        self.company_custom_db = Company.objects.create(
            name="Custom DB Company",
            email="customdb@company.com",
            phone=2222222222,
            activity_name="Custom Database Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1',
            database_config_json={
                "host": "custom.db.server.com",
                "name": "custom_company_db",
                "user": "custom_readonly_user",
                "password": "custom_secure_password",
                "port": 3306,
                "charset": "utf8mb4"
            }
        )
        
        self.user_custom_db = User.objects.create_user(
            username='customdbuser',
            email='customdb@test.com',
            password='testpass123',
            is_customer=True
        )
        self.user_custom_db.company = self.company_custom_db
        self.user_custom_db.save()
    
    def test_custom_database_config_loading(self):
        """Test that custom database configuration is loaded correctly"""
        service = ClientDataService(user=self.user_custom_db)
        
        self.assertTrue(hasattr(service, 'custom_db_config'))
        self.assertEqual(service.custom_db_config['host'], 'custom.db.server.com')
        self.assertEqual(service.custom_db_config['name'], 'custom_company_db')
        self.assertEqual(service.custom_db_config['user'], 'custom_readonly_user')
    
    def test_default_database_fallback(self):
        """Test fallback to default database when no custom config"""
        user_default = User.objects.create_user(
            username='defaultdbuser',
            email='defaultdb@test.com',
            password='testpass123',
            is_customer=True
        )
        
        service = ClientDataService(user=user_default)
        
        self.assertFalse(hasattr(service, 'custom_db_config'))
        self.assertEqual(service.db_alias, 'client_data')
    
    def test_incomplete_database_config_fallback(self):
        """Test fallback when database config is incomplete"""
        company_incomplete = Company.objects.create(
            name="Incomplete DB Company",
            email="incomplete@company.com",
            phone=3333333333,
            activity_name="Incomplete Config Testing",
            activity_type=Company.SERVICE,
            activity_status='1',
            subscription_start_date=date.today(),
            subscription_end_date=date(2025, 12, 31),
            subscription_status='1',
            database_config_json={
                "host": "incomplete.db.com",
                # Missing 'name' and 'user' fields
            }
        )
        
        user_incomplete = User.objects.create_user(
            username='incompleteuser',
            email='incomplete@test.com',
            password='testpass123',
            is_customer=True
        )
        user_incomplete.company = company_incomplete
        user_incomplete.save()
        
        service = ClientDataService(user=user_incomplete)
        
        # Should fall back to default connection
        self.assertFalse(hasattr(service, 'custom_db_config'))
