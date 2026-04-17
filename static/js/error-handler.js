/**
 * BloodLink Error Handler Utility
 * Provides consistent error handling and user feedback across the application
 */

class BloodLinkErrorHandler {
    constructor() {
        this.errorContainer = null;
        this.init();
    }

    init() {
        // Create error container if it doesn't exist
        if (!document.getElementById('errorContainer')) {
            this.errorContainer = document.createElement('div');
            this.errorContainer.id = 'errorContainer';
            this.errorContainer.className = 'error-container';
            document.body.appendChild(this.errorContainer);
        } else {
            this.errorContainer = document.getElementById('errorContainer');
        }
    }

    /**
     * Show an error message to the user
     * @param {string} message - The error message
     * @param {string} type - Error type: 'error', 'warning', 'info', 'success'
     * @param {Object} options - Additional options
     */
    showMessage(message, type = 'error', options = {}) {
        const {
            title = this.getDefaultTitle(type),
            duration = this.getDefaultDuration(type),
            dismissible = true,
            actions = []
        } = options;

        // Remove existing messages of the same type if specified
        if (options.replaceExisting) {
            this.removeMessagesByType(type);
        }

        const messageElement = this.createMessageElement(title, message, type, dismissible, actions);
        this.errorContainer.appendChild(messageElement);

        // Trigger animation
        setTimeout(() => {
            messageElement.classList.add('show');
        }, 10);

        // Auto-dismiss if duration is set
        if (duration > 0) {
            setTimeout(() => {
                this.dismissMessage(messageElement);
            }, duration);
        }

        return messageElement;
    }

    /**
     * Show a success message
     */
    showSuccess(message, options = {}) {
        return this.showMessage(message, 'success', { ...options, duration: 4000 });
    }

    /**
     * Show an error message
     */
    showError(message, options = {}) {
        return this.showMessage(message, 'error', { ...options, duration: 8000 });
    }

    /**
     * Show a warning message
     */
    showWarning(message, options = {}) {
        return this.showMessage(message, 'warning', { ...options, duration: 6000 });
    }

    /**
     * Show an info message
     */
    showInfo(message, options = {}) {
        return this.showMessage(message, 'info', { ...options, duration: 5000 });
    }

    /**
     * Handle API errors with user-friendly messages
     */
    handleApiError(error, context = '') {
        console.error('API Error:', error);

        let message = 'An unexpected error occurred. Please try again.';
        let title = 'Error';

        if (error.response) {
            // Server responded with error status
            const status = error.response.status;
            
            switch (status) {
                case 400:
                    message = 'Invalid request. Please check your input and try again.';
                    title = 'Validation Error';
                    break;
                case 401:
                    message = 'You are not authorized to perform this action. Please log in again.';
                    title = 'Authentication Error';
                    break;
                case 403:
                    message = 'You do not have permission to perform this action.';
                    title = 'Permission Denied';
                    break;
                case 404:
                    message = 'The requested resource was not found.';
                    title = 'Not Found';
                    break;
                case 429:
                    message = 'Too many requests. Please wait a moment and try again.';
                    title = 'Rate Limit Exceeded';
                    break;
                case 500:
                    message = 'Server error. Our team has been notified and is working on a fix.';
                    title = 'Server Error';
                    break;
                default:
                    message = `Server error (${status}). Please try again later.`;
            }

            // Try to extract specific error message from response
            if (error.response.data && error.response.data.message) {
                message = error.response.data.message;
            } else if (error.response.data && error.response.data.detail) {
                message = error.response.data.detail;
            }
        } else if (error.request) {
            // Network error
            message = 'Network error. Please check your internet connection and try again.';
            title = 'Connection Error';
        }

        // Add context if provided
        if (context) {
            message = `${context}: ${message}`;
        }

        return this.showError(message, { title });
    }

    /**
     * Handle form validation errors
     */
    handleFormErrors(form, errors) {
        // Clear existing field errors
        this.clearFieldErrors(form);

        let hasErrors = false;

        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                const errorMessage = Array.isArray(errors[fieldName]) 
                    ? errors[fieldName][0] 
                    : errors[fieldName];
                
                this.showFieldError(field, errorMessage);
                hasErrors = true;
            }
        });

        if (hasErrors) {
            this.showError('Please correct the errors below and try again.', {
                title: 'Form Validation Error',
                duration: 5000
            });
        }

        return hasErrors;
    }

    /**
     * Show error for a specific form field
     */
    showFieldError(field, message) {
        const formGroup = field.closest('.form-group, .mb-3');
        if (!formGroup) return;

        // Remove existing error for this field
        this.clearFieldError(field);

        // Add error styling
        field.classList.add('is-invalid', 'error');

        // Create error message
        const errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback field-error';
        errorElement.textContent = message;

        formGroup.appendChild(errorElement);

        // Shake animation
        formGroup.style.animation = 'shake 0.5s';
        setTimeout(() => {
            formGroup.style.animation = '';
        }, 500);
    }

    /**
     * Clear error for a specific field
     */
    clearFieldError(field) {
        const formGroup = field.closest('.form-group, .mb-3');
        if (formGroup) {
            const existingError = formGroup.querySelector('.field-error');
            if (existingError) {
                existingError.remove();
            }
        }
        
        field.classList.remove('is-invalid', 'error');
    }

    /**
     * Clear all field errors in a form
     */
    clearFieldErrors(form) {
        form.querySelectorAll('.field-error').forEach(error => error.remove());
        form.querySelectorAll('.is-invalid, .error').forEach(field => {
            field.classList.remove('is-invalid', 'error');
        });
    }

    /**
     * Dismiss a specific message
     */
    dismissMessage(messageElement) {
        if (messageElement && messageElement.parentNode) {
            messageElement.classList.remove('show');
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.remove();
                }
            }, 300);
        }
    }

    /**
     * Remove all messages of a specific type
     */
    removeMessagesByType(type) {
        const messages = this.errorContainer.querySelectorAll(`.alert-${type}`);
        messages.forEach(msg => this.dismissMessage(msg));
    }

    /**
     * Clear all messages
     */
    clearAll() {
        const messages = this.errorContainer.querySelectorAll('.alert');
        messages.forEach(msg => this.dismissMessage(msg));
    }

    /**
     * Create message element
     */
    createMessageElement(title, message, type, dismissible, actions) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';

        const icon = this.getIcon(type);
        
        let content = `
            <div class="d-flex align-items-start">
                <div class="me-3">
                    <span class="material-symbols-outlined">${icon}</span>
                </div>
                <div class="flex-grow-1">
                    ${title ? `<strong>${title}:</strong> ` : ''}${message}
        `;

        // Add action buttons if provided
        if (actions.length > 0) {
            content += '<div class="mt-2">';
            actions.forEach(action => {
                content += `
                    <button class="btn btn-sm ${action.class || 'btn-outline-secondary'} me-2" 
                            onclick="${action.onclick}">
                        ${action.text}
                    </button>
                `;
            });
            content += '</div>';
        }

        content += `
                </div>
        `;

        if (dismissible) {
            content += `
                <button type="button" class="btn-close" data-bs-dismiss="alert" 
                        aria-label="Close" onclick="this.closest('.alert').remove()">
                </button>
            `;
        }

        content += '</div>';
        alertDiv.innerHTML = content;

        return alertDiv;
    }

    /**
     * Get icon for message type
     */
    getIcon(type) {
        const icons = {
            error: 'error',
            warning: 'warning',
            info: 'info',
            success: 'check_circle'
        };
        return icons[type] || 'info';
    }

    /**
     * Get default title for message type
     */
    getDefaultTitle(type) {
        const titles = {
            error: 'Error',
            warning: 'Warning',
            info: 'Information',
            success: 'Success'
        };
        return titles[type] || '';
    }

    /**
     * Get default duration for message type
     */
    getDefaultDuration(type) {
        const durations = {
            error: 8000,
            warning: 6000,
            info: 5000,
            success: 4000
        };
        return durations[type] || 5000;
    }
}

// Global error handler instance
window.BloodLinkErrorHandler = new BloodLinkErrorHandler();

// Convenience functions
window.showError = (message, options) => window.BloodLinkErrorHandler.showError(message, options);
window.showSuccess = (message, options) => window.BloodLinkErrorHandler.showSuccess(message, options);
window.showWarning = (message, options) => window.BloodLinkErrorHandler.showWarning(message, options);
window.showInfo = (message, options) => window.BloodLinkErrorHandler.showInfo(message, options);

// Add CSS styles
const errorStyles = `
    .error-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
        pointer-events: none;
    }

    .error-container .alert {
        pointer-events: auto;
        margin-bottom: 10px;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    }

    .error-container .alert.show {
        opacity: 1;
        transform: translateX(0);
    }

    .error-container .alert-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }

    .error-container .alert-danger {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }

    .error-container .alert-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }

    .error-container .alert-info {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
    }

    .error-container .btn-close {
        filter: brightness(0) invert(1);
        opacity: 0.8;
    }

    .error-container .btn-close:hover {
        opacity: 1;
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }

    .field-error {
        animation: slideInDown 0.3s ease-out;
    }

    @keyframes slideInDown {
        from {
            transform: translateY(-10px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    .form-control.error,
    .form-control.is-invalid {
        border-color: #ef4444;
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    }

    .invalid-feedback {
        display: block;
        width: 100%;
        margin-top: 0.25rem;
        font-size: 0.875rem;
        color: #ef4444;
    }

    .field-error {
        display: block;
        width: 100%;
        margin-top: 0.25rem;
        font-size: 0.875rem;
        color: #ef4444;
    }
`;

// Add styles to page
const styleSheet = document.createElement('style');
styleSheet.textContent = errorStyles;
document.head.appendChild(styleSheet);
