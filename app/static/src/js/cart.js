import feather from 'feather-icons';

document.addEventListener('alpine:init', () => {
    Alpine.data('cartDisplay', () => ({
        cart: [],

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

        removeItem(equipmentId) {
            this.cart = this.cart.filter(item => item.equipment_id !== equipmentId);
            localStorage.setItem('bookingCart', JSON.stringify(this.cart));
            this.showNotification('Item removed from cart');
            feather.replace();
        },

        checkout() {
            console.log('Proceeding to checkout with items:', this.cart);
            window.location.href = '/checkout';
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