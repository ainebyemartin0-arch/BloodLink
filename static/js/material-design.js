// Material Design JavaScript for BloodLink

// Ripple Effect for Buttons
document.addEventListener('DOMContentLoaded', function() {
    // Add ripple effect to all buttons
    const buttons = document.querySelectorAll('.md-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Initialize Material Components
    initializeMaterialComponents();
});

// Initialize Material Design Components
function initializeMaterialComponents() {
    // Initialize form controls
    const formControls = document.querySelectorAll('.md-form-control');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        control.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Check initial value
        if (control.value) {
            control.parentElement.classList.add('focused');
        }
    });
    
    // Initialize floating labels
    const floatingLabels = document.querySelectorAll('.md-form-group');
    floatingLabels.forEach(group => {
        const input = group.querySelector('input, textarea, select');
        const label = group.querySelector('label');
        
        if (input && label) {
            // Add floating label class
            label.classList.add('md-floating-label');
            
            // Check initial value
            if (input.value) {
                group.classList.add('has-value');
            }
            
            input.addEventListener('input', function() {
                if (this.value) {
                    group.classList.add('has-value');
                } else {
                    group.classList.remove('has-value');
                }
            });
        }
    });
    
    // Initialize cards with hover effects
    const cards = document.querySelectorAll('.md-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Initialize smooth scrolling
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Material Toast Notifications
function showMaterialToast(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `md-toast md-toast-${type}`;
    toast.innerHTML = `
        <i class="material-icons">${getToastIcon(type)}</i>
        <span>${message}</span>
        <button class="md-toast-close" onclick="this.parentElement.remove()">
            <i class="material-icons">close</i>
        </button>
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, duration);
}

function getToastIcon(type) {
    const icons = {
        'success': 'check_circle',
        'error': 'error',
        'warning': 'warning',
        'info': 'info'
    };
    return icons[type] || 'info';
}

// Material Dialog/Modal
function showMaterialDialog(options) {
    const dialog = document.createElement('div');
    dialog.className = 'md-dialog-overlay';
    dialog.innerHTML = `
        <div class="md-dialog">
            <div class="md-dialog-header">
                <h3 class="md-dialog-title">${options.title}</h3>
            </div>
            <div class="md-dialog-content">
                ${options.content}
            </div>
            <div class="md-dialog-actions">
                ${options.actions ? options.actions : `
                    <button class="md-btn md-btn-outlined" onclick="closeMaterialDialog()">Cancel</button>
                    <button class="md-btn md-btn-primary" onclick="closeMaterialDialog()">OK</button>
                `}
            </div>
        </div>
    `;
    
    document.body.appendChild(dialog);
    
    // Animate in
    setTimeout(() => {
        dialog.classList.add('show');
    }, 100);
    
    return dialog;
}

function closeMaterialDialog() {
    const dialog = document.querySelector('.md-dialog-overlay');
    if (dialog) {
        dialog.classList.remove('show');
        setTimeout(() => {
            dialog.remove();
        }, 300);
    }
}

// Material Loading Spinner
function showMaterialSpinner(container) {
    const spinner = document.createElement('div');
    spinner.className = 'md-spinner-container';
    spinner.innerHTML = `
        <div class="md-spinner"></div>
        <div class="md-spinner-text">Loading...</div>
    `;
    
    if (container) {
        container.appendChild(spinner);
    } else {
        document.body.appendChild(spinner);
    }
    
    return spinner;
}

function hideMaterialSpinner(spinner) {
    if (spinner) {
        spinner.remove();
    }
}

// Material Form Validation
function validateMaterialForm(formElement) {
    const inputs = formElement.querySelectorAll('.md-form-control');
    let isValid = true;
    
    inputs.forEach(input => {
        const formGroup = input.closest('.md-form-group');
        const errorElement = formGroup.querySelector('.md-error-message');
        
        // Remove previous error state
        formGroup.classList.remove('has-error');
        if (errorElement) {
            errorElement.remove();
        }
        
        // Validate
        if (input.hasAttribute('required') && !input.value.trim()) {
            showFieldError(formGroup, `${input.previousElementSibling.textContent} is required`);
            isValid = false;
        } else if (input.type === 'email' && input.value && !isValidEmail(input.value)) {
            showFieldError(formGroup, 'Please enter a valid email address');
            isValid = false;
        } else if (input.type === 'tel' && input.value && !isValidPhone(input.value)) {
            showFieldError(formGroup, 'Please enter a valid phone number');
            isValid = false;
        }
    });
    
    return isValid;
}

function showFieldError(formGroup, message) {
    formGroup.classList.add('has-error');
    
    const errorElement = document.createElement('div');
    errorElement.className = 'md-error-message';
    errorElement.textContent = message;
    
    formGroup.appendChild(errorElement);
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
    return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

// Material Progress Bar
function updateMaterialProgress(progressElement, percentage) {
    const progressBar = progressElement.querySelector('.md-progress-bar');
    if (progressBar) {
        progressBar.style.width = Math.min(100, Math.max(0, percentage)) + '%';
    }
}

// Material Chip Component
function createMaterialChip(text, closable = false, onClose = null) {
    const chip = document.createElement('div');
    chip.className = 'md-chip';
    chip.innerHTML = `
        <span>${text}</span>
        ${closable ? '<i class="material-icons md-chip-close">close</i>' : ''}
    `;
    
    if (closable && onClose) {
        const closeBtn = chip.querySelector('.md-chip-close');
        closeBtn.addEventListener('click', () => {
            if (onClose) onClose(chip);
            chip.remove();
        });
    }
    
    return chip;
}

// Material Table Enhancements
function enhanceMaterialTable(tableElement) {
    const rows = tableElement.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on a link or button
            if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') {
                return;
            }
            
            // Toggle row selection
            this.classList.toggle('selected');
        });
        
        // Add hover effect
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(0, 0, 0, 0.04)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
}

// Material Theme Switcher
function switchMaterialTheme(theme) {
    const root = document.documentElement;
    
    if (theme === 'dark') {
        root.style.setProperty('--md-surface', '#121212');
        root.style.setProperty('--md-surface-variant', '#1e1e1e');
        root.style.setProperty('--md-background', '#000000');
        root.style.setProperty('--md-on-surface', '#ffffff');
        root.style.setProperty('--md-on-background', '#ffffff');
        root.style.setProperty('--md-text-primary', 'rgba(255, 255, 255, 0.87)');
        root.style.setProperty('--md-text-secondary', 'rgba(255, 255, 255, 0.6)');
        root.style.setProperty('--md-text-disabled', 'rgba(255, 255, 255, 0.38)');
        root.style.setProperty('--md-text-hint', 'rgba(255, 255, 255, 0.38)');
    } else {
        // Reset to light theme (default)
        root.style.setProperty('--md-surface', '#ffffff');
        root.style.setProperty('--md-surface-variant', '#f5f5f5');
        root.style.setProperty('--md-background', '#fafafa');
        root.style.setProperty('--md-on-surface', '#212121');
        root.style.setProperty('--md-on-background', '#212121');
        root.style.setProperty('--md-text-primary', 'rgba(0, 0, 0, 0.87)');
        root.style.setProperty('--md-text-secondary', 'rgba(0, 0, 0, 0.6)');
        root.style.setProperty('--md-text-disabled', 'rgba(0, 0, 0, 0.38)');
        root.style.setProperty('--md-text-hint', 'rgba(0, 0, 0, 0.38)');
    }
    
    // Save theme preference
    localStorage.setItem('material-theme', theme);
}

// Load saved theme
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('material-theme');
    if (savedTheme) {
        switchMaterialTheme(savedTheme);
    }
});

// Material Animation Helpers
function animateElement(element, animation, duration = 300) {
    element.style.animation = `${animation} ${duration}ms ease-out`;
    
    return new Promise(resolve => {
        setTimeout(() => {
            element.style.animation = '';
            resolve();
        }, duration);
    });
}

function fadeInElement(element, duration = 300) {
    element.style.opacity = '0';
    element.style.display = 'block';
    
    setTimeout(() => {
        element.style.transition = `opacity ${duration}ms ease-in`;
        element.style.opacity = '1';
    }, 10);
    
    return new Promise(resolve => {
        setTimeout(() => {
            element.style.transition = '';
            resolve();
        }, duration);
    });
}

function fadeOutElement(element, duration = 300) {
    element.style.transition = `opacity ${duration}ms ease-out`;
    element.style.opacity = '0';
    
    return new Promise(resolve => {
        setTimeout(() => {
            element.style.display = 'none';
            element.style.transition = '';
            resolve();
        }, duration);
    });
}

// Material Form Auto-resize for textareas
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Initialize auto-resize for all textareas
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea[auto-resize]');
    textareas.forEach(textarea => {
        autoResizeTextarea(textarea);
        textarea.addEventListener('input', () => autoResizeTextarea(textarea));
    });
});

// Export functions for global use
window.MaterialDesign = {
    showToast: showMaterialToast,
    showDialog: showMaterialDialog,
    closeDialog: closeMaterialDialog,
    showSpinner: showMaterialSpinner,
    hideSpinner: hideMaterialSpinner,
    validateForm: validateMaterialForm,
    updateProgress: updateMaterialProgress,
    createChip: createMaterialChip,
    enhanceTable: enhanceMaterialTable,
    switchTheme: switchMaterialTheme,
    animate: animateElement,
    fadeIn: fadeInElement,
    fadeOut: fadeOutElement
};
