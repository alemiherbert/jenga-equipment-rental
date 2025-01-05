import feather from 'feather-icons';

document.addEventListener('alpine:init', () => {
    Alpine.data('dataTable', (dataSource, filterParams) => ({
        curPage: 1,
        filters: [],
        formData: {
            role: 'All'
        },
        users: [],
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

                if (this.formData.role && this.formData.role !== 'All') {
                    params.append('role', this.formData.role);
                }

                const response = await fetch(`/api/users?${params.toString()}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                const data = await response.json();

                this.users = data.items.map(item => ({
                    id: item.id,
                    name: item.name,
                    email: item.email,
                    role: item.role,
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
            this.users.sort((a, b) => {
                if (a[this.sortCol] < b[this.sortCol]) return this.sortAsc ? 1 : -1;
                if (a[this.sortCol] > b[this.sortCol]) return this.sortAsc ? -1 : 1;
                return 0;
            });
        },

        updateSelectAllStatus() {
            this.selectAll = this.selectedItems.length === this.users.length;
        },

        toggleAllCheckbox() {
            const filteredItems = this.filtered(this.users);

            if (filteredItems.length === this.selectedItems.length) {
                filteredItems.forEach((item) => (item.selected = false));
            } else {
                filteredItems.forEach((item) => (item.selected = true));
            }

            this.updateSelectAllStatus();
        },

        selectAllCheckbox() {
            this.selectAll = true;
            const filteredItems = this.filtered(this.users);
            filteredItems.map((item) => (item.selected = true));
        },

        deselectAllCheckbox() {
            this.selectAll = false;
            const filteredItems = this.filtered(this.users);
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
                    if (confirm('Are you sure you want to delete the selected users?')) {
                        this.deleteSelectedItems();
                    }
                    break;
                case 'edit':
                    console.log('Editing selected users:', this.selectedItems);
                    break;
                default:
                    console.log('Unknown action:', action);
            }
        },

        async deleteSelectedItems() {
            try {
                for (const item of this.selectedItems) {
                    const response = await fetch(`/api/users/${item.id}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`Failed to delete user with ID ${item.id}`);
                    }
                }

                this.fetchData();
                alert('Selected users deleted successfully');
            } catch (error) {
                console.error('Error deleting users:', error);
                alert('Failed to delete selected users');
            }
        },

        async deleteItem(item) {
            if (confirm(`Are you sure you want to delete ${item.name}?`)) {
                try {
                    const response = await fetch(`/api/users/${item.id}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`Failed to delete user with ID ${item.id}`);
                    }

                    this.fetchData();
                    alert('User deleted successfully');
                } catch (error) {
                    console.error('Error deleting user:', error);
                    alert('Failed to delete user');
                }
            }
        },

        async editItem(item) {
            const newName = prompt('Enter new name:', item.name);
            const newEmail = prompt('Enter new email:', item.email);
            const newRole = prompt('Enter new role:', item.role);

            if (newName === null || newEmail === null || newRole === null) {
                return;
            }

            try {
                const response = await fetch(`/api/users/${item.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: newName,
                        email: newEmail,
                        role: newRole
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to update user');
                }

                this.fetchData();
                alert('User updated successfully');
            } catch (error) {
                console.error('Error updating user:', error);
                alert('Failed to update user');
            }
        },

        get selectedItems() {
            return this.users.filter((item) => item.selected);
        },

        get pagedItems() {
            return this.users;
        },

        addNewUser() {
            window.location.href = '/admin/users/add';
        }
    }));
});