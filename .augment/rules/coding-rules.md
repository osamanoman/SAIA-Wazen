---
type: "always_apply"
---

As an expert Django Python full-stack developer, conduct a comprehensive code review of the SAIA Multi-Tenant Website Chatbot Platform implementation we've built so far. Focus on the following specific areas:

**Code Quality & Best Practices:**
1. Review all files in the `chatbot/` app (models.py, api.py, helpers.py, urls.py, apps.py) for Django best practices
2. Ensure proper use of Django ORM relationships, indexing, and query optimization
3. Verify that all models follow Django naming conventions and include appropriate `__str__` methods
4. Check that API endpoints follow RESTful design principles and proper HTTP status codes
5. Validate that all functions have appropriate docstrings and type hints

**Code Duplication & Reuse:**
1. Identify any duplicate functionality between the new `chatbot` app and existing apps (`users`, `company`, `product`, `project`)
2. Check if we're properly leveraging existing models (Company, User) instead of recreating similar functionality
3. Ensure we're using existing helper functions and utilities from the SAIA codebase where appropriate
4. Verify that the ThreadExtension model is the most efficient way to extend django_ai_assistant.Thread rather than duplicating functionality

**Integration & Architecture:**
1. Confirm that the chatbot app properly integrates with existing SAIA permissions system (`saia/permissions.py`)
2. Verify that company-specific AI assistant routing uses existing `company.get_company_assistant_id()` method
3. Ensure database migrations don't conflict with existing schema
4. Check that URL patterns don't create conflicts with existing routes

**Unnecessary File Creation:**
1. Identify if any new files could be consolidated into existing modules
2. Determine if functionality could be added to existing views/APIs rather than creating new ones
3. Assess whether separate helper functions are needed or if they could be methods on existing models

**Specific Action Items:**
- Modify existing code where possible instead of creating new files
- Consolidate duplicate functionality
- Ensure proper inheritance and composition patterns
- Maintain consistency with existing SAIA codebase architecture and patterns
- Provide specific recommendations for refactoring and consolidation

- avoid complexity 
- never do workarounds, if you couldnt solve an issue , go for root cause analysis , if you still couldnt fix it . ask me for the workaround approach and stop to give you permission.
