// featured-equipment-carousel.js
document.addEventListener('alpine:init', () => {
    Alpine.data('featuredEquipment', () => {
        // Get base carousel functionality
        const baseCarousel = Alpine.data('carousel')();
        
        return {
            // Spread base carousel properties
            ...baseCarousel,
            
            // Featured equipment specific state
            equipment: [],
            loading: true,
            error: null,
            autoplayInterval: null,

            async init() {
                // Initialize with base carousel's init if it exists
                if (typeof baseCarousel.init === 'function') {
                    baseCarousel.init.call(this);
                }
                
                await this.fetchEquipment();
                this.startAutoplay();
            },

            // Keep the base carousel's handleScroll method
            handleScroll(event) {
                if (typeof baseCarousel.handleScroll === 'function') {
                    baseCarousel.handleScroll.call(this, event);
                }
                this.scroll = event.target.scrollLeft;
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
                    
                    // After loading equipment, recalculate carousel scroll width
                    this.$nextTick(() => {
                        this.maxScroll = this.$refs.container.scrollWidth - this.$refs.container.clientWidth;
                    });
                } catch (err) {
                    this.error = 'Unable to load featured equipment. Please try again later.';
                    console.error('Error fetching equipment:', err);
                } finally {
                    this.loading = false;
                }
            },

            startAutoplay() {
                this.autoplayInterval = setInterval(() => {
                    if (!document.hidden && this.scroll < this.maxScroll) {
                        this.scrollNext();
                    } else if (!document.hidden) {
                        // Reset to start if we've reached the end
                        this.$refs.container.scrollTo({ left: 0, behavior: 'smooth' });
                        this.scroll = 0;
                    }
                }, 5000);
            },

            stopAutoplay() {
                if (this.autoplayInterval) {
                    clearInterval(this.autoplayInterval);
                }
            },

            // Override scroll methods while maintaining base functionality
            scrollPrev() {
                this.stopAutoplay();
                if (typeof baseCarousel.scrollPrev === 'function') {
                    baseCarousel.scrollPrev.call(this);
                }
            },

            scrollNext() {
                if (typeof baseCarousel.scrollNext === 'function') {
                    baseCarousel.scrollNext.call(this);
                }
            },

            rentEquipment(item) {
                this.stopAutoplay();
                window.location.href = `/rent/${item.id}`;
            },

            viewDetails(item) {
                this.stopAutoplay();
                window.location.href = `/equipment/${item.id}`;
            },

            // Cleanup
            destroy() {
                this.stopAutoplay();
                if (typeof baseCarousel.destroy === 'function') {
                    baseCarousel.destroy.call(this);
                }
            }
        };
    });
});