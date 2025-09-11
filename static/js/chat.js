/**
 * SAIA AI Assistant Chat Interface JavaScript
 * Simple and clean chat functionality
 */

document.addEventListener('DOMContentLoaded', function() {

    // Handle message input
    function setupMessageInput() {
        const inputArea = document.getElementById('input-area');
        const sendButton = document.getElementById('send-message-button');

        if (inputArea && sendButton) {
            // Enable/disable send button based on input
            function updateButtonState() {
                if (inputArea.value.trim()) {
                    sendButton.disabled = false;
                    sendButton.style.opacity = '1';
                } else {
                    sendButton.disabled = true;
                    sendButton.style.opacity = '0.5';
                }
            }

            inputArea.addEventListener('input', updateButtonState);

            // Handle Enter to send (Shift+Enter for new line)
            inputArea.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (this.value.trim()) {
                        // Trigger HTMX form submission
                        const form = this.closest('form');
                        if (form) {
                            htmx.trigger(form, 'submit');
                        }
                    }
                }
            });

            // Initial button state
            updateButtonState();
        }
    }

    // Handle HTMX events
    document.addEventListener('htmx:afterSwap', function(evt) {
        setupMessageInput();

        const inputArea = document.getElementById('input-area');
        if (inputArea) {
            setTimeout(() => inputArea.focus(), 100);
        }
    });

    // Maximize/minimize chat
    document.addEventListener('click', function(e) {
        if (e.target.id === 'maximize') {
            const chatWrapper = document.getElementById('chat-wrapper');
            if (chatWrapper) {
                chatWrapper.style.width = '95vw';
                chatWrapper.style.height = '90vh';
                chatWrapper.style.right = '2.5vw';
                chatWrapper.style.bottom = '5vh';

                e.target.classList.add('d-none');
                document.getElementById('minimize').classList.remove('d-none');
            }
        }

        if (e.target.id === 'minimize') {
            const chatWrapper = document.getElementById('chat-wrapper');
            if (chatWrapper) {
                chatWrapper.style.width = '800px';
                chatWrapper.style.height = '600px';
                chatWrapper.style.right = '20px';
                chatWrapper.style.bottom = '100px';

                e.target.classList.add('d-none');
                document.getElementById('maximize').classList.remove('d-none');
            }
        }
    });

    // Global Enter key handler for chat input (fallback)
    document.addEventListener('keydown', function(e) {
        if (e.target && e.target.id === 'input-area') {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const form = e.target.closest('form');
                const sendButton = document.getElementById('send-message-button');

                if (e.target.value.trim() && form && sendButton) {
                    // Try HTMX trigger first
                    if (typeof htmx !== 'undefined') {
                        htmx.trigger(form, 'submit');
                    } else {
                        // Fallback to button click
                        sendButton.click();
                    }
                }
            }
        }
    });

    // Initial setup
    setupMessageInput();
});
