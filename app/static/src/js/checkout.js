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
                const bookingPromises = this.cart.map(async (item) => {
                    const bookingData = {
                        equipment_id: item.equipment_id,
                        start_date: item.start_date,
                        end_date: item.end_date,
                    };
                    console.log(bookingData);
        
                    const bookingResponse = await fetch('/api/bookings', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(bookingData)
                    });
        
                    if (!bookingResponse.ok) {
                        throw new Error('Failed to create booking');
                    }
        
                    return bookingResponse.json();
                });
        
                // Wait for all bookings to be created
                const bookingResults = await Promise.all(bookingPromises);
        
                // Process payment
                const paymentResponse = await fetch('/api/payments', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        booking_id: bookingResults[0].booking_id,
                        rental_amount: bookingResults[0].rental_amount,
                        transport_amount: bookingResults[0].transport_amount,
                        total_amount: bookingResults[0].total_amount,
                        card_details: this.paymentDetails
                    })
                });
        
                if (!paymentResponse.ok) {
                    throw new Error('Failed to process payment');
                }
        
                const paymentResult = await paymentResponse.json();
        
                // Redirect to payment confirmation page
                window.location.href = `/payment-confirmation/${paymentResult.payment_reference}`;
            } catch (error) {
                this.error = 'Failed to process your order. Please try again.';
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
