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
        paymentMethod: 'pesa-pay',
        paymentDetails: {
            cardNumber: '',
            expiryMonth: '',
            expiryYear: '',
            cvv: '',
            cardholderName: ''
        },
        acceptedTerms: false,
        loading: false,
        error: null,

        init() {
            this.loadCart();
            this.$nextTick(() => feather.replace());
        },

        loadCart() {
            const savedCart = localStorage.getItem('bookingCart');
            this.cart = savedCart ? JSON.parse(savedCart) : [];
        },

        get totalAmount() {
            return this.cart.reduce((sum, item) => sum + item.total_amount, 0);
        },

        get canCheckout() {
            return this.cart.length > 0 && this.acceptedTerms && !this.loading;
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
            this.$nextTick(() => feather.replace());
        },

        validatePaymentDetails() {
            if (this.paymentMethod === 'pesa-pay') {
                const { cardNumber, expiryMonth, expiryYear, cvv, cardholderName } = this.paymentDetails;
                console.log(this.paymentDetails);
                if (!cardNumber || !expiryMonth || !expiryYear || !cvv || !cardholderName) {
                    return 'Please fill in all payment details.';
                }
                if (cardNumber.length !== 16 || !/^\d+$/.test(cardNumber)) {
                    return 'Invalid card number.';
                }
                if (expiryMonth.length !== 2 || expiryYear.length !== 4 || !/^\d+$/.test(expiryMonth) || !/^\d+$/.test(expiryYear)) {
                    return 'Invalid expiry date.';
                }
                if (cvv.length !== 3 || !/^\d+$/.test(cvv)) {
                    return 'Invalid CVV.';
                }
            }
            return null;
        },

        async submitCheckout() {
            if (!this.canCheckout) return;

            const paymentValidationError = this.validatePaymentDetails();
            if (paymentValidationError) {
                this.showNotification(paymentValidationError, 'error');
                return;
            }

            this.loading = true;
            this.error = null;

            try {
                // Load cart from local storage
                const cart = JSON.parse(localStorage.getItem('bookingCart') || '[]');
                if (cart.length === 0) {
                    throw new Error('Your cart is empty. Please add equipment to proceed.');
                }

                // Prepare payload for multiple bookings
                const bookingsPayload = cart.map(item => ({
                    equipment_id: item.equipment_id,
                    start_date: item.start_date,
                    end_date: item.end_date,
                    distance_km: item.distance_km || 0
                }));

                // Create multiple bookings at once
                const bookingsResponse = await fetch('/api/bookings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ bookings: bookingsPayload })
                });

                if (!bookingsResponse.ok) {
                    const errorResponse = await bookingsResponse.json();
                    console.error('Bookings Error:', errorResponse);
                    throw new Error('Failed to create bookings');
                }

                const bookingsResult = await bookingsResponse.json();

                const paymentPayload = {
                    booking_ids: bookingsResult.bookings.map(booking => booking.id),
                    total_amount: this.totalAmount,
                    billing: this.billing,
                    card_details: {
                        card_number: this.paymentDetails.cardNumber,
                        expiry_month: this.paymentDetails.expiryMonth,
                        expiry_year: this.paymentDetails.expiryYear,
                        cvv: this.paymentDetails.cvv,
                        cardholder_name: this.paymentDetails.cardholderName
                    }
                };

                const paymentResponse = await fetch('/api/payments', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(paymentPayload)
                });

                if (!paymentResponse.ok) {
                    const errorResponse = await paymentResponse.json();
                    console.error('Payment Error:', errorResponse);
                    throw new Error('Failed to process payment');
                }

                const paymentResult = await paymentResponse.json();

                // Redirect to payment confirmation page
                window.location.href = `/`;

                // Clear cart after successful payment
                localStorage.removeItem('bookingCart');
            } catch (error) {
                this.error = error.message || 'Failed to process your order. Please try again.';
                this.showNotification(this.error, 'error');
            } finally {
                this.loading = false;
            }
        },

        // Show notification
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
