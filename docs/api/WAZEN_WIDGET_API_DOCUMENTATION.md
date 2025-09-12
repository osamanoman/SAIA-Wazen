# Wazen Widget API Documentation

## Overview

The SAIA Chatbot Widget API provides a comprehensive set of endpoints for integrating the Wazen AI assistant into external websites. This API enables anonymous visitor sessions, real-time messaging, file uploads, and seamless handover to human agents.

**Base URL**: `https://your-domain.com/api/widget/`

## Authentication

The Widget API is designed for public access and does not require authentication. Security is maintained through:
- Rate limiting per IP address
- CORS validation
- Input validation and sanitization
- Session-based access control

## API Endpoints

### 1. Widget Configuration

#### GET `/config/{company_slug}/`

Get widget configuration for a company.

**Parameters:**
- `company_slug` (string): Company identifier (e.g., "wazen")

**Response:**
```json
{
  "company_name": "Wazen",
  "assistant_id": "wazen_ai_assistant",
  "welcome_message": "مرحباً! أنا مساعدك الذكي لشركة وازن. كيف يمكنني مساعدتك؟",
  "theme_config": {
    "primary_color": "#1e40af",
    "header_text": "Wazen Support",
    "position": "bottom-right"
  },
  "position": "bottom-right",
  "is_active": true
}
```

### 2. Session Management

#### POST `/session/create/{company_slug}/`

Create a new chat session for a website visitor.

**Parameters:**
- `company_slug` (string): Company identifier

**Request Body:**
```json
{
  "visitor_ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "referrer_url": "https://example.com/page",
  "visitor_metadata": {}
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "company_name": "Wazen",
  "assistant_id": "wazen_ai_assistant",
  "welcome_message": "مرحباً! كيف يمكنني مساعدتك؟",
  "theme_config": {...}
}
```

#### GET `/session/{session_id}/status/`

Get session status and information.

**Response:**
```json
{
  "session_id": "uuid-string",
  "status": "active",
  "is_active": true,
  "is_expired": false,
  "created_at": "2025-01-12T10:00:00Z",
  "last_activity": "2025-01-12T10:30:00Z",
  "message_count": 5,
  "duration_minutes": 30,
  "company_name": "Wazen"
}
```

#### GET `/session/{session_id}/messages/`

Get all messages in a chat session with pagination.

**Query Parameters:**
- `limit` (int, optional): Maximum messages to return (default: 50, max: 100)
- `offset` (int, optional): Number of messages to skip (default: 0)

**Response:**
```json
{
  "session_id": "uuid-string",
  "messages": [
    {
      "id": "message-uuid",
      "content": "Hello, how can I help you?",
      "message_type": "ai",
      "timestamp": "2025-01-12T10:00:00Z",
      "is_ai": true
    }
  ],
  "total_messages": 10,
  "returned_messages": 5,
  "session_status": "active",
  "pagination": {
    "limit": 50,
    "offset": 0,
    "has_more": false
  }
}
```

#### POST `/session/{session_id}/send/`

Send a message in a chat session.

**Request Body:**
```json
{
  "content": "I need help with insurance"
}
```

**Response:**
```json
{
  "id": "message-uuid",
  "content": "I'd be happy to help you with insurance! What type of insurance are you looking for?",
  "message_type": "ai",
  "timestamp": "2025-01-12T10:00:00Z",
  "is_ai": true
}
```

#### PUT `/session/{session_id}/close/`

Close a chat session.

**Request Body (optional):**
```json
{
  "reason": "user_closed"
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "status": "closed",
  "closed_at": "2025-01-12T10:30:00Z",
  "message": "Session closed successfully"
}
```

### 3. File Upload

#### POST `/session/{session_id}/upload/`

Upload a file (image) to a chat session.

**Request:** Multipart form data with `file` field

**File Restrictions:**
- Maximum size: 5MB
- Allowed types: JPEG, PNG, GIF, WebP
- Images only

**Response:**
```json
{
  "status": "success",
  "message": "File uploaded successfully",
  "file_info": {
    "filename": "image.jpg",
    "size": 1024000,
    "type": "image/jpeg",
    "url": "/media/widget_uploads/..."
  },
  "upload_time": "2025-01-12T10:00:00Z",
  "ai_response": {
    "content": "تم رفع الصورة بنجاح!",
    "timestamp": "2025-01-12T10:00:01Z",
    "has_response": true
  }
}
```

### 4. Session Utilities

#### POST `/session/{session_id}/clear/`

Clear/reset a chat session and create a fresh one.

**Response:**
```json
{
  "status": "success",
  "message": "Session cleared successfully",
  "new_session": {
    "session_id": "new-uuid-string",
    "thread_id": 123
  },
  "cleared_at": "2025-01-12T10:30:00Z"
}
```

#### POST `/session/{session_id}/handover/`

Request handover to human agent.

**Request Body:**
```json
{
  "reason": "Complex technical issue",
  "priority": "high"
}
```

**Response:**
```json
{
  "handover_id": "handover-uuid",
  "session_id": "session-uuid",
  "status": "pending",
  "priority": "high",
  "requested_at": "2025-01-12T10:30:00Z",
  "message": "Handover request created successfully"
}
```

### 5. Integration Endpoints

#### GET `/embed/{company_slug}/`

Generate widget embed HTML for a specific company.

**Query Parameters:**
- `position` (string): Widget position (default: "bottom-right")
- `auto_open` (boolean): Auto-open widget (default: false)
- `theme` (string): Widget theme (default: "default")
- `debug` (boolean): Enable debug mode (default: false)

**Response:** HTML content for embedding

#### GET `/integration/{company_slug}/`

Get integration code snippets for different methods.

**Response:**
```json
{
  "company": "Wazen",
  "integration_methods": {
    "simple_script_tag": "<script src=\"...\" data-company=\"wazen\"></script>",
    "advanced_javascript": "...",
    "iframe_embed": "...",
    "react_component": "...",
    "wordpress_plugin": "..."
  },
  "urls": {
    "api_base": "https://your-domain.com",
    "loader_script": "https://your-domain.com/static/widget/js/saia-widget-loader.js",
    "embed_page": "https://your-domain.com/widget/embed/wazen/"
  }
}
```

#### GET `/demo/{company_slug}/`

Serve the widget demo page.

**Response:** HTML demo page with working widget

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error type",
  "message": "Human-readable error message"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (session/company not found)
- `403` - Forbidden (widget not active)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

## Rate Limiting

The API implements rate limiting per IP address:
- Widget config: 60 requests per minute
- Session creation: 10 requests per minute
- Message sending: 30 requests per minute
- File upload: 5 requests per minute

## CORS Configuration

The API supports cross-origin requests with proper CORS headers. Allowed origins are configurable per company.

## Integration Examples

### Simple Script Tag
```html
<script 
    src="https://your-domain.com/static/widget/js/saia-widget-loader.js"
    data-company="wazen"
    data-api-url="https://your-domain.com"
    data-position="bottom-right"
    async>
</script>
```

### Advanced JavaScript
```javascript
saia('init', {
    companySlug: 'wazen',
    apiBaseUrl: 'https://your-domain.com',
    position: 'bottom-right',
    autoOpen: false,
    onReady: function(widget) {
        console.log('Widget ready!');
    }
});
```

## Security Considerations

1. **Input Validation**: All inputs are validated and sanitized
2. **Rate Limiting**: Prevents abuse and ensures fair usage
3. **File Upload Security**: Strict file type and size validation
4. **Session Management**: Secure session handling with expiration
5. **CORS Protection**: Configurable origin restrictions
6. **Data Isolation**: Company-specific data separation

## Support

For technical support and integration assistance, contact the SAIA development team.
