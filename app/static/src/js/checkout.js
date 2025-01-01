import feather from 'feather-icons';

document.addEventListener('alpine:init', () => {
    Alpine.data('checkoutForm', () => ({
        cart: [],
        billing: {
            name: '',
            email: '',
            phone: '',
            city: '',
            address: ''
        },
        paymentMethod: 'mobile_money',
        acceptedTerms: false,
        loading: false,
        error: null,

        init() {
            const savedCart = localStorage.getItem('bookingCart');
            this.cart = savedCart ? JSON.parse(savedCart) : [];
            
            this.$nextTick(() => {
                feather.replace();
            });
        },

        get totalAmount() {
            return this.cart.reduce((sum, item) => sum + item.total_amount, 0);
        },

        get canCheckout() {
            return this.cart.length > 0 && 
                   this.acceptedTerms &&
                   !this.loading;
        },

        formatCurrency(amount) {
            return new Intl.NumberFormat('en-UG').format(amount);
        },

        formatDate(dateString) {
            return new Date(dateString).toLocaleDateString('en-UG', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        },

        removeFromCart(equipmentId) {
            this.cart = this.cart.filter(item => item.equipment_id !== equipmentId);
            localStorage.setItem('bookingCart', JSON.stringify(this.cart));
            this.showNotification('Item removed from cart');
            feather.replace();
        },

        async submitCheckout() {
            if (!this.canCheckout) return;

            this.loading = true;
            this.error = null;

            try {
                const orderData = {
                    billing: this.billing,
                    payment_method: this.paymentMethod,
                    items: this.cart,
                    total_amount: this.totalAmount
                };

                const response = await fetch('/api/orders', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(orderData)
                });

                if (!response.ok) {
                    throw new Error('Failed to process order');
                }

                const result = await response.json();

                // Clear cart after successful order
                localStorage.removeItem('bookingCart');
                
                // Redirect to confirmation page
                window.location.href = `/order-confirmation/${result.order_id}`;
            } catch (error) {
                this.error = 'Failed to process your order. Please try again.';
                this.showNotification(this.error, 'error');
            } finally {
                this.loading = false;
            }
        },

        showNotification(message, type = 'success') {
            const notification = document.createElement('div');
            notification.className = `notification notification--${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);

            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
    }));
});