document.addEventListener('alpine:init', () => {
    Alpine.data('authComponent', () => ({
        isAuthenticated: false,

        async checkAuthStatus() {
            try {
                const response = await fetch('/api/users/me', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });

                if (!response.ok) throw new Error('Not logged in');
                const data = await response.json();
                this.isAuthenticated = true;
            } catch (error) {
                console.warn('Authentication check failed:', error);
                this.isAuthenticated = false;
            }
        },

        logout() {
            const token = localStorage.getItem('access_token');
            fetch('/logout', {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            })
                .then(() => {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    this.isAuthenticated = false;
                    window.location.reload();
                })
                .catch((error) => console.error('Logout failed:', error));
        }
    }));

    // User Component for Displaying Name
    Alpine.data('userComponent', () => ({
        userName: 'Guest',

        async fetchUser() {
            try {
                const response = await fetch('/api/users/me', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });

                if (!response.ok) throw new Error('Not logged in');
                const data = await response.json();
                this.userName = data.name || 'User';
            } catch (error) {
                console.warn('Unable to fetch user:', error);
                this.userName = 'Guest';
            }
        }
    }));
});