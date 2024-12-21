import './site-navigation';
import './theme-switcher';
import './theme-detection';
import Alpine from 'alpinejs';
import focus from '@alpinejs/focus'
import searchComponent from './components/search';

window.Alpine = Alpine;
window.searchComponent = searchComponent;
Alpine.plugin(focus)
Alpine.start();