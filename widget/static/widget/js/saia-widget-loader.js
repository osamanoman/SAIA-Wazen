/**
 * SAIA Widget Loader Script
 * 
 * This is the main integration script that websites embed to load the SAIA widget.
 * It handles dynamic loading, configuration, and initialization of the widget.
 * 
 * Usage:
 * <script>
 *   (function(w,d,s,o,f,js,fjs){
 *     w['SAIAWidgetObject']=o;w[o]=w[o]||function(){(w[o].q=w[o].q||[]).push(arguments)};
 *     js=d.createElement(s),fjs=d.getElementsByTagName(s)[0];
 *     js.id=o;js.src=f;js.async=1;fjs.parentNode.insertBefore(js,fjs);
 *   })(window,document,'script','saia','https://your-domain.com/static/widget/js/saia-widget-loader.js');
 *   
 *   saia('init', {
 *     companySlug: 'your-company',
 *     apiBaseUrl: 'https://your-api-domain.com'
 *   });
 * </script>
 */

(function(window, document) {
    'use strict';
    
    // Prevent multiple initializations
    if (window.SAIAWidgetLoader) {
        return;
    }
    
    // Widget loader class
    class SAIAWidgetLoader {
        constructor() {
            this.isLoaded = false;
            this.isLoading = false;
            this.widget = null;
            this.config = {};
            this.queue = [];
            
            // Default configuration
            this.defaults = {
                apiBaseUrl: window.location.origin,
                position: 'bottom-right',
                autoOpen: false,
                showWelcomeMessage: true,
                enableSound: true,
                theme: 'default',
                debug: false,
                maxMessages: 100,
                sessionTimeout: 30 * 60 * 1000, // 30 minutes
                
                // Asset URLs (can be overridden)
                cssUrl: null,
                jsUrl: null
            };
            
            this.init();
        }
        
        init() {
            // Process any queued commands
            if (window.saia && window.saia.q) {
                this.queue = window.saia.q;
                this.processQueue();
            }
            
            // Replace the global function
            window.saia = this.saia.bind(this);
        }
        
        /**
         * Main API function
         */
        saia(command, ...args) {
            switch (command) {
                case 'init':
                    this.initWidget(args[0] || {});
                    break;
                    
                case 'open':
                    this.openWidget();
                    break;
                    
                case 'close':
                    this.closeWidget();
                    break;
                    
                case 'toggle':
                    this.toggleWidget();
                    break;
                    
                case 'destroy':
                    this.destroyWidget();
                    break;
                    
                case 'config':
                    return this.getConfig();
                    
                case 'state':
                    return this.getState();
                    
                default:
                    if (this.isLoaded && this.widget && typeof this.widget[command] === 'function') {
                        return this.widget[command](...args);
                    } else {
                        // Queue command for later execution
                        this.queue.push([command, ...args]);
                    }
            }
        }
        
        /**
         * Initialize the widget
         */
        async initWidget(config = {}) {
            if (this.isLoading || this.isLoaded) {
                return;
            }
            
            // Validate required configuration
            if (!config.companySlug) {
                console.error('[SAIA Widget] companySlug is required for initialization');
                return;
            }
            
            this.isLoading = true;
            this.config = { ...this.defaults, ...config };
            
            try {
                // Load CSS first
                await this.loadCSS();
                
                // Load JavaScript
                await this.loadJS();
                
                // Initialize widget
                this.widget = new window.SAIAWidget(this.config);
                this.isLoaded = true;
                this.isLoading = false;
                
                // Process any queued commands
                this.processQueue();
                
                console.log('[SAIA Widget] Initialized successfully');
                
            } catch (error) {
                this.isLoading = false;
                console.error('[SAIA Widget] Failed to initialize:', error);
                
                if (this.config.onError) {
                    this.config.onError('Failed to initialize widget', error);
                }
            }
        }
        
        /**
         * Load CSS stylesheet
         */
        loadCSS() {
            return new Promise((resolve, reject) => {
                // Check if CSS is already loaded
                if (document.querySelector('link[href*="saia-widget.css"]')) {
                    resolve();
                    return;
                }
                
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.type = 'text/css';
                link.href = this.config.cssUrl || this.getAssetUrl('css/saia-widget.css');
                
                link.onload = () => resolve();
                link.onerror = () => reject(new Error('Failed to load CSS'));
                
                document.head.appendChild(link);
            });
        }
        
        /**
         * Load JavaScript
         */
        loadJS() {
            return new Promise((resolve, reject) => {
                // Check if JS is already loaded
                if (window.SAIAWidget) {
                    resolve();
                    return;
                }
                
                const script = document.createElement('script');
                script.type = 'text/javascript';
                script.async = true;
                script.src = this.config.jsUrl || this.getAssetUrl('js/saia-widget.js');
                
                script.onload = () => {
                    if (window.SAIAWidget) {
                        resolve();
                    } else {
                        reject(new Error('SAIAWidget class not found after loading script'));
                    }
                };
                
                script.onerror = () => reject(new Error('Failed to load JavaScript'));
                
                document.head.appendChild(script);
            });
        }
        
        /**
         * Get asset URL
         */
        getAssetUrl(path) {
            // Try to determine base URL from current script
            const scripts = document.getElementsByTagName('script');
            const currentScript = scripts[scripts.length - 1];
            const scriptSrc = currentScript.src;
            
            if (scriptSrc) {
                const baseUrl = scriptSrc.substring(0, scriptSrc.lastIndexOf('/'));
                return baseUrl.replace('/js', '') + '/' + path;
            }
            
            // Fallback to API base URL
            return this.config.apiBaseUrl + '/static/widget/' + path;
        }
        
        /**
         * Process queued commands
         */
        processQueue() {
            while (this.queue.length > 0) {
                const [command, ...args] = this.queue.shift();
                this.saia(command, ...args);
            }
        }
        
        /**
         * Open widget
         */
        openWidget() {
            if (this.widget && typeof this.widget.open === 'function') {
                this.widget.open();
            } else {
                this.queue.push(['open']);
            }
        }
        
        /**
         * Close widget
         */
        closeWidget() {
            if (this.widget && typeof this.widget.close === 'function') {
                this.widget.close();
            } else {
                this.queue.push(['close']);
            }
        }
        
        /**
         * Toggle widget
         */
        toggleWidget() {
            if (this.widget && typeof this.widget.toggle === 'function') {
                this.widget.toggle();
            } else {
                this.queue.push(['toggle']);
            }
        }
        
        /**
         * Destroy widget
         */
        destroyWidget() {
            if (this.widget && typeof this.widget.destroy === 'function') {
                this.widget.destroy();
                this.widget = null;
                this.isLoaded = false;
            }
        }
        
        /**
         * Get configuration
         */
        getConfig() {
            return this.config;
        }
        
        /**
         * Get widget state
         */
        getState() {
            if (this.widget && typeof this.widget.getState === 'function') {
                return this.widget.getState();
            }
            
            return {
                isLoaded: this.isLoaded,
                isLoading: this.isLoading,
                hasWidget: !!this.widget
            };
        }
    }
    
    // Initialize loader
    window.SAIAWidgetLoader = new SAIAWidgetLoader();
    
    // Auto-detect configuration from script tag
    const currentScript = document.currentScript || (function() {
        const scripts = document.getElementsByTagName('script');
        return scripts[scripts.length - 1];
    })();
    
    if (currentScript) {
        const companySlug = currentScript.getAttribute('data-company');
        const apiBaseUrl = currentScript.getAttribute('data-api-url');
        const autoOpen = currentScript.getAttribute('data-auto-open') === 'true';
        const position = currentScript.getAttribute('data-position');
        const theme = currentScript.getAttribute('data-theme');
        
        if (companySlug) {
            // Auto-initialize with detected configuration
            const autoConfig = {
                companySlug: companySlug
            };
            
            if (apiBaseUrl) autoConfig.apiBaseUrl = apiBaseUrl;
            if (autoOpen) autoConfig.autoOpen = autoOpen;
            if (position) autoConfig.position = position;
            if (theme) autoConfig.theme = theme;
            
            // Initialize after DOM is ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    window.saia('init', autoConfig);
                });
            } else {
                window.saia('init', autoConfig);
            }
        }
    }
    
})(window, document);
