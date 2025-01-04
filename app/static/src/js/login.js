// login.js
document.addEventListener('alpine:init', () => {
    Alpine.data('login', () => ({
        form: {
            email: '',
            password: '',
            remember: false
        },
        error: null,
        errors: {},
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
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        email: this.form.email,
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
                        case 401:
                            this.error = 'Invalid email or password';
                            break;
                        case 400:
                            this.error = data.msg || 'Missing required fields';
                            break;
                        case 500:
                            throw new Error('Server error. Please try again later.');
                        default:
                            throw new Error(data.msg || 'Login failed');
                    }
                    return;
                }

                if (data.access_token && data.refresh_token) {
                    this.storeAuthTokens(data);
                    
                    // Handle remember me
                    if (this.form.remember) {
                        localStorage.setItem('remember_token', data.access_token);
                    }
                    
                    window.location.href = '/';
                } else {
                    throw new Error('Invalid server response: missing tokens');
                }
            } catch (error) {
                console.error('Login error:', error);
                
                this.error = error.message || 'An unexpected error occurred. Please try again.';
                
                if (error instanceof TypeError && error.message === 'Failed to fetch') {
                    this.error = 'Unable to connect to the server. Please check your internet connection.';
                }
            } finally {
                this.isSubmitting = false;
            }
        },

        validateForm() {
            let isValid = true;

            if (!this.form.email.trim()) {
                this.errors.email = 'Email is required';
                isValid = false;
            } else if (!this.isValidEmail(this.form.email)) {
                this.errors.email = 'Please enter a valid email';
                isValid = false;
            }

            if (!this.form.password) {
                this.errors.password = 'Password is required';
                isValid = false;
            }

            return isValid;
        },

        isValidEmail(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        },

        storeAuthTokens(tokens) {
            localStorage.setItem('access_token', tokens.access_token);
            localStorage.setItem('refresh_token', tokens.refresh_token);
        },

        clearErrors() {
            if (Object.keys(this.errors).length > 0) {
                this.errors = {};
            }
            if (this.error) {
                this.error = null;
            }
        }
    }));
});