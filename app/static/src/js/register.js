// registration.js
document.addEventListener('alpine:init', () => {
    Alpine.data('registration', () => ({
        form: {
            name: '',
            email: '',
            password: '',
            passwordConfirmation: '',
            agreement: false,
            phone: '',
            company: ''
        },
        errors: {},
        error: null,
        isSubmitting: false,

        init() {
            this.$watch('form', () => {
                this.clearErrors();
            });
        },

        async handleSubmit() {
            this.clearErrors();
            
            if (!this.validateForm()) {
                return;
            }

            this.isSubmitting = true;

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: this.form.name,
                        email: this.form.email,
                        password: this.form.password,
                        phone: this.form.phone,
                        company: this.form.company
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    switch (response.status) {
                        case 409:
                            this.errors.email = 'This email is already registered';
                            break;
                        case 400:
                            this.handleValidationErrors(data);
                            break;
                        default:
                            throw new Error(data.msg || 'Registration failed');
                    }
                    return;
                }

                if (data.tokens) {
                    // Store tokens
                    this.storeAuthTokens(data.tokens);
                    // Redirect to dashboard
                    window.location.href = '/dashboard';
                }
            } catch (error) {
                this.error = error.message;
            } finally {
                this.isSubmitting = false;
            }
        },

        validateForm() {
            let isValid = true;

            // Name validation
            if (!this.form.name.trim()) {
                this.errors.name = 'Name is required';
                isValid = false;
            } else if (this.form.name.length < 2) {
                this.errors.name = 'Name must be at least 2 characters';
                isValid = false;
            }

            // Email validation
            if (!this.form.email.trim()) {
                this.errors.email = 'Email is required';
                isValid = false;
            } else if (!this.isValidEmail(this.form.email)) {
                this.errors.email = 'Please enter a valid email';
                isValid = false;
            }

            // Password validation
            if (!this.form.password) {
                this.errors.password = 'Password is required';
                isValid = false;
            } else if (!this.isValidPassword(this.form.password)) {
                this.errors.password = 'Password must be at least 8 characters and contain at least one number';
                isValid = false;
            }

            // Password confirmation validation
            if (this.form.password !== this.form.passwordConfirmation) {
                this.errors.passwordConfirmation = 'Passwords do not match';
                isValid = false;
            }

            // Agreement validation
            if (!this.form.agreement) {
                this.errors.agreement = 'You must agree to the terms';
                isValid = false;
            }

            return isValid;
        },

        isValidEmail(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        },

        isValidPassword(password) {
            return password.length >= 8 && /\d/.test(password);
        },

        handleValidationErrors(data) {
            // Handle specific field errors from API
            if (data.errors) {
                Object.keys(data.errors).forEach(field => {
                    this.errors[field] = data.errors[field];
                });
            } else {
                this.error = data.msg || 'Validation failed';
            }
        },

        storeAuthTokens(tokens) {
            localStorage.setItem('access_token', tokens.access_token);
            localStorage.setItem('refresh_token', tokens.refresh_token);
        },

        clearErrors() {
            // Only clear field-specific errors when fields change
            if (Object.keys(this.errors).length > 0) {
                this.errors = {};
            }
            // Clear general error message
            if (this.error) {
                this.error = null;
            }
        }
    }));
});