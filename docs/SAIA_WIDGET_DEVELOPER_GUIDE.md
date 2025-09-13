# SAIA Widget Developer Integration Guide

## 🎯 Overview

This guide provides everything you need to integrate the SAIA Multi-Tenant Chatbot Widget into your website. The widget enables AI-powered customer support through the Wazen AI assistant.

**Integration Time**: 15-30 minutes  
**Demo**: http://localhost:8000/api/widget/demo/wazen/

---

## 🚀 Step 1: Choose Your Integration Method

### Method A: Simple Script Tag (Recommended - 5 minutes)

Add this single line before your closing `</body>` tag:

```html
<script 
    src="http://localhost:8000/static/widget/js/saia-widget-loader.js"
    data-company="wazen"
    data-api-url="http://localhost:8000"
    data-position="bottom-right"
    data-auto-open="false"
    data-theme="default"
    async>
</script>
```

**That's it!** The widget will automatically appear in the bottom-right corner.

### Method B: Advanced JavaScript (Full Control)

For custom event handling and advanced configuration:

```html
<script>
(function(w,d,s,o,f,js,fjs){
    w['SAIAWidgetObject']=o;w[o]=w[o]||function(){(w[o].q=w[o].q||[]).push(arguments)};
    js=d.createElement(s),fjs=d.getElementsByTagName(s)[0];
    js.id=o;js.src=f;js.async=1;fjs.parentNode.insertBefore(js,fjs);
})(window,document,'script','saia','http://localhost:8000/static/widget/js/saia-widget-loader.js');

saia('init', {
    companySlug: 'wazen',
    apiBaseUrl: 'http://localhost:8000',
    position: 'bottom-right',
    autoOpen: false,
    showWelcomeMessage: true,
    theme: 'default',
    
    // Event callbacks
    onReady: function(widget) {
        console.log('Widget ready!');
    },
    onOpen: function(widget) {
        console.log('Widget opened');
        // Track with your analytics
        gtag('event', 'widget_opened', { company: 'wazen' });
    },
    onMessage: function(message, widget) {
        console.log('New message:', message);
        // Track conversations
        gtag('event', 'widget_message', { company: 'wazen' });
    }
});
</script>
```

---

## ⚙️ Step 2: Configuration Options

### Basic Configuration

```javascript
{
    // Required
    companySlug: 'wazen',           // Your company identifier
    apiBaseUrl: 'http://localhost:8000',  // API server URL
    
    // Widget Position
    position: 'bottom-right',       // bottom-right, bottom-left, top-right, top-left
    
    // Behavior
    autoOpen: false,                // Auto-open widget on page load
    autoOpenDelay: 3000,           // Delay before auto-opening (ms)
    showWelcomeMessage: true,      // Show initial welcome message
    enableSound: true,             // Enable notification sounds
    
    // Styling
    theme: 'default',              // default, modern, minimal, corporate
    
    // Advanced
    debug: false,                  // Enable debug logging
    maxMessages: 100,              // Max messages in memory
    sessionTimeout: 1800000        // Session timeout (30 minutes)
}
```

### Custom Theme Configuration

```javascript
theme: {
    primary_color: '#1e40af',      // Your brand color
    secondary_color: '#f3f4f6',    // Background color
    text_color: '#1f2937',         // Text color
    header_bg: '#1e40af',          // Header background
    header_text: '#ffffff',        // Header text color
    font_family: 'system-ui, -apple-system, sans-serif',
    border_radius: '8px',          // Border radius
    shadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
}
```

---

## 🎨 Step 3: Custom Styling (Optional)

Override widget styles with your own CSS:

```css
/* Custom widget styling */
.saia-widget {
    --saia-primary-color: #your-brand-color;
    --saia-secondary-color: #f8f9fa;
    --saia-text-color: #333333;
    --saia-border-radius: 12px;
    --saia-shadow: 0 8px 32px rgba(0,0,0,0.12);
}

/* Custom header */
.saia-widget-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Custom message bubbles */
.saia-message-user .saia-message-content {
    background: var(--saia-primary-color);
    color: white;
}

.saia-message-bot .saia-message-content {
    background: #f8f9fa;
    color: #333;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .saia-widget {
        width: calc(100vw - 20px) !important;
        max-width: 400px !important;
    }
}
```

---

## 🧪 Step 4: Test Your Integration

### 1. Basic Test

Open your website and check:
- ✅ Widget appears in the specified position
- ✅ No console errors
- ✅ Widget opens when clicked
- ✅ Can send and receive messages

### 2. JavaScript Test

```javascript
// Check widget status
setTimeout(() => {
    const state = saia('state');
    console.log('Widget loaded:', state.isLoaded);
    console.log('Session ID:', state.sessionId);
}, 3000);
```

### 3. Use the Demo Page

Visit: **http://localhost:8000/api/widget/demo/wazen/**

The demo page shows:
- Live widget functionality
- API status monitoring
- Integration code examples
- Configuration options

---

## 🔌 API Documentation

### How the Widget API Works

The widget uses a **session-based API architecture**:

1. **Configuration** → Get widget settings for your company
2. **Session Creation** → Create anonymous chat session for visitor
3. **Message Exchange** → Send user messages, receive AI responses
4. **Session Management** → Handle session lifecycle

### Core API Endpoints

#### 1. Widget Configuration
**Get widget settings for your company**

```http
GET /api/widget/config/{company_slug}/
```

**Example Request:**
```bash
curl http://localhost:8000/api/widget/config/wazen/
```

**Response:**
```json
{
    "company_name": "Wazen",
    "assistant_id": "wazen_ai_assistant",
    "welcome_message": "Hello! How can Wazen help you today?",
    "theme_config": {
        "primary_color": "#1e40af",
        "secondary_color": "#f3f4f6",
        "text_color": "#1f2937",
        "header_bg": "#1e40af",
        "header_text": "#ffffff"
    },
    "position": "bottom-right",
    "auto_open": false,
    "is_active": true,
    "rate_limit": 20,
    "max_message_length": 2000
}
```

#### 2. Create Chat Session
**Create a new anonymous chat session**

```http
POST /api/widget/session/create/{company_slug}/
Content-Type: application/json
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/widget/session/create/wazen/ \
  -H "Content-Type: application/json" \
  -d '{
    "visitor_ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "referrer_url": "https://example.com/page",
    "visitor_metadata": {
      "page_title": "Product Page",
      "user_id": "anonymous_123"
    }
  }'
```

**Response:**
```json
{
    "session_id": "3204a942-41ee-480d-abef-a19095bfe259",
    "company_name": "Wazen",
    "assistant_id": "wazen_ai_assistant",
    "welcome_message": "Hello! How can Wazen help you today?",
    "theme_config": {...},
    "rate_limit": 20,
    "max_message_length": 2000
}
```

#### 3. Send Message
**Send a user message and get AI response**

```http
POST /api/widget/session/{session_id}/send/
Content-Type: application/json
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/widget/session/3204a942-41ee-480d-abef-a19095bfe259/send/ \
  -H "Content-Type: application/json" \
  -d '{"content": "اعرض جميع الخدمات"}'
```

**Response:**
```json
{
    "content": "يسعدني أن أعرض عليك خدمات التأمين المتاحة:\n\n1. **تأمين شامل للمركبات** - 1200 ريال\n2. **تأمين ضد الغير للمركبات** - 400 ريال\n\nأي خدمة تود معرفة المزيد عنها؟",
    "timestamp": "2025-01-13T10:30:00Z",
    "message_type": "ai",
    "session_id": "3204a942-41ee-480d-abef-a19095bfe259"
}
```

#### 4. Get Message History
**Retrieve all messages in a session**

```http
GET /api/widget/session/{session_id}/messages/
```

**Example Request:**
```bash
curl http://localhost:8000/api/widget/session/3204a942-41ee-480d-abef-a19095bfe259/messages/
```

**Response:**
```json
{
    "messages": [
        {
            "content": "اعرض جميع الخدمات",
            "message_type": "user",
            "timestamp": "2025-01-13T10:29:45Z"
        },
        {
            "content": "يسعدني أن أعرض عليك خدمات التأمين المتاحة...",
            "message_type": "ai",
            "timestamp": "2025-01-13T10:30:00Z"
        }
    ],
    "total_messages": 2,
    "session_status": "active"
}
```

#### 5. File Upload
**Upload files (images, PDFs, documents)**

```http
POST /api/widget/session/{session_id}/upload/
Content-Type: multipart/form-data
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/widget/session/3204a942-41ee-480d-abef-a19095bfe259/upload/ \
  -F "file=@document.pdf"
```

**Response:**
```json
{
    "file_info": {
        "filename": "document.pdf",
        "size": 1024000,
        "type": "application/pdf"
    },
    "upload_time": "2025-01-13T10:31:00Z",
    "ai_response": {
        "has_response": true,
        "content": "شكراً لك على إرسال الملف. سأقوم بمراجعته...",
        "timestamp": "2025-01-13T10:31:15Z"
    }
}
```

#### 6. Session Management
**Manage session lifecycle**

```http
# Get session status
GET /api/widget/session/{session_id}/status/

# Close session
PUT /api/widget/session/{session_id}/close/

# Clear session messages (start fresh)
POST /api/widget/session/{session_id}/clear/
```

---

## 🔒 Security & Rate Limits

### Automatic Security Features
- ✅ **CORS Protection** - Handles cross-origin requests automatically
- ✅ **Input Validation** - Max 2000 characters per message
- ✅ **File Validation** - Max 10MB, allowed types: images, PDFs, documents
- ✅ **XSS Protection** - Content sanitization
- ✅ **Session Security** - UUID-based session IDs

### Rate Limits
- **Widget Config**: 60 requests/minute per IP
- **Session Create**: 10 requests/minute per IP
- **Message Send**: 20 requests/minute per session
- **File Upload**: 5 requests/minute per session

---

## 🔧 Widget Control Methods

### Control the Widget Programmatically

```javascript
// Open/Close widget
saia('open');           // Open widget
saia('close');          // Close widget
saia('toggle');         // Toggle open/closed state

// Get information
saia('config');         // Get widget configuration
saia('state');          // Get current state
saia('getSession');     // Get session information
saia('getMessages');    // Get message history

// Send messages
saia('sendMessage', 'Hello from JavaScript!');  // Send message
saia('clearMessages');                          // Clear conversation

// Cleanup
saia('destroy');        // Remove widget completely
```

### Widget State Object

```javascript
const state = saia('state');
console.log(state);

// Output:
{
    isLoaded: true,           // Widget loaded successfully
    isLoading: false,         // Currently loading
    isOpen: false,            // Widget is open
    sessionId: "uuid-here",   // Current session ID
    messages: [...],          // Message history
    config: {...}             // Widget configuration
}
```

---

## 📱 Framework Integration Examples

### React Integration

```jsx
import { useEffect } from 'react';

function SAIAWidget() {
    useEffect(() => {
        const script = document.createElement('script');
        script.src = 'http://localhost:8000/static/widget/js/saia-widget-loader.js';
        script.async = true;
        document.head.appendChild(script);

        script.onload = () => {
            window.saia('init', {
                companySlug: 'wazen',
                apiBaseUrl: 'http://localhost:8000',
                position: 'bottom-right',
                onReady: (widget) => {
                    console.log('SAIA Widget ready in React!');
                }
            });
        };

        return () => {
            if (window.saia) {
                window.saia('destroy');
            }
        };
    }, []);

    return null; // Widget renders itself
}

export default SAIAWidget;
```

### Vue.js Integration

```vue
<template>
  <div>
    <!-- Widget will be injected automatically -->
  </div>
</template>

<script>
export default {
  name: 'SAIAWidget',
  mounted() {
    const script = document.createElement('script');
    script.src = 'http://localhost:8000/static/widget/js/saia-widget-loader.js';
    script.async = true;
    document.head.appendChild(script);

    script.onload = () => {
      window.saia('init', {
        companySlug: 'wazen',
        apiBaseUrl: 'http://localhost:8000',
        position: 'bottom-right'
      });
    };
  },
  beforeDestroy() {
    if (window.saia) {
      window.saia('destroy');
    }
  }
};
</script>
```

### WordPress Integration

Add to your theme's `functions.php` file:

```php
<?php
function add_saia_widget() {
    ?>
    <script
        src="http://localhost:8000/static/widget/js/saia-widget-loader.js"
        data-company="wazen"
        data-api-url="http://localhost:8000"
        data-position="bottom-right"
        async>
    </script>
    <?php
}
add_action('wp_footer', 'add_saia_widget');
?>
```

---

## 🚨 Troubleshooting

### Widget Not Loading?

**Check 1: Script Loading**
```javascript
if (typeof saia === 'undefined') {
    console.error('❌ SAIA script not loaded');
} else {
    console.log('✅ SAIA script loaded');
}
```

**Check 2: Widget State**
```javascript
setTimeout(() => {
    const state = saia('state');
    if (state.isLoaded) {
        console.log('✅ Widget loaded successfully');
    } else {
        console.error('❌ Widget failed to load:', state);
    }
}, 5000);
```

### API Connection Issues?

**Test API Directly:**
```bash
# Test config endpoint
curl http://localhost:8000/api/widget/config/wazen/

# Should return 200 OK with company configuration
```

**Check Network in Browser:**
1. Open DevTools → Network tab
2. Reload page with widget
3. Look for failed requests to `/api/widget/` endpoints
4. Check response status codes and error messages

### CORS Errors?

**Ensure exact URL match:**
```javascript
saia('init', {
    companySlug: 'wazen',
    apiBaseUrl: 'http://localhost:8000', // No trailing slash!
});
```

### Messages Not Sending?

**Enable debug mode:**
```javascript
saia('init', {
    companySlug: 'wazen',
    apiBaseUrl: 'http://localhost:8000',
    debug: true, // Enable debug logging
});

// Check console for [SAIA Widget] debug messages
```

---

## 📊 Analytics Integration (Optional)

### Google Analytics 4

```javascript
saia('init', {
    companySlug: 'wazen',
    apiBaseUrl: 'http://localhost:8000',

    onReady: (widget) => {
        gtag('event', 'widget_loaded', {
            company: 'wazen'
        });
    },

    onOpen: (widget) => {
        gtag('event', 'widget_opened', {
            company: 'wazen'
        });
    },

    onMessage: (message, widget) => {
        gtag('event', 'widget_message', {
            company: 'wazen',
            message_type: message.is_ai ? 'ai_response' : 'user_message'
        });
    }
});
```

---

## 🎯 Production Deployment

### Update URLs for Production

```javascript
// Replace localhost with your production domain
saia('init', {
    companySlug: 'wazen',
    apiBaseUrl: 'https://your-production-domain.com', // Update this
    debug: false, // Disable debug in production
});
```

### Performance Optimization

```html
<!-- Preload widget assets for faster loading -->
<link rel="preload" href="https://your-domain.com/static/widget/js/saia-widget-loader.js" as="script">

<!-- Load widget with high priority -->
<script
    src="https://your-domain.com/static/widget/js/saia-widget-loader.js"
    data-company="wazen"
    data-api-url="https://your-domain.com"
    async
    fetchpriority="high">
</script>
```

---

## ✅ Final Checklist

Before going live, verify:

- [ ] **Widget loads** without console errors
- [ ] **API connectivity** working (test with demo page)
- [ ] **Messages send/receive** successfully
- [ ] **Styling matches** your website design
- [ ] **Mobile responsive** on all devices
- [ ] **Production URLs** updated (no localhost)
- [ ] **Debug mode** disabled
- [ ] **Analytics tracking** configured (optional)
- [ ] **Error handling** tested

---

## 🎉 You're Done!

Your SAIA chatbot widget is now integrated and ready to provide AI-powered customer support to your website visitors.

**🌐 Test Your Integration**: http://localhost:8000/api/widget/demo/wazen/

**📞 Need Help?** Check the demo page for live examples and API status monitoring.
