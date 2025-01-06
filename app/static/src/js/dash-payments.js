import feather from 'feather-icons';

document.addEventListener('alpine:init', () => {
    Alpine.data('paymentDataTable', (dataSource, filterParams) => ({
        curPage: 1,
        filters: [],
        formData: {
            status: 'All',
            min_amount: '',
            max_amount: '',
            start_date: '',
            end_date: ''
        },
        payments: [],
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
        
                if (this.formData.min_amount) {
                    params.append('min_amount', this.formData.min_amount);
                }
        
                if (this.formData.max_amount) {
                    params.append('max_amount', this.formData.max_amount);
                }
        
                if (this.formData.start_date) {
                    params.append('start_date', this.formData.start_date);
                }
        
                if (this.formData.end_date) {
                    params.append('end_date', this.formData.end_date);
                }
        
                const response = await fetch(`/api/payments?${params.toString()}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                const data = await response.json();
        
                this.payments = data.items.map(item => ({
                    id: item.id,
                    total_amount: item.total_amount,
                    currency: item.currency,
                    status: item.status,
                    created_at: item.created_at,
                    user_name: item.user_name,
                    user_id: item.user_id,
                    payment_reference: item.payment_reference,
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
            this.payments.sort((a, b) => {
                if (a[this.sortCol] < b[this.sortCol]) return this.sortAsc ? 1 : -1;
                if (a[this.sortCol] > b[this.sortCol]) return this.sortAsc ? -1 : 1;
                return 0;
            });
        },

        updateSelectAllStatus() {
            this.selectAll = this.selectedItems.length === this.payments.length;
        },

        toggleAllCheckbox() {
            const filteredItems = this.filtered(this.payments);

            if (filteredItems.length === this.selectedItems.length) {
                filteredItems.forEach((item) => (item.selected = false));
            } else {
                filteredItems.forEach((item) => (item.selected = true));
            }

            this.updateSelectAllStatus();
        },

        selectAllCheckbox() {
            this.selectAll = true;
            const filteredItems = this.filtered(this.payments);
            filteredItems.map((item) => (item.selected = true));
        },

        deselectAllCheckbox() {
            this.selectAll = false;
            const filteredItems = this.filtered(this.payments);
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
                    if (confirm('Are you sure you want to delete the selected payments?')) {
                        this.deleteSelectedItems();
                    }
                    break;
                case 'edit':
                    console.log('Editing selected payments:', this.selectedItems);
                    break;
                default:
                    console.log('Unknown action:', action);
            }
        },

        async deleteSelectedItems() {
            try {
                for (const item of this.selectedItems) {
                    const response = await fetch(`/api/payments/${item.id}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`Failed to delete payment with ID ${item.id}`);
                    }
                }

                this.fetchData();
                alert('Selected payments deleted successfully');
            } catch (error) {
                console.error('Error deleting payments:', error);
                alert('Failed to delete selected payments');
            }
        },

        async deleteItem(item) {
            if (confirm(`Are you sure you want to delete payment #${item.id}?`)) {
                try {
                    const response = await fetch(`/api/payments/${item.id}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`Failed to delete payment with ID ${item.id}`);
                    }

                    this.fetchData();
                    alert('Payment deleted successfully');
                } catch (error) {
                    console.error('Error deleting payment:', error);
                    alert('Failed to delete payment');
                }
            }
        },

        async editItem(item) {
            const newStatus = prompt('Enter new status (pending/succeeded/failed/refunded):', item.status);

            if (newStatus === null) {
                return;
            }

            try {
                const response = await fetch(`/api/payments/${item.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        status: newStatus
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to update payment');
                }

                this.fetchData();
                alert('Payment updated successfully');
            } catch (error) {
                console.error('Error updating payment:', error);
                alert('Failed to update payment');
            }
        },

        get selectedItems() {
            return this.payments.filter((item) => item.selected);
        },

        get pagedItems() {
            return this.payments;
        }
    }));
});