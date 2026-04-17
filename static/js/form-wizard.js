// ===== MULTI-STEP FORM WIZARD COMPONENT =====

class FormWizard {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with id '${containerId}' not found`);
            return;
        }

        this.options = {
            steps: options.steps || [],
            showProgress: options.showProgress !== false,
            allowNavigation: options.allowNavigation !== false,
            validateOnStep: options.validateOnStep !== false,
            onFinish: options.onFinish || null,
            onStepChange: options.onStepChange || null,
            onValidation: options.onValidation || null,
            animationDuration: options.animationDuration || 300,
            ...options
        };

        this.currentStep = 0;
        this.formData = {};
        this.validationErrors = {};
        this.isSubmitting = false;

        this.init();
    }

    init() {
        this.createWizardStructure();
        this.bindEvents();
        this.showStep(0);
    }

    createWizardStructure() {
        const wizardHtml = `
            <div class="form-wizard">
                ${this.options.showProgress ? this.createProgress() : ''}
                ${this.createHeader()}
                <div class="wizard-content">
                    ${this.createSteps()}
                </div>
                <div class="wizard-actions">
                    <div class="wizard-summary">
                        Step <span class="current-step">1</span> of <span class="total-steps">${this.options.steps.length}</span>
                    </div>
                    <div class="wizard-buttons">
                        <button type="button" class="wizard-btn wizard-btn-secondary" id="wizard-prev" disabled>
                            <i class="material-icons">chevron_left</i>
                            Previous
                        </button>
                        <button type="button" class="wizard-btn wizard-btn-primary" id="wizard-next">
                            Next
                            <i class="material-icons">chevron_right</i>
                        </button>
                        <button type="button" class="wizard-btn wizard-btn-outline" id="wizard-cancel">
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        `;

        this.container.innerHTML = wizardHtml;

        // Store references to elements
        this.stepElements = this.container.querySelectorAll('.wizard-step');
        this.progressSteps = this.container.querySelectorAll('.progress-step');
        this.prevBtn = this.container.querySelector('#wizard-prev');
        this.nextBtn = this.container.querySelector('#wizard-next');
        this.cancelBtn = this.container.querySelector('#wizard-cancel');
        this.currentStepSpan = this.container.querySelector('.current-step');
        this.totalStepsSpan = this.container.querySelector('.total-steps');
        this.progressBar = this.container.querySelector('.progress-line-fill');
    }

    createProgress() {
        const stepsHtml = this.options.steps.map((step, index) => `
            <div class="progress-step" data-step="${index}">
                <div class="step-indicator" data-step="${index}">
                    ${index + 1}
                </div>
                <div class="step-title">${step.title}</div>
            </div>
        `).join('');

        return `
            <div class="wizard-progress">
                <div class="progress-steps">
                    <div class="progress-line">
                        <div class="progress-line-fill" style="width: 0%"></div>
                    </div>
                    ${stepsHtml}
                </div>
            </div>
        `;
    }

    createHeader() {
        return `
            <div class="wizard-header">
                <h2 class="wizard-title">${this.options.title || 'Form Wizard'}</h2>
                <p class="wizard-subtitle">${this.options.subtitle || 'Complete the form step by step'}</p>
            </div>
        `;
    }

    createSteps() {
        return this.options.steps.map((step, index) => `
            <div class="wizard-step" data-step="${index}">
                ${this.createStepContent(step, index)}
            </div>
        `).join('');
    }

    createStepContent(step, index) {
        switch (step.type) {
            case 'form':
                return this.createFormStep(step, index);
            case 'review':
                return this.createReviewStep(step, index);
            case 'success':
                return this.createSuccessStep(step, index);
            default:
                return this.createFormStep(step, index);
        }
    }

    createFormStep(step, index) {
        const formFields = step.fields || [];
        const fieldsHtml = formFields.map(field => this.createFormField(field, index)).join('');

        return `
            <form class="wizard-form" data-step="${index}" novalidate>
                <div class="form-row">
                    ${fieldsHtml}
                </div>
            </form>
        `;
    }

    createFormField(field, stepIndex) {
        const fieldId = `field-${stepIndex}-${field.name}`;
        const required = field.required ? 'required' : '';
        const requiredIndicator = field.required ? '<span class="required-indicator">*</span>' : '';

        switch (field.type) {
            case 'text':
            case 'email':
            case 'tel':
            case 'number':
            case 'date':
                return `
                    <div class="form-group">
                        <label class="form-label" for="${fieldId}">
                            ${field.label}${requiredIndicator}
                        </label>
                        <input type="${field.type}" 
                               class="form-input" 
                               id="${fieldId}" 
                               name="${field.name}" 
                               placeholder="${field.placeholder || ''}"
                               ${required}
                               data-validation="${field.validation || ''}">
                        ${field.help ? `<div class="form-help">${field.help}</div>` : ''}
                        <div class="form-error" id="${fieldId}-error"></div>
                    </div>
                `;

            case 'select':
                const options = field.options || [];
                const optionsHtml = options.map(option => 
                    `<option value="${option.value}">${option.label}</option>`
                ).join('');

                return `
                    <div class="form-group">
                        <label class="form-label" for="${fieldId}">
                            ${field.label}${requiredIndicator}
                        </label>
                        <select class="form-select" id="${fieldId}" name="${field.name}" ${required}>
                            <option value="">${field.placeholder || 'Select an option'}</option>
                            ${optionsHtml}
                        </select>
                        ${field.help ? `<div class="form-help">${field.help}</div>` : ''}
                        <div class="form-error" id="${fieldId}-error"></div>
                    </div>
                `;

            case 'textarea':
                return `
                    <div class="form-group">
                        <label class="form-label" for="${fieldId}">
                            ${field.label}${requiredIndicator}
                        </label>
                        <textarea class="form-textarea" 
                                  id="${fieldId}" 
                                  name="${field.name}" 
                                  placeholder="${field.placeholder || ''}"
                                  rows="${field.rows || 4}"
                                  ${required}
                                  data-validation="${field.validation || ''}"></textarea>
                        ${field.help ? `<div class="form-help">${field.help}</div>` : ''}
                        <div class="form-error" id="${fieldId}-error"></div>
                    </div>
                `;

            case 'checkbox':
                return `
                    <div class="form-group">
                        <label class="form-checkbox" for="${fieldId}">
                            <input type="checkbox" class="form-checkbox" id="${fieldId}" name="${field.name}" value="${field.value || 'true'}">
                            ${field.label}
                        </label>
                        ${field.help ? `<div class="form-help">${field.help}</div>` : ''}
                        <div class="form-error" id="${fieldId}-error"></div>
                    </div>
                `;

            case 'radio':
                const radioOptions = field.options || [];
                const radioHtml = radioOptions.map(option => `
                    <label class="form-radio">
                        <input type="radio" name="${field.name}" value="${option.value}" ${option.checked ? 'checked' : ''}>
                        ${option.label}
                    </label>
                `).join('');

                return `
                    <div class="form-group">
                        <div class="form-label">${field.label}${requiredIndicator}</div>
                        <div class="radio-group">
                            ${radioHtml}
                        </div>
                        ${field.help ? `<div class="form-help">${field.help}</div>` : ''}
                        <div class="form-error" id="${field.name}-error"></div>
                    </div>
                `;

            default:
                return '';
        }
    }

    createReviewStep(step, index) {
        return `
            <div class="step-review">
                <h3>Review Your Information</h3>
                <div id="review-content-${index}">
                    <!-- Review content will be populated dynamically -->
                </div>
            </div>
        `;
    }

    createSuccessStep(step, index) {
        return `
            <div class="step-success">
                <div class="success-icon">
                    <i class="material-icons">check_circle</i>
                </div>
                <h2 class="success-title">${step.title || 'Success!'}</h2>
                <p class="success-message">${step.message || 'Your form has been submitted successfully.'}</p>
                ${step.action ? `
                    <button type="button" class="wizard-btn wizard-btn-primary" onclick="${step.action}">
                        ${step.actionText || 'Continue'}
                    </button>
                ` : ''}
            </div>
        `;
    }

    bindEvents() {
        // Navigation buttons
        this.prevBtn.addEventListener('click', () => this.previousStep());
        this.nextBtn.addEventListener('click', () => this.nextStep());
        this.cancelBtn.addEventListener('click', () => this.cancel());

        // Step indicators (if navigation is allowed)
        if (this.options.allowNavigation) {
            this.progressSteps.forEach((step, index) => {
                step.addEventListener('click', () => this.goToStep(index));
            });
        }

        // Form validation
        this.container.addEventListener('input', (e) => {
            if (e.target.classList.contains('form-input') || 
                e.target.classList.contains('form-select') || 
                e.target.classList.contains('form-textarea')) {
                this.validateField(e.target);
            }
        });

        // Keyboard navigation
        this.container.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                this.nextStep();
            } else if (e.key === 'ArrowLeft' && e.ctrlKey) {
                e.preventDefault();
                this.previousStep();
            }
        });
    }

    showStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.options.steps.length) {
            return;
        }

        // Validate current step before moving
        if (this.options.validateOnStep && stepIndex > this.currentStep) {
            if (!this.validateStep(this.currentStep)) {
                return;
            }
        }

        // Update current step
        this.currentStep = stepIndex;
        
        // Hide all steps
        this.stepElements.forEach((step, index) => {
            step.classList.remove('active');
            if (index < stepIndex) {
                step.classList.add('completed');
            } else {
                step.classList.remove('completed');
            }
        });

        // Show current step
        this.stepElements[stepIndex].classList.add('active');

        // Update progress
        this.updateProgress();

        // Update buttons
        this.updateButtons();

        // Update summary
        this.updateSummary();

        // Handle special step types
        const currentStepConfig = this.options.steps[stepIndex];
        if (currentStepConfig.type === 'review') {
            this.populateReview(stepIndex);
        }

        // Trigger callback
        if (this.options.onStepChange) {
            this.options.onStepChange(stepIndex, currentStepConfig);
        }
    }

    updateProgress() {
        if (!this.options.showProgress) return;

        // Update step indicators
        this.progressSteps.forEach((step, index) => {
            const indicator = step.querySelector('.step-indicator');
            indicator.classList.remove('active', 'completed');
            
            if (index < this.currentStep) {
                indicator.classList.add('completed');
            } else if (index === this.currentStep) {
                indicator.classList.add('active');
            }
        });

        // Update progress bar
        const progress = ((this.currentStep + 1) / this.options.steps.length) * 100;
        if (this.progressBar) {
            this.progressBar.style.width = `${progress}%`;
        }
    }

    updateButtons() {
        // Previous button
        this.prevBtn.disabled = this.currentStep === 0;

        // Next button
        const isLastStep = this.currentStep === this.options.steps.length - 1;
        const currentStepConfig = this.options.steps[this.currentStep];
        
        if (isLastStep) {
            this.nextBtn.innerHTML = '<i class="material-icons">check</i> Finish';
            this.nextBtn.classList.remove('wizard-btn-primary');
            this.nextBtn.classList.add('wizard-btn-primary');
        } else if (currentStepConfig.type === 'success') {
            this.nextBtn.style.display = 'none';
        } else {
            this.nextBtn.innerHTML = 'Next <i class="material-icons">chevron_right</i>';
            this.nextBtn.classList.add('wizard-btn-primary');
            this.nextBtn.classList.remove('wizard-btn-secondary');
            this.nextBtn.style.display = 'flex';
        }

        // Disable next button if current step is success type
        if (currentStepConfig.type === 'success') {
            this.nextBtn.disabled = true;
        }
    }

    updateSummary() {
        if (this.currentStepSpan) {
            this.currentStepSpan.textContent = this.currentStep + 1;
        }
    }

    validateStep(stepIndex) {
        const step = this.options.steps[stepIndex];
        if (step.type !== 'form') {
            return true;
        }

        const form = this.container.querySelector(`.wizard-form[data-step="${stepIndex}"]`);
        const fields = form.querySelectorAll('.form-input, .form-select, .form-textarea');
        let isValid = true;

        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const fieldName = field.name;
        const fieldId = field.id;
        const errorElement = document.getElementById(`${fieldId}-error`);
        const validation = field.dataset.validation;
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Clear previous error
        field.classList.remove('error');
        if (errorElement) {
            errorElement.textContent = '';
        }

        // Required validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }

        // Type-specific validation
        if (value && validation) {
            switch (validation) {
                case 'email':
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(value)) {
                        isValid = false;
                        errorMessage = 'Please enter a valid email address';
                    }
                    break;

                case 'phone':
                    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
                    if (!phoneRegex.test(value) || value.length < 10) {
                        isValid = false;
                        errorMessage = 'Please enter a valid phone number';
                    }
                    break;

                case 'number':
                    if (isNaN(value) || parseFloat(value) < 0) {
                        isValid = false;
                        errorMessage = 'Please enter a valid number';
                    }
                    break;

                case 'date':
                    const date = new Date(value);
                    if (isNaN(date.getTime())) {
                        isValid = false;
                        errorMessage = 'Please enter a valid date';
                    }
                    break;
            }
        }

        // Show error if invalid
        if (!isValid) {
            field.classList.add('error');
            if (errorElement) {
                errorElement.textContent = errorMessage;
            }
        }

        // Store validation result
        if (!isValid) {
            this.validationErrors[fieldName] = errorMessage;
        } else {
            delete this.validationErrors[fieldName];
        }

        // Trigger validation callback
        if (this.options.onValidation) {
            this.options.onValidation(fieldName, value, isValid, errorMessage);
        }

        return isValid;
    }

    collectFormData(stepIndex) {
        const step = this.options.steps[stepIndex];
        if (step.type !== 'form') {
            return;
        }

        const form = this.container.querySelector(`.wizard-form[data-step="${stepIndex}"]`);
        const formData = new FormData(form);
        
        // Convert to regular object
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        // Store in overall form data
        this.formData = { ...this.formData, ...data };
    }

    nextStep() {
        const currentStepConfig = this.options.steps[this.currentStep];
        
        // Handle finish
        if (this.currentStep === this.options.steps.length - 1) {
            if (currentStepConfig.type === 'success') {
                return;
            }
            this.finish();
            return;
        }

        // Collect form data from current step
        this.collectFormData(this.currentStep);

        // Move to next step
        this.showStep(this.currentStep + 1);
    }

    previousStep() {
        if (this.currentStep > 0) {
            this.showStep(this.currentStep - 1);
        }
    }

    goToStep(stepIndex) {
        if (stepIndex >= 0 && stepIndex < this.options.steps.length) {
            // Collect data from all previous steps
            for (let i = 0; i < stepIndex; i++) {
                this.collectFormData(i);
            }
            
            this.showStep(stepIndex);
        }
    }

    populateReview(stepIndex) {
        const reviewContent = document.getElementById(`review-content-${stepIndex}`);
        if (!reviewContent) return;

        let reviewHtml = '';
        
        Object.keys(this.formData).forEach(key => {
            const value = this.formData[key];
            if (value) {
                reviewHtml += `
                    <div class="review-item">
                        <span class="review-label">${this.formatFieldName(key)}:</span>
                        <span class="review-value">${this.formatValue(value)}</span>
                    </div>
                `;
            }
        });

        reviewContent.innerHTML = reviewHtml;
    }

    formatFieldName(fieldName) {
        return fieldName.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    formatValue(value) {
        if (typeof value === 'boolean') {
            return value ? 'Yes' : 'No';
        }
        return value;
    }

    finish() {
        // Collect final form data
        this.collectFormData(this.currentStep);

        // Validate all steps
        let isValid = true;
        for (let i = 0; i < this.options.steps.length; i++) {
            if (!this.validateStep(i)) {
                isValid = false;
                this.goToStep(i);
                break;
            }
        }

        if (!isValid) {
            return;
        }

        // Show loading state
        this.isSubmitting = true;
        this.nextBtn.disabled = true;
        this.nextBtn.innerHTML = '<i class="material-icons">hourglass_empty</i> Submitting...';

        // Call finish callback
        if (this.options.onFinish) {
            this.options.onFinish(this.formData, () => {
                this.isSubmitting = false;
                this.nextBtn.disabled = false;
            });
        }
    }

    cancel() {
        if (confirm('Are you sure you want to cancel? All entered data will be lost.')) {
            // Reset form
            this.currentStep = 0;
            this.formData = {};
            this.validationErrors = {};
            this.showStep(0);
            
            // Clear form fields
            this.container.querySelectorAll('form').forEach(form => form.reset());
            
            // Clear errors
            this.container.querySelectorAll('.form-error').forEach(error => {
                error.textContent = '';
            });
            this.container.querySelectorAll('.form-input, .form-select, .form-textarea').forEach(field => {
                field.classList.remove('error');
            });
        }
    }

    // Public methods
    getFormData() {
        return this.formData;
    }

    setFormData(data) {
        this.formData = data;
    }

    getCurrentStep() {
        return this.currentStep;
    }

    goToNextStep() {
        this.nextStep();
    }

    goToPreviousStep() {
        this.previousStep();
    }

    reset() {
        this.currentStep = 0;
        this.formData = {};
        this.validationErrors = {};
        this.isSubmitting = false;
        this.showStep(0);
        
        // Reset forms
        this.container.querySelectorAll('form').forEach(form => form.reset());
        
        // Clear errors
        this.container.querySelectorAll('.form-error').forEach(error => {
            error.textContent = '';
        });
        this.container.querySelectorAll('.form-input, .form-select, .form-textarea').forEach(field => {
            field.classList.remove('error');
        });
    }

    destroy() {
        // Remove event listeners
        this.prevBtn.removeEventListener('click', this.previousStep);
        this.nextBtn.removeEventListener('click', this.nextStep);
        this.cancelBtn.removeEventListener('click', this.cancel);
        
        // Clear container
        this.container.innerHTML = '';
    }
}

// Export for global use
window.FormWizard = FormWizard;
