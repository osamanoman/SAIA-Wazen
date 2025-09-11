"""
Custom context processors for SAIA
"""

def assistant_context(request):
    """
    Add assistant type context to all templates
    """
    if not request.user.is_authenticated:
        return {}
    
    user = request.user
    selected_company_id = request.session.get('selected_company_id')
    selected_company_name = request.session.get('selected_company_name')
    is_customer_user = (hasattr(user, 'is_customer') and user.is_customer) or bool(selected_company_id)
    
    # Import assistant classes to check which one should be used
    from product.hybrid_ai_assistant import HybridCustomerAIAssistant
    from saia.utils import should_use_hybrid_assistant
    
    if selected_company_id:
        if should_use_hybrid_assistant(selected_company_name):
            assistant_type = f"Knowledge Assistant - {selected_company_name}"
            assistant_description = f"Get help with {selected_company_name} services and information"
        else:
            assistant_type = f"Customer Data Assistant - {selected_company_name}"
            assistant_description = f"Access {selected_company_name}'s MySQL database"
    elif hasattr(user, 'is_customer') and user.is_customer:
        if hasattr(user, 'company') and user.company and should_use_hybrid_assistant(user.company.name):
            assistant_type = "Knowledge Assistant"
            assistant_description = "Get help with services, policies, and company information"
        else:
            assistant_type = "Customer Data Assistant"
            assistant_description = "Access your company's MySQL database"
    else:
        assistant_type = "SAIA System Assistant"
        assistant_description = "Manage SAIA system data and operations"
    
    return {
        'assistant_type': assistant_type,
        'assistant_description': assistant_description,
        'is_customer_user': is_customer_user,
    }
