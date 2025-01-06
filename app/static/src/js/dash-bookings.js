import feather from 'feather-icons';

document.addEventListener('alpine:init', () => {
    Alpine.data('bookingDataTable', (dataSource, filterParams) => ({
        curPage: 1,
        filters: [],
        formData: {
            status: 'All',
            equipment_id: '',
            start_date: '',
            end_date: ''
        },
        bookings: [],
        loading: false,
        error: null,
        pageSize: 10,
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

                if (this.formData.status && this.formData.status !== 'All') {
                    params.append('status', this.formData.status);
                }

                if (this.formData.equipment_id) {
                    params.append('equipment_id', this.formData.equipment_id);
                }

                if (this.formData.start_date) {
                    params.append('start_date', this.formData.start_date);
                }

                if (this.formData.end_date) {
                    params.append('end_date', this.formData.end_date);
                }

                const response = await fetch(`/api/bookings?${params.toString()}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                const data = await response.json();

                this.bookings = data.items.map(item => ({
                    id: item.id,
                    start_date: item.start_date,
                    end_date: item.end_date,
                    rental_amount: item.rental_amount,
                    status: item.status,
                    equipment_name: item.equipment_name,
                    user_name: item.user_name,
                    payment_id: item.payment_id,
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
            this.bookings.sort((a, b) => {
                if (a[this.sortCol] < b[this.sortCol]) return this.sortAsc ? 1 : -1;
                if (a[this.sortCol] > b[this.sortCol]) return this.sortAsc ? -1 : 1;
                return 0;
            });
        },

        updateSelectAllStatus() {
            this.selectAll = this.selectedItems.length === this.bookings.length;
        },

        toggleAllCheckbox() {
            const filteredItems = this.filtered(this.bookings);

            if (filteredItems.length === this.selectedItems.length) {
                filteredItems.forEach((item) => (item.selected = false));
            } else {
                filteredItems.forEach((item) => (item.selected = true));
            }

            this.updateSelectAllStatus();
        },

        selectAllCheckbox() {
            this.selectAll = true;
            const filteredItems = this.filtered(this.bookings);
            filteredItems.map((item) => (item.selected = true));
        },

        deselectAllCheckbox() {
            this.selectAll = false;
            const filteredItems = this.filtered(this.bookings);
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
                    if (confirm('Are you sure you want to delete the selected bookings?')) {
                        this.deleteSelectedItems();
                    }
                    break;
                case 'edit':
                    console.log('Editing selected bookings:', this.selectedItems);
                    break;
                default:
                    console.log('Unknown action:', action);
            }
        },

        async deleteSelectedItems() {
            try {
                for (const item of this.selectedItems) {
                    const response = await fetch(`/api/bookings/${item.id}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`Failed to delete booking with ID ${item.id}`);
                    }
                }

                this.fetchData();
                alert('Selected bookings deleted successfully');
            } catch (error) {
                console.error('Error deleting bookings:', error);
                alert('Failed to delete selected bookings');
            }
        },

        async deleteItem(item) {
            if (confirm(`Are you sure you want to delete booking #${item.id}?`)) {
                try {
                    const response = await fetch(`/api/bookings/${item.id}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`Failed to delete booking with ID ${item.id}`);
                    }

                    this.fetchData();
                    alert('Booking deleted successfully');
                } catch (error) {
                    console.error('Error deleting booking:', error);
                    alert('Failed to delete booking');
                }
            }
        },

        async editItem(item) {
            const newStatus = prompt('Enter new status (pending/confirmed/cancelled):', item.status);

            if (newStatus === null) {
                return;
            }

            try {
                const response = await fetch(`/api/bookings/${item.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        status: newStatus
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to update booking');
                }

                this.fetchData();
                alert('Booking updated successfully');
            } catch (error) {
                console.error('Error updating booking:', error);
                alert('Failed to update booking');
            }
        },

        get selectedItems() {
            return this.bookings.filter((item) => item.selected);
        },

        get pagedItems() {
            return this.bookings;
        },

        addNewBooking() {
            window.location.href = '/admin/bookings/add';
        }
    }));
});
