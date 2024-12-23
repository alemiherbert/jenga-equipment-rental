export default () => ({
        equipment: [
            {
                "id": "7451",
                "name": "15\" Circular Saw",
                "category": "Power Tools",
                "image": "/static/dist/img/hero.jpg",
                "dayRate": 45.00,
                "available": false,
                "isNew": false
            },
            {
                "id": "5849",
                "name": "18\" Electric Drill",
                "category": "Power Tools",
                "image": "/static/dist/img/hero.jpg",
                "dayRate": 45.00,
                "available": true,
                "isNew": true
            },
            {
                "id": "9037",
                "name": "12\" Angle Grinder",
                "category": "Power Tools",
                "image": "/static/dist/img/hero.jpg",
                "dayRate": 45.00,
                "available": true,
                "isNew": false
            },
            {
                "id": "3094",
                "name": "8\" Hammer Drill",
                "category": "Power Tools",
                "image": "/static/dist/img/hero.jpg",
                "dayRate": 45.00,
                "available": true,
                "isNew": false
            },
            {
                "id": "8272",
                "name": "10\" Jigsaw",
                "category": "Power Tools",
                "image": "/static/dist/img/hero.jpg",
                "dayRate": 45.00,
                "available": true,
                "isNew": false
            }
        ],
        loading: false,
        error: null,
        autoplayInterval: null,
        scroll: 0,
        maxScroll: 0,
        isAutoplayEnabled: true,
    
        init() {
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