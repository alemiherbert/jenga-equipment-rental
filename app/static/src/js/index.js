import Alpine from 'alpinejs';
import focus from '@alpinejs/focus'
import searchComponent from './components/search';
import './theme-switcher';
import './theme-detection';

window.Alpine = Alpine;
window.searchComponent = searchComponent;
Alpine.plugin(focus)
Alpine.start();