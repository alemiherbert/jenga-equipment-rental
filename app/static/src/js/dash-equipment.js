import { data } from 'alpinejs';
import feather from 'feather-icons';

document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentDataTable', (dataSource, filterParams) => ({
        curPage: 1,
        filters: [],
        formData: {
            location: 'All',
            category: 'All',
            status: 'All'
        },
        equipment: [],
        loading: false,
        error: null,
        pageSize: 20,
        resultsCount: null,
        search: '',
        selectAll: false,
        sortAsc: false,
        sortCol: null,
        total: null,
        bulkActionType: 'bulk-edit',

        async init() {
            await this.fetchData();
            this.updateResultsCount();

            this.$nextTick(() => feather.replace());
            
            this.$watch('formData', () => {
                this.curPage = 1;
                this.fetchData();
            }, { deep: true });

            this.$watch('search', Alpine.debounce(() => {
                this.curPage = 1;
                this.fetchData();
            }, 300));
        },

        async fetchData() {
            this.loading = true;
            this.error = null;

            try {
                const params = new URLSearchParams({
                    page: this.curPage,
                    per_page: this.pageSize,
                });

                if (this.search) {
                    params.append('search', this.search);
                }

                if (this.formData.location && this.formData.location !== 'All') {
                    params.append('location', this.formData.location);
                }

                if (this.formData.category && this.formData.category !== 'All') {
                    params.append('category', this.formData.category);
                }

                if (this.formData.status && this.formData.status !== 'All') {
                    params.append('status', this.formData.status);
                }

                const response = await fetch(`/api/equipment?${params.toString()}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                const data = await response.json();

                this.equipment = data.items.map(item => ({
                    id: item.id,
                    name: item.name,
                    location: item.location,
                    price_per_day: item.price_per_day,
                    status: item.status,
                    image: item.image ? `/uploads/${item.image}` : 'https://picsum.photos/80/80',
                    selected: false
                }));
                this.total = data._meta.total_items;
                this.updateResultsCount();
            } catch (error) {
                this.error = error.message;
                console.error('Error fetching data:', error);
            } finally {
                setTimeout(() => {
                    feather.replace();
                }, 100);
                this.loading = false;
            }
        },

        viewPage(index) {
            this.curPage = index;
            this.fetchData();
        },

        nextPage() {
            if (this.curPage < this.totalPages()) {
                this.curPage += 1;
                this.fetchData();
            }
        },

        previousPage() {
            if (this.curPage > 1) {
                this.curPage -= 1;
                this.fetchData();
            }
        },

        totalPages() {
            return Math.ceil(this.total / this.pageSize);
        },

        pages() {
            return Array.from({ length: this.totalPages() });
        },

        sort(col) {
            if (this.sortCol === col) this.sortAsc = !this.sortAsc;
            this.sortCol = col;
            this.equipment.sort((a, b) => {
                if (a[this.sortCol] < b[this.sortCol]) return this.sortAsc ? 1 : -1;
                if (a[this.sortCol] > b[this.sortCol]) return this.sortAsc ? -1 : 1;
                return 0;
            });
        },

        updateSelectAllStatus() {
            this.selectAll = this.selectedItems.length === this.equipment.length;
        },

        toggleAllCheckbox() {
            const filteredItems = this.filtered(this.equipment);

            if (filteredItems.length === this.selectedItems.length) {
                filteredItems.forEach((item) => (item.selected = false));
            } else {
                filteredItems.forEach((item) => (item.selected = true));
            }

            this.updateSelectAllStatus();
        },

        selectAllCheckbox() {
            this.selectAll = true;
            const filteredItems = this.filtered(this.equipment);
            filteredItems.map((item) => (item.selected = true));
        },

        deselectAllCheckbox() {
            this.selectAll = false;
            const filteredItems = this.filtered(this.equipment);
            filteredItems.map((item) => (item.selected = false));
        },

        updateResultsCount() {
            const start = (this.curPage - 1) * this.pageSize + 1;
            const end = Math.min(this.curPage * this.pageSize, this.total);

            this.resultsCount = `Showing ${start} to ${end} of ${this.total} results`;
        },

        filtered(...items) {
            const values = items.shift();
            const props = items.length ? items : null;

            return values.filter((i) => {
                const y = { ...i };
                delete y.userId;

                if (props) {
                    const okeys = Object.keys(y).filter((b) => !props.includes(b));
                    okeys.map((d) => delete y[d]);
                }

                const itemToSearch = Object.values(y).join();

                return itemToSearch.toLowerCase().includes(this.search.toLowerCase());
            });
        },

        bulkAction(action) {
            if (this.selectedItems.length === 0) {
                alert('No items selected');
                return;
            }

            switch (action) {
                case 'delete':
                    if (confirm('Are you sure you want to delete the selected items?')) {
                        this.deleteSelectedItems();
                    }
                    break;
                case 'edit':
                    console.log('Editing selected items:', this.selectedItems);
                    break;
                default:
                    console.log('Unknown action:', action);
            }
        },

        async deleteSelectedItems() {
            try {
                for (const item of this.selectedItems) {
                    const response = await fetch(`/api/equipment/${item.id}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`Failed to delete item with ID ${item.id}`);
                    }
                }

                this.fetchData();
                alert('Selected items deleted successfully');
            } catch (error) {
                console.error('Error deleting items:', error);
                alert('Failed to delete selected items');
            }
        },

        async deleteItem(item) {
            if (confirm(`Are you sure you want to delete ${item.name}?`)) {
                try {
                    const response = await fetch(`/api/equipment/${item.id}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`Failed to delete item with ID ${item.id}`);
                    }

                    this.fetchData();
                    alert('Item deleted successfully');
                } catch (error) {
                    console.error('Error deleting item:', error);
                    alert('Failed to delete item');
                }
            }
        },

        async editItem(item) {
            const newName = prompt('Enter new name:', item.name);
            const newPrice = prompt('Enter new price per day:', item.price_per_day);
            const newStatus = prompt('Enter new status (available/rented):', item.status);

            if (newName === null || newPrice === null || newStatus === null) {
                return;
            }

            try {
                const response = await fetch(`/api/equipment/${item.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: newName,
                        price_per_day: parseFloat(newPrice),
                        status: newStatus
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to update item');
                }

                this.fetchData();
                alert('Item updated successfully');
            } catch (error) {
                console.error('Error updating item:', error);
                alert('Failed to update item');
            }
        },

        get selectedItems() {
            return this.equipment.filter((item) => item.selected);
        },

        get pagedItems() {
            return this.equipment;
        },

        addNewEquipment() {
            window.location.href = '/admin/equipment/add'
        }
    }));
});
