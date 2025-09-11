/**
 * SAIA Multi-Tenant Website Chatbot Widget
 * 
 * A comprehensive, embeddable chatbot widget that integrates with the SAIA platform
 * to provide AI-powered customer support for any website.
 * 
 * Features:
 * - Multi-tenant support with company-specific AI assistants
 * - Responsive design with customizable themes
 * - Real-time messaging with typing indicators
 * - Session management and message history
 * - Cross-browser compatibility
 * - Easy integration with minimal configuration
 * 
 * @version 1.0.0
 * @author SAIA Team
 */

class SAIAWidget {
    constructor(options = {}) {
        // Configuration with defaults
        this.config = {
            // Required: Company identifier
            companySlug: options.companySlug || null,
            
            // API Configuration
            apiBaseUrl: options.apiBaseUrl || window.location.origin,
            
            // Widget Positioning
            position: options.position || 'bottom-right', // bottom-right, bottom-left, top-right, top-left
            
            // Widget Behavior
            autoOpen: options.autoOpen || false,
            showWelcomeMessage: options.showWelcomeMessage !== false,
            enableSound: options.enableSound !== false,
            
            // Styling
            theme: options.theme || 'default',
            customCSS: options.customCSS || null,
            
            // Advanced Options
            debug: options.debug || false,
            maxMessages: options.maxMessages || 100,
            sessionTimeout: options.sessionTimeout || 30 * 60 * 1000, // 30 minutes
            
            // Callbacks
            onReady: options.onReady || null,
            onOpen: options.onOpen || null,
            onClose: options.onClose || null,
            onMessage: options.onMessage || null,
            onError: options.onError || null
        };

        // Validate required configuration
        if (!this.config.companySlug) {
            throw new Error('SAIA Widget: companySlug is required');
        }

        // Internal state
        this.state = {
            isInitialized: false,
            isOpen: false,
            isLoading: false,
            isConnected: false,
            sessionId: this.getStoredSessionId(), // Load existing session from storage
            messages: [],
            companyConfig: null,
            lastActivity: Date.now()
        };

        // DOM elements
        this.elements = {
            container: null,
            widget: null,
            header: null,
            messages: null,
            input: null,
            sendButton: null,
            toggleButton: null
        };

        // Initialize widget when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    /**
     * Get stored session ID from localStorage
     */
    getStoredSessionId() {
        try {
            const storageKey = `saia_widget_session_${this.config.companySlug}`;
            console.log('[SAIA Widget Debug] Looking for stored session with key:', storageKey);
            const storedData = localStorage.getItem(storageKey);
            console.log('[SAIA Widget Debug] Stored data found:', storedData);

            if (storedData) {
                const sessionData = JSON.parse(storedData);
                console.log('[SAIA Widget Debug] Parsed session data:', sessionData);

                // Check if session is still valid (not expired)
                const now = Date.now();
                const sessionAge = now - sessionData.timestamp;
                const maxAge = 24 * 60 * 60 * 1000; // 24 hours

                console.log('[SAIA Widget Debug] Session age:', sessionAge, 'ms, Max age:', maxAge, 'ms');

                if (sessionAge < maxAge) {
                    console.log('[SAIA Widget Debug] ✅ Restored session from storage:', sessionData.sessionId);
                    this.log('Restored session from storage:', sessionData.sessionId);
                    return sessionData.sessionId;
                } else {
                    console.log('[SAIA Widget Debug] ❌ Stored session expired, removing...');
                    this.log('Stored session expired, removing...');
                    localStorage.removeItem(storageKey);
                }
            } else {
                console.log('[SAIA Widget Debug] No stored session found');
            }
        } catch (error) {
            console.log('[SAIA Widget Debug] Error loading stored session:', error);
            this.log('Error loading stored session:', error);
        }
        return null;
    }

    /**
     * Store session ID in localStorage
     */
    storeSessionId(sessionId) {
        try {
            const storageKey = `saia_widget_session_${this.config.companySlug}`;
            const sessionData = {
                sessionId: sessionId,
                timestamp: Date.now()
            };
            console.log('[SAIA Widget Debug] 💾 Storing session with key:', storageKey, 'data:', sessionData);
            localStorage.setItem(storageKey, JSON.stringify(sessionData));
            console.log('[SAIA Widget Debug] ✅ Session stored successfully');
            this.log('Session stored in localStorage:', sessionId);
        } catch (error) {
            console.log('[SAIA Widget Debug] ❌ Error storing session:', error);
            this.log('Error storing session:', error);
        }
    }

    /**
     * Remove stored session ID from localStorage
     */
    removeStoredSession() {
        try {
            const storageKey = `saia_widget_session_${this.config.companySlug}`;
            localStorage.removeItem(storageKey);
            this.log('Session removed from localStorage');
        } catch (error) {
            this.log('Error removing stored session:', error);
        }
    }

    /**
     * Load existing messages for a restored session
     */
    async loadExistingMessages() {
        if (!this.state.sessionId) {
            console.log('[SAIA Widget Debug] ❌ No session ID to load messages for');
            return;
        }

        try {
            console.log('[SAIA Widget Debug] 📜 Loading existing messages for session:', this.state.sessionId);
            this.log('Loading existing messages for session:', this.state.sessionId);

            const response = await fetch(`${this.config.apiBaseUrl}/api/widget/session/${this.state.sessionId}/messages/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            console.log('[SAIA Widget Debug] Messages API response status:', response.status);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('[SAIA Widget Debug] Messages API response data:', data);

            // Clear existing messages and load from server
            this.state.messages = [];

            if (data.messages && data.messages.length > 0) {
                console.log('[SAIA Widget Debug] ✅ Loading', data.messages.length, 'existing messages');
                data.messages.forEach(message => {
                    console.log('[SAIA Widget Debug] Adding message:', message.message_type, message.content.substring(0, 50) + '...');

                    // Convert API message format to widget message format
                    const widgetMessage = {
                        content: message.content,
                        is_ai: message.message_type === 'ai',
                        timestamp: message.timestamp || new Date().toISOString()
                    };

                    this.addMessage(widgetMessage);

                    // Also add to state messages array
                    this.state.messages.push(widgetMessage);
                });
                this.log(`Loaded ${data.messages.length} existing messages`);
            } else {
                console.log('[SAIA Widget Debug] ℹ️ No existing messages found');
                this.log('No existing messages found');
            }

        } catch (error) {
            console.log('[SAIA Widget Debug] ❌ Error loading existing messages:', error);
            this.log('Error loading existing messages:', error);
            // If we can't load messages, the session might be invalid
            // Clear it and create a new one
            this.removeStoredSession();
            this.state.sessionId = null;
            await this.createSession();
        }
    }

    /**
     * Initialize the widget
     */
    async init() {
        try {
            this.log('Initializing SAIA Widget...');
            
            // Load company configuration
            await this.loadCompanyConfig();
            
            // Create widget DOM structure
            this.createWidgetDOM();
            
            // Apply theme and styling
            this.applyTheme();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Auto-open if configured
            if (this.config.autoOpen) {
                await this.open();
            }

            this.state.isInitialized = true;
            this.log('Widget initialized successfully');
            
            // Call ready callback
            if (this.config.onReady) {
                this.config.onReady(this);
            }
            
        } catch (error) {
            this.handleError('Failed to initialize widget', error);
        }
    }

    /**
     * Load company configuration from API
     */
    async loadCompanyConfig() {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/api/widget/config/${this.config.companySlug}/`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.state.companyConfig = await response.json();
            this.log('Company configuration loaded:', this.state.companyConfig);
            
        } catch (error) {
            throw new Error(`Failed to load company configuration: ${error.message}`);
        }
    }

    /**
     * Create the widget DOM structure
     */
    createWidgetDOM() {
        // Create main container
        this.elements.container = document.createElement('div');
        this.elements.container.id = 'saia-widget-container';
        this.elements.container.className = `saia-widget-container ${this.config.position}`;
        
        // Create toggle button
        this.elements.toggleButton = document.createElement('button');
        this.elements.toggleButton.id = 'saia-widget-toggle';
        this.elements.toggleButton.className = 'saia-widget-toggle';
        this.elements.toggleButton.innerHTML = this.getToggleButtonHTML();
        this.elements.toggleButton.setAttribute('aria-label', 'Open chat');
        
        // Create main widget
        this.elements.widget = document.createElement('div');
        this.elements.widget.id = 'saia-widget';
        this.elements.widget.className = 'saia-widget hidden';
        this.elements.widget.innerHTML = this.getWidgetHTML();
        
        // Get references to key elements
        this.elements.header = this.elements.widget.querySelector('.saia-widget-header');
        this.elements.messages = this.elements.widget.querySelector('.saia-widget-messages');
        this.elements.input = this.elements.widget.querySelector('.saia-widget-input');
        this.elements.sendButton = this.elements.widget.querySelector('.saia-widget-send');
        this.elements.attachmentButton = this.elements.widget.querySelector('.saia-widget-attachment');
        this.elements.fileInput = this.elements.widget.querySelector('.saia-widget-file-input');
        
        // Add to container
        this.elements.container.appendChild(this.elements.toggleButton);
        this.elements.container.appendChild(this.elements.widget);
        
        // Add to page
        document.body.appendChild(this.elements.container);
    }

    /**
     * Get toggle button HTML
     */
    getToggleButtonHTML() {
        return `
            <svg class="saia-widget-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <span class="saia-widget-badge" style="display: none;">1</span>
        `;
    }

    /**
     * Get main widget HTML structure
     */
    getWidgetHTML() {
        const companyName = this.state.companyConfig?.company_name || 'Support';
        const welcomeMessage = this.state.companyConfig?.welcome_message || 'Hello! How can we help you today?';
        
        return `
            <div class="saia-widget-header">
                <div class="saia-widget-header-content">
                    <div class="saia-widget-avatar">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                    </div>
                    <div class="saia-widget-header-text">
                        <div class="saia-widget-title">${companyName}</div>
                        <div class="saia-widget-status">Online</div>
                    </div>
                </div>
                <button class="saia-widget-close" aria-label="Close chat">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            
            <div class="saia-widget-messages" role="log" aria-live="polite" aria-label="Chat messages">
                ${this.config.showWelcomeMessage ? `
                    <div class="saia-message saia-message-bot">
                        <div class="saia-message-avatar">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                <circle cx="12" cy="7" r="4"></circle>
                            </svg>
                        </div>
                        <div class="saia-message-content">
                            <div class="saia-message-text">${welcomeMessage}</div>
                            <div class="saia-message-time">${this.formatTime(new Date())}</div>
                        </div>
                    </div>
                ` : ''}
            </div>
            
            <div class="saia-widget-input-container">
                <div class="saia-widget-typing" style="display: none;">
                    <div class="saia-typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <span class="saia-typing-text">AI is typing...</span>
                </div>
                <div class="saia-widget-input-wrapper">
                    <button class="saia-widget-attachment" aria-label="Attach file" title="Attach image">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66L9.64 16.2a2 2 0 0 1-2.83-2.83l8.49-8.49"></path>
                        </svg>
                    </button>
                    <textarea
                        class="saia-widget-input"
                        placeholder="Type your message..."
                        rows="1"
                        aria-label="Type your message"
                    ></textarea>
                    <button class="saia-widget-send" aria-label="Send message" disabled>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22,2 15,22 11,13 2,9 22,2"></polygon>
                        </svg>
                    </button>
                </div>
                <input type="file" class="saia-widget-file-input" accept="image/*" style="display: none;" aria-label="Select image file">
            </div>
        `;
    }

    /**
     * Apply theme and styling
     */
    applyTheme() {
        if (!this.state.companyConfig?.theme_config) return;
        
        const theme = this.state.companyConfig.theme_config;
        const root = document.documentElement;
        
        // Apply CSS custom properties
        root.style.setProperty('--saia-primary-color', theme.primary_color || '#1e40af');
        root.style.setProperty('--saia-secondary-color', theme.secondary_color || '#f3f4f6');
        root.style.setProperty('--saia-text-color', theme.text_color || '#1f2937');
        root.style.setProperty('--saia-header-bg', theme.header_bg || '#1e40af');
        root.style.setProperty('--saia-header-text', theme.header_text || '#ffffff');
        root.style.setProperty('--saia-font-family', theme.font_family || 'system-ui, -apple-system, sans-serif');
        root.style.setProperty('--saia-border-radius', theme.border_radius || '8px');
        root.style.setProperty('--saia-shadow', theme.shadow || '0 4px 6px -1px rgba(0, 0, 0, 0.1)');
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Toggle button click
        this.elements.toggleButton.addEventListener('click', () => {
            this.toggle();
        });
        
        // Close button click
        const closeButton = this.elements.widget.querySelector('.saia-widget-close');
        closeButton.addEventListener('click', () => {
            this.close();
        });
        
        // Input handling
        this.elements.input.addEventListener('input', () => {
            this.handleInputChange();
        });
        
        this.elements.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Send button click
        this.elements.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // Attachment button click
        this.elements.attachmentButton.addEventListener('click', () => {
            this.elements.fileInput.click();
        });

        // File input change
        this.elements.fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Auto-resize textarea
        this.elements.input.addEventListener('input', () => {
            this.autoResizeTextarea();
        });

        // Session timeout handling
        this.setupSessionTimeout();
    }

    /**
     * Handle input changes
     */
    handleInputChange() {
        const hasText = this.elements.input.value.trim().length > 0;
        this.elements.sendButton.disabled = !hasText;
        this.elements.sendButton.classList.toggle('active', hasText);
    }

    /**
     * Auto-resize textarea based on content
     */
    autoResizeTextarea() {
        const textarea = this.elements.input;
        textarea.style.height = 'auto';
        const newHeight = Math.min(textarea.scrollHeight, 120); // Max 120px
        textarea.style.height = newHeight + 'px';
    }

    /**
     * Format time for display
     */
    formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    /**
     * Log debug messages
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[SAIA Widget]', ...args);
        }
    }

    /**
     * Handle errors
     */
    handleError(message, error = null) {
        console.error('[SAIA Widget Error]', message, error);

        if (this.config.onError) {
            this.config.onError(message, error);
        }

        // Show user-friendly error message
        this.showErrorMessage('Something went wrong. Please try again later.');
    }

    /**
     * Toggle widget open/closed
     */
    async toggle() {
        if (this.state.isOpen) {
            this.close();
        } else {
            await this.open();
        }
    }

    /**
     * Open the widget
     */
    async open() {
        if (this.state.isOpen) return;

        try {
            this.log('Opening widget...');

            // Ensure DOM is created
            if (!this.elements.widget) {
                this.log('Widget DOM not found, recreating...');
                this.createWidgetDOM();
                this.applyTheme();
                this.setupEventListeners();
            }

            // Create session if needed
            if (!this.state.sessionId) {
                await this.createSession();
            } else {
                // Load existing messages for restored session
                await this.loadExistingMessages();
            }

            // Show widget (with null checks)
            if (this.elements.widget) {
                this.elements.widget.classList.remove('hidden');
            }
            if (this.elements.toggleButton) {
                this.elements.toggleButton.classList.add('hidden');
            }
            this.state.isOpen = true;

            // Focus input
            setTimeout(() => {
                this.elements.input.focus();
            }, 100);

            // Update activity
            this.updateActivity();

            // Call callback
            if (this.config.onOpen) {
                this.config.onOpen(this);
            }

            this.log('Widget opened');

        } catch (error) {
            this.handleError('Failed to open widget', error);
        }
    }

    /**
     * Close the widget
     */
    close() {
        if (!this.state.isOpen) return;

        this.log('Closing widget...');

        // Hide widget
        this.elements.widget.classList.add('hidden');
        this.elements.toggleButton.classList.remove('hidden');
        this.state.isOpen = false;

        // Call callback
        if (this.config.onClose) {
            this.config.onClose(this);
        }

        this.log('Widget closed');
    }

    /**
     * Create a new chat session
     */
    async createSession() {
        try {
            this.log('Creating new session...');
            this.state.isLoading = true;

            const response = await fetch(`${this.config.apiBaseUrl}/api/widget/session/create/${this.config.companySlug}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    visitor_ip: await this.getClientIP(),
                    user_agent: navigator.userAgent,
                    visitor_metadata: {
                        url: window.location.href,
                        referrer: document.referrer,
                        screen_resolution: `${screen.width}x${screen.height}`,
                        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                        language: navigator.language
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.state.sessionId = data.session_id;
            this.state.isConnected = true;

            // Store session ID for persistence across page refreshes
            this.storeSessionId(this.state.sessionId);

            this.log('Session created:', this.state.sessionId);

        } catch (error) {
            throw new Error(`Failed to create session: ${error.message}`);
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Send a message
     */
    async sendMessage() {
        const content = this.elements.input.value.trim();
        if (!content || this.state.isLoading) return;

        try {
            this.log('Sending message:', content);

            // Add user message to UI
            this.addMessage({
                content: content,
                is_ai: false,
                timestamp: new Date().toISOString()
            });

            // Clear input
            this.elements.input.value = '';
            this.handleInputChange();
            this.autoResizeTextarea();

            // Show typing indicator
            this.showTypingIndicator();

            // Send to API
            const response = await fetch(`${this.config.apiBaseUrl}/api/widget/session/${this.state.sessionId}/send/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            // Hide typing indicator
            this.hideTypingIndicator();

            // Add AI response to UI
            this.addMessage({
                content: this.extractMessageContent(data.content),
                is_ai: true,
                timestamp: data.timestamp
            });

            // Update activity
            this.updateActivity();

            // Call callback
            if (this.config.onMessage) {
                this.config.onMessage(data, this);
            }

        } catch (error) {
            this.hideTypingIndicator();
            this.handleError('Failed to send message', error);
        }
    }

    /**
     * Handle file upload
     */
    async handleFileUpload(file) {
        if (this.state.isLoading) return;

        try {
            // Validate file size (5MB max)
            const maxSize = 5 * 1024 * 1024; // 5MB
            if (file.size > maxSize) {
                this.showError('File too large. Maximum size is 5MB.');
                return;
            }

            // Validate file type (images only)
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                this.showError('Only image files (JPEG, PNG, GIF, WebP) are allowed.');
                return;
            }

            this.log('Uploading file:', file.name);

            // Show upload indicator
            this.addMessage({
                content: `📎 Uploading ${file.name}...`,
                is_ai: false,
                timestamp: new Date().toISOString(),
                isUploading: true
            });

            // Create form data
            const formData = new FormData();
            formData.append('file', file);

            // Upload file
            const response = await fetch(`${this.config.apiBaseUrl}/api/widget/session/${this.state.sessionId}/upload/`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            // Remove upload indicator and add success message
            this.removeUploadingMessage();
            this.addMessage({
                content: `✅ File uploaded successfully: ${file.name}`,
                is_ai: false,
                timestamp: data.upload_time,
                isFileUpload: true,
                fileInfo: data.file_info
            });

            // Update activity
            this.updateActivity();

            // Clear file input
            this.elements.fileInput.value = '';

            // Call callback
            if (this.config.onFileUpload) {
                this.config.onFileUpload(data, this);
            }

        } catch (error) {
            this.removeUploadingMessage();
            this.handleError('Failed to upload file', error);
            // Clear file input
            this.elements.fileInput.value = '';
        }
    }

    /**
     * Remove uploading message
     */
    removeUploadingMessage() {
        const uploadingMessages = this.elements.messages.querySelectorAll('.saia-message[data-uploading="true"]');
        uploadingMessages.forEach(msg => msg.remove());
    }

    /**
     * Show error message
     */
    showError(message) {
        this.addMessage({
            content: `❌ ${message}`,
            is_ai: true,
            timestamp: new Date().toISOString(),
            isError: true
        });
    }

    /**
     * Extract message content from API response
     */
    extractMessageContent(content) {
        if (typeof content === 'string') {
            try {
                const parsed = JSON.parse(content);
                if (parsed.data && parsed.data.content) {
                    return parsed.data.content;
                }
            } catch (e) {
                // If parsing fails, return original content
            }
        }
        return content;
    }

    /**
     * Add a message to the UI
     */
    addMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `saia-message ${message.is_ai ? 'saia-message-bot' : 'saia-message-user'}`;

        // Add special attributes for different message types
        if (message.isUploading) {
            messageElement.setAttribute('data-uploading', 'true');
        }
        if (message.isFileUpload) {
            messageElement.setAttribute('data-file-upload', 'true');
        }
        if (message.isError) {
            messageElement.setAttribute('data-error', 'true');
        }

        const time = new Date(message.timestamp);
        const timeString = this.formatTime(time);

        if (message.is_ai) {
            messageElement.innerHTML = `
                <div class="saia-message-avatar">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                </div>
                <div class="saia-message-content">
                    <div class="saia-message-text">${this.formatMessageText(message.content)}</div>
                    <div class="saia-message-time">${timeString}</div>
                </div>
            `;
        } else {
            messageElement.innerHTML = `
                <div class="saia-message-content">
                    <div class="saia-message-text">${this.formatMessageText(message.content)}</div>
                    <div class="saia-message-time">${timeString}</div>
                </div>
            `;
        }

        // Add message to DOM (with null check)
        if (this.elements.messages) {
            this.elements.messages.appendChild(messageElement);
            this.scrollToBottom();
        } else {
            this.log('Warning: messages container not found, cannot display message');
        }

        // Store message
        this.state.messages.push(message);

        // Limit message history
        if (this.state.messages.length > this.config.maxMessages) {
            this.state.messages.shift();
            const firstMessage = this.elements.messages.firstElementChild;
            if (firstMessage) {
                firstMessage.remove();
            }
        }
    }

    /**
     * Format message text (basic HTML escaping and link detection)
     */
    formatMessageText(text) {
        // Escape HTML
        const escaped = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');

        // Convert line breaks
        const withBreaks = escaped.replace(/\n/g, '<br>');

        // Simple URL detection and linking
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const withLinks = withBreaks.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');

        return withLinks;
    }

    /**
     * Scroll messages to bottom
     */
    scrollToBottom() {
        setTimeout(() => {
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
        }, 100);
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        const typingElement = this.elements.widget.querySelector('.saia-widget-typing');
        typingElement.style.display = 'flex';
        this.scrollToBottom();
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        const typingElement = this.elements.widget.querySelector('.saia-widget-typing');
        typingElement.style.display = 'none';
    }

    /**
     * Show error message in chat
     */
    showErrorMessage(message) {
        this.addMessage({
            content: message,
            is_ai: true,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Get client IP (best effort)
     */
    async getClientIP() {
        try {
            // Try to get IP from a public service
            const response = await fetch('https://api.ipify.org?format=json');
            const data = await response.json();
            return data.ip;
        } catch (error) {
            // Fallback to a default value
            return '127.0.0.1';
        }
    }

    /**
     * Update last activity timestamp
     */
    updateActivity() {
        this.state.lastActivity = Date.now();
    }

    /**
     * Set up session timeout handling
     */
    setupSessionTimeout() {
        setInterval(() => {
            const timeSinceActivity = Date.now() - this.state.lastActivity;
            if (timeSinceActivity > this.config.sessionTimeout && this.state.sessionId) {
                this.log('Session timeout reached');
                this.closeSession();
            }
        }, 60000); // Check every minute
    }

    /**
     * Close the current session
     */
    async closeSession() {
        if (!this.state.sessionId) return;

        try {
            await fetch(`${this.config.apiBaseUrl}/api/widget/session/${this.state.sessionId}/close/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ reason: 'timeout' })
            });

            this.state.sessionId = null;
            this.state.isConnected = false;

            // Remove stored session
            this.removeStoredSession();

            this.log('Session closed');

        } catch (error) {
            this.log('Error closing session:', error);
        }
    }

    /**
     * Destroy the widget
     */
    destroy() {
        this.log('Destroying widget...');

        // Close session
        if (this.state.sessionId) {
            this.closeSession();
        }

        // Remove DOM elements
        if (this.elements.container && this.elements.container.parentNode) {
            this.elements.container.parentNode.removeChild(this.elements.container);
        }

        // Clear state
        this.state = {};
        this.elements = {};

        this.log('Widget destroyed');
    }

    /**
     * Get widget state (for debugging)
     */
    getState() {
        return {
            config: this.config,
            state: this.state,
            messages: this.state.messages
        };
    }
}

// Global initialization function
window.SAIAWidget = SAIAWidget;

// Auto-initialize if configuration is provided
if (typeof window.saiaWidgetConfig !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        window.saiaWidget = new SAIAWidget(window.saiaWidgetConfig);
    });
}
