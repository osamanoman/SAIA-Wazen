# Company-Specific AI Assistants System

## Overview

The SAIA system now supports **automated generation of company-specific AI assistants** that provide complete isolation and customization for each company. This eliminates the previous single-class approach and provides proper separation of concerns.

## 🎯 Key Features

- **Automated File Generation**: AI assistant files are automatically created when new companies are added
- **Complete Isolation**: Each company gets their own dedicated assistant with isolated tools and configurations
- **Zero Code Duplication**: Uses template-based generation to maintain consistency
- **Seamless Integration**: Works with existing SAIA multi-tenant architecture
- **Security**: Company verification ensures users can only access their company's assistant
- **Scalable**: Supports unlimited companies without performance degradation

## 🏗️ Architecture

### File Structure
```
product/assistants/
├── __init__.py                          # Auto-discovery system
├── assistant_template.py               # Template for generating assistants
├── {company_slug}_ai_assistant.py      # Generated company assistants
└── ...
```

### Generated Assistant Example
Each company gets a dedicated assistant file like `wazen_ai_assistant.py`:

```python
class WazenAIAssistant(SAIAAIAssistantMixin, AIAssistant):
    id = "wazen_ai_assistant"
    name = "Wazen Business Assistant"
    
    def _verify_wazen_user(self):
        # Company-specific user verification
        
    @method_tool
    def get_wazen_invoices(self, limit: int = 30) -> str:
        # Company-specific tools
```

## 🚀 How It Works

### 1. Automatic Generation
When a new company is created:
1. Django signal triggers `create_company_assistant()`
2. Template system generates company-specific assistant file
3. Assistant is automatically discovered and registered

### 2. Routing System
Enhanced routing logic in `project/views.py`:
1. Check for company-specific assistant first
2. Fall back to default `CustomerDataAIAssistant` if none exists
3. Maintain existing admin/customer user separation

### 3. Discovery System
The `product/assistants/__init__.py` automatically:
- Scans for `*_ai_assistant.py` files
- Imports and registers all company assistants
- Provides registry for routing system

## 📋 Usage

### For New Companies
1. Create company through Django admin
2. AI assistant file is automatically generated
3. Users are automatically routed to company-specific assistant

### For Existing Companies
Use the management command:
```bash
# Generate for all companies
python manage.py generate_company_assistants

# Generate for specific company
python manage.py generate_company_assistants --company-name "Wazen"

# Dry run to see what would be created
python manage.py generate_company_assistants --dry-run

# Force regeneration
python manage.py generate_company_assistants --force
```

### Django Admin Actions
- Select companies in admin interface
- Use "Generate dedicated AI assistants" action
- View "AI Assistant" column to see status

## 🔧 Technical Implementation

### Key Components

1. **Company Model Extensions** (`company/models.py`)
   - `get_company_assistant_id()`: Returns assistant ID if exists
   - `has_dedicated_assistant()`: Checks for dedicated assistant

2. **Signal System** (`company/signals.py`)
   - Auto-generates assistant files on company creation
   - Handles template processing and file writing

3. **Template System** (`product/assistants/assistant_template.py`)
   - Generates consistent assistant code
   - Handles naming conventions and security

4. **Discovery System** (`product/assistants/__init__.py`)
   - Auto-imports all company assistants
   - Maintains registry for routing

5. **Enhanced Routing** (`project/views.py`)
   - Prioritizes company-specific assistants
   - Maintains backward compatibility

6. **Security Updates** (`saia/permissions.py`)
   - Allows users to access their company's assistant
   - Maintains isolation between companies

## 🛡️ Security Features

- **Company Verification**: Each assistant verifies user belongs to correct company
- **Read-Only Database Access**: All database operations are read-only
- **Permission System**: Updated to allow company-specific assistant access
- **Complete Isolation**: No cross-company data access possible

## 🎨 Customization

### Template Customization
Modify `assistant_template.py` to:
- Add new default tools
- Change instruction templates
- Modify security patterns

### Company-Specific Tools
Each generated assistant includes:
- `get_{company}_invoices()`: Company invoice data
- `get_{company}_clients()`: Company client data  
- `get_{company}_overview()`: Business overview
- `analyze_{company}_performance()`: Performance metrics

## 📊 Benefits

### Before (Single Class Approach)
- ❌ All companies shared `CustomerDataAIAssistant`
- ❌ Dynamic configuration loading
- ❌ Mixed company logic in single file
- ❌ Maintenance and security risks

### After (Company-Specific Approach)
- ✅ Each company has dedicated assistant
- ✅ Complete isolation and security
- ✅ Easy customization per company
- ✅ Scalable architecture
- ✅ Zero code duplication

## 🔍 Monitoring

### Admin Interface
- View "AI Assistant" column in company list
- See which companies have dedicated assistants
- Use admin actions to generate assistants

### Logging
All operations are logged with company context:
```
INFO: Created AI assistant file for company 'Wazen': wazen_ai_assistant.py
INFO: User john@wazen.com routed to wazen_ai_assistant
```

## 🚀 Future Enhancements

- **Custom Tool Templates**: Company-specific tool templates
- **Advanced Customization**: Per-company instruction customization
- **Performance Monitoring**: Company-specific usage analytics
- **Bulk Operations**: Batch assistant management tools

## 📝 Migration Notes

- Existing companies continue using `CustomerDataAIAssistant` until assistants are generated
- No breaking changes to existing functionality
- Gradual migration supported through management commands
- Full backward compatibility maintained

---

**The company-specific AI assistant system provides a scalable, secure, and maintainable solution for multi-tenant AI assistant management in the SAIA platform.**
