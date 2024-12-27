import feather from 'feather-icons';

export default () => ({
    equipment: [],
    loading: false,
    error: null,
    page: 1,
    totalPages: 1,
    breadcrumb: 'All',
    search: '',
    formData: {
        location: 'All',
        category: 'All'
    },
    filters: [],

    init() {
        this.fetchEquipment();
        this.$watch('equipment', () => {
            feather.replace();
        });
        this.$watch('search', () => {
            this.page = 1;
            this.fetchEquipment();
        });
        this.$watch('formData', () => {
            this.submitForm(this.formData);
        }, { deep: true });
    },

    async fetchEquipment() {
        this.loading = true;
        this.error = null;

        try {
            const params = new URLSearchParams({
                page: this.page,
                per_page: 12
            });

            if (this.search) {
                params.append('search', this.search);
            }

            if (this.formData.location !== 'All') {
                params.append('location', this.formData.location);
            }

            if (this.formData.category !== 'All') {
                params.append('category', this.formData.category);
            }

            const response = await fetch(`/api/equipment?${params.toString()}`);
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
            this.totalPages = data._meta.total_pages;
            this.updateBreadcrumb();
        } catch (error) {
            this.error = error.message;
            console.error('Error fetching equipment:', error);
        } finally {
            this.loading = false;
        }
    },

    submitForm(formData) {
        this.filters = [];
        if (formData.location !== 'All') {
            this.filters.push(`Location: ${formData.location}`);
        }
        if (formData.category !== 'All') {
            this.filters.push(`Category: ${formData.category}`);
        }

        this.page = 1;
        console.log(this.filters);
        this.fetchEquipment();
    },

    updateBreadcrumb() {
        if (this.filters.length > 0) {
            this.breadcrumb = this.filters.join(', ');
        } else if (this.page > 1) {
            this.breadcrumb = `Page ${this.page}`;
        } else {
            this.breadcrumb = 'All';
        }
    },

    prevPage() {
        if (this.page > 1) {
            this.page--;
            this.fetchEquipment();
        }
    },

    nextPage() {
        if (this.page < this.totalPages) {
            this.page++;
            this.fetchEquipment();
        }
    },

    resetFilters() {
        this.formData = {
            location: 'All',
            category: 'All'
        };
        this.filters = [];
        this.page = 1;
        this.fetchEquipment();
    }
});
