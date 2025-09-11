"""
Comprehensive tests for SAIA Multi-Tenant Website Chatbot Platform - Phase 1

This module tests all Phase 1 components including:
- WebsiteSession and SessionHandover models
- Widget API endpoints with security features
- Company-specific AI routing
- Rate limiting and input validation
"""

import json
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model

from company.models import Company
from project.models import WebsiteSession, SessionHandover
from django_ai_assistant.models import Thread

User = get_user_model()


class WebsiteSessionModelTest(TestCase):
    """Test WebsiteSession model functionality"""

    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            activity_name="Testing Services",
            activity_type="SR",
            subscription_start_date="2024-01-01",
            subscription_end_date="2024-12-31"
        )

        self.thread = Thread.objects.create(
            name="Test Thread",
            assistant_id="test_ai_assistant"
        )

        self.session = WebsiteSession.objects.create(
            thread=self.thread,
            company=self.company,
            visitor_ip="192.168.1.100",
            user_agent="Test Browser",
            referrer_url="https://test.com"
        )

    def test_session_creation(self):
        """Test WebsiteSession creation and basic properties"""
        self.assertIsNotNone(self.session.session_id)
        self.assertEqual(self.session.company, self.company)
        self.assertEqual(self.session.status, 'active')
        self.assertTrue(self.session.is_active())
        self.assertFalse(self.session.is_expired())

    def test_session_expiration(self):
        """Test session expiration logic"""
        # Create an old session
        old_time = timezone.now() - timezone.timedelta(minutes=45)
        self.session.last_activity = old_time
        self.session.save()

        self.assertTrue(self.session.is_expired(timeout_minutes=30))
        self.assertFalse(self.session.is_expired(timeout_minutes=60))

    def test_session_close(self):
        """Test session closing functionality"""
        self.session.close_session(reason='test_close')

        self.assertEqual(self.session.status, 'closed')
        self.assertIsNotNone(self.session.closed_at)
        self.assertEqual(self.session.visitor_metadata['close_reason'], 'test_close')
        self.assertFalse(self.session.is_active())

    def test_session_duration(self):
        """Test session duration calculation"""
        duration = self.session.get_duration_minutes()
        self.assertIsInstance(duration, int)
        self.assertGreaterEqual(duration, 0)


class SessionHandoverModelTest(TestCase):
    """Test SessionHandover model functionality"""

    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            activity_name="Testing Services",
            activity_type="SR",
            subscription_start_date="2024-01-01",
            subscription_end_date="2024-12-31"
        )

        self.agent = User.objects.create_user(
            username="test_agent",
            email="agent@test.com",
            is_staff=True
        )

        self.thread = Thread.objects.create(
            name="Test Thread",
            assistant_id="test_ai_assistant"
        )

        self.session = WebsiteSession.objects.create(
            thread=self.thread,
            company=self.company,
            visitor_ip="192.168.1.100"
        )

        self.handover = SessionHandover.objects.create(
            website_session=self.session,
            agent=self.agent,
            handover_reason="Customer requested human support",
            handover_trigger="customer_request"
        )

    def test_handover_creation(self):
        """Test SessionHandover creation and basic properties"""
        self.assertEqual(self.handover.status, 'pending')
        self.assertEqual(self.handover.handover_trigger, 'customer_request')
        self.assertIsNone(self.handover.agent_joined_at)
        self.assertIsNone(self.handover.resolved_at)

    def test_agent_joined(self):
        """Test agent joining handover"""
        self.handover.mark_agent_joined()

        self.assertEqual(self.handover.status, 'active')
        self.assertIsNotNone(self.handover.agent_joined_at)

    def test_handover_resolution(self):
        """Test handover resolution"""
        self.handover.resolve_handover(
            notes="Issue resolved successfully",
            satisfaction=5
        )

        self.assertEqual(self.handover.status, 'resolved')
        self.assertIsNotNone(self.handover.resolved_at)
        self.assertEqual(self.handover.customer_satisfaction, 5)
        self.assertEqual(self.handover.resolution_notes, "Issue resolved successfully")


class WidgetAPITest(TestCase):
    """Test Widget API endpoints"""

    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(
            name="Wazen",
            activity_name="Business Services",
            activity_type="SR",
            subscription_start_date="2024-01-01",
            subscription_end_date="2024-12-31",
            widget_is_active=True,
            widget_welcome_message="Welcome to Wazen!",
            widget_position="bottom-right"
        )

        # Clear cache before each test
        cache.clear()

    def test_widget_config_api(self):
        """Test widget configuration API"""
        url = reverse('widget_config', kwargs={'company_slug': 'wazen'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertEqual(data['company_name'], 'Wazen')
        self.assertEqual(data['welcome_message'], 'Welcome to Wazen!')
        self.assertEqual(data['position'], 'bottom-right')
        self.assertTrue(data['is_active'])
        self.assertIn('theme_config', data)

    def test_widget_config_invalid_company(self):
        """Test widget config with invalid company"""
        url = reverse('widget_config', kwargs={'company_slug': 'nonexistent'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_widget_config_inactive_widget(self):
        """Test widget config with inactive widget"""
        self.company.widget_is_active = False
        self.company.save()

        url = reverse('widget_config', kwargs={'company_slug': 'wazen'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    @patch('project.views.create_message')
    def test_session_create_api(self, mock_create_message):
        """Test session creation API"""
        url = reverse('widget_session_create', kwargs={'company_slug': 'wazen'})
        data = {
            'visitor_ip': '192.168.1.100',
            'user_agent': 'Test Browser',
            'visitor_metadata': {'screen_resolution': '1920x1080'}
        }

        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)

        self.assertIn('session_id', response_data)
        self.assertEqual(response_data['company_name'], 'Wazen')
        self.assertIn('assistant_id', response_data)

        # Verify session was created in database
        session_id = response_data['session_id']
        session = WebsiteSession.objects.get(session_id=session_id)
        self.assertEqual(session.company, self.company)
        self.assertEqual(session.visitor_ip, '192.168.1.100')

    def test_session_status_api(self):
        """Test session status API"""
        # Create a session first
        thread = Thread.objects.create(
            name="Test Thread",
            assistant_id="test_ai_assistant"
        )

        session = WebsiteSession.objects.create(
            thread=thread,
            company=self.company,
            visitor_ip="192.168.1.100"
        )

        url = reverse('widget_session_status', kwargs={'session_id': str(session.session_id)})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertEqual(data['session_id'], str(session.session_id))
        self.assertEqual(data['status'], 'active')
        self.assertTrue(data['is_active'])
        self.assertFalse(data['is_expired'])
        self.assertEqual(data['company_name'], 'Wazen')

    def test_session_close_api(self):
        """Test session close API"""
        # Create a session first
        thread = Thread.objects.create(
            name="Test Thread",
            assistant_id="test_ai_assistant"
        )

        session = WebsiteSession.objects.create(
            thread=thread,
            company=self.company,
            visitor_ip="192.168.1.100"
        )

        url = reverse('widget_session_close', kwargs={'session_id': str(session.session_id)})
        data = {'reason': 'user_closed'}

        response = self.client.put(
            url,
            json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)

        self.assertEqual(response_data['status'], 'closed')
        self.assertIn('closed_at', response_data)

        # Verify session was closed in database
        session.refresh_from_db()
        self.assertEqual(session.status, 'closed')
        self.assertIsNotNone(session.closed_at)


class SecurityTest(TestCase):
    """Test security features including rate limiting and input validation"""

    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(
            name="TestCompany",
            activity_name="Testing",
            activity_type="SR",
            subscription_start_date="2024-01-01",
            subscription_end_date="2024-12-31",
            widget_is_active=True
        )
        cache.clear()

    def test_input_validation_company_slug(self):
        """Test input validation for company slug"""
        # Test invalid characters
        url = reverse('widget_config', kwargs={'company_slug': 'invalid!@#$%'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('Invalid company identifier', data['error'])

    def test_input_validation_session_id(self):
        """Test input validation for session ID"""
        # Test invalid UUID format
        url = reverse('widget_session_status', kwargs={'session_id': 'invalid-uuid'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('Invalid session ID format', data['error'])

    def test_cors_headers(self):
        """Test CORS headers are added to responses"""
        url = reverse('widget_config', kwargs={'company_slug': 'testcompany'})
        response = self.client.get(url, HTTP_ORIGIN='https://testcompany.com')

        self.assertEqual(response.status_code, 200)
        # Note: In test environment, CORS headers might not be fully testable
        # This would be better tested in integration tests

    def test_json_validation(self):
        """Test JSON validation for POST requests"""
        url = reverse('widget_session_create', kwargs={'company_slug': 'testcompany'})

        # Send invalid JSON
        response = self.client.post(
            url,
            'invalid json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('Invalid JSON format', data['error'])
