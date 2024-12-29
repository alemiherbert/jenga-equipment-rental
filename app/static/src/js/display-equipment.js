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
            availabilty: '',
            transport_cost_per_km: 0
        },
        loading: true,
        error: null,
        showBookingForm: false,
        booking: {
            startDate: '',
            endDate: '',
            distance: 0
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
        },
        get today() {
            return new Date().toISOString().split('T')[0];
        },

        get totalDays() {
            if (!this.booking.startDate || !this.booking.endDate) return 0;
            const start = new Date(this.booking.startDate);
            const end = new Date(this.booking.endDate);
            const diff = end - start;
            return Math.ceil(diff / (1000 * 60 * 60 * 24));
        },

        get equipmentCost() {
            return this.totalDays * this.equipment.price_per_day;
        },

        get transportCost() {
            return this.booking.distance * this.equipment.transport_cost_per_km * 2; // Round trip
        },

        get totalCost() {
            return this.equipmentCost + this.transportCost;
        },

        get isValidBooking() {
            return this.booking.startDate &&
                this.booking.endDate &&
                this.booking.distance >= 0 &&
                new Date(this.booking.endDate) >= new Date(this.booking.startDate);
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
                this.equipment = data;
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

        async submitBooking() {
            if (!this.isValidBooking) return;

            this.loading = true;
            this.error = null;

            try {
                const response = await fetch('/api/bookings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        equipment_id: this.equipment.id,
                        start_date: this.booking.startDate,
                        end_date: this.booking.endDate,
                        distance: this.booking.distance,
                        equipment_cost: this.equipmentCost,
                        transport_cost: this.transportCost,
                        total_amount: this.totalCost
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || 'Booking failed');
                }

                window.location.href = '/bookings/success';
            } catch (error) {
                this.error = error.message || 'Failed to create booking. Please try again.';
            } finally {
                this.loading = false;
            }
        }
    }));
});