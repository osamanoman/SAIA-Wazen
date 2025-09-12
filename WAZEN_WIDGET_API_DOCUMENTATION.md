# 🤖 SAIA Wazen AI Assistant Widget - Integration Guide

## 📋 Overview

The SAIA Wazen AI Assistant Widget is a powerful, embeddable chatbot that provides intelligent customer support in Arabic (Saudi dialect) for Wazen's insurance services. This guide will help you integrate the widget into your website quickly and easily.

## 🚀 Quick Start (30 seconds)

### Method 1: Simple Script Tag (Recommended)

Add this single line to your website's HTML:

```html
<script src="http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js" 
        data-company="wazen" 
        data-position="bottom-right">
</script>
```

**That's it!** The widget will automatically appear on your website.

---

## 🛠️ Integration Methods

### Method 1: Script Tag Integration (Easiest)

**Step 1:** Add the script tag to your HTML (before closing `</body>` tag):

```html
<script src="http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js" 
        data-company="wazen" 
        data-position="bottom-right"
        data-theme="default">
</script>
```

**Step 2:** Customize with data attributes:

```html
<script src="http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js" 
        data-company="wazen"
        data-position="bottom-right"
        data-theme="wazen-blue"
        data-greeting="أهلاً بك في وازن! كيف يمكنني مساعدتك؟"
        data-placeholder="اكتب رسالتك هنا..."
        data-title="مساعد وازن الذكي">
</script>
```

### Method 2: JavaScript API (Advanced)

**Step 1:** Load the widget script:

```html
<script src="http://127.0.0.1:8000/static/widget/js/saia-widget.js"></script>
```

**Step 2:** Initialize the widget:

```javascript
// Initialize widget
const widget = new SAIAWidget({
    company: 'wazen',
    apiBaseUrl: 'http://127.0.0.1:8000',
    position: 'bottom-right',
    theme: 'wazen-blue',
    greeting: 'أهلاً بك في وازن! كيف يمكنني مساعدتك؟',
    placeholder: 'اكتب رسالتك هنا...',
    title: 'مساعد وازن الذكي'
});

// Show widget
widget.show();
```

### Method 3: React Integration

```jsx
import { useEffect } from 'react';

function App() {
    useEffect(() => {
        // Load widget script
        const script = document.createElement('script');
        script.src = 'http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js';
        script.setAttribute('data-company', 'wazen');
        script.setAttribute('data-position', 'bottom-right');
        document.body.appendChild(script);

        return () => {
            document.body.removeChild(script);
        };
    }, []);

    return (
        <div className="App">
            {/* Your app content */}
        </div>
    );
}
```

---

## ⚙️ Configuration Options

### Widget Positioning

```html
data-position="bottom-right"    <!-- Default: Bottom right corner -->
data-position="bottom-left"     <!-- Bottom left corner -->
data-position="top-right"       <!-- Top right corner -->
data-position="top-left"        <!-- Top left corner -->
```

### Themes

```html
data-theme="default"            <!-- Default blue theme -->
data-theme="wazen-blue"         <!-- Wazen brand blue -->
data-theme="wazen-green"        <!-- Wazen brand green -->
data-theme="minimal"            <!-- Clean minimal theme -->
```

### Text Customization

```html
data-title="مساعد وازن الذكي"                    <!-- Widget title -->
data-greeting="أهلاً بك في وازن!"                <!-- Welcome message -->
data-placeholder="اكتب رسالتك هنا..."            <!-- Input placeholder -->
data-offline-message="نحن غير متاحين حالياً"     <!-- Offline message -->
```

### Behavior Options

```html
data-auto-open="true"           <!-- Auto-open widget on page load -->
data-show-launcher="true"       <!-- Show/hide launcher button -->
data-enable-sound="false"       <!-- Enable/disable notification sounds -->
data-session-timeout="30"       <!-- Session timeout in minutes -->
```

---

## 🔧 Advanced Configuration

### Custom Styling

```html
<script src="http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js" 
        data-company="wazen"
        data-custom-css="https://yoursite.com/custom-widget.css">
</script>
```

### Event Handling

```javascript
// Listen to widget events
window.addEventListener('saia-widget-ready', function() {
    console.log('Widget is ready');
});

window.addEventListener('saia-widget-message-sent', function(event) {
    console.log('Message sent:', event.detail.message);
});

window.addEventListener('saia-widget-message-received', function(event) {
    console.log('Message received:', event.detail.message);
});
```

---

## 📱 Mobile Responsiveness

The widget is fully responsive and works perfectly on:
- ✅ Desktop computers
- ✅ Tablets
- ✅ Mobile phones
- ✅ All modern browsers

---

## 🔒 Security & Privacy

- ✅ **HTTPS Ready**: Works with SSL certificates
- ✅ **CORS Configured**: Secure cross-origin requests
- ✅ **Rate Limited**: Prevents abuse
- ✅ **Input Sanitized**: XSS protection
- ✅ **Session Secure**: Encrypted session management

---

## 🧪 Testing Your Integration

### Step 1: Basic Test

1. Add the widget to your website
2. Refresh the page
3. Look for the chat icon in the bottom-right corner
4. Click it and type: "السلام عليكم"
5. You should get a response in Arabic

### Step 2: Service Test

1. Type: "أريد طلب خدمة التأمين الشامل"
2. The AI should start collecting your information
3. Follow the prompts to test the full flow

### Step 3: Mobile Test

1. Open your website on mobile
2. Verify the widget appears and works correctly
3. Test typing and scrolling

---

## 🚨 Troubleshooting

### Widget Not Appearing?

1. **Check Console**: Open browser dev tools, look for errors
2. **Check URL**: Ensure the script URL is correct
3. **Check Company**: Verify `data-company="wazen"` is correct

### Widget Not Responding?

1. **Check Network**: Ensure API endpoints are reachable
2. **Check CORS**: Verify your domain is allowed
3. **Check Rate Limits**: You might be sending too many requests

### Arabic Text Issues?

1. **Check Encoding**: Ensure your page uses UTF-8 encoding:
   ```html
   <meta charset="UTF-8">
   ```
2. **Check Font**: Ensure Arabic fonts are available

---

## 📞 Support

If you need help integrating the widget:

- **Technical Issues**: Check the browser console for error messages
- **Integration Help**: Follow this documentation step by step
- **Custom Requirements**: Contact the development team

---

## 🎯 What the Widget Provides

### ✅ Features
- **Arabic Support**: Full Saudi dialect conversation
- **Service Ordering**: Complete insurance service ordering flow
- **Smart Responses**: Context-aware AI responses
- **Session Persistence**: Conversations persist across page reloads
- **Mobile Optimized**: Perfect mobile experience
- **Customizable**: Themes, colors, and text customization

### ✅ AI Capabilities
- **Greetings**: Responds to Arabic greetings warmly
- **Service Information**: Provides detailed service information
- **Order Processing**: Guides users through service ordering
- **Data Collection**: Collects customer information step by step
- **Validation**: Validates user input with helpful Arabic error messages

---

## 🔗 API Endpoints Reference

The widget uses these endpoints (handled automatically):

- `GET /api/widget/config/wazen/` - Widget configuration
- `POST /api/widget/session/create/wazen/` - Create chat session
- `POST /api/widget/session/{id}/send/` - Send message
- `GET /api/widget/session/{id}/messages/` - Get messages
- `PUT /api/widget/session/{id}/close/` - Close session

**Note**: You don't need to call these directly - the widget handles everything!

---

---

## 💻 Complete Implementation Examples

### Example 1: Basic HTML Website

```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>موقع وازن للتأمين</title>
</head>
<body>
    <h1>مرحباً بكم في وازن</h1>
    <p>نحن نقدم أفضل خدمات التأمين في المملكة</p>

    <!-- SAIA Widget Integration -->
    <script src="http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js"
            data-company="wazen"
            data-position="bottom-right"
            data-theme="wazen-blue"
            data-title="مساعد وازن الذكي"
            data-greeting="أهلاً وسهلاً بك في وازن! كيف يمكنني مساعدتك اليوم؟">
    </script>
</body>
</html>
```

### Example 2: WordPress Integration

**Step 1:** Add to your theme's `functions.php`:

```php
function add_saia_widget() {
    ?>
    <script src="http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js"
            data-company="wazen"
            data-position="bottom-right"
            data-theme="wazen-blue">
    </script>
    <?php
}
add_action('wp_footer', 'add_saia_widget');
```

**Step 2:** Or add directly to your theme's `footer.php` before `</body>`:

```html
<script src="http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js"
        data-company="wazen"
        data-position="bottom-right">
</script>
```

### Example 3: Next.js Integration

```jsx
// components/SAIAWidget.js
import { useEffect } from 'react';

export default function SAIAWidget() {
    useEffect(() => {
        const script = document.createElement('script');
        script.src = 'http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js';
        script.setAttribute('data-company', 'wazen');
        script.setAttribute('data-position', 'bottom-right');
        script.setAttribute('data-theme', 'wazen-blue');
        script.async = true;

        document.body.appendChild(script);

        return () => {
            if (document.body.contains(script)) {
                document.body.removeChild(script);
            }
        };
    }, []);

    return null;
}

// pages/_app.js
import SAIAWidget from '../components/SAIAWidget';

function MyApp({ Component, pageProps }) {
    return (
        <>
            <Component {...pageProps} />
            <SAIAWidget />
        </>
    );
}

export default MyApp;
```

### Example 4: Vue.js Integration

```vue
<!-- components/SAIAWidget.vue -->
<template>
    <div></div>
</template>

<script>
export default {
    name: 'SAIAWidget',
    mounted() {
        this.loadWidget();
    },
    beforeDestroy() {
        this.removeWidget();
    },
    methods: {
        loadWidget() {
            const script = document.createElement('script');
            script.src = 'http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js';
            script.setAttribute('data-company', 'wazen');
            script.setAttribute('data-position', 'bottom-right');
            script.id = 'saia-widget-script';
            document.body.appendChild(script);
        },
        removeWidget() {
            const script = document.getElementById('saia-widget-script');
            if (script) {
                document.body.removeChild(script);
            }
        }
    }
};
</script>
```

---

## 🎨 Custom Styling Guide

### Override Widget Colors

```css
/* Add to your website's CSS */
.saia-widget {
    --primary-color: #1e40af;      /* Wazen blue */
    --secondary-color: #10b981;    /* Wazen green */
    --text-color: #1f2937;         /* Dark text */
    --background-color: #ffffff;   /* White background */
    --border-radius: 12px;         /* Rounded corners */
}

.saia-widget-launcher {
    background: linear-gradient(135deg, #1e40af, #10b981) !important;
    box-shadow: 0 4px 20px rgba(30, 64, 175, 0.3) !important;
}

.saia-widget-header {
    background: linear-gradient(135deg, #1e40af, #10b981) !important;
}
```

### Custom Animations

```css
.saia-widget-launcher {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
```

---

## 📊 Analytics & Tracking

### Track Widget Usage

```javascript
// Track when widget opens
window.addEventListener('saia-widget-opened', function() {
    // Google Analytics
    gtag('event', 'widget_opened', {
        'event_category': 'engagement',
        'event_label': 'saia_widget'
    });

    // Facebook Pixel
    fbq('track', 'Lead');
});

// Track when user sends message
window.addEventListener('saia-widget-message-sent', function(event) {
    gtag('event', 'widget_message_sent', {
        'event_category': 'engagement',
        'event_label': 'user_interaction'
    });
});

// Track service requests
window.addEventListener('saia-widget-service-requested', function(event) {
    gtag('event', 'service_requested', {
        'event_category': 'conversion',
        'event_label': event.detail.service
    });
});
```

---

## 🔧 Advanced Customization

### Conditional Loading

```javascript
// Only load widget on specific pages
if (window.location.pathname.includes('/insurance') ||
    window.location.pathname.includes('/services')) {

    const script = document.createElement('script');
    script.src = 'http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js';
    script.setAttribute('data-company', 'wazen');
    document.body.appendChild(script);
}
```

### Time-based Display

```javascript
// Show widget only during business hours
const now = new Date();
const hour = now.getHours();
const isBusinessHours = hour >= 8 && hour <= 18;

if (isBusinessHours) {
    // Load widget
    const script = document.createElement('script');
    script.src = 'http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js';
    script.setAttribute('data-company', 'wazen');
    document.body.appendChild(script);
} else {
    // Show offline message
    console.log('Widget offline - outside business hours');
}
```

### User Segmentation

```javascript
// Different widget behavior for different users
const userType = getUserType(); // Your function to determine user type

const widgetConfig = {
    'new_visitor': {
        greeting: 'مرحباً بك في وازن! هل تحتاج مساعدة في اختيار التأمين المناسب؟',
        theme: 'wazen-blue'
    },
    'returning_customer': {
        greeting: 'أهلاً بك مرة أخرى! كيف يمكنني مساعدتك اليوم؟',
        theme: 'wazen-green'
    },
    'premium_customer': {
        greeting: 'أهلاً بعميلنا المميز! نحن هنا لخدمتك',
        theme: 'premium-gold'
    }
};

const config = widgetConfig[userType] || widgetConfig['new_visitor'];

const script = document.createElement('script');
script.src = 'http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js';
script.setAttribute('data-company', 'wazen');
script.setAttribute('data-greeting', config.greeting);
script.setAttribute('data-theme', config.theme);
document.body.appendChild(script);
```

---

## 🚀 Performance Optimization

### Lazy Loading

```javascript
// Load widget only when user scrolls or after delay
let widgetLoaded = false;

function loadWidget() {
    if (widgetLoaded) return;

    const script = document.createElement('script');
    script.src = 'http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js';
    script.setAttribute('data-company', 'wazen');
    document.body.appendChild(script);

    widgetLoaded = true;
}

// Load after 3 seconds
setTimeout(loadWidget, 3000);

// Or load on scroll
window.addEventListener('scroll', function() {
    if (window.scrollY > 500) {
        loadWidget();
    }
}, { once: true });
```

### Preload Resources

```html
<!-- Add to <head> for faster loading -->
<link rel="preload" href="http://127.0.0.1:8000/static/widget/js/saia-widget.js" as="script">
<link rel="preload" href="http://127.0.0.1:8000/static/widget/css/saia-widget.css" as="style">
```

---

**🚀 Ready to integrate? Start with the Quick Start section above!**

## 📞 Need Help?

- **Quick Issues**: Check the Troubleshooting section
- **Custom Integration**: Follow the Advanced Customization examples
- **Performance**: Use the Performance Optimization techniques
- **Styling**: Refer to the Custom Styling Guide

**The widget is designed to work out-of-the-box with minimal setup. Most websites only need the simple script tag!**
