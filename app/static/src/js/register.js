// registration.js
document.addEventListener('alpine:init', () => {
    Alpine.data('registration', () => ({
        form: {
            name: '',
            email: '',
            phone: '',
            company: '',
            password: '',
            passwordConfirmation: '',
            agreement: false
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
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        name: this.form.name,
                        email: this.form.email,
                        phone: this.form.phone,
                        company: this.form.company,
                        password: this.form.password
                    })
                });

                let data;
                try {
                    data = await response.json();
                } catch (e) {
                    throw new Error('Invalid JSON response from server');
                }

                if (!response.ok) {
                    switch (response.status) {
                        case 409:
                            this.errors.email = 'This email is already registered';
                            break;
                        case 400:
                            this.handleValidationErrors(data);
                            break;
                        case 500:
                            throw new Error('Server error. Please try again later.');
                        default:
                            throw new Error(data.msg || 'Registration failed');
                    }
                    return;
                }

                if (data.tokens) {
                    this.storeAuthTokens(data.tokens);
                    window.location.href = '/home';
                } else {
                    throw new Error('Invalid server response: missing tokens');
                }
            } catch (error) {
                // Log the error for debugging
                console.error('Registration error:', error);
                
                // Set user-friendly error message
                this.error = error.message || 'An unexpected error occurred. Please try again.';
                
                // Handle specific network errors
                if (error instanceof TypeError && error.message === 'Failed to fetch') {
                    this.error = 'Unable to connect to the server. Please check your internet connection.';
                }
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

            // Phone validation
            if (!this.form.phone.trim()) {
                this.errors.phone = 'Phone number is required';
                isValid = false;
            } else if (!this.isValidPhone(this.form.phone)) {
                this.errors.phone = 'Please enter a valid phone number';
                isValid = false;
            }

            // Company name validation
            if (!this.form.company.trim()) {
                this.errors.company = 'Company name is required';
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

        isValidPhone(phone) {
            return /^\+?[\d\s-]{10,}$/.test(phone);
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