/**
 * BloodLink Loading States Utility
 * Provides consistent loading indicators and progress feedback across the application
 */

class BloodLinkLoadingStates {
    constructor() {
        this.loadingOverlay = null;
        this.activeLoaders = new Map();
        this.init();
    }

    init() {
        // Create global loading overlay
        this.createLoadingOverlay();
        
        // Initialize form loading states
        this.initFormLoading();
        
        // Initialize button loading states
        this.initButtonLoading();
        
        // Initialize AJAX loading states
        this.initAjaxLoading();
    }

    /**
     * Create global loading overlay
     */
    createLoadingOverlay() {
        this.loadingOverlay = document.createElement('div');
        this.loadingOverlay.id = 'globalLoadingOverlay';
        this.loadingOverlay.className = 'loading-overlay';
        this.loadingOverlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <div class="loading-text">Processing...</div>
            </div>
        `;
        document.body.appendChild(this.loadingOverlay);
    }

    /**
     * Show global loading overlay
     */
    showGlobalLoading(message = 'Processing...') {
        if (this.loadingOverlay) {
            const loadingText = this.loadingOverlay.querySelector('.loading-text');
            if (loadingText) {
                loadingText.textContent = message;
            }
            this.loadingOverlay.classList.add('show');
        }
    }

    /**
     * Hide global loading overlay
     */
    hideGlobalLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.remove('show');
        }
    }

    /**
     * Initialize form loading states
     */
    initFormLoading() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            const submitBtn = form.querySelector('button[type="submit"]');
            
            if (submitBtn && !submitBtn.classList.contains('no-loading')) {
                this.setButtonLoading(submitBtn, true, 'Submitting...');
            }
        });
    }

    /**
     * Initialize button loading states
     */
    initButtonLoading() {
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('button[data-loading], .btn[data-loading]');
            if (btn && !btn.disabled) {
                const loadingText = btn.getAttribute('data-loading') || 'Loading...';
                this.setButtonLoading(btn, true, loadingText);
            }
        });
    }

    /**
     * Initialize AJAX loading states
     */
    initAjaxLoading() {
        // Monitor fetch requests
        const originalFetch = window.fetch;
        window.fetch = (...args) => {
            this.showGlobalLoading('Loading data...');
            return originalFetch(...args)
                .finally(() => {
                    this.hideGlobalLoading();
                });
        };

        // Monitor XMLHttpRequest
        const originalXHROpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url) {
            this.addEventListener('loadstart', () => {
                window.BloodLinkLoadingStates.showGlobalLoading('Loading data...');
            });
            this.addEventListener('loadend', () => {
                window.BloodLinkLoadingStates.hideGlobalLoading();
            });
            return originalXHROpen.apply(this, arguments);
        };
    }

    /**
     * Set button loading state
     */
    setButtonLoading(button, loading, text = 'Loading...') {
        if (loading) {
            // Store original content
            if (!button.hasAttribute('data-original-content')) {
                button.setAttribute('data-original-content', button.innerHTML);
            }
            
            // Set loading state
            button.disabled = true;
            button.classList.add('loading');
            button.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                ${text}
            `;
            
            // Track active loader
            this.activeLoaders.set(button, true);
        } else {
            // Restore original content
            const originalContent = button.getAttribute('data-original-content');
            if (originalContent) {
                button.innerHTML = originalContent;
                button.removeAttribute('data-original-content');
            }
            
            button.disabled = false;
            button.classList.remove('loading');
            
            // Remove from active loaders
            this.activeLoaders.delete(button);
        }
    }

    /**
     * Reset all loading states
     */
    resetAllLoading() {
        this.activeLoaders.forEach((_, button) => {
            this.setButtonLoading(button, false);
        });
        this.activeLoaders.clear();
        this.hideGlobalLoading();
    }

    /**
     * Show progress bar for long operations
     */
    showProgressBar(container, options = {}) {
        const {
            message = 'Processing...',
            showPercentage = true,
            indeterminate = false
        } = options;

        const progressBar = document.createElement('div');
        progressBar.className = 'progress-container';
        progressBar.innerHTML = `
            <div class="progress-message">${message}</div>
            <div class="progress">
                <div class="progress-bar ${indeterminate ? 'progress-bar-indeterminate' : ''}" 
                     role="progressbar" 
                     style="width: ${indeterminate ? '100%' : '0%'}"
                     aria-valuenow="${indeterminate ? 100 : 0}" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                    ${showPercentage && !indeterminate ? '0%' : ''}
                </div>
            </div>
        `;

        if (container) {
            container.appendChild(progressBar);
        } else {
            document.body.appendChild(progressBar);
        }

        return {
            element: progressBar,
            update: (percentage) => {
                if (!indeterminate) {
                    const bar = progressBar.querySelector('.progress-bar');
                    bar.style.width = percentage + '%';
                    bar.setAttribute('aria-valuenow', percentage);
                    if (showPercentage) {
                        bar.textContent = percentage + '%';
                    }
                }
            },
            setMessage: (newMessage) => {
                const messageEl = progressBar.querySelector('.progress-message');
                if (messageEl) {
                    messageEl.textContent = newMessage;
                }
            },
            complete: () => {
                setTimeout(() => {
                    progressBar.remove();
                }, 1000);
            }
        };
    }

    /**
     * Show skeleton loading for content areas
     */
    showSkeletonLoader(container, options = {}) {
        const {
            lines = 3,
            height = '1rem',
            className = 'skeleton-loader'
        } = options;

        const skeleton = document.createElement('div');
        skeleton.className = className;
        
        for (let i = 0; i < lines; i++) {
            const line = document.createElement('div');
            line.className = 'skeleton-line';
            line.style.height = height;
            
            // Vary widths for more realistic appearance
            const width = i === lines - 1 ? '60%' : '100%';
            line.style.width = width;
            
            skeleton.appendChild(line);
        }

        if (container) {
            container.innerHTML = '';
            container.appendChild(skeleton);
        }

        return skeleton;
    }

    /**
     * Hide skeleton loader
     */
    hideSkeletonLoader(container) {
        const skeleton = container.querySelector('.skeleton-loader');
        if (skeleton) {
            skeleton.remove();
        }
    }
}

// Global loading states instance
window.BloodLinkLoadingStates = new BloodLinkLoadingStates();

// Convenience functions
window.showLoading = (message) => window.BloodLinkLoadingStates.showGlobalLoading(message);
window.hideLoading = () => window.BloodLinkLoadingStates.hideGlobalLoading();
window.setButtonLoading = (btn, loading, text) => window.BloodLinkLoadingStates.setButtonLoading(btn, loading, text);

// Add CSS styles
const loadingStyles = `
    /* Global Loading Overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
    }

    .loading-overlay.show {
        opacity: 1;
        visibility: visible;
    }

    .loading-spinner {
        background: white;
        padding: 2rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        text-align: center;
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #dc2626;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }

    .loading-text {
        color: #333;
        font-weight: 500;
    }

    /* Button Loading States */
    .btn.loading {
        pointer-events: none;
        opacity: 0.7;
    }

    .spinner-border-sm {
        width: 1rem;
        height: 1rem;
        border-width: 0.125em;
    }

    /* Progress Bar */
    .progress-container {
        margin: 1rem 0;
    }

    .progress-message {
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #333;
    }

    .progress {
        height: 1rem;
        background-color: #e9ecef;
        border-radius: 0.25rem;
        overflow: hidden;
    }

    .progress-bar {
        background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%);
        transition: width 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.75rem;
        font-weight: 500;
    }

    .progress-bar-indeterminate {
        background: linear-gradient(90deg, #dc2626 0%, #ef4444 50%, #dc2626 100%);
        background-size: 200% 100%;
        animation: progress-indeterminate 1.5s ease-in-out infinite;
    }

    /* Skeleton Loader */
    .skeleton-loader {
        padding: 1rem;
    }

    .skeleton-line {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: skeleton-loading 1.5s ease-in-out infinite;
        border-radius: 0.25rem;
        margin-bottom: 0.5rem;
    }

    .skeleton-line:last-child {
        margin-bottom: 0;
    }

    /* Animations */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes progress-indeterminate {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    @keyframes skeleton-loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* Form Loading States */
    form.loading {
        pointer-events: none;
        opacity: 0.6;
    }

    .form-group.loading {
        position: relative;
    }

    .form-group.loading::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 0.25rem;
    }

    .form-group.loading::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 20px;
        height: 20px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #dc2626;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        z-index: 1;
    }

    /* Table Loading */
    .table-loading {
        position: relative;
    }

    .table-loading::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10;
    }

    .table-loading::before {
        content: 'Loading...';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #666;
        font-weight: 500;
        z-index: 11;
    }
`;

// Add styles to page
const styleSheet = document.createElement('style');
styleSheet.textContent = loadingStyles;
document.head.appendChild(styleSheet);
