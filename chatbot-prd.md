# 🤖 SAIA Multi-Tenant Website Chatbot Platform - PRD

**Product Requirements Document**  
**Version:** 1.0  
**Date:** September 2025  
**Project:** SAIA Website Chatbot Integration Platform  

---

## 📋 **Executive Summary**

Transform the SAIA Business Management System into a scalable multi-tenant SaaS chatbot platform that enables customers to integrate AI-powered chat support directly into their websites. Each customer gets their own isolated AI assistant with company-specific knowledge, branding, and admin dashboard.

### **Business Objectives**
- 🎯 **Revenue Growth**: New SaaS revenue stream from chatbot subscriptions
- 🚀 **Market Expansion**: Serve multiple customers simultaneously  
- 🔧 **Platform Leverage**: Maximize existing SAIA infrastructure investment
- 🏢 **Customer Value**: Provide AI-powered customer support solutions

---

## 🎯 **Product Vision**

**"Enable any business to deploy intelligent, company-specific AI chatbots on their websites within minutes, powered by SAIA's robust multi-tenant architecture."**

### **Success Metrics**
- **Customer Onboarding**: < 24 hours from signup to live chatbot
- **Response Accuracy**: > 85% relevant responses using company knowledge
- **Platform Uptime**: 99.9% availability
- **Customer Satisfaction**: > 4.5/5 rating from end customers

---

## 👥 **Target Users**

### **Primary Users**
1. **Business Owners** - Want AI chatbots for their websites
2. **Customer Support Managers** - Need to monitor and manage chat sessions
3. **Website Visitors** - Seeking instant support and information

### **Secondary Users**
1. **SAIA Platform Administrators** - Manage the overall platform
2. **Support Agents** - Handle escalated conversations
3. **Developers** - Integrate chatbot widgets into websites

---

## ✨ **Core Features**

### **Phase 1: Foundation (Weeks 1-2)**

#### **1.1 Multi-Tenant Session Management**
- **Anonymous Session Tracking**: Cookie-based visitor identification
- **Company Isolation**: Complete data separation between customers
- **Session Lifecycle**: Active → Closed → Archived states
- **Visitor Analytics**: IP, user agent, session duration tracking

**Technical Requirements:**
```python
class WebsiteSession(models.Model):
    session_id = models.UUIDField(unique=True)
    thread = models.OneToOneField(Thread, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    visitor_ip = models.GenericIPAddressField()
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
```

#### **1.2 Public API Endpoints**
- **Session Creation**: `POST /api/widget/session/create/`
- **Message Sending**: `POST /api/widget/session/{id}/send/`
- **Message History**: `GET /api/widget/session/{id}/messages/`
- **Session Status**: `GET /api/widget/session/{id}/status/`

**Security Requirements:**
- Rate limiting: 100 requests/minute per IP
- CORS configuration for customer domains
- Input sanitization and validation
- Session timeout: 30 minutes of inactivity

#### **1.3 Extended Thread System**
- **Session Types**: Admin vs Website differentiation
- **Anonymous Support**: Threads without Django User accounts
- **Company Routing**: Automatic AI assistant selection
- **Message Persistence**: Full conversation history storage

### **Phase 2: Widget Development (Week 3)**

#### **2.1 Embeddable Chat Widget**
- **Responsive Design**: Mobile-first, works on all screen sizes
- **Custom Theming**: Company colors, logos, messages
- **Real-time Messaging**: Instant message delivery
- **Session Persistence**: Maintains conversation across page reloads

**Widget Features:**
- Minimized/Expanded states
- Typing indicators
- Message timestamps
- Emoji support
- File attachment capability (future)

**Integration Code:**
```html
<script src="https://saia-platform.com/widget/chatbot.js"></script>
<script>
new SAIAChatWidget({
    company: 'wazen',
    container: '#chatbot',
    theme: {
        primaryColor: '#1e40af',
        headerText: 'Wazen Support',
        welcomeMessage: 'مرحباً! كيف يمكنني مساعدتك؟'
    }
});
</script>
```

#### **2.2 Widget Customization**
- **Branding Options**: Logo, colors, fonts
- **Language Support**: RTL/LTR text direction
- **Welcome Messages**: Company-specific greetings
- **Position Control**: Bottom-right, bottom-left, custom
- **Size Options**: Compact, standard, large

### **Phase 3: Admin Dashboard (Week 4)**

#### **3.1 Customer Admin Interface**
- **Session Monitoring**: Real-time active conversations
- **Conversation History**: Searchable message archives
- **Visitor Analytics**: Daily/weekly/monthly statistics
- **Performance Metrics**: Response times, resolution rates

**Dashboard Sections:**
1. **Live Sessions**: Currently active website conversations
2. **Recent Conversations**: Last 24 hours activity
3. **Analytics**: Visitor trends, popular questions
4. **Settings**: Widget customization, AI configuration

#### **3.2 Agent Handover System**
- **Escalation Triggers**: Complex queries, customer requests
- **Agent Notifications**: Real-time alerts for new handovers
- **Seamless Transition**: Context preservation during handover
- **Resolution Tracking**: Time to resolution metrics

**Handover Workflow:**
1. AI detects need for human assistance
2. Session marked for agent review
3. Agent receives notification
4. Agent joins conversation
5. Resolution and session closure

### **Phase 4: Advanced Features (Week 5)**

#### **4.1 Analytics & Reporting**
- **Conversation Analytics**: Volume, duration, satisfaction
- **AI Performance**: Response accuracy, knowledge gaps
- **Customer Insights**: Common questions, user behavior
- **Business Intelligence**: ROI metrics, cost per conversation

#### **4.2 Knowledge Management**
- **Company Knowledge Base**: Upload and manage content
- **AI Training**: Improve responses with company data
- **Content Categories**: Organize information by topics
- **Search Analytics**: Track knowledge base usage

---

## 🏗️ **Technical Architecture**

### **Database Schema Extensions**

#### **New Models:**
```python
# Website session tracking
class WebsiteSession(models.Model):
    session_id = models.UUIDField(unique=True, default=uuid.uuid4)
    thread = models.OneToOneField(Thread, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    visitor_ip = models.GenericIPAddressField()
    user_agent = models.TextField()
    status = models.CharField(max_length=20, default='active')
    referrer_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

# Agent handover management
class SessionHandover(models.Model):
    website_session = models.ForeignKey(WebsiteSession, on_delete=models.CASCADE)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    handover_reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

# Widget customization
class WidgetConfiguration(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    theme_config = models.JSONField(default=dict)
    welcome_message = models.TextField()
    position = models.CharField(max_length=20, default='bottom-right')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### **Extended Models:**
```python
# Add to existing Thread model
class Thread(models.Model):
    # ... existing fields ...
    session_type = models.CharField(
        max_length=20, 
        choices=[('admin', 'Admin'), ('website', 'Website')],
        default='admin'
    )
    is_anonymous = models.BooleanField(default=False)
    visitor_metadata = models.JSONField(default=dict, blank=True)
```

### **API Architecture**

#### **Public Widget API (No Authentication)**
```python
# Widget session management
POST   /api/widget/session/create/
GET    /api/widget/session/{session_id}/messages/
POST   /api/widget/session/{session_id}/send/
PUT    /api/widget/session/{session_id}/status/
GET    /api/widget/company/{slug}/config/

# Widget assets
GET    /static/widget/chatbot.js
GET    /static/widget/chatbot.css
GET    /static/widget/themes/{theme}.css
```

#### **Admin API (Authenticated)**
```python
# Session management
GET    /api/admin/website-sessions/
GET    /api/admin/website-sessions/{id}/
PUT    /api/admin/website-sessions/{id}/handover/
POST   /api/admin/website-sessions/{id}/close/

# Analytics
GET    /api/admin/analytics/conversations/
GET    /api/admin/analytics/performance/
GET    /api/admin/analytics/knowledge-gaps/

# Configuration
GET    /api/admin/widget-config/
PUT    /api/admin/widget-config/
POST   /api/admin/knowledge-base/upload/
```

### **Security Architecture**

#### **Data Isolation**
- **Company-Level Isolation**: All data filtered by company association
- **Session Security**: UUID-based session identification
- **API Rate Limiting**: Prevent abuse and ensure fair usage
- **Input Validation**: Sanitize all user inputs

#### **Authentication & Authorization**
- **Public API**: No auth required, rate-limited by IP
- **Admin API**: Django session authentication
- **Permission System**: Extend existing SAIA permissions
- **CORS Configuration**: Allow customer domains

---

## 🎨 **User Experience Design**

### **Widget UX Requirements**

#### **Visual Design**
- **Modern Interface**: Clean, professional appearance
- **Brand Consistency**: Match customer's website design
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance**: < 2 second load time

#### **Interaction Design**
- **Intuitive Controls**: Clear send button, input field
- **Visual Feedback**: Typing indicators, message status
- **Error Handling**: Graceful failure with retry options
- **Mobile Optimization**: Touch-friendly interface

#### **Conversation Flow**
1. **Welcome Message**: Company-specific greeting
2. **User Input**: Natural language question/request
3. **AI Processing**: Company assistant generates response
4. **Response Display**: Formatted, helpful answer
5. **Follow-up**: Offer additional assistance

### **Admin Dashboard UX**

#### **Dashboard Layout**
- **Overview Cards**: Active sessions, daily stats
- **Session List**: Real-time conversation monitoring
- **Quick Actions**: Handover, close, view details
- **Search & Filter**: Find specific conversations

#### **Responsive Design**
- **Desktop**: Full-featured dashboard
- **Tablet**: Optimized layout for touch
- **Mobile**: Essential features only

---

## 📊 **Success Metrics & KPIs**

### **Business Metrics**
- **Customer Acquisition**: New chatbot customers per month
- **Revenue Growth**: Monthly recurring revenue from chatbot subscriptions
- **Customer Retention**: Churn rate < 5% monthly
- **Platform Utilization**: Average sessions per customer per day

### **Technical Metrics**
- **Response Time**: < 2 seconds average AI response time
- **Uptime**: 99.9% platform availability
- **Scalability**: Support 1000+ concurrent sessions
- **Error Rate**: < 0.1% API error rate

### **User Experience Metrics**
- **Conversation Completion**: > 80% conversations reach resolution
- **User Satisfaction**: > 4.5/5 average rating
- **Knowledge Accuracy**: > 85% relevant AI responses
- **Agent Handover Rate**: < 15% of conversations escalated

---

## 🚀 **Implementation Timeline**

### **Phase 1: Foundation (Weeks 1-2)**
- [ ] Extend database models for website sessions
- [ ] Create public API endpoints for widget
- [ ] Implement anonymous session management
- [ ] Add company-specific AI assistant routing
- [ ] Set up basic security and rate limiting

### **Phase 2: Widget Development (Week 3)**
- [ ] Build responsive chat widget interface
- [ ] Implement real-time messaging functionality
- [ ] Add customization options (themes, branding)
- [ ] Create widget embedding system
- [ ] Test cross-browser compatibility

### **Phase 3: Admin Dashboard (Week 4)**
- [ ] Extend existing admin interface for website sessions
- [ ] Add real-time session monitoring
- [ ] Implement agent handover workflow
- [ ] Create analytics and reporting views
- [ ] Add session management controls

### **Phase 4: Advanced Features (Week 5)**
- [ ] Build comprehensive analytics dashboard
- [ ] Add knowledge base management tools
- [ ] Implement advanced customization options
- [ ] Create customer onboarding automation
- [ ] Performance optimization and testing

### **Phase 5: Launch Preparation (Week 6)**
- [ ] End-to-end testing with multiple customers
- [ ] Documentation and user guides
- [ ] Customer onboarding process
- [ ] Marketing materials and pricing
- [ ] Production deployment and monitoring

---

## 🔧 **Technical Requirements**

### **Infrastructure**
- **Database**: PostgreSQL with proper indexing for performance
- **Caching**: Redis for session management and rate limiting
- **CDN**: Static asset delivery for widget files
- **Monitoring**: Phoenix observability for AI assistant tracing

### **Performance Requirements**
- **Concurrent Users**: Support 1000+ simultaneous website visitors
- **Response Time**: < 2 seconds for AI responses
- **Widget Load Time**: < 1 second for initial widget load
- **Database Queries**: Optimized with proper indexing

### **Security Requirements**
- **Data Encryption**: HTTPS for all communications
- **Input Validation**: Sanitize all user inputs
- **Rate Limiting**: Prevent API abuse
- **Session Security**: Secure session token generation

---

## 💰 **Business Model**

### **Pricing Tiers**
1. **Starter**: $49/month - 1000 conversations, basic features
2. **Professional**: $149/month - 5000 conversations, analytics
3. **Enterprise**: $399/month - Unlimited conversations, custom features

### **Revenue Projections**
- **Year 1**: 50 customers, $150K ARR
- **Year 2**: 200 customers, $600K ARR  
- **Year 3**: 500 customers, $1.5M ARR

---

## 🎯 **Success Criteria**

### **MVP Success (End of Phase 4)**
- [ ] 5 pilot customers successfully using chatbots
- [ ] 95% uptime during pilot period
- [ ] < 3 second average response time
- [ ] Positive feedback from pilot customers

### **Launch Success (3 months post-launch)**
- [ ] 25 paying customers
- [ ] $10K monthly recurring revenue
- [ ] 99.9% platform uptime
- [ ] 4.5+ customer satisfaction rating

### **Scale Success (6 months post-launch)**
- [ ] 100 paying customers
- [ ] $50K monthly recurring revenue
- [ ] Platform handling 10K+ daily conversations
- [ ] Automated customer onboarding process

---

**Document Status:** Draft v1.0  
**Next Review:** Weekly during implementation  
**Stakeholders:** Product, Engineering, Sales, Customer Success
