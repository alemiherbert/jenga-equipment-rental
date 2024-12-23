export default () => ({
    equipment: [
        {
            "id": "123",
            "name": "20\" Chainsaw",
            "category": "Power Tools",
            "image": "/static/dist/img/hero.jpg",
            "dayRate": 45.00,
            "available": true,
            "isNew": false
        },
        {
            "id": "13",
            "name": "20\" Chainsaw",
            "category": "Power Tools",
            "image": "/static/dist/img/hero.jpg",
            "dayRate": 45.00,
            "available": true,
            "isNew": false
        },
        {
            "id": "23",
            "name": "20\" Chainsaw",
            "category": "Power Tools",
            "image": "/static/dist/img/hero.jpg",
            "dayRate": 45.00,
            "available": true,
            "isNew": false
        },
        {
            "id": "1263",
            "name": "20\" Chainsaw",
            "category": "Power Tools",
            "image": "/static/dist/img/hero.jpg",
            "dayRate": 45.00,
            "available": true,
            "isNew": false
        },
        {
            "id": "12638",
            "name": "20\" Chainsaw",
            "category": "Power Tools",
            "image": "/static/dist/img/hero.jpg",
            "dayRate": 45.00,
            "available": true,
            "isNew": false
        }
    ],
    loading: true,
    error: null,
    autoplayInterval: null,
    scroll: 0,
    maxScroll: 0,
    scrollAmount: 300,

    init() {
        this.$nextTick(() => {
            this.updateMaxScroll();
        });

        this.$watch('equipment', () => {
            this.$nextTick(() => {
                this.updateMaxScroll();
            });
        });

        window.addEventListener('resize', () => {
            this.updateMaxScroll();
        });

        this.$watch('scroll', value => {
            this.$refs.container.scrollTo({
                left: value,
                behavior: 'smooth'
            });
        });

        // Start autoplay after initialization
        this.startAutoplay();
    },

    updateMaxScroll() {
        if (this.$refs.container) {
            this.maxScroll = this.$refs.container.scrollWidth - this.$refs.container.clientWidth;
        }
    },

    scrollPrev() {
        if (this.scroll === 0) {
            // If at the start, jump to end
            this.scroll = this.maxScroll;
        } else {
            this.scroll = Math.max(0, this.scroll - this.scrollAmount);
        }
    },

    scrollNext() {
        if (this.scroll >= this.maxScroll) {
            // If at the end, smoothly reset to start
            this.scroll = 0;
        } else {
            this.scroll = Math.min(this.maxScroll, this.scroll + this.scrollAmount);
        }
    },

    handleScroll(event) {
        this.scroll = event.target.scrollLeft;
    },

    startAutoplay() {
        this.autoplayInterval = setInterval(() => {
            if (!document.hidden) {
                this.scrollNext();
            }
        }, 5000); // Rotate every 5 seconds

        // Stop autoplay when tab is not visible
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopAutoplay();
            } else {
                this.startAutoplay();
            }
        });

        // Stop autoplay on user interaction
        this.$refs.container.addEventListener('mouseenter', () => this.stopAutoplay());
        this.$refs.container.addEventListener('mouseleave', () => this.startAutoplay());
        this.$refs.container.addEventListener('touchstart', () => this.stopAutoplay());
        this.$refs.container.addEventListener('touchend', () => this.startAutoplay());
    },

    stopAutoplay() {
        if (this.autoplayInterval) {
            clearInterval(this.autoplayInterval);
            this.autoplayInterval = null;
        }
    },

    async fetchEquipment() {
        this.loading = true;
        this.error = null;

        try {
            const response = await fetch('/api/featured-equipment');
            if (!response.ok) {
                throw new Error('Failed to fetch equipment');
            }

            this.equipment = await response.json();

            this.$nextTick(() => {
                this.updateMaxScroll();
            });
        } catch (err) {
            this.error = 'Unable to load featured equipment. Please try again later.';
            console.error('Error fetching equipment:', err);
        } finally {
            this.loading = false;
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