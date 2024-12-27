import feather from 'feather-icons';

export default () => ({
    equipment: [],
    loading: false,
    error: null,

    init() {
        this.fetchEquipment();
        this.$watch('equipment', () => {
            feather.replace();
            console.log('fdkjgbkjfdbbgkdjf b')
        });
    },

    async fetchEquipment() {
        this.loading = true;
        this.error = null;

        try {
            const response = await fetch('/api/equipment');
            if (!response.ok) {
                throw new Error('Failed to fetch equipment');
            }
            const data = await response.json();
            this.equipment = data.items.map(item => ({
                id: item.id,
                name: item.name,
                category: item.category,
                location: item.location || "Kampala",
                image: "/static/dist/img/hero.jpg",
                dayRate: item.price_per_day,
                available: item.status === "available",
                isNew: false
            }));
        } catch (error) {
            this.error = error.message;
            console.error('Error fetching equipment:', error);
        } finally {
            this.loading = false;
        }
    }
});
