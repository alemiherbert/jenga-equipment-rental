import Alpine from "alpinejs";

document.addEventListener('alpine:init', () => {
    Alpine.store('auth', {
        tokens: {
            access: localStorage.getItem('access_token'),
            refresh: localStorage.getItem('refresh_token')
        },

        init() {
            // Intercept all fetch requests, and add token
            const originalFetch = window.fetch;
            window.fetch = async function (...args) {
                let [url, options = {}] = args;
                console.log("Fetch called with args: ", args)

                const token = localStorage.getItem('access_token');
                if (token) {
                    options.headers = {
                        ...options.headers,
                        'Authorization': `Bearer ${token}`
                    };
                }

                const response = await originalFetch(url, options);

                // If unauthorized, redirect to login
                // if (response.status === 401) {
                //     window.location.href = '/login';
                // }

                return response;
            };
        },

        clearTokens() {
            this.tokens = { access: null, refresh: null };
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        },

        isAuthenticated() {
            return !!this.tokens.access;
        }
    });
});


// User state management
Alpine.data('userState', () => ({
    userName: 'guest',
    
    init() {
        if (Alpine.store('auth').isAuthenticated()) {
            this.checkAuthStatus();
        }
    },

    async checkAuthStatus() {
        try {
            const response = await fetch('/api/users/me');
            if (!response.ok) throw new Error('Auth failed');
            const data = await response.json();
            this.userName = data.name;
        } catch (error) {
            console.error('Auth check failed:', error);
            this.userName = 'guest';
        }
    }
}));

