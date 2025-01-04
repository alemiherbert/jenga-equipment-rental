import feather from 'feather-icons';

export default () => ({
    equipment: [],
    loading: false,
    error: null,
    autoplayInterval: null,
    scroll: 0,
    maxScroll: 0,
    isAutoplayEnabled: true,

    init() {
        this.fetchFeaturedEquipment();

        this.$nextTick(() => {
            this.updateMaxScroll();
            if (this.isAutoplayEnabled) {
                this.startAutoplay();
            }
        });

        this.$watch('equipment', () => {
            this.$nextTick(() => {
                this.updateMaxScroll();
            });
            feather.replace();
        });

        window.addEventListener('resize', () => {
            this.updateMaxScroll();
        });

        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopAutoplay();
            } else if (this.isAutoplayEnabled) {
                this.startAutoplay();
            }
        });

        this.$refs.container.addEventListener('mouseenter', () => {
            this.stopAutoplay();
        });

        this.$refs.container.addEventListener('mouseleave', () => {
            if (this.isAutoplayEnabled) {
                this.startAutoplay();
            }
        });

        this.$watch('scroll', value => {
            this.$refs.container.scrollTo({
                left: value,
                behavior: 'smooth'
            });
        });
    },

    async fetchFeaturedEquipment() {
        this.loading = true;
        this.error = null;

        try {
            const response = await fetch('/api/equipment/featured');
            if (!response.ok) {
                throw new Error('Failed to fetch featured equipment');
            }
            const data = await response.json();

            this.equipment = data.featured_equipment.map(item => ({
                id: item.id,
                name: item.name,
                category: item.category,
                image: item.image ? `/uploads/${item.image}` : 'https://picsum.photos/600/400',
                location: item.location || "Kampala",
                dayRate: item.price_per_day,
                available: item.status === "available",
                isNew: false
            }));
        } catch (error) {
            this.error = error.message;
            console.error('Error fetching featured equipment:', error);
        } finally {
            this.loading = false;
        }
    },

    updateMaxScroll() {
        if (this.$refs.container) {
            this.maxScroll = this.$refs.container.scrollWidth - this.$refs.container.clientWidth;
        }
    },

    scrollPrev() {
        this.stopAutoplay();
        this.scroll = Math.max(0, this.scroll - 300);
    },

    scrollNext() {
        this.scroll = Math.min(this.maxScroll, this.scroll + 300);
    },

    handleScroll(event) {
        this.scroll = event.target.scrollLeft;
    },

    startAutoplay() {
        this.stopAutoplay();
        this.autoplayInterval = setInterval(() => {
            if (!document.hidden) {
                if (this.scroll >= this.maxScroll) {
                    this.scroll = 0;
                } else {
                    this.scrollNext();
                }
            }
        }, 3000);
    },

    stopAutoplay() {
        if (this.autoplayInterval) {
            clearInterval(this.autoplayInterval);
            this.autoplayInterval = null;
        }
    },

    rentEquipment(item) {
        this.stopAutoplay();
        window.location.href = `/rent/${item.id}`;
    },

    viewDetails(item) {
        this.stopAutoplay();
        window.location.href = `/equipment/${item.id}`;
    }
});