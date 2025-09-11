"""
AI Tools Registry for SAIA Multi-Tenant System

This module provides a centralized registry of all available AI tools
that can be enabled/disabled per customer company.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class ToolCategory(Enum):
    """Categories for AI tools"""
    DATABASE = "database"
    INVOICES = "invoices"
    CONTACTS = "contacts"
    ANALYTICS = "analytics"
    SYSTEM = "system"


class SubscriptionLevel(Enum):
    """Subscription levels for tool access"""
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class AIToolInfo:
    """Information about an AI tool"""
    name: str
    display_name: str
    description: str
    category: ToolCategory
    subscription_level: SubscriptionLevel
    method_name: str
    is_premium: bool = False
    requires_permissions: List[str] = None
    
    def __post_init__(self):
        if self.requires_permissions is None:
            self.requires_permissions = []


class AIToolsRegistry:
    """Registry of all available AI tools with metadata"""
    
    # Complete registry of all AI tools in CustomerDataAIAssistant
    TOOLS = {
        # System/Database Tools
        "test_customer_database_connection": AIToolInfo(
            name="test_customer_database_connection",
            display_name="Test Database Connection",
            description="Test connection to customer's MySQL database and verify connectivity",
            category=ToolCategory.SYSTEM,
            subscription_level=SubscriptionLevel.BASIC,
            method_name="test_customer_database_connection",
            requires_permissions=["view_database"]
        ),
        
        "list_customer_tables": AIToolInfo(
            name="list_customer_tables",
            display_name="List Database Tables",
            description="List all tables available in customer's database",
            category=ToolCategory.DATABASE,
            subscription_level=SubscriptionLevel.BASIC,
            method_name="list_customer_tables",
            requires_permissions=["view_database"]
        ),
        
        "describe_customer_table": AIToolInfo(
            name="describe_customer_table",
            display_name="Describe Table Structure",
            description="Get structure/schema of a specific table in customer's database",
            category=ToolCategory.DATABASE,
            subscription_level=SubscriptionLevel.BASIC,
            method_name="describe_customer_table",
            requires_permissions=["view_database"]
        ),
        
        "get_customer_table_sample": AIToolInfo(
            name="get_customer_table_sample",
            display_name="Get Table Sample Data",
            description="Get sample data from a customer table for analysis",
            category=ToolCategory.DATABASE,
            subscription_level=SubscriptionLevel.BASIC,
            method_name="get_customer_table_sample",
            requires_permissions=["view_database"]
        ),
        
        "count_customer_table_rows": AIToolInfo(
            name="count_customer_table_rows",
            display_name="Count Table Rows",
            description="Count total rows in a customer table",
            category=ToolCategory.DATABASE,
            subscription_level=SubscriptionLevel.BASIC,
            method_name="count_customer_table_rows",
            requires_permissions=["view_database"]
        ),
        
        "search_customer_data": AIToolInfo(
            name="search_customer_data",
            display_name="Search Customer Data",
            description="Search for specific data in customer's table with filters",
            category=ToolCategory.DATABASE,
            subscription_level=SubscriptionLevel.PREMIUM,
            method_name="search_customer_data",
            is_premium=True,
            requires_permissions=["view_database", "search_data"]
        ),
        
        # Invoice Tools
        "get_all_invoices": AIToolInfo(
            name="get_all_invoices",
            display_name="Get All Invoices",
            description="Retrieve all invoices from the customer database with pagination",
            category=ToolCategory.INVOICES,
            subscription_level=SubscriptionLevel.BASIC,
            method_name="get_all_invoices",
            requires_permissions=["view_invoices"]
        ),
        
        "get_latest_invoice": AIToolInfo(
            name="get_latest_invoice",
            display_name="Get Latest Invoice",
            description="Get the most recent invoice from the customer database",
            category=ToolCategory.INVOICES,
            subscription_level=SubscriptionLevel.BASIC,
            method_name="get_latest_invoice",
            requires_permissions=["view_invoices"]
        ),
        
        "get_invoice_count": AIToolInfo(
            name="get_invoice_count",
            display_name="Count Invoices",
            description="Get the total count of invoices in the customer database",
            category=ToolCategory.INVOICES,
            subscription_level=SubscriptionLevel.BASIC,
            method_name="get_invoice_count",
            requires_permissions=["view_invoices"]
        ),
        
        "get_invoice_by_number": AIToolInfo(
            name="get_invoice_by_number",
            display_name="Get Invoice by Number",
            description="Get a specific invoice by its invoice number",
            category=ToolCategory.INVOICES,
            subscription_level=SubscriptionLevel.BASIC,
            method_name="get_invoice_by_number",
            requires_permissions=["view_invoices"]
        ),
        
        # Contact Tools
        "get_contacts": AIToolInfo(
            name="get_contacts",
            display_name="Get Customer Contacts",
            description="Get all contacts (customers) from the customer database",
            category=ToolCategory.CONTACTS,
            subscription_level=SubscriptionLevel.BASIC,
            method_name="get_contacts",
            requires_permissions=["view_contacts"]
        ),
        
        # Analytics Tools
        "get_database_overview": AIToolInfo(
            name="get_database_overview",
            display_name="Database Overview",
            description="Get an overview of the customer database including table counts",
            category=ToolCategory.ANALYTICS,
            subscription_level=SubscriptionLevel.PREMIUM,
            method_name="get_database_overview",
            is_premium=True,
            requires_permissions=["view_database", "view_analytics"]
        ),
        
        "get_comprehensive_database_overview": AIToolInfo(
            name="get_comprehensive_database_overview",
            display_name="Comprehensive Database Overview",
            description="Get a comprehensive overview of the customer's database structure and available data",
            category=ToolCategory.ANALYTICS,
            subscription_level=SubscriptionLevel.PREMIUM,
            method_name="get_comprehensive_database_overview",
            is_premium=True,
            requires_permissions=["view_database", "view_analytics"]
        ),
    }
    
    @classmethod
    def get_all_tools(cls) -> Dict[str, AIToolInfo]:
        """Get all available tools"""
        return cls.TOOLS.copy()
    
    @classmethod
    def get_tools_by_category(cls, category: ToolCategory) -> Dict[str, AIToolInfo]:
        """Get tools filtered by category"""
        return {
            name: tool for name, tool in cls.TOOLS.items()
            if tool.category == category
        }
    
    @classmethod
    def get_tools_by_subscription(cls, subscription_level: SubscriptionLevel) -> Dict[str, AIToolInfo]:
        """Get tools available for a subscription level"""
        level_hierarchy = {
            SubscriptionLevel.BASIC: [SubscriptionLevel.BASIC],
            SubscriptionLevel.PREMIUM: [SubscriptionLevel.BASIC, SubscriptionLevel.PREMIUM],
            SubscriptionLevel.ENTERPRISE: [SubscriptionLevel.BASIC, SubscriptionLevel.PREMIUM, SubscriptionLevel.ENTERPRISE]
        }
        
        allowed_levels = level_hierarchy.get(subscription_level, [])
        return {
            name: tool for name, tool in cls.TOOLS.items()
            if tool.subscription_level in allowed_levels
        }
    
    @classmethod
    def get_basic_tools(cls) -> List[str]:
        """Get list of basic tool names (for default company configuration)"""
        return [
            name for name, tool in cls.TOOLS.items()
            if tool.subscription_level == SubscriptionLevel.BASIC
        ]
    
    @classmethod
    def get_premium_tools(cls) -> List[str]:
        """Get list of premium tool names"""
        return [
            name for name, tool in cls.TOOLS.items()
            if tool.is_premium
        ]
    
    @classmethod
    def get_tool_info(cls, tool_name: str) -> AIToolInfo:
        """Get information about a specific tool"""
        return cls.TOOLS.get(tool_name)
    
    @classmethod
    def is_tool_available(cls, tool_name: str, subscription_level: SubscriptionLevel) -> bool:
        """Check if a tool is available for a subscription level"""
        tool = cls.get_tool_info(tool_name)
        if not tool:
            return False
        
        available_tools = cls.get_tools_by_subscription(subscription_level)
        return tool_name in available_tools
    
    @classmethod
    def get_tools_for_company(cls, company) -> List[str]:
        """Get available tools for a specific company based on their configuration and subscription"""
        # If company has custom enabled tools, use those
        if hasattr(company, 'enabled_tools_json') and company.enabled_tools_json:
            return company.enabled_tools_json
        
        # Otherwise, determine based on subscription status
        if hasattr(company, 'subscription_status') and company.subscription_status == '1':  # Active
            # Active subscription gets basic + premium tools
            basic_tools = cls.get_basic_tools()
            premium_tools = cls.get_premium_tools()
            return basic_tools + premium_tools
        else:
            # Inactive subscription gets only basic tools
            return cls.get_basic_tools()
    
    @classmethod
    def get_categories(cls) -> List[ToolCategory]:
        """Get all tool categories"""
        return list(ToolCategory)
    
    @classmethod
    def get_subscription_levels(cls) -> List[SubscriptionLevel]:
        """Get all subscription levels"""
        return list(SubscriptionLevel)
