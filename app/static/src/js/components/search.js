const searchComponent = (() => ({
    notificationOpen: false,
    sidebarOpen: false,
    search: {
        blank: false,
        count: window.search.length,
        items: window.search,
        open: false,
        term: '',
        show() {
            this.open = true;
            setTimeout(() => $focus.focus($refs.searchInput), 250);
        },
        close() {
            this.open = false;
            $refs.searchOpen.focus();
        },
        filteredItems() {
            if (this.term === '') {
                return this.items;
            }
            const result = this.items.filter((item) => {
                return item.caption
                    .replace(/ /g, '')
                    .toLowerCase()
                    .includes(this.term.replace(/ /g, '').toLowerCase());
            });
            this.blank = result.length === 0;
            this.count = result.length;
            return result;
        }
    }
}))();

export default searchComponent;
