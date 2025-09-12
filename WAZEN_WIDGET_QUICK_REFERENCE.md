# 🚀 SAIA Wazen Widget - Quick Reference

## ⚡ 30-Second Integration

```html
<script src="http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js" 
        data-company="wazen" 
        data-position="bottom-right">
</script>
```

## 📋 Configuration Cheat Sheet

### Essential Attributes
```html
data-company="wazen"                    <!-- Required: Company identifier -->
data-position="bottom-right"            <!-- Widget position -->
data-theme="wazen-blue"                 <!-- Color theme -->
```

### Text Customization
```html
data-title="مساعد وازن الذكي"           <!-- Widget title -->
data-greeting="أهلاً بك في وازن!"       <!-- Welcome message -->
data-placeholder="اكتب رسالتك..."       <!-- Input placeholder -->
```

### Behavior Options
```html
data-auto-open="false"                  <!-- Auto-open on load -->
data-show-launcher="true"               <!-- Show chat button -->
data-session-timeout="30"               <!-- Timeout in minutes -->
```

## 🎨 Available Themes

| Theme | Description | Use Case |
|-------|-------------|----------|
| `default` | Standard blue | General use |
| `wazen-blue` | Wazen brand blue | Official branding |
| `wazen-green` | Wazen brand green | Alternative branding |
| `minimal` | Clean minimal | Modern websites |

## 📱 Positions

| Position | Description |
|----------|-------------|
| `bottom-right` | Bottom right corner (default) |
| `bottom-left` | Bottom left corner |
| `top-right` | Top right corner |
| `top-left` | Top left corner |

## 🔧 JavaScript API

### Initialize Widget
```javascript
const widget = new SAIAWidget({
    company: 'wazen',
    apiBaseUrl: 'http://127.0.0.1:8000',
    position: 'bottom-right',
    theme: 'wazen-blue'
});
```

### Control Widget
```javascript
widget.show();          // Show widget
widget.hide();          // Hide widget
widget.toggle();        // Toggle visibility
widget.open();          // Open chat window
widget.close();         // Close chat window
widget.destroy();       // Remove widget
```

### Event Listeners
```javascript
window.addEventListener('saia-widget-ready', () => {
    console.log('Widget loaded');
});

window.addEventListener('saia-widget-message-sent', (e) => {
    console.log('User sent:', e.detail.message);
});

window.addEventListener('saia-widget-message-received', (e) => {
    console.log('AI replied:', e.detail.message);
});
```

## 🎯 Common Use Cases

### WordPress
```php
// Add to functions.php
function add_saia_widget() {
    echo '<script src="http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js" data-company="wazen"></script>';
}
add_action('wp_footer', 'add_saia_widget');
```

### React
```jsx
useEffect(() => {
    const script = document.createElement('script');
    script.src = 'http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js';
    script.setAttribute('data-company', 'wazen');
    document.body.appendChild(script);
    return () => document.body.removeChild(script);
}, []);
```

### Vue.js
```javascript
mounted() {
    const script = document.createElement('script');
    script.src = 'http://127.0.0.1:8000/static/widget/js/saia-widget-loader.js';
    script.setAttribute('data-company', 'wazen');
    document.body.appendChild(script);
}
```

## 🔍 Testing Checklist

- [ ] Widget appears on page load
- [ ] Chat button is clickable
- [ ] Chat window opens/closes
- [ ] Arabic text displays correctly
- [ ] Test message: "السلام عليكم"
- [ ] Service request: "أريد طلب خدمة التأمين الشامل"
- [ ] Mobile responsive
- [ ] No console errors

## 🚨 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Widget not showing | Check script URL and data-company attribute |
| Arabic text broken | Add `<meta charset="UTF-8">` to HTML head |
| Console errors | Check browser network tab for failed requests |
| Not responsive | Ensure viewport meta tag is present |

## 📊 Analytics Tracking

```javascript
// Google Analytics
window.addEventListener('saia-widget-opened', () => {
    gtag('event', 'widget_opened', {
        'event_category': 'engagement'
    });
});

// Facebook Pixel
window.addEventListener('saia-widget-message-sent', () => {
    fbq('track', 'Lead');
});
```

## 🎨 Quick Styling

```css
.saia-widget {
    --primary-color: #1e40af;
    --secondary-color: #10b981;
    --border-radius: 12px;
}
```

## 🔗 API Endpoints (Auto-handled)

- `GET /api/widget/config/wazen/` - Widget config
- `POST /api/widget/session/create/wazen/` - Create session
- `POST /api/widget/session/{id}/send/` - Send message
- `GET /api/widget/session/{id}/messages/` - Get messages

## ✅ Browser Support

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+
- ✅ Mobile browsers

## 🔒 Security Features

- ✅ CORS protection
- ✅ Rate limiting
- ✅ XSS prevention
- ✅ Input sanitization
- ✅ Session encryption

---

**Need more details? Check the full documentation: `WAZEN_WIDGET_API_DOCUMENTATION.md`**
