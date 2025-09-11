# SAIA Multi-Tenant AI Assistant - Customer Onboarding Guide

## 📋 **Overview**

This guide provides step-by-step instructions for onboarding new customers to the SAIA Multi-Tenant AI Assistant system. Each customer can have their own customized AI assistant with specific tools, instructions, and database connections.

---

## 🚀 **Quick Start Checklist**

- [ ] Create company record in Django admin
- [ ] Configure AI assistant settings
- [ ] Set up customer database connection (optional)
- [ ] Configure AI tools and permissions
- [ ] Create customer users
- [ ] Test AI assistant functionality
- [ ] Provide customer training

---

## 📝 **Step 1: Create Company Record**

### **Access Django Admin**
1. Navigate to `/admin/company/company/`
2. Click "Add Company"
3. Fill in basic company information:

```
Company Information:
├── Name: [Customer Company Name]
├── Email: [Primary contact email]
├── Phone: [Contact phone number]
├── Activity Name: [Business description]
├── Activity Type: [Service/Commercial/Industrial]
└── Activity Status: [Active]

Subscription Details:
├── Subscription Start Date: [Today's date]
├── Subscription End Date: [End date]
└── Subscription Status: [Active/Inactive]
```

---

## 🤖 **Step 2: Configure AI Assistant Settings**

### **AI Assistant Configuration Section**

#### **2.1 AI Language**
- **English (en)**: Default for international customers
- **Arabic (ar)**: For Arabic-speaking customers

#### **2.2 AI Temperature (Creativity Level)**
- **0.1**: Very focused, business-oriented (recommended)
- **0.2**: Slightly more creative
- **0.3**: Balanced creativity and focus
- **Higher values**: More creative but less predictable

#### **2.3 Custom AI Instructions**
Create industry-specific instructions. Examples:

**Insurance Company:**
```
🏢 **[Company Name] Insurance AI Assistant**

You are the dedicated AI assistant for [Company Name], specializing in insurance operations.

**🎯 YOUR MISSION:**
1. **POLICY MANAGEMENT**: Help manage insurance policies and claims
2. **RISK ASSESSMENT**: Provide insights on risk analysis and underwriting
3. **CUSTOMER SERVICE**: Support insurance customer inquiries
4. **COMPLIANCE**: Ensure regulatory compliance in all recommendations

**🔒 SECURITY & COMPLIANCE:**
- Access only [Company Name]'s authorized insurance database
- Maintain strict confidentiality of customer data
- Follow insurance industry regulations and standards
```

**Retail Company:**
```
🏢 **[Company Name] Retail Intelligence Assistant**

You are the dedicated AI assistant for [Company Name], specializing in retail operations.

**🎯 YOUR MISSION:**
1. **INVENTORY MANAGEMENT**: Help track and manage inventory levels
2. **SALES ANALYTICS**: Analyze sales trends and customer behavior
3. **CUSTOMER INSIGHTS**: Understand customer preferences and patterns
4. **OPERATIONAL EFFICIENCY**: Optimize retail operations and processes

**🔒 RETAIL FOCUS:**
- Access only [Company Name]'s retail database
- Focus on sales, inventory, and customer data
- Provide actionable retail business insights
```

#### **2.4 Database Configuration (Optional)**
For customers with their own databases:

```json
{
    "host": "customer.database.com",
    "name": "customer_business_db",
    "user": "readonly_user",
    "password": "secure_password",
    "port": 3306,
    "charset": "utf8mb4"
}
```

**⚠️ Security Requirements:**
- Use read-only database user
- Ensure secure password
- Limit database permissions
- Test connection before deployment

---

## 🛠️ **Step 3: Configure AI Tools**

### **Available Tool Categories**

#### **📊 Database Tools (5 tools)**
- **Test Database Connection**: Verify database connectivity
- **List Database Tables**: Show available tables
- **Describe Table Structure**: Get table schema information
- **Get Table Sample Data**: Preview table contents
- **Count Table Rows**: Get row counts for tables

#### **📄 Invoice Tools (4 tools)**
- **Get All Invoices**: Retrieve invoice lists with pagination
- **Get Latest Invoice**: Show most recent invoice
- **Count Invoices**: Get total invoice count
- **Get Invoice by Number**: Find specific invoice

#### **👥 Contact Tools (1 tool)**
- **Get Customer Contacts**: Access customer/contact information

#### **📈 Analytics Tools (2 tools) - Premium**
- **Database Overview**: Comprehensive database analysis
- **Search Customer Data**: Advanced data search capabilities

#### **⚙️ System Tools (1 tool)**
- **Test Customer Database Connection**: System connectivity testing

### **Tool Configuration by Subscription Level**

#### **Basic Subscription (10 tools)**
- All Database tools (except Search Customer Data)
- All Invoice tools
- All Contact tools
- All System tools

#### **Premium Subscription (13 tools)**
- All Basic tools
- All Analytics tools (premium features)
- Advanced search capabilities

### **Custom Tool Selection**
Check/uncheck tools in the admin interface based on:
- Customer subscription level
- Business requirements
- Security considerations
- User training level

---

## 👤 **Step 4: Create Customer Users**

### **User Creation Process**
1. Navigate to `/admin/auth/user/`
2. Click "Add User"
3. Configure user settings:

```
User Information:
├── Username: [unique_username]
├── Email: [user@customer.com]
├── Password: [secure_password]
├── First Name: [User's first name]
├── Last Name: [User's last name]
├── Is Customer: ✓ [Check this box]
└── Company: [Select the customer's company]
```

### **User Permissions**
- **is_customer**: Must be checked
- **Company**: Must be assigned to customer's company
- **Staff status**: Usually unchecked for customer users
- **Superuser**: Never checked for customer users

---

## 🧪 **Step 5: Test AI Assistant Functionality**

### **Testing Checklist**

#### **5.1 Basic Functionality**
- [ ] User can log in successfully
- [ ] AI assistant loads with correct company branding
- [ ] Custom instructions are applied
- [ ] AI language setting is correct
- [ ] AI temperature setting is working

#### **5.2 Tool Testing**
- [ ] Enabled tools are accessible
- [ ] Disabled tools are properly blocked
- [ ] Tool responses are appropriate
- [ ] Database connection works (if configured)
- [ ] Error messages are user-friendly

#### **5.3 Security Testing**
- [ ] User can only access their company's data
- [ ] Database isolation is working
- [ ] Tool permissions are enforced
- [ ] No access to other companies' information

### **Test Commands**
```
# Test database connection
"Test our database connection"

# Test invoice tools
"Show me our latest invoices"

# Test contact tools
"Get our customer contacts"

# Test disabled tools (should be blocked)
"Give me a database overview" (if not enabled)
```

---

## 📚 **Step 6: Customer Training**

### **Training Materials to Provide**

#### **6.1 User Guide**
- How to access the AI assistant
- Available commands and tools
- Best practices for queries
- Security guidelines

#### **6.2 Industry-Specific Examples**
Provide examples relevant to customer's industry:

**Insurance Examples:**
- "Show me claims from last month"
- "What's our policy renewal rate?"
- "Find high-risk customers"

**Retail Examples:**
- "Show me top-selling products"
- "What's our inventory status?"
- "Analyze customer purchase patterns"

#### **6.3 Troubleshooting Guide**
- Common error messages and solutions
- Who to contact for support
- How to request additional tools or features

---

## 🔧 **Step 7: Ongoing Maintenance**

### **Regular Tasks**
- [ ] Monitor AI assistant usage
- [ ] Review and update custom instructions
- [ ] Adjust tool permissions as needed
- [ ] Update database connections if changed
- [ ] Collect customer feedback

### **Performance Monitoring**
- Response times
- Error rates
- User satisfaction
- Tool usage statistics

---

## 📞 **Support and Troubleshooting**

### **Common Issues**

#### **Database Connection Problems**
- Verify database credentials
- Check network connectivity
- Confirm read-only permissions
- Test connection manually

#### **Tool Access Issues**
- Verify tool is enabled for company
- Check user permissions
- Confirm subscription level
- Review tool configuration

#### **AI Response Issues**
- Review custom instructions
- Check AI temperature setting
- Verify language setting
- Consider instruction refinement

### **Getting Help**
- **Technical Support**: [support@saia.com]
- **Documentation**: [docs.saia.com]
- **Training**: [training@saia.com]

---

## ✅ **Onboarding Completion Checklist**

- [ ] Company record created and configured
- [ ] AI assistant settings customized
- [ ] Database connection tested (if applicable)
- [ ] AI tools configured and tested
- [ ] Customer users created and tested
- [ ] Customer training completed
- [ ] Support contacts provided
- [ ] Feedback mechanism established

**🎉 Customer is now ready to use their customized SAIA AI Assistant!**
