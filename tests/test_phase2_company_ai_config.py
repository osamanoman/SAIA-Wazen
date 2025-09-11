"""
Phase 2 Tests: Company AI Configuration

Tests for the AI configuration fields added to the Company model.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from datetime import date

from company.models import Company

User = get_user_model()


class CompanyAIConfigurationTests(TestCase):
    """Test Company model AI configuration fields"""
    
    def setUp(self):
        """Set up test data"""
        self.company_data = {
            'name': 'Test Company',
            'email': 'test@company.com',
            'phone': 1234567890,
            'activity_name': 'Software Development',
            'activity_type': Company.SERVICE,
            'activity_status': '1',
            'subscription_start_date': date.today(),
            'subscription_end_date': date(2025, 12, 31),
            'subscription_status': '1',
        }
    
    def test_company_ai_fields_default_values(self):
        """Test that AI config fields have proper defaults"""
        company = Company.objects.create(**self.company_data)
        
        # Test default values
        self.assertEqual(company.enabled_tools_json, [])
        self.assertEqual(company.database_config_json, {})
        self.assertEqual(company.ai_language, 'en')
        self.assertEqual(company.ai_temperature, 0.1)
        self.assertIsNone(company.ai_instructions_template)
    
    def test_ai_temperature_validation_valid_range(self):
        """Test AI temperature field accepts valid values"""
        company = Company.objects.create(**self.company_data)
        
        # Test valid values
        valid_temperatures = [0.0, 0.1, 0.5, 1.0, 1.5, 2.0]
        for temp in valid_temperatures:
            company.ai_temperature = temp
            company.full_clean()  # Should not raise ValidationError
    
    def test_ai_temperature_validation_invalid_range(self):
        """Test AI temperature field rejects invalid values"""
        company = Company.objects.create(**self.company_data)
        
        # Test invalid values
        invalid_temperatures = [-0.1, -1.0, 2.1, 3.0, 10.0]
        for temp in invalid_temperatures:
            company.ai_temperature = temp
            with self.assertRaises(ValidationError) as context:
                company.full_clean()
            self.assertIn('ai_temperature', context.exception.message_dict)
    
    def test_enabled_tools_json_structure(self):
        """Test enabled_tools_json accepts list format"""
        company = Company.objects.create(
            **self.company_data,
            enabled_tools_json=["tool1", "tool2", "tool3"]
        )
        
        self.assertIsInstance(company.enabled_tools_json, list)
        self.assertEqual(len(company.enabled_tools_json), 3)
        self.assertIn("tool1", company.enabled_tools_json)
    
    def test_enabled_tools_json_validation_invalid_type(self):
        """Test enabled_tools_json rejects non-list values"""
        company = Company.objects.create(**self.company_data)
        
        # Test invalid types
        invalid_values = ["not_a_list", 123, {"key": "value"}]
        for invalid_value in invalid_values:
            company.enabled_tools_json = invalid_value
            with self.assertRaises(ValidationError) as context:
                company.full_clean()
            self.assertIn('enabled_tools_json', context.exception.message_dict)
    
    def test_database_config_json_structure(self):
        """Test database_config_json accepts dict format"""
        config = {
            "host": "db.testcompany.com",
            "name": "test_company_db",
            "user": "readonly_user"
        }
        company = Company.objects.create(
            **self.company_data,
            database_config_json=config
        )
        
        self.assertIsInstance(company.database_config_json, dict)
        self.assertEqual(company.database_config_json["host"], "db.testcompany.com")
    
    def test_database_config_json_validation_invalid_type(self):
        """Test database_config_json rejects non-dict values"""
        company = Company.objects.create(**self.company_data)
        
        # Test invalid types
        invalid_values = ["not_a_dict", 123, ["list", "value"]]
        for invalid_value in invalid_values:
            company.database_config_json = invalid_value
            with self.assertRaises(ValidationError) as context:
                company.full_clean()
            self.assertIn('database_config_json', context.exception.message_dict)
    
    def test_ai_language_choices(self):
        """Test AI language field accepts valid choices"""
        company = Company.objects.create(**self.company_data)
        
        # Test valid choices
        valid_languages = ['en', 'ar']
        for lang in valid_languages:
            company.ai_language = lang
            company.full_clean()  # Should not raise
    
    def test_custom_ai_instructions(self):
        """Test custom AI instructions template"""
        custom_instructions = "You are a specialized assistant for Test Company."
        company = Company.objects.create(
            **self.company_data,
            ai_instructions_template=custom_instructions
        )
        
        self.assertEqual(company.ai_instructions_template, custom_instructions)
    
    def test_get_ai_instructions_custom(self):
        """Test get_ai_instructions method with custom instructions"""
        custom_instructions = "Custom instructions for Test Company"
        company = Company.objects.create(
            **self.company_data,
            ai_instructions_template=custom_instructions
        )
        
        self.assertEqual(company.get_ai_instructions(), custom_instructions)
    
    def test_get_ai_instructions_default(self):
        """Test get_ai_instructions method with default instructions"""
        company = Company.objects.create(**self.company_data)
        
        instructions = company.get_ai_instructions()
        self.assertIn(company.name, instructions)
        self.assertIn(company.activity_name, instructions)
        self.assertIn("Business Intelligence Assistant", instructions)
    
    def test_get_enabled_tools_custom(self):
        """Test get_enabled_tools method with custom tools"""
        custom_tools = ["tool1", "tool2", "custom_tool"]
        company = Company.objects.create(
            **self.company_data,
            enabled_tools_json=custom_tools
        )
        
        self.assertEqual(company.get_enabled_tools(), custom_tools)
    
    def test_get_enabled_tools_default_active_subscription(self):
        """Test get_enabled_tools method with default tools for active subscription"""
        company = Company.objects.create(**self.company_data)
        
        tools = company.get_enabled_tools()
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 4)  # Should have basic + premium tools
        self.assertIn('get_customer_sales_summary', tools)
        self.assertIn('generate_business_reports', tools)  # Premium tool
    
    def test_get_enabled_tools_default_inactive_subscription(self):
        """Test get_enabled_tools method with default tools for inactive subscription"""
        company_data = self.company_data.copy()
        company_data['subscription_status'] = '0'  # Inactive
        company = Company.objects.create(**company_data)
        
        tools = company.get_enabled_tools()
        self.assertIsInstance(tools, list)
        self.assertEqual(len(tools), 4)  # Should have only basic tools
        self.assertIn('get_customer_sales_summary', tools)
        self.assertNotIn('generate_business_reports', tools)  # No premium tools


class CompanyAIConfigAdminTests(TestCase):
    """Test Company admin interface with AI configuration"""
    
    def setUp(self):
        """Set up admin user and test data"""
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.client.login(username='admin', password='testpass123')
    
    def test_company_admin_ai_config_fields_visible(self):
        """Test AI config fields appear in Company admin"""
        response = self.client.get('/admin/company/company/add/')
        self.assertEqual(response.status_code, 200)
        
        # Check that AI configuration fields are present
        self.assertContains(response, 'ai_instructions_template')
        self.assertContains(response, 'enabled_tools_json')
        self.assertContains(response, 'database_config_json')
        self.assertContains(response, 'ai_language')
        self.assertContains(response, 'ai_temperature')
        self.assertContains(response, 'AI Assistant Configuration')
    
    def test_company_ai_config_save_via_admin(self):
        """Test saving AI configuration through admin interface"""
        data = {
            'name': 'Admin Test Company',
            'email': 'admin@testcompany.com',
            'phone': '1234567890',
            'activity_name': 'Testing Services',
            'activity_type': Company.SERVICE,
            'activity_status': '1',
            'subscription_start_date': '2025-01-01',
            'subscription_end_date': '2025-12-31',
            'subscription_status': '1',
            'ai_language': 'ar',
            'ai_temperature': '0.2',
            'ai_instructions_template': 'Custom instructions for admin test',
            'enabled_tools_json': '["tool1", "tool2"]',
            'database_config_json': '{"host": "test.db.com"}',
        }
        
        response = self.client.post('/admin/company/company/add/', data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful save
        
        # Verify the company was created with AI configuration
        company = Company.objects.get(name='Admin Test Company')
        self.assertEqual(company.ai_language, 'ar')
        self.assertEqual(company.ai_temperature, 0.2)
        self.assertEqual(company.ai_instructions_template, 'Custom instructions for admin test')
        self.assertEqual(company.enabled_tools_json, ["tool1", "tool2"])
        self.assertEqual(company.database_config_json, {"host": "test.db.com"})
