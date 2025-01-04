import feather from 'feather-icons';

document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentDetails', () => ({
        equipment: {
            category: '',
            featured: false,
            id: null,
            location: '',
            name: '',
            price_per_day: 0,
            status: '',
            image: '',
            transport_cost_per_km: 0
        },
        loading: true,
        error: null,
        dateError: null,
        showBookingForm: false,
        booking: {
            startDate: '',
            endDate: ''
        },
        cart: [],

        get today() {
            return new Date().toISOString().split('T')[0];
        },

        init() {
            const pathSegments = window.location.pathname.split('/');
            const equipmentId = pathSegments[pathSegments.length - 1];

            if (!equipmentId) {
                this.error = 'Equipment ID not found';
                this.loading = false;
                return;
            }

            this.fetchEquipmentDetails(equipmentId);

            const savedCart = localStorage.getItem('bookingCart');
            this.cart = savedCart ? JSON.parse(savedCart) : [];
        },

        get isEquipmentInCart() {
            return this.cart.some(item => item.equipment_id === this.equipment.id);
        },

        get isEquipmentAvailable() {
            return this.equipment.status === 'available';
        },

        get canAddToCart() {
            return this.isValidBooking &&
                !this.isEquipmentInCart &&
                this.isEquipmentAvailable &&
                !this.dateError;
        },

        validateDates() {
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            const startDate = new Date(this.booking.startDate);
            const endDate = new Date(this.booking.endDate);

            if (startDate < today) {
                this.dateError = 'Start date cannot be in the past';
                return false;
            }

            if (endDate < startDate) {
                this.dateError = 'End date must be after start date';
                return false;
            }

            this.dateError = null;
            return true;
        },

        get totalDays() {
            if (!this.booking.startDate || !this.booking.endDate) return 0;
            const start = new Date(this.booking.startDate);
            const end = new Date(this.booking.endDate);
            const diff = end - start;
            return Math.ceil(diff / (1000 * 60 * 60 * 24)) + 1;
        },

        get equipmentCost() {
            return this.totalDays * this.equipment.price_per_day;
        },

        get transportCost() {
            return 100000; // Flat transportation cost for now
        },

        get totalCost() {
            return this.equipmentCost + this.transportCost;
        },

        get isValidBooking() {
            return this.booking.startDate &&
                this.booking.endDate &&
                this.validateDates();
        },

        formatCurrency(amount) {
            return new Intl.NumberFormat('en-UG').format(amount);
        },

        async fetchEquipmentDetails(equipmentId) {
            this.loading = true;
            this.error = null;

            try {
                const response = await fetch(`/api/equipment/${equipmentId}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch equipment details');
                }
                const data = await response.json();

                this.equipment = {
                    ...data,
                    image: data.image ? `/uploads/${data.image}` : 'https://picsum.photos/600/400'
                };
            } catch (error) {
                this.error = 'Unable to load equipment details. Please try again later.';
                console.error('Error:', error);
            } finally {
                this.loading = false;
                this.$nextTick(() => {
                    feather.replace();
                });
            }
        },

        addToCart() {
            if (!this.canAddToCart) return;

            const cartItem = {
                equipment_id: this.equipment.id,
                equipment_name: this.equipment.name,
                start_date: this.booking.startDate,
                end_date: this.booking.endDate,
                image: this.equipment.image,
                equipment_cost: this.equipmentCost,
                transport_cost: this.transportCost,
                total_amount: this.totalCost
            };
            

            this.cart.push(cartItem);
            localStorage.setItem('bookingCart', JSON.stringify(this.cart));
            this.showNotification('Equipment added to cart successfully', 'success');
            this.resetForm();
        },

        removeFromCart() {
            this.cart = this.cart.filter(item => item.equipment_id !== this.equipment.id);
            localStorage.setItem('bookingCart', JSON.stringify(this.cart));
            this.showNotification('Equipment removed from cart', 'success');
        },

        viewCart() {
            window.location.href = '/cart';
        },

        resetForm() {
            this.booking = {
                startDate: '',
                endDate: ''
            };
            this.dateError = null;
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