export default () => ({
    scroll: 0,
    maxScroll: 0,
    
    init() {
        this.maxScroll = this.$refs.container.scrollWidth - this.$refs.container.clientWidth;
        
        window.addEventListener('resize', () => {
            this.maxScroll = this.$refs.container.scrollWidth - this.$refs.container.clientWidth;
        });
        
        this.$watch('scroll', value => {
            this.$refs.container.scrollTo({ 
                left: value, 
                behavior: 'smooth' 
            });
        });
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