export default () => ({
    scroll: 0,
    maxScroll: 0,
    
    init() {

        this.updateMaxScroll();
        
        window.addEventListener('resize', () => {
            this.updateMaxScroll();
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
        this.scroll = Math.max(0, this.scroll - 300);
    },
    
    scrollNext() {
        this.scroll = Math.min(this.maxScroll, this.scroll + 300);
    },
    
    handleScroll(event) {
        this.scroll = event.target.scrollLeft;
    }
});